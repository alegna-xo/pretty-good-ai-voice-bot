import os
from pathlib import Path

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_FROM_NUMBER")
target_number = os.getenv("TARGET_PHONE_NUMBER")

required = {
    "TWILIO_ACCOUNT_SID": sid,
    "TWILIO_AUTH_TOKEN": token,
    "TWILIO_FROM_NUMBER": from_number,
    "TARGET_PHONE_NUMBER": target_number,
}

missing = [name for name, value in required.items() if not value]

if missing:
    print("Missing environment variables:")
    for item in missing:
        print(f"  - {item}")
    raise SystemExit(1)

twiml = """
<Response>
    <Pause length="8"/>
    <Say voice="Polly.Joanna">
        Hi, my name is Sarah Johnson.
    </Say>

    <Pause length="10"/>

    <Say voice="Polly.Joanna">
        I would like to schedule an appointment with a primary care doctor.
    </Say>

    <Pause length="10"/>

    <Say voice="Polly.Joanna">
        The appointment is for a persistent cough and sore throat.
    </Say>

    <Pause length="10"/>

    <Say voice="Polly.Joanna">
        I am available Tuesday or Wednesday afternoon.
    </Say>

    <Pause length="5"/>

    <Say voice="Polly.Joanna">
        Thank you.
    </Say>

    <Hangup/>
</Response>
"""

client = Client(sid, token)

print(f"Calling {target_number}...")
print(f"From {from_number}")

call = client.calls.create(
    to=target_number,
    from_=from_number,
    twiml=twiml,
    record=True,
)

Path("logs").mkdir(exist_ok=True)
Path("logs/last_call_sid.txt").write_text(call.sid)

print("\nSUCCESS")
print(f"Call SID: {call.sid}")
print(f"Status:   {call.status}")
print(f"SID saved to logs/last_call_sid.txt — run fetch_transcript.py when the call ends")