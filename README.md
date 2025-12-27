
# Command Butler 🧹🧠
**A security-first, offline, AI-assisted command-line helper for Linux**

Command Butler is a **local CLI agent** that translates fuzzy human intent  
(e.g. _“fix net”_, _“list process”_) into **safe, predefined Linux commands**.

It is **not**:
- a shell
- a daemon
- an auto-executing AI

It is designed for **control, safety, and transparency**.

---

## ✨ Features

- 🧠 **Local SLM (Phi-3-mini via Ollama)** — no cloud, no API keys
- 🔐 **Strict command sandbox** — AI selects from a fixed catalog only
- 🧱 **Decision ≠ Execution** — strong separation of concerns
- 🔁 **Multi-step agent loop** — bounded, safe, inspectable
- 🗂️ **Audit logging** — every run is recorded locally
- 🧵 **UNIX domain sockets** — no TCP ports, no network exposure
- 🧍 **Human-in-the-loop execution** — sudo password retained
- ⚡ **Fast & lightweight** — runs on laptops, VMs, low-RAM systems

---

## 🧠 Architecture Overview



butler CLI
↓ (UNIX socket)
engine.py
├─ SLM Decision (intent → command_id)
├─ Executor (restricted OS user)
├─ SLM Analyzer (output → next step)
├─ Loop safety cap
└─ Audit logger


**Important guarantees**
- AI never generates shell commands
- Only commands in `commands.json` can run
- No background shell, no network daemon

---


## 🧪 Usage

### 1️⃣ Start the engine (one-shot listener)
python3 engine/engine.py

###2️⃣ In another terminal
python3 cli/butler.py "fix net"
python3 cli/butler.py "list process"

###📜 Audit Log

All executions are recorded in history.jsonl:

{
  "time": "2025-12-27T12:52:01Z",
  "user": "zagot",
  "intent": "fix net",
  "steps": 1,
  "commands": ["nmcli device status"],
  "status": "done"
}


This enables:

debugging

replay

future memory (RAG)

explainability

###🔐 Security Model

❌ No arbitrary shell execution

❌ No TCP / HTTP ports

❌ No silent privilege escalation

❌ No cloud dependency

✅ Explicit sudo password

✅ Append-only audit log

✅ Group-restricted UNIX socket

Command Butler is safe by default.



###🛠️ Requirements

Linux (Arch / Kali tested)

Python 3.10+

Ollama

Phi-3-mini model

###🧠 Philosophy

AI should assist, not take control.

Command Butler exists to keep humans in charge.
