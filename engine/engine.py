#!/usr/bin/env python3

import socket
import os
import json
import sys

from slm_decision import decide
from slm_analyzer import analyze
from executor import run_as_bot
from logger import log_run

SOCKET_PATH = "/run/command-butler/butler.sock"
CATALOG_PATH = os.path.join(
    os.path.dirname(__file__),
    "../catalog/commands.json"
)

MAX_STEPS = 3

# ----------------------------
# Setup socket
# ----------------------------

if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
os.chmod(SOCKET_PATH, 0o660)
server.listen(1)

print("[+] Butler engine listening")

# ----------------------------
# Load catalog
# ----------------------------

with open(CATALOG_PATH) as f:
    catalog = json.load(f)
    COMMANDS = {c["id"]: c for c in catalog}

# ----------------------------
# Accept request
# ----------------------------

conn, _ = server.accept()
raw = conn.recv(4096)

if not raw:
    conn.close()
    server.close()
    sys.exit(0)

request = json.loads(raw.decode())
intent = request.get("input", "")

decision = decide(intent, COMMANDS)

# ----------------------------
# Handle decision
# ----------------------------

if decision["action"] == "reject":
    conn.sendall(f"❌ {decision['reason']}\n".encode())

elif decision["action"] == "approve":
    conn.sendall(json.dumps({
        "status": "approval_required",
        "reason": decision["reason"],
        "cmd": COMMANDS[decision["cmd_id"]]["cmd"]
    }).encode())

elif decision["action"] == "execute":
    current_cmd_id = decision["cmd_id"]
    full_output = ""
    executed_cmds = []
    steps = 0

    while steps < MAX_STEPS:
        steps += 1
        cmd_entry = COMMANDS[current_cmd_id]
        executed_cmds.append(cmd_entry["cmd"])

        output = run_as_bot(cmd_entry["cmd"])
        full_output += output + "\n"

        analysis = analyze(intent, output, COMMANDS)

        if analysis["result"] == "done":
            log_run(
                intent=intent,
                commands=executed_cmds,
                steps=steps,
                status="done"
            )
            conn.sendall(full_output.encode())
            break

        current_cmd_id = analysis["next_cmd_id"]

    else:
        log_run(
            intent=intent,
            commands=executed_cmds,
            steps=steps,
            status="stopped_loop_cap"
        )
        conn.sendall(
            (full_output + "\n⚠️ Stopped after max steps for safety\n").encode()
        )

# ----------------------------
# Cleanup
# ----------------------------

conn.close()
server.close()
