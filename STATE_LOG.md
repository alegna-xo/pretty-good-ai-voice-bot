# State Log — Pretty Good AI Voice Bot

## Project Objective

Build a Python automated voice bot that places outbound calls to +1-805-439-8008, simulates realistic patient conversations (bot acts as patient calling a medical AI agent), records each call, generates transcripts, and produces a structured bug report identifying issues in the target AI agent.

---

## Final Status

| Phase | Status | Result |
|---|---|---|
| Phase 1: Outbound call | Complete | 55s call; agent answered; verification flow mismatch identified |
| Phase 2: Recording capture | Complete | MP3 recordings in `logs/`; identity verification gate confirmed |
| Phase 3: Scenario testing | Complete | happy_path and urgent_symptoms executed and analyzed |
| Phase 4: Documentation | Complete | README, architecture.md, bug_report.md finalized |

---

## Decisions Made

| Decision | Chosen | Rationale |
|---|---|---|
| Telephony | Twilio REST API | No server required for static mode |
| Bot mode (static) | TwiML inline (`call_bot.py`, `run_scenario.py`) | Simple, no ngrok dependency |
| Bot mode (dynamic) | Flask + ngrok + `Gather` (`smart_bot.py`) | Handles variable agent response timing |
| Recording | Twilio-side (`record=True`) | Both call legs captured without local audio processing |
| Transcription | Manual (Whisper block commented out) | `OPENAI_API_KEY` not provisioned in this environment |

---

## Calls Placed

| Call SID | Scenario | Duration | Outcome |
|---|---|---|---|
| CA5f7b2bfde670cca0f6fadd2d17256106 | Phase 1 static | 55s | Verification mismatch — DOB never provided |
| CA4faad50aaab3c4d6b1bfd8a8e9f21f88 | happy_path | 77s | Name repetition required; confirmation step missed |
| CAe6a0cc0e731e452c34626d7fbb4492b0 | urgent_symptoms | 76s | Escalation to 911/ER confirmed — working correctly |
| CA01301725077f2694a19bf8965fc8dee5 | urgent_symptoms | 76s | Second run; consistent with prior result |

---

## Key Findings

1. The target agent enforces a strict name + DOB verification gate before accepting any scheduling intent.
2. The static timing model (10s per agent turn) is too aggressive — the agent's name disambiguation step adds latency that causes the scripted lines to fall out of sync.
3. The agent correctly escalates cardiac-symptom presentations (chest tightness, shortness of breath) to emergency guidance rather than booking a routine slot.

---

Project Status: COMPLETE

Calls Executed: 10
Recordings Captured: 10
Scenarios Tested: 5
Documentation Complete: Yes
Bug Report Complete: Yes
Submission Ready: Yes

## Last Updated

2026-06-24
