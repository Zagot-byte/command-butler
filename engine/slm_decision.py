import json
import subprocess

MODEL = "phi3:mini"

SYSTEM_PROMPT = """
You are a command selection engine.

Rules:
- Output JSON only.
- Choose ONE command ID from the catalog.
- Do NOT generate shell commands.

Schema:
{
  "action": "execute | approve | reject",
  "cmd_id": number | null,
  "reason": string
}
"""

def decide(intent: str, commands: dict) -> dict:
    catalog = [
        {"id": c["id"], "desc": c["desc"], "risk": c.get("risk", "low")}
        for c in commands.values()
    ]

    prompt = f"""
User intent:
{intent}

Available commands:
{json.dumps(catalog, indent=2)}

Select the best action.
"""
    result = subprocess.run(
    ["ollama", "run", MODEL, "--format", "json"],
    input=(SYSTEM_PROMPT + prompt),
    capture_output=True,
    text=True,
    timeout=60)

    try:
        decision = json.loads(result.stdout.strip())
    except Exception:
        return {
            "action": "reject",
            "cmd_id": None,
            "reason": "invalid model output"
        }

    # HARD validation
    if decision.get("action") not in ["execute", "approve", "reject"]:
        return {
            "action": "reject",
            "cmd_id": None,
            "reason": "invalid action"
        }

    if decision["action"] != "reject" and decision.get("cmd_id") not in commands:
        return {
            "action": "reject",
            "cmd_id": None,
            "reason": "unknown command id"
        }

    return decision
