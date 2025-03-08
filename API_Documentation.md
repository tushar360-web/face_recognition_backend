"""
# API Documentation for Face Recognition System

## Base URL
```
http://127.0.0.1:5000
```
For production deployment, replace this with the actual server URL.
# for run server- python server.py
---
## 1️⃣ **Upload Image (Admin Panel)**
Uploads an image to the database along with event and date metadata.

**Endpoint:**
```
POST /upload
```

**Request Parameters:**
- `image`: (file) Image file to upload (JPEG/PNG format recommended)
- `event`: (string) Event name (Required)
- `date`: (string) Event date in `YYYY-MM-DD` format (Required)

**Example Request (Python Requests):**
```python
import requests
files = {"image": open("test.jpg", "rb")}
data = {"event": "birthday", "date": "2025-02-17"}
response = requests.post("http://127.0.0.1:5000/upload", files=files, data=data)
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "image_id": "67b2cc3450ac8c4b07c2bf22"
}
```

---
## 2️⃣ **Search Image (Face Recognition)**
Uploads an image to find matches in the database.

**Endpoint:**
```
POST /search
```

**Request Parameters:**
- `image`: (file) Image file to search (JPEG/PNG)
- `event`: (string, optional) Filter search by event name
- `date`: (string, optional) Filter search by event date (`YYYY-MM-DD`)

**Example Request:**
```python
import requests
files = {"image": open("search.jpg", "rb")}
data = {"event": "birthday", "date": "2025-02-17"}
response = requests.post("http://127.0.0.1:5000/search", files=files, data=data)
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "matches": [
    {
      "image_id": "67b2cc3450ac8c4b07c2bf22",
      "image_url": "http://127.0.0.1:5000/get_image/67b2cc3450ac8c4b07c2bf22",
      "similarity": 0.7322,
      "event": "birthday",
      "date": "2025-02-17"
    }
  ],
  "processing_time": "0.32 sec"
}
```

---
## 3️⃣ **Retrieve Image (View Matched Image)**
Fetches an image from the database using `image_id`.

**Endpoint:**
```
GET /get_image/<image_id>
```

**Example Request:**
```python
import requests
image_id = "67b2cc3450ac8c4b07c2bf22"
url = f"http://127.0.0.1:5000/get_image/{image_id}"
response = requests.get(url)
if response.status_code == 200:
    with open("matched_image.jpg", "wb") as f:
        f.write(response.content)
    print("✅ Image saved as matched_image.jpg")
else:
    print("❌ Error", response.json())
```

**Response:** *(Returns image binary)*
If the image exists, it returns the actual image in `image/jpeg` format.
If not, it returns:
```json
{
  "status": "error",
  "message": "Image not found"
}
```

---
## 4️⃣ **Download Image**
Allows downloading an image by `image_id`.

**Endpoint:**
```
GET /download/<image_id>
```

**Example Request:**
```python
import requests
image_id = "67b2cc3450ac8c4b07c2bf22"
url = f"http://127.0.0.1:5000/download/{image_id}"
response = requests.get(url)
if response.status_code == 200:
    with open("downloaded_image.jpg", "wb") as f:
        f.write(response.content)
    print("✅ Image downloaded successfully")
else:
    print("❌ Error", response.json())
```

**Response:** *(Returns image binary as file attachment)*
If the image exists, it will be downloaded.
If not, it returns:
```json
{
  "status": "error",
  "message": "Image not found"
}
```

---
## 5️⃣ **View Image in Web**
This API allows embedding an image in a web app.

**Endpoint:**
```
GET /view/<image_id>
```

**Example Usage (HTML):**
```html
<img src="http://127.0.0.1:5000/view/67b2cc3450ac8c4b07c2bf22" alt="Matched Face" />
```

---
## 6️⃣ **Database Information**
MongoDB stores images in **GridFS**, splitting them between:
- `fs.files` → Stores metadata (filename, event, date, etc.)
- `fs.chunks` → Stores actual image binary data

Each uploaded image is stored with its `_id` and can be retrieved using API calls.

---
## 🔹 Additional Notes
- **CORS Policy**: If integrating with a frontend, ensure CORS is enabled in Flask if needed.

# ✅ Enable CORS for all routes and allow specific frontend domains
Modify your server.py like this:

from flask import Flask
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
here add this 

# ✅ Enable CORS for all routes and allow specific frontend domains
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://yourfrontend.com"]}})

# ✅ OR, if you want to allow all origins (Not recommended for production)
# CORS(app)

Explanation:
CORS(app) → Allows all frontend apps to access your API (useful for testing but risky in production).
CORS(app, resources={r"/*": {"origins": [...]}}) → Restricts access to only specific frontend domains like React, Vue, or mobile apps.

- **Deployment**: For AWS, use **MongoDB Atlas** and **Elasticache Redis** instead of local MongoDB & Redis.
- **Scaling**: Consider adding **Gunicorn + Nginx** for production deployment.

---
"""

