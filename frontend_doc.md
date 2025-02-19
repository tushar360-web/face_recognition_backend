"""Project Frontend Integration Guide

This document should guide the frontend team in integrating the UI with the backend APIs

1. Overview

This document provides guidelines for integrating the frontend with the backend API for the face recognition project. The backend is built using Flask, MongoDB (GridFS), Redis, and FaceNet for face detection.

2. API Endpoints

2.1 Upload Image (Admin Panel)

Endpoint: POST /upload

Description: Uploads an image with metadata (event & date) to GridFS.

Request Parameters:

image: (File) The image file to be uploaded.

event: (String) The event name associated with the image.

date: (String) The date of the event (format: YYYY-MM-DD).

Response:
{
  "status": "success",
  "image_id": "<MongoDB ObjectID>"
}
Frontend Task: Implement a file upload form with event and date fields.

2.2 Search Image (User Panel)

Endpoint: POST /search

Description: Searches for matching faces in the database.

Request Parameters:

image: (File) The image file to search for matches.

event: (Optional) (String) Filter search by event name.

date: (Optional) (String) Filter search by event date (format: YYYY-MM-DD).

Response:
{
  "status": "success",
  "matches": [
    {
      "image_id": "<MongoDB ObjectID>",
      "image_url": "http://127.0.0.1:5000/get_image/<image_id>",
      "download_url": "http://127.0.0.1:5000/download/<image_id>",
      "similarity": 0.85
    }
  ],
  "processing_time": "0.32 sec"
}
Frontend Task: Display matched images using image_url and provide a download button using download_url.

2.3 Retrieve Image

Endpoint: GET /get_image/<image_id>

Description: Retrieves and displays an image from the database.

Frontend Task: Use this API to fetch and display images.

2.4 Download Image

Endpoint: GET /download/<image_id>

Description: Provides an option to download the stored image.

Frontend Task: Implement a download button linking to this endpoint.

3. Frontend Implementation Guidelines

File Upload Forms: Use multipart/form-data when sending images.

Handle API Responses: Display messages based on API responses.

Caching: Utilize browser caching to optimize repeated searches.

UI Suggestions:

Display image previews for uploaded and searched images.

Implement a loading animation while waiting for search results.

Provide a clear button to reset the search form.

4. Example HTML Form (Admin Upload Panel)
<form action="/upload" method="POST" enctype="multipart/form-data">
    <label>Event Name:</label>
    <input type="text" name="event" required>
    <label>Date:</label>
    <input type="date" name="date" required>
    <label>Image:</label>
    <input type="file" name="image" required>
    <button type="submit">Upload</button>
</form>
5. Example JavaScript for Fetching Matched Images
fetch('/search', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    let resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';
    data.matches.forEach(match => {
        let imgElement = document.createElement('img');
        imgElement.src = match.image_url;
        imgElement.alt = 'Matched Face';
        resultsContainer.appendChild(imgElement);
        
        let downloadLink = document.createElement('a');
        downloadLink.href = match.download_url;
        downloadLink.innerText = 'Download Image';
        resultsContainer.appendChild(downloadLink);
    });
})
.catch(error => console.error('Error:', error));

6. Deployment Considerations

Production Server: Change API URLs from 127.0.0.1 to the deployed server’s address.

MongoDB Cloud (If Used): Update connection URL in database.py.

Security: Implement proper authentication for uploading and searching images."""

