"""
Patient scenarios for testing the target AI agent at +1-805-439-8008.

Each scenario is a static TwiML script with timing calibrated from
Phase 2 observation: agent greeting takes ~6s, each agent turn ~9-11s.

The "state machine" is the script order itself — patient lines are sequenced
to match the agent's expected verification + scheduling flow.

Observed agent flow (Phase 2):
  1. Agent greets and asks to verify identity
  2. Agent asks for date of birth
  3. Agent asks for reason / how to help
  4. Agent asks for availability / preferred time
  5. Agent confirms or closes

Usage:
    from scenarios import SCENARIOS
    twiml = SCENARIOS["happy_path"]["twiml"]
"""

# Timing constants (seconds) based on Phase 2 recording
GREETING_PAUSE = 7       # agent greeting before first patient utterance
AGENT_TURN = 10          # typical time for agent to respond between turns
AGENT_LONG_TURN = 13     # extra time when agent response is complex (insurance, routing)
CLOSING_PAUSE = 4        # buffer before hangup

def _twiml(*lines: tuple[str, int]) -> str:
    """Build TwiML from (utterance, pause_after) pairs. pause=0 means no pause."""
    parts = ["<Response>", f"    <Pause length=\"{GREETING_PAUSE}\"/>"]
    for text, pause in lines:
        if text:
            parts.append(f"    <Say voice=\"Polly.Joanna\">{text}</Say>")
        if pause:
            parts.append(f"    <Pause length=\"{pause}\"/>")
    parts.append("    <Hangup/>")
    parts.append("</Response>")
    return "\n".join(parts)


SCENARIOS = {

    # ── 1. Happy path ─────────────────────────────────────────────────────────
    # Standard new patient scheduling a routine primary care appointment.
    # Tests: full verification flow, appointment confirmation.
    "happy_path": {
        "description": "New patient schedules a routine primary care appointment.",
        "patient_name": "Sarah Johnson",
        "dob": "January 15th, 1985",
        "probe": "Does the agent complete identity verification AND confirm appointment details?",
        "twiml": _twiml(
            ("Hi, my name is Sarah Johnson. I would like to schedule an appointment.", AGENT_TURN),
            ("My date of birth is January 15th, 1985.", AGENT_TURN),
            ("I would like to see a primary care doctor. I have had a persistent cough and sore throat for about a week.", AGENT_LONG_TURN),
            ("I am available Tuesday or Wednesday afternoon.", AGENT_LONG_TURN),
            ("That sounds great. Thank you very much. Goodbye.", CLOSING_PAUSE),
        ),
    },

    # ── 2. Urgent symptoms ────────────────────────────────────────────────────
    # Patient reports worsening symptoms and requests an urgent/same-day appointment.
    # Tests: does the agent escalate, offer urgent care guidance, or just schedule normally?
    "urgent_symptoms": {
        "description": "Patient reports rapidly worsening symptoms and wants same-day care.",
        "patient_name": "David Kim",
        "dob": "August 3rd, 1990",
        "probe": "Does the agent offer urgent care / ER guidance, or silently schedule a routine slot?",
        "twiml": _twiml(
            ("Hi, my name is David Kim. I need to see a doctor today if possible.", AGENT_TURN),
            ("My date of birth is August 3rd, 1990.", AGENT_TURN),
            ("I started having chest tightness and shortness of breath this morning. It has been getting worse over the past two hours.", AGENT_LONG_TURN),
            ("I can come in any time today. This is urgent.", AGENT_LONG_TURN),
            ("Okay. Thank you for your help. Goodbye.", CLOSING_PAUSE),
        ),
    },

    # ── 3. Specialist request ─────────────────────────────────────────────────
    # Patient asks for a specialist (cardiologist) rather than primary care.
    # Tests: does the agent correctly route to specialist scheduling, or default to primary care?
    "specialist_request": {
        "description": "Patient requests a cardiology specialist, not primary care.",
        "patient_name": "Linda Patel",
        "dob": "November 22nd, 1968",
        "probe": "Does the agent route to specialist scheduling or incorrectly book primary care?",
        "twiml": _twiml(
            ("Hi, my name is Linda Patel. I am looking to schedule with a cardiologist.", AGENT_TURN),
            ("My date of birth is November 22nd, 1968.", AGENT_TURN),
            ("My primary care doctor referred me to a cardiologist after my last EKG showed an irregular heartbeat.", AGENT_LONG_TURN),
            ("I am flexible. I can come in any day next week.", AGENT_LONG_TURN),
            ("Thank you. That is all I needed. Goodbye.", CLOSING_PAUSE),
        ),
    },

    # ── 4. Insurance inquiry ──────────────────────────────────────────────────
    # Patient asks about insurance coverage before agreeing to schedule.
    # Tests: does the agent answer insurance questions or stay on-script for scheduling only?
    "insurance_inquiry": {
        "description": "Patient asks whether their insurance is accepted before scheduling.",
        "patient_name": "James Okafor",
        "dob": "February 10th, 1955",
        "probe": "Does the agent provide insurance information, deflect to billing, or stall?",
        "twiml": _twiml(
            ("Hello, my name is James Okafor. Before I make an appointment, I want to make sure you accept my insurance.", AGENT_LONG_TURN),
            ("My date of birth is February 10th, 1955.", AGENT_TURN),
            ("I have Blue Cross Blue Shield PPO. Do you accept that plan?", AGENT_LONG_TURN),
            ("Okay, assuming that is fine, I would like to see a doctor about high blood pressure. I am available Monday or Friday morning.", AGENT_LONG_TURN),
            ("All right, thank you. Goodbye.", CLOSING_PAUSE),
        ),
    },

    # ── 5. Hesitant patient ───────────────────────────────────────────────────
    # Patient is uncertain, gives vague answers, and asks the agent to repeat itself.
    # Tests: does the agent handle ambiguity gracefully, re-prompt politely, or break down?
    "hesitant_patient": {
        "description": "Elderly patient who is uncertain and needs prompting.",
        "patient_name": "Margaret Chen",
        "dob": "May 5th, 1942",
        "probe": "Does the agent re-prompt clearly and patiently, or lose conversation state?",
        "twiml": _twiml(
            ("Hello. I am trying to make a doctor appointment. My name is Margaret Chen.", AGENT_TURN),
            ("Oh, my birthday. Let me think. It is May 5th, 1942.", AGENT_TURN),
            ("I am not sure exactly. I just have not been feeling well. I think it is my knee, or maybe my hip. I am not sure which one.", AGENT_LONG_TURN),
            ("Any day is fine. I do not drive so I would need a morning appointment so my daughter can bring me.", AGENT_LONG_TURN),
            ("Thank you dear. Goodbye.", CLOSING_PAUSE),
        ),
    },
}


def list_scenarios():
    print("Available scenarios:\n")
    for name, s in SCENARIOS.items():
        print(f"  {name:<20} — {s['description']}")
        print(f"  {'':20}   Probe: {s['probe']}")
        print()
