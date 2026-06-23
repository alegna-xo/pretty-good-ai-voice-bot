"""
Place a test call using a named patient scenario.

Usage:
    python src/run_scenario.py                      # list scenarios
    python src/run_scenario.py happy_path           # run a scenario
    python src/run_scenario.py urgent_symptoms
    python src/run_scenario.py specialist_request
    python src/run_scenario.py insurance_inquiry
    python src/run_scenario.py hesitant_patient

After the call ends, run:
    python src/fetch_transcript.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from twilio.rest import Client

from scenarios import SCENARIOS, list_scenarios

load_dotenv()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        list_scenarios()
        print("Usage: python src/run_scenario.py <scenario_name>")
        return

    name = sys.argv[1]
    if name not in SCENARIOS:
        print(f"ERROR: Unknown scenario '{name}'")
        print()
        list_scenarios()
        raise SystemExit(1)

    scenario = SCENARIOS[name]

    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    target = os.getenv("TARGET_PHONE_NUMBER")

    missing = [k for k, v in {
        "TWILIO_ACCOUNT_SID": sid,
        "TWILIO_AUTH_TOKEN": token,
        "TWILIO_FROM_NUMBER": from_number,
        "TARGET_PHONE_NUMBER": target,
    }.items() if not v]

    if missing:
        for m in missing:
            print(f"Missing env var: {m}")
        raise SystemExit(1)

    print(f"Scenario    : {name}")
    print(f"Description : {scenario['description']}")
    print(f"Patient     : {scenario['patient_name']} (DOB {scenario['dob']})")
    print(f"Probe       : {scenario['probe']}")
    print(f"Target      : {target}")
    print()

    client = Client(sid, token)
    call = client.calls.create(
        to=target,
        from_=from_number,
        twiml=scenario["twiml"],
        record=True,
    )

    Path("logs").mkdir(exist_ok=True)
    Path("logs/last_call_sid.txt").write_text(call.sid)

    # Save scenario metadata alongside the SID for the bug report
    meta = (
        f"scenario={name}\n"
        f"patient_name={scenario['patient_name']}\n"
        f"dob={scenario['dob']}\n"
        f"probe={scenario['probe']}\n"
        f"description={scenario['description']}\n"
    )
    Path("logs/last_call_meta.txt").write_text(meta)

    print(f"Call placed : {call.sid}")
    print(f"Status      : {call.status}")
    print()
    print("Wait for the call to complete, then run:")
    print("    python src/fetch_transcript.py")


if __name__ == "__main__":
    main()
