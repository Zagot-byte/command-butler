# engine/logger.py

import json
import time
import os
import getpass

# Resolve project root deterministically
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

HISTORY_PATH = os.path.join(PROJECT_ROOT, "history.jsonl")

def log_run(*, intent: str, commands: list, steps: int, status: str):
    """
    Append one immutable audit record.
    """
    entry = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "user": getpass.getuser(),
        "intent": intent,
        "steps": steps,
        "commands": commands,
        "status": status,
    }

    # Ensure file exists
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
        f.flush()
        os.fsync(f.fileno())
