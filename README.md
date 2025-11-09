# **FLAM-Backend-Assignment-QueueCTL**

QueueCTL is a lightweight CLI-based background job queue system built with Python and MongoDB.  
It supports retries with exponential backoff, a Dead Letter Queue (DLQ) for failed jobs, and persistent storage for reliable background processing.

---

## **Features**
- CLI-based job management (`enqueue`, `status`, `worker-start`, `dlq list`)
- Persistent job storage in MongoDB
- Automatic retry with exponential backoff (`delay = base ^ attempts`)
- Dead Letter Queue (DLQ) for permanently failed jobs
- Multiple worker support with atomic job locking
- Graceful worker shutdown and PID tracking
- Configurable retry and backoff parameters

---

## ⚙️ **Setup Instructions**

```bash
# Clone the repository
git clone https://github.com/pksanjayy/FLAM-Backend-Assignment-QueueCTL.git
cd FLAM-Backend-Assignment-QueueCTL

# Install dependencies
pip install -r requirements.txt

# Ensure MongoDB is running locally
mongod --dbpath <your-db-path>

# Verify setup
python -m queuectl.cli ping
