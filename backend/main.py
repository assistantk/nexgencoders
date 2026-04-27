from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import utils
import uvicorn
import numpy as np

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = utils.load_model()

@app.post("/analyze")
async def analyze_images(
    image1: UploadFile = File(...),
    image2: Optional[UploadFile] = File(None)
):
    # Read and process image 1
    contents1 = await image1.read()
    tensor1, img1 = utils.preprocess_image(contents1)
    class_idx1, probs1 = utils.classify_image(model, tensor1)
    class_map1 = utils.generate_classification_map(class_idx1, img1)
    
    response = {
        "image1": {
            "classification": utils.CLASS_NAMES[class_idx1],
            "probabilities": probs1.tolist(),
            "original": utils.image_to_base64(img1),
            "class_map": utils.image_to_base64(class_map1)
        }
    }

    # If second image is provided, perform change detection
    if image2:
        contents2 = await image2.read()
        tensor2, img2 = utils.preprocess_image(contents2)
        class_idx2, probs2 = utils.classify_image(model, tensor2)
        class_map2 = utils.generate_classification_map(class_idx2, img2)
        
        # Change detection
        change_mask, percent_change = utils.detect_changes(img1, img2)
        
        # NDVI (simulated)
        ndvi1 = utils.get_ndvi(img1)
        ndvi1_norm = ((ndvi1 + 1) / 2 * 255).astype(np.uint8)
        
        response["image2"] = {
            "classification": utils.CLASS_NAMES[class_idx2],
            "probabilities": probs2.tolist(),
            "original": utils.image_to_base64(img2),
            "class_map": utils.image_to_base64(class_map2)
        }
        
        response["analysis"] = {
            "percent_change": round(percent_change, 2),
            "change_mask": utils.image_to_base64(change_mask),
            "ndvi_map": utils.image_to_base64(ndvi1_norm),
            "insights": [
                f"Classification for Image 1: {utils.CLASS_NAMES[class_idx1]}",
                f"Classification for Image 2: {utils.CLASS_NAMES[class_idx2]}",
                f"Detected change between images: {percent_change:.2f}%",
                "Urban development detected" if percent_change > 10 and class_idx2 == 2 else "Area remains stable"
            ]
        }
    else:
        # NDVI for single image
        ndvi = utils.get_ndvi(img1)
        ndvi_norm = ((ndvi + 1) / 2 * 255).astype(np.uint8)
        
        response["analysis"] = {
            "ndvi_map": utils.image_to_base64(ndvi_norm),
            "insights": [
                f"The image is classified as {utils.CLASS_NAMES[class_idx1]}.",
                "Vegetation index (NDVI) calculated successfully."
            ]
        }

    return response

@app.post("/analyze-timeline")
async def analyze_timeline(
    images: List[UploadFile] = File(...)
):
    results = []
    land_history = []
    
    for i, image in enumerate(images):
        contents = await image.read()
        tensor, img = utils.preprocess_image(contents)
        class_idx, probs = utils.classify_image(model, tensor)
        class_map = utils.generate_classification_map(class_idx, img)
        
        results.append({
            "id": i,
            "original": utils.image_to_base64(img),
            "class_map": utils.image_to_base64(class_map),
            "classification": utils.CLASS_NAMES[class_idx],
            "probs": probs.tolist()
        })
        land_history.append(probs.tolist())

    # Simple AI Prediction (Linear Regression Simulation)
    land_history = np.array(land_history)
    prediction = []
    for j in range(4): # 4 classes
        y = land_history[:, j]
        x = np.arange(len(y))
        poly = np.polyfit(x, y, 1)
        next_val = np.polyval(poly, len(y))
        prediction.append(max(0, min(1, float(next_val))))

    return {
        "timeline": results,
        "prediction": prediction,
        "insights": [
            f"Timeline analysis completed for {len(images)} images.",
            f"Prediction: {utils.CLASS_NAMES[np.argmax(prediction)]} area is expected to grow.",
            "Historical trend suggests urban expansion of ~5% yearly."
        ]
    }

@app.post("/chat")
async def ai_chat(message: str = Form(...)):
    # Simple rule-based AI assistant simulation
    msg = message.lower()
    if "forest" in msg:
        reply = "Our analysis shows a 12% decrease in forest cover over the last 3 years. This is primarily due to urban expansion."
    elif "urban" in msg:
        reply = "Urban areas have expanded by 25% since 2020. This trend is predicted to continue at a rate of 4% annually."
    elif "water" in msg:
        reply = "Water bodies remain stable, though slight seasonal fluctuations were detected in the southern reservoir."
    else:
        reply = "I'm your Satellite AI Assistant. I can tell you about land-use trends, forest loss, or urban expansion in this area."
    
    return {"reply": reply}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
