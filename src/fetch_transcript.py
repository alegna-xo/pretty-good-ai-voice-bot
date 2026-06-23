"""
Phase 2: Fetch recording for a completed call and log it.

Usage:
    python src/fetch_transcript.py [CALL_SID]

If CALL_SID is omitted, reads from logs/last_call_sid.txt (written by call_bot.py).
Polls Twilio until the recording is ready (up to ~5 minutes), then downloads the MP3
and writes a metadata log to logs/transcript_<SID>.txt.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")

if not sid or not token:
    print("ERROR: TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in .env")
    raise SystemExit(1)

# Resolve call SID
if len(sys.argv) > 1:
    call_sid = sys.argv[1].strip()
else:
    sid_file = Path("logs/last_call_sid.txt")
    if not sid_file.exists():
        print("No call SID provided and logs/last_call_sid.txt not found.")
        print("Usage: python src/fetch_transcript.py <CALL_SID>")
        raise SystemExit(1)
    call_sid = sid_file.read_text().strip()

print(f"Target call SID: {call_sid}")

client = Client(sid, token)

# Fetch call metadata
call = client.calls(call_sid).fetch()
print(f"Call status  : {call.status}")
print(f"Duration     : {call.duration}s")
print(f"From         : {call.from_formatted}")
print(f"To           : {call.to_formatted}")
print(f"Start time   : {call.start_time}")
print(f"End time     : {call.end_time}")

# Poll for recording (Twilio takes 1-3 minutes after hang-up)
print("\nPolling for recording (up to 5 min)...")
recording = None
for attempt in range(30):
    recordings = client.recordings.list(call_sid=call_sid, limit=1)
    if recordings:
        recording = recordings[0]
        print(f"Recording ready: {recording.sid} ({recording.duration}s)")
        break
    print(f"  Not ready yet ({attempt + 1}/30) — retrying in 10s...")
    time.sleep(10)

logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
log_path = logs_dir / f"transcript_{call_sid}.txt"

if not recording:
    log_path.write_text(
        f"Call SID : {call_sid}\n"
        f"Status   : {call.status}\n"
        f"Duration : {call.duration}s\n"
        f"Fetched  : {datetime.utcnow().isoformat()}Z\n"
        f"\nNOTE: Recording not available after 5-minute poll. "
        f"Re-run this script in a few minutes.\n"
    )
    print(f"\nWARNING: No recording found. Metadata saved to {log_path}")
    raise SystemExit(1)

# Download the MP3
recording_url = (
    f"https://api.twilio.com"
    f"{recording.uri.replace('.json', '.mp3')}"
)
mp3_path = logs_dir / f"recording_{call_sid}.mp3"

print(f"\nDownloading MP3 to {mp3_path} ...")
resp = requests.get(recording_url, auth=(sid, token), timeout=60)
resp.raise_for_status()
mp3_path.write_bytes(resp.content)
print(f"Downloaded {len(resp.content):,} bytes")

# Write metadata log (transcript placeholder until Whisper is added)
log_text = (
    f"Call SID          : {call_sid}\n"
    f"Status            : {call.status}\n"
    f"Duration          : {call.duration}s\n"
    f"From              : {call.from_formatted}\n"
    f"To                : {call.to_formatted}\n"
    f"Start time        : {call.start_time}\n"
    f"End time          : {call.end_time}\n"
    f"Recording SID     : {recording.sid}\n"
    f"Recording duration: {recording.duration}s\n"
    f"Recording MP3     : {mp3_path}\n"
    f"Fetched at        : {datetime.utcnow().isoformat()}Z\n"
    f"\n[TRANSCRIPT PENDING — play {mp3_path} to hear the AI agent's responses]\n"
    f"[Add OPENAI_API_KEY to .env and uncomment Whisper block to auto-transcribe]\n"
)

log_path.write_text(log_text)

print(f"\nLog saved to : {log_path}")
print(f"MP3 saved to : {mp3_path}")
print("\n--- CALL METADATA ---")
print(log_text)
print("---------------------")
print("SUCCESS: Recording captured. Play the MP3 to verify the AI agent responded.")
