import json
import subprocess

MODEL = "phi3:mini"

SYSTEM_PROMPT = """
You are a command output analyzer.

Rules:
- You MUST output valid JSON only.
- You MUST NOT generate shell commands.
- You MUST NOT suggest actions outside the command catalog.
- Decide if the problem is resolved or another command is needed.

Output schema:
{
  "result": "done | next",
  "next_cmd_id": number | null,
  "reason": string
}
"""

def analyze(intent: str, output: str, commands: dict) -> dict:
    catalog_summary = [
        {"id": c["id"], "desc": c["desc"]}
        for c in commands.values()
    ]

    prompt = f"""
Original user intent:
{intent}

Command output:
{output}

Available commands:
{json.dumps(catalog_summary, indent=2)}

Analyze whether the issue is resolved.
If not, choose the next command ID.
"""

    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=(SYSTEM_PROMPT + prompt),
        capture_output=True,
        text=True,
        timeout=60
    )

    try:
        analysis = json.loads(result.stdout.strip())
    except Exception:
        return {
            "result": "done",
            "next_cmd_id": None,
            "reason": "invalid analyzer output"
        }

    # HARD validation
    if analysis.get("result") not in ["done", "next"]:
        return {
            "result": "done",
            "next_cmd_id": None,
            "reason": "invalid result value"
        }

    if analysis["result"] == "next":
        if analysis.get("next_cmd_id") not in commands:
            return {
                "result": "done",
                "next_cmd_id": None,
                "reason": "invalid next command id"
            }

    return analysis
