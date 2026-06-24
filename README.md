# Pretty Good AI Voice Bot

Automated patient simulator that places outbound calls to an AI scheduling agent, records the conversation, and produces structured bug reports.

**Target agent**: +1-805-439-8008

---

## Project Walkthrough

Loom Video:
https://www.loom.com/share/b74be4f3ac6445cb91d1c98a47d71297

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

## Findings

### Phase 1 — Static Script (call_bot.py)

**Call:** CA5f7b2bfde670cca0f6fadd2d17256106 | 55s  
**Result:** Verification flow mismatch. The agent opened with an identity verification request (name and date of birth) but the static TwiML script was written for a scheduling flow. The bot delivered scheduling lines before identity was confirmed, causing the agent to stall awaiting DOB. The call ended before reaching the scheduling stage.

**Key finding:** The target agent enforces a strict identity verification gate — name and DOB must both be confirmed before any scheduling action is accepted.

---

### Phase 2 — Scenario: happy_path (Sarah Johnson)

**Call:** CA4faad50aaab3c4d6b1bfd8a8e9f21f88 | 77s  
**Result:** Partial success. The agent caught the DOB (`January 15th, 1985`) on the first attempt but needed the patient name repeated before advancing. The static scenario script advanced to the reason/availability lines before the agent had confirmed both identity fields, creating a timing mismatch. Appointment scheduling was partially reached but the confirmation step was missed before hangup.

**Key finding:** The static timing model (10s per turn) is too aggressive. The agent spends additional time on name disambiguation before accepting DOB.

---

### Phase 3 — Scenario: urgent_symptoms (David Kim)

**Call:** CAe6a0cc0e731e452c34626d7fbb4492b0 | 76s  
**Result:** Escalation behavior confirmed. When the patient reported chest tightness and shortness of breath worsening over two hours, the agent recognized the potential emergency and recommended calling 911 or going to an emergency room rather than scheduling a routine appointment. The agent did not silently book a standard slot.

**Key finding:** The target agent has functional urgency/escalation logic for cardiac-symptom keywords. It does not route emergency presentations to normal scheduling.

---

## Phase Log

| Phase | Status | Result |
|---|---|---|
| Phase 1: Outbound call | Complete | 55s call; verification flow mismatch — agent awaited DOB bot never provided |
| Phase 2: Recording capture | Complete | 217KB MP3; identity verification gate confirmed |
| Phase 3: Scenario testing | Complete | happy_path (timing mismatch), urgent_symptoms (escalation confirmed) |
| Phase 4: Bug reports + README | Complete | |

## Final Testing Results

A total of 10 automated outbound test calls were executed against the target medical voice AI agent.

Scenarios tested included:

* Happy Path Appointment Scheduling
* Urgent Symptoms
* Hesitant Patient
* Insurance Inquiry
* Specialist Request

Key Findings:

* The agent appropriately escalated urgent chest pain symptoms and recommended emergency care.
* The agent consistently attempted identity verification before scheduling.
* Static scripted callers can create conversational timing mismatches when the agent requests additional verification information.
* The agent maintained conversation context across multiple patient scenarios.

All calls were recorded and analyzed as part of the testing process.
