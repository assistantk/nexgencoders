 Satellite Image Analysis System 🛰️

A complete full-stack application for analyzing satellite imagery using AI. This system performs land use classification, change detection between two time periods, and provides environmental insights like NDVI.

## 🚀 Features
- **Land Use Classification:** Detects Water, Forest, Urban, and Agriculture.
- **Change Detection:** Compare two images and highlight changes with percentage calculation.
- **NDVI Analysis:** Simulated Vegetation Index calculation.
- **Interactive Dashboard:** Modern dark-themed UI with Chart.js visualizations.
- **AI-Powered:** Custom CNN model built with PyTorch.

## 🛠️ Tech Stack
- **Backend:** FastAPI (Python)
- **AI/ML:** PyTorch, OpenCV, NumPy
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Chart.js
- **Environment:** Windows/Linux/macOS

## 📂 Project Structure
```
nexGencoders/
├── ai_model/          # AI Model definition and training scripts
│   ├── model.py       # CNN Architecture
│   ├── train.py       # Training script
│   └── satellite_model.pth # Trained weights
├── backend/           # FastAPI Backend
│   ├── main.py        # API Endpoints
│   └── utils.py       # Image processing helpers
├── frontend/          # Web Interface
│   ├── index.html
│   ├── style.css
│   └── script.js
├── requirements.txt   # Python dependencies
└── README.md
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.8+
- Node.js (Optional, only if using advanced frontend frameworks)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Train the Model (Optional)
The system comes with a training script. You can run it to generate the initial model weights:
```bash
python ai_model/train.py
```

### 4. Run the Backend
```bash
cd backend
python main.py
```
The API will be available at `http://localhost:8000`.

### 5. Run the Frontend
Simply open `frontend/index.html` in your web browser.

---

## 🎓 Suggestions for MIT-Level Improvement
To elevate this project to an elite academic level, consider these enhancements:

1. **Transfer Learning:** Instead of a simple CNN, use a pre-trained **ResNet-50** or **EfficientNet** fine-tuned on the **EuroSAT** or **BigEarthNet** datasets.
2. **U-Net for Segmentation:** Implement a **U-Net** architecture for pixel-level semantic segmentation instead of whole-image classification.
3. **Real Satellite Data API:** Integrate the **Sentinel-Hub API** or **Google Earth Engine API** to fetch real-time satellite imagery for any coordinate.
4. **Time-Series Analysis:** Add support for multiple images over time to plot land-use trends over years (e.g., deforestation tracking).
5. **Atmospheric Correction:** Implement algorithms like **DOS (Dark Object Subtraction)** to correct for haze and clouds in raw satellite data.
6. **Dockerization:** Use Docker and Docker Compose to containerize the entire stack for easy deployment.

---
Built with ❤️ by NexGencoders
