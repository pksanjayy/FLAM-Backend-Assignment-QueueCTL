# FLAM-Backend-Assignment-QueueCTL
QueueCTL is a lightweight CLI-based background job queue system built with Python and MongoDB. It supports retries with exponential backoff, a Dead Letter Queue for failed jobs, and persistent storage for reliable background processing.

**Features**
-> CLI-based job management (enqueue, status, worker-start, dlq list)
-> Persistent job storage in MongoDB
-> Automatic retry with exponential backoff (delay = base ^ attempts)
-> Dead Letter Queue (DLQ) for permanently failed jobs
-> Multiple worker support with atomic job locking
-> Graceful worker shutdown and PID tracking
-> Configurable retry and backoff parameters
