import click
import json
import datetime
import multiprocessing
import os
import psutil

from queuectl.db import db, init_db
from queuectl.worker import worker_loop
from queuectl.pid_manager import write_pid, read_pids, clear_pids
from queuectl.config import get_config, set_config, get_all_config

init_db()


@click.group()
def cli():
    pass


@cli.command()
@click.argument("job_json", nargs=-1)
def enqueue(job_json):
    import ast
    import json
    import datetime
    from pymongo.errors import DuplicateKeyError
    from queuectl.db import db

    raw = " ".join(job_json).strip()

    if raw.startswith("{") and raw.endswith("}"):
        if ":" in raw and '"' not in raw:
            parts = []
            body = raw.strip("{}")
            for segment in body.split(","):
                key, value = segment.split(":", 1)
                key = key.strip().strip("'").strip('"')
                value = value.strip().strip("'").strip('"')
                parts.append(f'"{key}":"{value}"')
            raw_fixed = "{" + ",".join(parts) + "}"
        else:
            raw_fixed = raw.replace("'", '"')
    else:
        raw_fixed = raw

    try:
        data = json.loads(raw_fixed)
    except Exception as e:
        print("Invalid JSON input.")
        print(f"Error: {e}")
        print(f"Raw received: {raw}")
        return

    now = datetime.datetime.now(datetime.UTC).isoformat()
    data["_id"] = data.get("id", data.get("_id", f"job-{now}"))

    job = {
        "_id": data["_id"],
        "command": data["command"],
        "state": "pending",
        "attempts": 0,
        "max_retries": data.get("max_retries", 3),
        "created_at": now,
        "updated_at": now,
        "next_run_at": None,
        "last_error": None
    }

    try:
        db.jobs.insert_one(job)
        print(f"Enqueued job: {job['_id']}")
    except DuplicateKeyError:
        print(f"Job with ID '{job['_id']}' already exists.")



@cli.command()
@click.option("--count", default=1, help="Number of workers to start")
@click.option("--daemon/--no-daemon", default=False)
def worker_start(count, daemon):
    """Start one or more worker processes."""
    procs = []
    for i in range(count):
        p = multiprocessing.Process(target=worker_loop, args=(i,))
        p.start()
        procs.append(p)
        write_pid(p.pid)
        click.echo(f"Started worker {i} (pid={p.pid})")
    if not daemon:
        for p in procs:
            p.join()


@cli.command("worker-stop")
def worker_stop():
    """Stop all worker processes."""
    from queuectl.pid_manager import read_pids, clear_pids

    pids = read_pids()
    if not pids:
        click.echo("No workers found.")
        return

    for pid in pids:
        try:
            process = psutil.Process(pid)
            click.echo(f"Stopping worker (pid={pid})...")
            process.terminate()
            try:
                process.wait(timeout=5)
                click.echo(f"Worker {pid} stopped successfully.")
            except psutil.TimeoutExpired:
                click.echo(f"Worker {pid} did not stop in time, killing forcefully.")
                process.kill()
        except psutil.NoSuchProcess:
            click.echo(f"Worker {pid} not found (already exited).")

    clear_pids()
    click.echo("All workers stopped and PID file cleared.")


@cli.command("status")
def show_status():
    """Display summary of job states and active workers."""
    import traceback
    try:
        from queuectl.db import db
        from queuectl.pid_manager import read_pids

        jobs_collection = db.get_collection("jobs")

        if "jobs" not in db.list_collection_names():
            click.echo("No jobs found in database.")
            return

        pipeline = [{"$group": {"_id": "$state", "count": {"$sum": 1}}}]
        cursor = jobs_collection.aggregate(pipeline)

        result = []
        for doc in cursor:
            if isinstance(doc, dict):
                result.append(doc)

        if not result:
            click.echo("No jobs found.")
        else:
            click.echo("Job Status Summary:")
            for r in result:
                state = str(r.get("_id", "unknown"))
                count = r.get("count", 0)
                click.echo(f" - {state}: {count}")

        pids = read_pids()
        if pids:
            click.echo(f"Active workers: {', '.join(map(str, pids))}")
        else:
            click.echo("No active workers.")

    except Exception as e:
        click.echo(f"Error reading jobs: {e}")
        traceback.print_exc()


@cli.command()
@click.option("--state", default="pending", help="Filter jobs by state")
def list(state):
    """List all jobs by their state."""
    for j in db.jobs.find({"state": state}):
        click.echo(f"{j['_id']} | {j['state']} | attempts={j['attempts']} | cmd={j['command']}")


@cli.group()
def dlq():
    """Dead Letter Queue management."""
    pass


@dlq.command("list")
def dlq_list():
    """List all jobs in the Dead Letter Queue."""
    for j in db.dlq.find():
        click.echo(f"{j['_id']} | {j.get('last_error')}")


@dlq.command("retry")
@click.argument("job_id")
def dlq_retry(job_id):
    """Retry a job from the Dead Letter Queue."""
    j = db.dlq.find_one({"_id": job_id})
    if not j:
        click.echo("Job not found in DLQ.")
        return
    db.dlq.delete_one({"_id": job_id})
    j["state"] = "pending"
    j["attempts"] = 0
    db.jobs.insert_one(j)
    click.echo(f"Retried job {job_id} from DLQ.")


@cli.group()
def config():
    """System configuration management."""
    pass


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Get configuration values."""
    if key:
        value = get_config(key, None)
        if value is None:
            click.echo(f"{key} not found.")
        else:
            click.echo(f"{key} = {value}")
    else:
        for k, v in get_all_config().items():
            click.echo(f"{k} = {v}")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set configuration values."""
    try:
        if value.isdigit():
            value = int(value)
    except Exception:
        pass
    set_config(key, value)
    click.echo(f"Updated {key} = {value}")


@cli.command()
def ping():
    """Check CLI connectivity."""
    print("CLI is active.")


if __name__ == "__main__":
    cli()
