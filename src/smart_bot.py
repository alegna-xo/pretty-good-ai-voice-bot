"""
Phase 3: State-machine patient bot.

Starts a local webhook server, tunnels it via ngrok, places a Twilio call
to the target AI agent, and drives the conversation with intent-based
keyword matching rather than a fixed timed script.

Usage:
    python src/smart_bot.py

Logs saved to logs/smart_call_<SID>.txt
"""

import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse

load_dotenv()

# ── Patient profile ───────────────────────────────────────────────────────────

PATIENT = {
    "name": "Sarah Johnson",
    "dob": "January 15th, 1985",
    "reason": (
        "I would like to schedule an appointment with a primary care doctor. "
        "I have had a persistent cough and sore throat for about a week."
    ),
    "availability": "I am available Tuesday or Wednesday afternoon.",
    "closing": "No, that is everything. Thank you so much. Goodbye.",
}

# ── State machine ─────────────────────────────────────────────────────────────
# Ordered list — states are matched front-to-back with a forward bias so the
# bot advances naturally through the conversation and doesn't repeat itself.

STATES = [
    {
        "name": "verify_name",
        "keywords": ["name", "verify", "who am i speaking", "may i have", "full name", "speaking with"],
        "say": f"My name is {PATIENT['name']}.",
    },
    {
        "name": "verify_dob",
        "keywords": ["date of birth", "birthday", "born", "dob", "birth date"],
        "say": f"My date of birth is {PATIENT['dob']}.",
    },
    {
        "name": "state_reason",
        "keywords": ["help you", "how can i", "what brings", "reason", "calling about", "assist"],
        "say": PATIENT["reason"],
    },
    {
        "name": "state_availability",
        "keywords": ["available", "schedule", "when", "time", "prefer", "come in", "appointment"],
        "say": PATIENT["availability"],
    },
    {
        "name": "confirm",
        "keywords": ["confirm", "scheduled", "booked", "appointment is", "great", "perfect",
                     "all set", "anything else", "is there anything", "can i help"],
        "say": PATIENT["closing"],
    },
]

# Per-call runtime state keyed by CallSid
call_states: dict[str, dict] = {}

app = Flask(__name__)


# ── Intent detection ──────────────────────────────────────────────────────────

def detect_intent(speech: str, from_idx: int) -> int:
    """Return the STATES index that best matches the agent's speech.

    Searches forward from from_idx first so the conversation advances
    naturally. Falls back to a full scan if nothing matches ahead.
    """
    lower = speech.lower()
    for i in range(from_idx, len(STATES)):
        if any(kw in lower for kw in STATES[i]["keywords"]):
            return i
    for i in range(from_idx):
        if any(kw in lower for kw in STATES[i]["keywords"]):
            return i
    return from_idx  # no match — stay put and re-listen


# ── Logging ───────────────────────────────────────────────────────────────────

def log(call_sid: str, text: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{ts}] {text}"
    print(line)
    call_states.setdefault(call_sid, {"state_idx": 0, "log": []})["log"].append(line)


def save_log(call_sid: str):
    Path("logs").mkdir(exist_ok=True)
    path = Path(f"logs/smart_call_{call_sid}.txt")
    lines = call_states.get(call_sid, {}).get("log", [])
    path.write_text("\n".join(lines) + "\n")
    print(f"\nLog saved → {path}")


# ── TwiML helpers ─────────────────────────────────────────────────────────────

def gather_response(action_url: str, say_text: str | None = None) -> str:
    """TwiML: optionally say something, then listen for agent speech."""
    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action=action_url,
        method="POST",
        speech_timeout="auto",
        timeout=12,
        language="en-US",
    )
    if say_text:
        gather.say(say_text, voice="Polly.Joanna")
    resp.append(gather)
    resp.redirect(action_url)  # fallback if agent stays silent
    return str(resp)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/answer", methods=["POST"])
def answer():
    """Twilio calls this when the agent picks up. Pause for greeting, then listen."""
    call_sid = request.form.get("CallSid", "unknown")
    call_states[call_sid] = {"state_idx": 0, "log": []}
    log(call_sid, "=== CALL STARTED ===")

    base = request.url_root.rstrip("/")
    resp = VoiceResponse()
    resp.pause(length=6)  # let the agent's opening greeting play out
    gather = Gather(
        input="speech",
        action=f"{base}/respond",
        method="POST",
        speech_timeout="auto",
        timeout=12,
        language="en-US",
    )
    resp.append(gather)
    resp.redirect(f"{base}/respond")
    return str(resp), 200, {"Content-Type": "text/xml"}


@app.route("/respond", methods=["POST"])
def respond():
    """Twilio calls this after each agent utterance with the transcribed speech."""
    call_sid = request.form.get("CallSid", "unknown")
    agent_speech = request.form.get("SpeechResult", "").strip()
    base = request.url_root.rstrip("/")

    state = call_states.setdefault(call_sid, {"state_idx": 0, "log": []})

    if not agent_speech:
        log(call_sid, "AGENT: [silence — re-listening]")
        return gather_response(f"{base}/respond"), 200, {"Content-Type": "text/xml"}

    log(call_sid, f"AGENT: {agent_speech}")

    idx = detect_intent(agent_speech, state["state_idx"])
    matched = STATES[idx]
    state["state_idx"] = idx + 1  # advance past the matched state

    log(call_sid, f"STATE: {matched['name']}")
    log(call_sid, f"BOT  : {matched['say']}")

    is_last = idx >= len(STATES) - 1

    if is_last:
        resp = VoiceResponse()
        resp.pause(length=1)
        resp.say(matched["say"], voice="Polly.Joanna")
        resp.pause(length=3)
        resp.hangup()
        save_log(call_sid)
        return str(resp), 200, {"Content-Type": "text/xml"}

    twiml = gather_response(f"{base}/respond", say_text=matched["say"])
    return twiml, 200, {"Content-Type": "text/xml"}


# ── Call placement ────────────────────────────────────────────────────────────

def place_call(public_url: str):
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    call = client.calls.create(
        to=os.getenv("TARGET_PHONE_NUMBER"),
        from_=os.getenv("TWILIO_FROM_NUMBER"),
        url=f"{public_url}/answer",
        record=True,
    )
    print(f"\nCall placed → {call.sid}")
    Path("logs").mkdir(exist_ok=True)
    Path("logs/last_call_sid.txt").write_text(call.sid)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        from pyngrok import ngrok
    except ImportError:
        print("ERROR: run  pip install pyngrok  then try again")
        sys.exit(1)

    tunnel = ngrok.connect(5000)
    public_url = tunnel.public_url.replace("http://", "https://")
    print(f"ngrok URL  → {public_url}")
    print("Placing call in 2 s...")

    threading.Timer(2.0, place_call, args=[public_url]).start()

    print("Webhook server running — press Ctrl+C to stop after the call ends\n")
    app.run(port=5000, debug=False, use_reloader=False)
