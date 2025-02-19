import numpy as np
import cv2
from keras_facenet import FaceNet
from database import db, fs
from PIL import Image

# Load FaceNet Model (Automatically handles face detection)
embedder = FaceNet()

def extract_face_embedding(image_path):
    try:
        # ✅ Load image with PIL to ensure correct format
        image = Image.open(image_path).convert("RGB")
        
        # ✅ Resize image to 160x160 for FaceNet
        image = image.resize((320, 320))  # Resize to 160 *1320instead of 160x160  
        
        # ✅ Convert to NumPy array
        image = np.array(image)

        # ✅ Convert RGB image to OpenCV BGR format
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Detect faces & extract embeddings
        detections = embedder.extract(image, threshold=0.20)
        print("🔍 Detections:", detections)  # Debugging

        if not detections or len(detections) == 0:
            print("❌ No face detected.")
            return None

        embeddings = [d["embedding"].tolist() for d in detections]  # ✅ Convert to list before saving
        print(f"✅ Extracted {len(embeddings)} face embeddings.")
        return embeddings

    except Exception as e:
        print(f"❌ Error extracting face embedding: {e}")
        return None
