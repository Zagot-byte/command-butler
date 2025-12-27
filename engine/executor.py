import subprocess

def run_as_bot(cmd: list) -> str:
    result = subprocess.run(
        ["sudo", "-u", "butler", "env"] + cmd,
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr
