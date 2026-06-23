# Pretty Good AI Voice Bot

Automated patient simulator that places outbound calls to an AI scheduling agent, records the conversation, and produces structured bug reports.

**Target agent**: +1-805-439-8008

---

## How It Works

The bot places a Twilio outbound call with a static TwiML script. Each script is a patient "scenario" — a sequence of utterances timed to match the agent's expected verification and scheduling flow, calibrated from live call recordings.

```
run_scenario.py  →  Twilio places call  →  Agent answers
                                         ↓
                     Patient script plays (name → DOB → reason → availability → confirm)
                                         ↓
                     Call ends, recording available on Twilio (~2 min)
                                         ↓
fetch_transcript.py  →  Download MP3 to logs/
                                         ↓
generate_report.py   →  Pre-fill bug report in reports/
                                         ↓
                         Listen to MP3 and fill in findings
```

No server, no ngrok, no streaming. All logic runs locally; calls are placed synchronously via the Twilio REST API.

---

## Setup

**Prerequisites**: Python 3.11+, a Twilio account, an active phone number.

```bash
pip install -r requirements.txt
```

Create `.env`:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=+1XXXXXXXXXX
TARGET_PHONE_NUMBER=+18054398008
```

---

## Usage

### 1. Run a scenario

```bash
python src/run_scenario.py                    # list all scenarios
python src/run_scenario.py happy_path
python src/run_scenario.py urgent_symptoms
python src/run_scenario.py specialist_request
python src/run_scenario.py insurance_inquiry
python src/run_scenario.py hesitant_patient
```

### 2. Download the recording (after call ends)

```bash
python src/fetch_transcript.py
# or with an explicit SID:
python src/fetch_transcript.py CA...
```

Recording saved to `logs/recording_<SID>.mp3`.

### 3. Generate the bug report

```bash
python src/generate_report.py
```

Pre-filled markdown report written to `reports/bug_report_<scenario>_<SID>.md`.
Open the MP3, listen, and fill in the AGENT BEHAVIOR and BUGS FOUND sections.

---

## Scenarios

| Scenario | Patient | Tests |
|---|---|---|
| `happy_path` | Sarah Johnson | Full verification → scheduling → confirm |
| `urgent_symptoms` | David Kim | Escalation / urgent care routing |
| `specialist_request` | Linda Patel | Specialist vs. primary care routing |
| `insurance_inquiry` | James Okafor | Insurance question handling |
| `hesitant_patient` | Margaret Chen | Ambiguity tolerance / re-prompting |

Each scenario probes a different failure mode. Observation from Phase 2: the agent opens with identity verification (name, then DOB) before accepting scheduling requests. All scenarios are scripted to complete that flow before advancing to the scenario-specific test.

---

## Timing Model

Calibrated from Phase 2 recording (55s call, incomplete due to bot skipping verification):

| Event | Pause |
|---|---|
| Agent greeting | 7s |
| Agent turn (typical) | 10s |
| Agent turn (complex response) | 13s |
| After final patient line | 4s then hangup |

A complete happy-path call should run ~75–90 seconds.

---

## Output Files

```
logs/
  last_call_sid.txt          — SID of the most recent call
  last_call_meta.txt         — scenario metadata for report generation
  recording_<SID>.mp3        — raw call recording (both sides)
  transcript_<SID>.txt       — call metadata log

reports/
  bug_report_<scenario>_<SID>.md   — structured findings (fill in after listening)
```

---

## File Structure

```
src/
  scenarios.py          — patient scenario definitions + TwiML scripts
  run_scenario.py       — place a call for a named scenario
  fetch_transcript.py   — download recording from Twilio after call ends
  generate_report.py    — generate pre-filled bug report markdown
  call_bot.py           — Phase 1 static script (kept for reference)
```

---

## Phase Log

| Phase | Status | Result |
|---|---|---|
| Phase 1: Outbound call | Complete | 55s call, agent answered |
| Phase 2: Recording capture | Complete | 217KB MP3, agent requested identity verification |
| Phase 3: State-machine scenarios | In progress | |
| Phase 4: Bug reports + README | In progress | |
