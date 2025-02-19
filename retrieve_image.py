import sys
import io
from database import fs
from PIL import Image

def download_image(image_id, output_path):
    """
    Download image from GridFS using image_id and save as a file.
    """
    try:
        # Fetch image from GridFS
        image_data = fs.get(image_id).read()

        # Convert bytes to image
        img = Image.open(io.BytesIO(image_data))
        img.save(output_path)

        print(f"✅ Image downloaded successfully as {output_path}")

    except Exception as e:
        print(f"❌ Error downloading image: {e}")

# Run from CLI
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python retrieve_image.py <image_id> <output_path>")
        sys.exit(1)

    download_image(sys.argv[1], sys.argv[2])
