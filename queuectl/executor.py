import subprocess, shlex

def run_command(cmd: str, timeout=None):
    try:
        args = shlex.split(cmd)
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)
