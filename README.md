# **FLAM-Backend-Assignment-QueueCTL**

QueueCTL is a lightweight CLI-based background job queue system built with Python and MongoDB.  
It supports retries with exponential backoff, a Dead Letter Queue (DLQ) for failed jobs, and persistent storage for reliable background processing.

---
## 🎥 **Demo Video**
Watch the full project demo here:  
[View on Google Drive](https://drive.google.com/file/d/1L5I0zfSzV5WsgfyFbbzswpg0_DnI3sa5/view?usp=drive_link)

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
```
---

## ⚙️ **Usage example**
```bash
# Enqueue a job
python -m queuectl.cli enqueue '{"id":"job10","command":"cmd /C echo Hello QueueCTL"}'

# Start a worker
python -m queuectl.cli worker-start --count 1

# Check job status
python -m queuectl.cli status

# List completed jobs
python -m queuectl.cli list --state completed

# View failed jobs (DLQ)
python -m queuectl.cli dlq list

# Retry a DLQ job
python -m queuectl.cli dlq retry job1

# Stop workers
python -m queuectl.cli worker-stop

# Configuration management
python -m queuectl.cli config get
python -m queuectl.cli config set max_retries 5
python -m queuectl.cli config set backoff_base 3
```
---
## **Architecture Overview**

- QueueCTL follows a modular, event-driven architecture:
- Job Queue (jobs collection) — Stores all job documents with metadata like command, state, attempts, timestamps, etc.
- Worker Process (worker.py) — Continuously polls pending jobs, executes them, and updates their state based on success or failure.
- Retry Mechanism — Failed jobs retry automatically using exponential backoff (delay = base ^ attempts).
- Dead Letter Queue (dlq collection) — Stores permanently failed jobs after exceeding retry limits.
- Config Management (config collection) — Allows runtime configuration of retry counts and backoff base.
- PID Manager — Tracks active workers and enables graceful shutdowns across multiple worker processes

---

### **System Architecture Diagram**
Below is a high-level view of QueueCTL’s components and their interactions:

![QueueCTL Architecture Overview](https://drive.google.com/uc?export=view&id=1CFRg86IRogPv1hGmcxkxdg5uMCelEkH0)

---
## **Assumptions & Trade-offs**

- MongoDB is used for simplicity and durability; Redis could be used for higher throughput.
- Worker polling interval is fixed (can be optimized with event triggers).
- Commands are executed via the system shell (subprocess).
- No job priority queue implemented (kept simple for clarity).
- Focused on reliability and concurrency, not scheduling (cron-like).

---
## **Testing Instructions**
```bash
# Start MongoDB
mongod

# Enqueue jobs
python -m queuectl.cli enqueue '{"id":"job2","command":"cmd /C echo Testing Queue"}'

# Start a worker and observe
python -m queuectl.cli worker-start --count 1

# Simulate a failure (invalid command)
python -m queuectl.cli enqueue '{"id":"failjob","command":"invalidcommand"}'

# Check job states
python -m queuectl.cli status

# Retry failed DLQ jobs
python -m queuectl.cli dlq retry failjob

```
---
## **Technologies Used**

- Python 3.13
- MongoDB (Persistent storage)
- Click (CLI framework)
- Multiprocessing (Parallel worker execution)
- psutil (Process management)

---
