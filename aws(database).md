""" To use MongoDB Atlas, AWS Deployment, and Redis in Production, you need to change some configurations in your project. Here are the exact changes needed in the code:

1️⃣ MongoDB Atlas (Instead of Local MongoDB)
🔹 Change in database.py

Replace local MongoDB connection with Atlas connection string.

Where to change? Replace this line:

python

client = MongoClient("mongodb://localhost:27017/")  # Change this
With this:

client = MongoClient("mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/?retryWrites=true&w=majority")
➡️ Replace <username>, <password>, and <cluster-name> with your MongoDB Atlas credentials.
➡️ Make sure your MongoDB Atlas allows connections from your server IP.

2️⃣ Using Redis on AWS (Instead of Local Redis)
🔹 Change in database.py

Replace local Redis connection with AWS ElastiCache Redis.

Where to change? Replace this:

redis_client = redis.Redis(host="localhost", port=6379, db=0)
With this:

redis_client = redis.Redis(host="<AWS_REDIS_ENDPOINT>", port=6379, db=0, decode_responses=True)
➡️ Replace <AWS_REDIS_ENDPOINT> with your Redis instance endpoint from AWS ElastiCache.
➡️ Ensure Redis is accessible from your server (Security Groups must allow access).

3️⃣ Deploy Flask on AWS (Instead of Localhost)
🔹 Change in server.py

Flask must listen to 0.0.0.0 instead of 127.0.0.1

Where to change? Modify this:

app.run(debug=True, host="127.0.0.1", port=5000)
To this:

app.run(debug=False, host="0.0.0.0", port=5000)
➡️ This allows the Flask app to be accessible from the public IP or domain.

4️⃣ Add waitress for Production
🔹 Change in server.py

Instead of using Flask's default development server, use waitress.

Where to change? Modify if __name__ == "__main__" section:

python

from waitress import serve
print("🚀 Running Production Server on AWS")
serve(app, host="0.0.0.0", port=5000)
➡️ Install Waitress before deploying:


pip install waitress
5️⃣ Enable CORS for AWS Frontend
🔹 Change in server.py

Currently,we have this:
CORS(app)
Modify it to allow AWS frontend domains:
python

CORS(app, resources={r"/*": {"origins": ["https://yourfrontend.com", "https://sub.yourfrontend.com"]}})
➡️ Replace "https://yourfrontend.com" with your actual frontend domain.
6️⃣ Configure Nginx & Gunicorn for AWS Deployment
🔹 If using AWS EC2, you need to use Nginx & Gunicorn

Install dependencies on AWS EC2:

sudo apt update && sudo apt install nginx python3-pip -y
pip install gunicorn
Run Gunicorn manually to check if it works:


gunicorn --bind 0.0.0.0:5000 server:app
Set up Nginx to forward requests to Gunicorn

sudo nano /etc/nginx/sites-available/flaskapp
Add this:

server {
    listen 80;
    server_name your_domain_or_public_ip;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
Enable Nginx config:

sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled
sudo systemctl restart nginx
✅ Now, Flask app is ready for AWS & MongoDB Atlas deployment! """