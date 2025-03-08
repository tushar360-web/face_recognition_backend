import numpy as np
from database import db, fs, redis_client
from face_recognition import extract_face_embedding
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import hashlib

def match_faces(image_path, event=None, date=None, department=None, district=None, threshold=0.50):
    """
    Match uploaded image against stored face embeddings with caching.
    Returns the matched images' metadata.
    """
    try:
        # Extract embedding from uploaded image
        query_embeddings = extract_face_embedding(image_path)
        if query_embeddings is None:
            print("❌ No face detected in uploaded image.")
            return {"status": "error", "message": "No face detected."}

        matched_images = []

        # Generate a unique cache key based on query image and filters
        query_hash = hashlib.md5(open(image_path, "rb").read()).hexdigest()
        cache_key = f"search:{query_hash}:{event}:{date}:{department}:{district}"

        # Check if results are already cached in Redis
        cached_results = redis_client.get(cache_key)
        if cached_results:
            print("✅ Using Cached Search Results")
            return pickle.loads(cached_results)

        # Build the query filter
        query_filter = {}
        if event:
            query_filter["event"] = event
        if date:
            query_filter["date"] = date
        if department:
            query_filter["department"] = department
        if district:
            query_filter["district"] = district

        # Retrieve stored images from MongoDB based on filters
        for record in db.image_metadata.find(query_filter):
            stored_embeddings = record.get("face_embeddings")
            if stored_embeddings:
                for stored_embedding in stored_embeddings:
                    # Convert stored embeddings (lists) back to NumPy arrays
                    stored_embedding = np.array(stored_embedding, dtype=np.float32)

                    similarity = cosine_similarity([query_embeddings[0]], [stored_embedding])[0][0]
                    if similarity >= threshold:
                        matched_images.append({
                            "image_id": str(record["image_id"]),  # Convert ObjectId to string
                            "event": record["event"],
                            "date": record["date"],
                            "department": record.get("department"),
                            "district": record.get("district"),
                            "similarity": round(float(similarity), 4)  # Convert to float and round
                        })

        if matched_images:
            matched_images = sorted(matched_images, key=lambda x: x["similarity"], reverse=True)
            print(f"✅ Found {len(matched_images)} matching images.")

            # Store results in Redis Cache for 1 hour
            redis_client.setex(cache_key, 3600, pickle.dumps(matched_images))
        else:
            print("❌ No matching images found.")

        return {"status": "success", "matches": matched_images}

    except Exception as e:
        print(f"❌ Error matching faces: {e}")
        return {"status": "error", "message": str(e)}
