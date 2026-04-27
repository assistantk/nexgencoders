document.addEventListener('DOMContentLoaded', () => {
    // Check Authentication
    if (localStorage.getItem('isLoggedIn') !== 'true') {
        window.location.href = 'login.html';
    }

    // Initialize icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.onclick = () => {
            localStorage.removeItem('isLoggedIn');
            window.location.href = 'login.html';
        };
    }

    const resultsSection = document.getElementById('results-section');
    const loader = document.getElementById('loader');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatBox = document.getElementById('chat-box');
    const mapSearchInput = document.getElementById('map-search-input');
    const mapSearchBtn = document.getElementById('map-search-btn');
    const captureBtn = document.getElementById('capture-image-btn');
    const liveMonitorBtn = document.getElementById('live-monitor-btn');
    
    let chartInstance = null;
    let predChartInstance = null;
    let timelineData = [];
    let map = null;
    let liveMonitorInterval = null;

    // --- Map Initialization ---
    const initMap = () => {
        const defaultLoc = [37.3382, -121.8863];
        map = L.map('satellite-map', {
            center: defaultLoc,
            zoom: 16,
            crossOrigin: true
        });

        L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
            maxZoom: 20,
            subdomains:['mt0','mt1','mt2','mt3'],
            attribution: 'Google Maps Satellite'
        }).addTo(map);

        // Update Telemetry on Map Move
        map.on('move', () => {
            const center = map.getCenter();
            document.getElementById('tel-lat').innerText = center.lat.toFixed(4);
            document.getElementById('tel-lon').innerText = center.lng.toFixed(4);
            document.getElementById('tel-alt').innerText = Math.round(20000 / map.getZoom());
        });
    };

    initMap();

    // --- Live Monitor Toggle ---
    liveMonitorBtn.onclick = () => {
        if (liveMonitorInterval) {
            clearInterval(liveMonitorInterval);
            liveMonitorInterval = null;
            liveMonitorBtn.innerHTML = '<i data-lucide="radio"></i> Start Live Monitor';
            liveMonitorBtn.classList.remove('active');
        } else {
            liveMonitorBtn.innerHTML = '<i data-lucide="pause"></i> Stop Live Monitor';
            liveMonitorBtn.classList.add('active');
            // Auto-capture every 10 seconds
            liveMonitorInterval = setInterval(() => {
                captureBtn.click();
            }, 10000);
            captureBtn.click(); // Immediate first capture
        }
        lucide.createIcons();
    };

    // --- Map Search ---
    mapSearchBtn.onclick = async () => {
        const query = mapSearchInput.value;
        if (!query) return;

        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`);
            const data = await res.json();
            if (data.length > 0) {
                const { lat, lon } = data[0];
                map.setView([lat, lon], 16);
            } else {
                alert('Location not found.');
            }
        } catch (e) {
            console.error('Search error:', e);
        }
    };

    // --- Map Capture & Analysis ---
    captureBtn.onclick = async () => {
        captureBtn.disabled = true;
        captureBtn.innerHTML = '<i data-lucide="loader" class="spin"></i> Analyzing...';
        lucide.createIcons();
        loader.classList.remove('hidden');

        const mapElement = document.getElementById('satellite-map');
        
        try {
            const canvas = await html2canvas(mapElement, {
                useCORS: true,
                allowTaint: false,
                ignoreElements: (el) => el.classList.contains('leaflet-control-container')
            });

            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.95));
            const file = new File([blob], "captured_satellite.jpg", { type: "image/jpeg" });
            
            const formData = new FormData();
            formData.append('image1', file);

            const response = await fetch('http://localhost:8002/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Backend error');
            const data = await response.json();
            
            displayResults(data);
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            drawHeatmap(data.image1.probabilities);
        } catch (e) {
            console.error('Analysis error:', e);
            alert('Analysis failed. Ensure the backend is running on port 8002.');
        } finally {
            captureBtn.disabled = false;
            captureBtn.innerHTML = '<i data-lucide="camera"></i> Analyze Current View';
            lucide.createIcons();
            loader.classList.add('hidden');
        }
    };

    // --- Slider Logic ---
    const initSlider = () => {
        const slider = document.querySelector('.comparison-slider');
        const handle = document.querySelector('.handle');
        const resize = document.querySelector('.resize');
        let active = false;

        const move = (e) => {
            if (!active) return;
            let x = e.type === 'touchmove' ? e.touches[0].pageX : e.pageX;
            let rect = slider.getBoundingClientRect();
            let pos = ((x - rect.left) / rect.width) * 100;
            if (pos < 0) pos = 0;
            if (pos > 100) pos = 100;
            handle.style.left = pos + '%';
            resize.style.width = pos + '%';
        };

        handle.addEventListener('mousedown', () => active = true);
        window.addEventListener('mouseup', () => active = false);
        window.addEventListener('mousemove', move);
        
        handle.addEventListener('touchstart', () => active = true);
        window.addEventListener('touchend', () => active = false);
        window.addEventListener('touchmove', move);
    };

    function displayResults(data) {
        document.getElementById('slider-before').src = `data:image/png;base64,${data.image1.original}`;
        if (data.image2) {
            document.getElementById('slider-after').src = `data:image/png;base64,${data.image2.original}`;
            document.getElementById('slider-card').classList.remove('hidden');
            initSlider();
        } else {
            document.getElementById('slider-card').classList.add('hidden');
        }

        document.getElementById('res-img-1').src = `data:image/png;base64,${data.image1.class_map}`;
        document.getElementById('class-label-1').innerText = `Location Map: ${data.image1.classification}`;

        const resImgBox2 = document.getElementById('res-img-box-2');
        if (data.image2) {
            resImgBox2.classList.remove('hidden');
            document.getElementById('res-img-2').src = `data:image/png;base64,${data.image2.class_map}`;
            document.getElementById('class-label-2').innerText = `Location Map 2: ${data.image2.classification}`;
        } else {
            resImgBox2.classList.add('hidden');
        }

        const changeCard = document.getElementById('change-card');
        if (data.analysis.change_mask) {
            changeCard.classList.remove('hidden');
            document.getElementById('change-mask').src = `data:image/png;base64,${data.analysis.change_mask}`;
            document.getElementById('percent-change').innerText = `${data.analysis.percent_change}%`;
        } else {
            changeCard.classList.add('hidden');
        }

        const insightsList = document.getElementById('insights-list');
        insightsList.innerHTML = '';
        data.analysis.insights.forEach(insight => {
            const div = document.createElement('div');
            div.className = 'insight-item';
            div.innerText = insight;
            insightsList.appendChild(div);
        });

        updateChart(data.image1.probabilities);
    }

    function displayTimeline(data) {
        timelineData = data.timeline;
        const range = document.getElementById('timeline-range');
        const img = document.getElementById('timeline-img');
        const section = document.getElementById('timeline-section');
        
        section.classList.remove('hidden');
        range.max = timelineData.length - 1;
        range.value = 0;
        img.src = `data:image/png;base64,${timelineData[0].original}`;

        range.oninput = (e) => {
            const frame = timelineData[e.target.value];
            img.src = `data:image/png;base64,${frame.original}`;
        };
    }

    function displayPrediction(pred) {
        const labels = ['Water', 'Forest', 'Urban', 'Agriculture'];
        const maxIdx = pred.indexOf(Math.max(...pred));
        document.getElementById('growth-pred').innerText = `${labels[maxIdx]} Growth Predicted`;
        
        const ctx = document.getElementById('prediction-chart').getContext('2d');
        if (predChartInstance) predChartInstance.destroy();
        
        predChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Current', 'Next Year', '+5 Years'],
                datasets: [{
                    label: 'Predicted Trend',
                    data: [pred[maxIdx] * 0.8, pred[maxIdx], pred[maxIdx] * 1.2],
                    borderColor: '#f59e0b',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(245, 158, 11, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { display: false }, x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } } }
            }
        });
    }

    // --- Chat Logic ---
    chatSend.onclick = async () => {
        const text = chatInput.value;
        if (!text) return;
        
        const userDiv = document.createElement('div');
        userDiv.className = 'user-msg';
        userDiv.innerText = text;
        chatBox.appendChild(userDiv);
        chatInput.value = '';

        const formData = new FormData();
        formData.append('message', text);
        
        const res = await fetch('http://localhost:8002/chat', { method: 'POST', body: formData });
        const data = await res.json();
        
        const aiDiv = document.createElement('div');
        aiDiv.className = 'ai-msg';
        aiDiv.innerText = data.reply;
        chatBox.appendChild(aiDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // --- Heatmap Logic ---
    function drawHeatmap(probs) {
        const canvas = document.getElementById('heatmap-canvas');
        const ctx = canvas.getContext('2d');
        const width = canvas.offsetWidth;
        const height = canvas.offsetHeight;
        canvas.width = width;
        canvas.height = height;

        const colors = ['#38bdf8', '#22c55e', '#94a3b8', '#f59e0b'];
        probs.forEach((p, i) => {
            ctx.fillStyle = colors[i];
            ctx.globalAlpha = p;
            ctx.beginPath();
            ctx.arc(Math.random() * width, Math.random() * height, p * 100, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    function updateChart(probs) {
        const ctx = document.getElementById('distribution-chart').getContext('2d');
        if (chartInstance) chartInstance.destroy();
        chartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Water', 'Forest', 'Urban', 'Agriculture'],
                datasets: [{
                    data: probs,
                    backgroundColor: ['#38bdf8', '#22c55e', '#94a3b8', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#f8fafc' } } }
            }
        });
    }
});
