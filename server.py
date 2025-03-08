import os
import time
import datetime
import io
from flask import Flask, request, render_template, jsonify, send_file, Response, url_for
from werkzeug.utils import secure_filename
from database import fs, db, redis_client
from face_recognition import extract_face_embedding
from face_matching import match_faces
from bson import ObjectId
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define the maximum number of images to store
MAX_IMAGES = 50
def delete_oldest_images():
    """
    Delete the oldest images if the total exceeds MAX_IMAGES.
    """
    total_images = db.image_metadata.count_documents({})
    if total_images >= MAX_IMAGES:
        images_to_delete = total_images - MAX_IMAGES + 1  # Ensure space for the new image
        oldest_images = db.image_metadata.find().sort("uploaded_at", 1).limit(images_to_delete)
        for image in oldest_images:
            fs.delete(ObjectId(image["image_id"]))
            db.image_metadata.delete_one({"_id": image["_id"]})
        print(f" Deleted {images_to_delete} oldest images to maintain storage limit.")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        images = request.files.getlist("images[]")
        event = request.form.get("event")
        date = request.form.get("date")
        department = request.form.get("department")
        district = request.form.get("district")

        if not images or not event or not date or not department or not district:
            return jsonify({"status": "error", "message": "All fields are required."}), 400

        for image in images:
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(image_path)

                # Ensure storage limit is not exceeded
                delete_oldest_images()

                # Store in GridFS
                with open(image_path, "rb") as img_file:
                    image_data = img_file.read()
                image_id = fs.put(image_data, filename=filename, event=event, date=date, department=department, district=district)

                # Extract Face Embeddings
                embeddings = extract_face_embedding(image_path)

                if not embeddings:
                    return jsonify({"status": "error", "message": f"No face detected in image {filename}."}), 400

                # Save metadata
                db.image_metadata.insert_one({
                    "image_id": str(image_id),
                    "event": event,
                    "date": date,
                    "department": department,
                    "district": district,
                    "face_embeddings": embeddings,
                    "uploaded_at": datetime.datetime.utcnow()
                })

        return jsonify({"status": "success", "message": "Images uploaded successfully."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/search", methods=["POST"])
def search_image():
    try:
        start_time = time.time()
        image = request.files.get("image")
        event = request.form.get("event")
        date = request.form.get("date")
        department = request.form.get("department")
        district = request.form.get("district")

        if not image:
            return jsonify({"status": "error", "message": "Image is required for search."}), 400

        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

        # Check Redis cache first
        cache_key = f"search:{filename}:{event}:{date}:{department}:{district}"
        cached_results = redis_client.get(cache_key)

        if cached_results:
            print("✅ Using Cached Search Results")
            results = eval(cached_results.decode())
        else:
            results = match_faces(image_path, event, date, department, district)

            # Generate full URLs for image retrieval
            for match in results.get("matches", []):
                image_id = match["image_id"]
                match["image_url"] = url_for('get_image', image_id=image_id, _external=True)
                match["download_url"] = url_for('download_image', image_id=image_id, _external=True)

            redis_client.setex(cache_key, 3600, str(results))

        end_time = time.time()
        return jsonify({
            "status": results["status"],
            "matches": results.get("matches", []),
            "processing_time": f"{end_time - start_time:.2f} sec"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/download/<image_id>")
def download_image(image_id):
    try:
        file_id = ObjectId(image_id)
        image_data = fs.get(file_id).read()

        return send_file(
            io.BytesIO(image_data),
            mimetype="image/jpeg",
            as_attachment=True,
            download_name=f"{image_id}.jpg"
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404

@app.route("/get_image/<image_id>")
def get_image(image_id):
    """
    Retrieve and return an image from GridFS.
    """
    try:
        file_id = ObjectId(image_id)
        image_data = fs.get(file_id)

        response = Response(image_data.read(), mimetype="image/jpeg")
        response.headers["Content-Disposition"] = f'inline; filename="{image_data.filename}"'

        return response

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404

@app.route("/view/<image_id>")
def view_image(image_id):
    try:
        image_data = fs.get(ObjectId(image_id)).read()
        return send_file(io.BytesIO(image_data), mimetype="image/jpeg")
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404

if __name__ == "__main__":
    # Determine the environment mode
    env_mode = os.getenv('FLASK_ENV', 'development')
    if env_mode == 'development':
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        # Production settings
        app.run(debug=False, host='0.0.0.0', port=5000)
