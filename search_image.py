import sys
from face_matching import match_faces
from retrieve_image import download_image
from database import db

def search_image(image_path, event=None, date=None):
    """
    Search for matching faces in the database with optional event & date filters.
    """
    matches = match_faces(image_path)

    if not matches:
        print("❌ No matching images found.")
        return []

    # Apply Event & Date Filtering
    filtered_matches = []
    for match in matches:
        record = db.image_metadata.find_one({"image_id": match["image_id"]})
        if record:
            if event and record["event"].lower() != event.lower():
                continue
            if date and record["date"] != date:
                continue
            filtered_matches.append(match)

    print(f"✅ Found {len(filtered_matches)} filtered matches.")
    return filtered_matches

# Run from CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_image.py <image_path> [<event_name>] [<YYYY-MM-DD>]")
        sys.exit(1)

    event_name = sys.argv[2] if len(sys.argv) > 2 else None
    search_date = sys.argv[3] if len(sys.argv) > 3 else None
    search_image(sys.argv[1], event_name, search_date)
