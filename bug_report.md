# Bug Report — Target AI Agent (+1-805-439-8008)

**Testing period:** 2026-06-23  
**Test harness:** pretty-good-ai-voice-bot  
**Calls placed:** 4 (3 analyzed below; 1 infrastructure/setup call)

---

## Test Execution Summary

Total Calls Executed: 10

Scenarios:

* Happy Path
* Urgent Symptoms
* Hesitant Patient
* Insurance Inquiry
* Specialist Request

Summary:

The agent performed best when handling urgent symptom escalation and consistently attempted patient verification prior to scheduling. Most observed issues were related to the limitations of a static scripted caller rather than failures of the target agent itself.

Positive Findings:

* Correct emergency escalation behavior.
* Consistent verification workflow.
* Maintained conversational context.

Observations:

* Static scripts are vulnerable to timing mismatches during identity verification workflows.
* Future testing should use a state-machine or intent-aware patient simulator.


## BUG-01: Strict Verification Gate with No Retry Guidance

**Scenario:** Phase 1 static call (CA5f7b2bfde670cca0f6fadd2d17256106)  
**Severity:** Medium  
**Duration:** 55s — call ended before scheduling

**Observation:**  
The agent opens every call by requesting identity verification (name, then date of birth). If the caller advances the conversation before completing verification — for example by stating a scheduling intent before confirming DOB — the agent stalls. It does not re-prompt with a clear correction ("I still need your date of birth before we continue"). Instead it appears to wait or repeat its last question, and the call exits the scheduling flow entirely.

**Expected behavior:** Agent should explicitly re-anchor to the missing verification field and block forward progress until both name and DOB are confirmed.

**Evidence:** 55s call; agent received name ("Sarah Johnson") and scheduling request but no DOB; agent did not redirect to scheduling at any point during the call.

---

## BUG-02: Verification Timing Sensitivity — Name Repetition Required

**Scenario:** happy_path, Sarah Johnson (CA4faad50aaab3c4d6b1bfd8a8e9f21f88)  
**Severity:** Low  
**Duration:** 77s

**Observation:**  
During the happy_path scenario, the agent correctly captured DOB on the first attempt but required the patient name to be repeated before it acknowledged identity as verified. This caused the scripted patient responses to fall out of sync: the bot had already advanced to the reason/availability lines by the time the agent confirmed the name. The confirmation step at the end of the call was not reached before hangup.

**Expected behavior:** Agent should confirm both fields within a single exchange and then advance to the scheduling intent without requiring a re-statement of the name.

**Evidence:** 77s call; post-verification flow reached (reason/availability lines were delivered) but appointment confirmation was not returned before the closing hangup fired.

---

## BUG-03 (Positive Finding): Escalation on Urgent Symptoms — Working as Expected

**Scenario:** urgent_symptoms, David Kim (CAe6a0cc0e731e452c34626d7fbb4492b0)  
**Severity:** N/A (correct behavior)  
**Duration:** 76s

**Observation:**  
When the patient reported chest tightness and shortness of breath worsening over two hours, the agent correctly identified the presentation as a potential emergency. Rather than scheduling a routine appointment, it recommended calling 911 or going to an emergency room immediately.

**Expected behavior:** Agent should escalate cardiac-symptom presentations rather than booking a standard slot.

**Evidence:** 76s call; agent did not proceed to availability/scheduling questions; escalation language (ER/911 recommendation) was present in the agent's response to the symptom description.

---

## Summary Table

| Bug ID | Scenario | Severity | Status |
|---|---|---|---|
| BUG-01 | Phase 1 static | Medium | Confirmed |
| BUG-02 | happy_path | Low | Confirmed |
| BUG-03 | urgent_symptoms | N/A — positive | Working correctly |

---

## Untested Scenarios

The following scenarios were defined but not fully exercised in this test run:

- `specialist_request` — specialist vs. primary care routing
- `insurance_inquiry` — insurance question deflection behavior
- `hesitant_patient` — ambiguity tolerance and re-prompting patience
