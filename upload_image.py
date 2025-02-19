import os
import sys
import datetime
from database import fs, db
from PIL import Image
import io
from face_recognition import extract_face_embedding

def upload_image(image_path, event, date):
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file '{image_path}' not found.")
        return
    
    try:
        # Open Image
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()

        # Store image in GridFS
        image_id = fs.put(image_data, filename=os.path.basename(image_path), event=event, date=date)

        # Extract Face Embeddings
        embeddings = extract_face_embedding(image_path)

        # Store metadata in a collection
        db.image_metadata.insert_one({
            "image_id": image_id,
            "event": event,
            "date": date,
            "face_embeddings": embeddings,
            "uploaded_at": datetime.datetime.utcnow()
        })

        print(f"✅ Image uploaded successfully with ID: {image_id}")
    
    except Exception as e:
        print(f"❌ Error uploading image: {e}")

# Run from CLI
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python upload_image.py <image_path> <event_name> <YYYY-MM-DD>")
        sys.exit(1)

    upload_image(sys.argv[1], sys.argv[2], sys.argv[3])
