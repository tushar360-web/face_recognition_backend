import os
import time
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from flask import Response
from database import fs, db, redis_client  # Redis added
from face_recognition import extract_face_embedding
from face_matching import match_faces
import datetime
import io
from PIL import Image
from bson import ObjectId
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # you want to allow all origins (Not recommended for production)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/upload", methods=["POST"]) 
def upload_image():
    try:
        image = request.files["image"]
        event = request.form["event"]
        date = request.form["date"]

        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

            # Store in GridFS
            with open(image_path, "rb") as img_file:
                image_data = img_file.read()
            image_id = fs.put(image_data, filename=filename, event=event, date=date)

            # Extract Face Embeddings
            embeddings = extract_face_embedding(image_path)

            if not embeddings or len(embeddings) == 0:
                return jsonify({"status": "error", "message": "No face detected in image."})

            # ✅ FIX: Save embeddings directly, no `.tolist()` needed
            db.image_metadata.insert_one({
                "image_id": str(image_id),
                "event": event,
                "date": date,
                "face_embeddings": embeddings,  # ✅ FIXED: Store as it is
                "uploaded_at": datetime.datetime.utcnow()
            })

            return jsonify({"status": "success", "image_id": str(image_id)})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/search", methods=["POST"])
def search_image():
    try:
        start_time = time.time()
        image = request.files["image"]
        event = request.form.get("event")
        date = request.form.get("date")

        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

            # Check Redis cache first
            cache_key = f"search:{filename}:{event}:{date}"
            cached_results = redis_client.get(cache_key)

            if cached_results:
                print("✅ Using Cached Search Results")
                results = eval(cached_results.decode())  # Convert string back to dictionary
            else:
                results = match_faces(image_path, event, date)

                # ✅ Fix: Generate full URLs for image retrieval
                for match in results.get("matches", []):
                    image_id = match["image_id"]
                    match["image_url"] = f"http://127.0.0.1:5000/get_image/{image_id}" 
                    match["download_url"] = f"http://127.0.0.1:5000/download/{image_id}"  # 🔹 Add download link 

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
        file_id = ObjectId(image_id)  # Ensure ObjectId format
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
        # Ensure the ID is a valid ObjectId
        file_id = ObjectId(image_id)

        # Fetch the image from GridFS
        image_data = fs.get(file_id)

        # Create a response with correct content-type
        response = Response(image_data.read(), mimetype="image/jpeg")
        response.headers["Content-Disposition"] = f'inline; filename="{image_data.filename}"'

        return response

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/view/<image_id>")  
def view_image(image_id):
    try:
        image_data = fs.get(image_id).read()
        return send_file(io.BytesIO(image_data), mimetype="image/jpeg")
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    

if __name__ == "__main__":
    print("🚀 Starting Flask Server on http://127.0.0.1:5000/")
    app.run(debug=True, host="127.0.0.1", port=5000)


#for production and deployment code start from here

"""import os
import time
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from database import fs, db, redis_client  # Redis added
from face_recognition import extract_face_embedding
from face_matching import match_faces
import datetime
import io
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        image = request.files["image"]
        event = request.form["event"]
        date = request.form["date"]

        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

            # Store in GridFS
            with open(image_path, "rb") as img_file:
                image_data = img_file.read()
            image_id = fs.put(image_data, filename=filename, event=event, date=date)

            # Extract Face Embeddings
            embeddings = extract_face_embedding(image_path)

            if not embeddings or len(embeddings) == 0:
                return jsonify({"status": "error", "message": "No face detected in image."})

            # ✅ FIX: Save embeddings directly, no `.tolist()` needed
            db.image_metadata.insert_one({
                "image_id": str(image_id),
                "event": event,
                "date": date,
                "face_embeddings": embeddings,  # ✅ FIXED: Store as it is
                "uploaded_at": datetime.datetime.utcnow()
            })

            return jsonify({"status": "success", "image_id": str(image_id)})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/search", methods=["POST"])
def search_image():
    try:
        start_time = time.time()  # Start Timer
        image = request.files["image"]
        event = request.form.get("event")
        date = request.form.get("date")

        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

            # Check Redis cache first
            cache_key = f"search:{filename}:{event}:{date}"
            cached_results = redis_client.get(cache_key)

            if cached_results:
                print("✅ Using Cached Search Results")
                results = eval(cached_results.decode())  # Convert string back to dictionary
            else:
                # Find matching images
                results = match_faces(image_path, event, date)
                redis_client.setex(cache_key, 3600, str(results))  # Cache for 1 hour

            end_time = time.time()  # End Timer
            return jsonify({
                "status": results["status"],
                "matches": results.get("matches", []),  # Ensure matches exist
                "processing_time": f"{end_time - start_time:.2f} sec"
            })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/download/<image_id>")
def download_image(image_id):
    try:
        image_data = fs.get(image_id).read()
        img = Image.open(io.BytesIO(image_data))
        img_io = io.BytesIO()
        img.save(img_io, "JPEG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/jpeg", as_attachment=True, download_name=f"{image_id}.jpg")

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    # 🔹 Production Setup: Use Waitress instead of Flask Dev Server
    from waitress import serve
    print("🚀 Running Production Server on Port 5000")
    serve(app, host="0.0.0.0", port=5000)

"""
"""1️⃣ Replace the old server.py with this version in your project.
2️⃣ Install waitress (if not installed yet):

bash
Copy
Edit
pip install waitress
3️⃣ Restart the Flask Server:

bash
Copy
Edit
python server.py
4️⃣ Test API Calls (Upload/Search Images).
5️⃣ Deploy with Systemd & Nginx"""