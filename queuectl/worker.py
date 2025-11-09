import time
import datetime
import signal
import os
from queuectl.db import db
from queuectl.executor import run_command
from queuectl.config import get_config

STOP = False


def handle_signal(signum, frame):
    global STOP
    STOP = True


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def exponential_backoff(attempts: int) -> int:
    base = get_config("backoff_base", 2)
    return base ** attempts


def claim_job():
    now = datetime.datetime.utcnow().isoformat()
    job = db.jobs.find_one_and_update(
        {
            "state": "pending",
            "$or": [{"next_run_at": {"$lte": now}}, {"next_run_at": None}],
        },
        {
            "$set": {"state": "processing", "updated_at": now},
            "$inc": {"attempts": 1},
        },
        sort=[("created_at", 1)],
        return_document=True,
    )
    return job


def mark_completed(job_id: str):
    db.jobs.update_one(
        {"_id": job_id},
        {
            "$set": {
                "state": "completed",
                "updated_at": datetime.datetime.utcnow().isoformat(),
            }
        },
    )


def move_to_dead(job, error):
    job["state"] = "dead"
    job["last_error"] = str(error)
    job["updated_at"] = datetime.datetime.now(datetime.UTC).isoformat()
    db.dlq.replace_one({"_id": job["_id"]}, job, upsert=True)
    db.jobs.delete_one({"_id": job["_id"]})
    print(f"[Worker] Job {job['_id']} moved to DLQ.")


def reschedule_retry(job_id: str, attempts: int):
    delay = exponential_backoff(attempts)
    next_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)
    db.jobs.update_one(
        {"_id": job_id},
        {
            "$set": {
                "state": "pending",
                "next_run_at": next_time.isoformat(),
                "updated_at": datetime.datetime.utcnow().isoformat(),
            }
        },
    )
    print(f"[Worker] Retrying job {job_id} in {delay} seconds.")


def worker_loop(worker_id: int = 0, poll_interval: int = 2):
    print(f"Worker {worker_id} started.")
    while not STOP:
        job = claim_job()
        if not job:
            time.sleep(poll_interval)
            continue

        job_id = job["_id"]
        cmd = job["command"]
        attempts = job["attempts"]
        max_retries = job.get("max_retries", get_config("max_retries", 3))

        print(f"[Worker {worker_id}] Processing job {job_id}: {cmd}")
        code, out, err = run_command(cmd)

        if code == 0:
            mark_completed(job_id)
            print(f"[Worker {worker_id}] Job {job_id} completed.")
        else:
            if attempts >= max_retries:
                move_to_dead(job, err)
                print(f"[Worker {worker_id}] Job {job_id} moved to DLQ.")
            else:
                reschedule_retry(job_id, attempts)

    print(f"Worker {worker_id} stopped gracefully.")
