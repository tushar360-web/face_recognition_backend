# Frontend Integration Guide for Face Recognition Project

This document provides a comprehensive guide for integrating the frontend (Next.js + Tailwind CSS) with the backend APIs (Flask + MongoDB + Redis + FaceNet).

## 1️⃣ Overview

### **Tech Stack**
- **Frontend:** Next.js, Tailwind CSS
- **Backend:** Flask, MongoDB (GridFS or Server Storage), Redis, FaceNet
- **Database:** MongoDB
- **Storage:** GridFS (by default) or Server Storage (optional)
- **Routing:** Next.js API routes (`/admin`, `/search`)
- **Environment Configuration:** `.env.local`

### **Setup Frontend Locally**

#### **1. Install VS Code and Extensions**
- Download **Visual Studio Code** 
- Install the following VS Code extensions:
  - **ESLint** (for linting)
  - **Prettier** (for code formatting)
  - **Tailwind CSS IntelliSense** (for Tailwind CSS autocomplete)
  - **JavaScript (ES6+) Snippets** (for better JavaScript development)

#### **2. Install Node.js and Dependencies**
- Download and install **Node.js** (LTS version) from: [https://nodejs.org/](https://nodejs.org/)
- Install dependencies using:
```bash
npm install  # Installs required packages
npm run dev  # Starts the Next.js development server
```

### **3. Environment Configuration**
Create a `.env.local` file in the root directory and add:
```ini
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:5000
```
Replace `127.0.0.1:5000` with the actual backend URL when in production.

## 2️⃣ API Endpoints Integration

### **2.1 Upload Image (Admin Panel)**
Uploads multiple images to the server with metadata.

**📌 Endpoint:** `POST /upload`

**🔹 Request Parameters:**
- `images[]`: (File) Multiple images (JPEG/PNG)
- `event`: (String) Event name (Required)
- `date`: (String) Event date in `YYYY-MM-DD` format (Required)
- `department`: (String) Department (Required)
- `district`: (String) District (Required)
- `location`: (String) Location details (Required)

**📌 Integration in Next.js (`/admin/page.js`)**
```javascript
const handleUpload = async (event) => {
    event.preventDefault();
    let formData = new FormData();
    formData.append("event", event.target.event.value);
    formData.append("date", event.target.date.value);
    formData.append("department", event.target.department.value);
    formData.append("district", event.target.district.value);
    formData.append("location", event.target.location.value);

    let imageFiles = event.target.images.files;
    for (let i = 0; i < imageFiles.length; i++) {
        formData.append("images[]", imageFiles[i]);
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
    });
    const data = await response.json();
    console.log(data);
};
```

---

### **2.2 Search Image (User Panel)**
Users upload an image to search for matches.

**📌 Endpoint:** `POST /search`

**📌 Integration in Next.js (`/search/page.js`)**
```javascript
const handleSearch = async (event) => {
    event.preventDefault();
    let formData = new FormData();
    formData.append("event", event.target.event.value);
    formData.append("date", event.target.date.value);
    formData.append("department", event.target.department.value);
    formData.append("district", event.target.district.value);
    formData.append("image", event.target.image.files[0]);

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/search`, {
        method: "POST",
        body: formData,
    });
    const data = await response.json();
    console.log("Search Results:", data);
};
```

---

### **2.3 Displaying Search Results in UI**
```javascript
useEffect(() => {
    if (searchResults.length > 0) {
        searchResults.forEach(match => {
            let imgElement = document.createElement('img');
            imgElement.src = match.image_url;
            imgElement.alt = 'Matched Face';
            document.getElementById('results').appendChild(imgElement);
        });
    }
}, [searchResults]);
```

---

## 3️⃣ **Deployment Considerations**
- **Change API URLs** from `127.0.0.1` to the deployed server.
- **Use HTTPS** in production.
- **Ensure authentication** for image uploads.
- **Optimize caching** for faster search responses.

This guide ensures a smooth integration of the frontend with the backend APIs. 🚀

