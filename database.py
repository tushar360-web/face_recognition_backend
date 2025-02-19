from pymongo import MongoClient
import gridfs
import redis

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Change to your MongoDB URL
db = client["face_recognition_db"]  # Database name

# GridFS setup for storing images
fs = gridfs.GridFS(db)

# Ensure indexes for faster searches
db.image_metadata.create_index([("event", 1)])
db.image_metadata.create_index([("date", 1)])
db.image_metadata.create_index([("face_embeddings",1)])

# Connect to Redis for caching
redis_client = redis.Redis(host="localhost", port=6379, db=0)

print("✅ MongoDB & Redis Connected & Indexes Created!")

