import cv2
import numpy as np
import torch
import sys
import os
from PIL import Image
import io
import base64

# Add ai_model directory to path to import SatelliteCNN
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai_model')))
from model import SatelliteCNN

# Define colors for classification
CLASS_COLORS = {
    0: (255, 0, 0),    # Water -> Blue (OpenCV uses BGR, so this is actually Red if not careful, let's use RGB for now and convert)
    1: (0, 255, 0),    # Forest -> Green
    2: (128, 128, 128), # Urban -> Gray
    3: (0, 255, 255)   # Agriculture -> Yellow
}

CLASS_NAMES = {
    0: "Water",
    1: "Forest",
    2: "Urban",
    3: "Agriculture"
}

def load_model():
    model = SatelliteCNN(num_classes=4)
    model_path = os.path.join(os.path.dirname(__file__), '..', 'ai_model', 'satellite_model.pth')
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
    model.eval()
    return model

def preprocess_image(image_bytes):
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize to 64x64 for the model
    img_resized = cv2.resize(img, (64, 64))
    
    # Normalize
    img_normalized = img_resized.astype(np.float32) / 255.0
    
    # Convert to torch tensor (C, H, W)
    tensor = torch.from_numpy(img_normalized).permute(2, 0, 1).unsqueeze(0)
    return tensor, img

def classify_image(model, tensor):
    with torch.no_grad():
        output = model(tensor)
        probabilities = torch.softmax(output, dim=1)
        prediction = torch.argmax(probabilities, dim=1).item()
    return prediction, probabilities.numpy()[0]

def get_ndvi(image_rgb):
    # Simplified NDVI calculation (usually requires Near-Infrared band)
    # Here we simulate it using Green and Red bands as a placeholder
    # NDVI = (NIR - Red) / (NIR + Red)
    # For simulation: (Green - Red) / (Green + Red + epsilon)
    r = image_rgb[:, :, 0].astype(float)
    g = image_rgb[:, :, 1].astype(float)
    ndvi = (g - r) / (g + r + 1e-10)
    return ndvi

def generate_classification_map(prediction_idx, image_rgb):
    # Create a colored map based on classification
    h, w, _ = image_rgb.shape
    color = CLASS_COLORS[prediction_idx]
    
    # Create a solid color map
    color_map = np.full((h, w, 3), color, dtype=np.uint8)
    
    # Blend with original image for transparency
    alpha = 0.5
    blended = cv2.addWeighted(image_rgb, 1 - alpha, color_map, alpha, 0)
    return blended

def detect_changes(img1, img2):
    # Ensure same size
    img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Difference
    diff = cv2.absdiff(img1, img2_resized)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
    
    # Threshold to find significant changes
    _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
    
    # Highlight changed regions in red
    change_highlight = img2_resized.copy()
    change_highlight[thresh > 0] = [255, 0, 0] # Red in RGB
    
    # Calculate % change
    change_pixels = np.count_nonzero(thresh)
    total_pixels = thresh.size
    percent_change = (change_pixels / total_pixels) * 100
    
    return change_highlight, percent_change

def image_to_base64(img_array):
    # Check if grayscale (like NDVI)
    if len(img_array.shape) == 2:
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
    else:
        # Convert RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    _, buffer = cv2.imencode('.png', img_bgr)
    return base64.b64encode(buffer).decode('utf-8')
