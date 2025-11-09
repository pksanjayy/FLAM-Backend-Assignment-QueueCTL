import os
RUN_DIR = "run"
PID_FILE = os.path.join(RUN_DIR, "workers.pid")

def write_pid(pid):
    os.makedirs(RUN_DIR, exist_ok=True)
    with open(PID_FILE, "a") as f:
        f.write(str(pid) + "\n")

def read_pids():
    if not os.path.exists(PID_FILE):
        return []
    with open(PID_FILE) as f:
        return [int(p.strip()) for p in f.readlines() if p.strip()]

def clear_pids():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
