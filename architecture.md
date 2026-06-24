# Architecture — Pretty Good AI Voice Bot

## Overview

The bot is a serverless outbound call harness built on Twilio's REST API. There are two execution modes: a static TwiML mode (`call_bot.py`, `run_scenario.py`) and a dynamic webhook mode (`smart_bot.py`). In static mode, the entire patient script is compiled into a TwiML document and submitted at call-creation time; Twilio plays it sequentially with fixed pauses, and no runtime logic runs on the local machine during the call. In dynamic mode, `smart_bot.py` starts a Flask server, exposes it via ngrok, and receives a POST from Twilio after each agent utterance containing a live speech-to-text transcription (`SpeechResult`). A forward-biased keyword matcher maps the transcription to the next conversation state and returns a new TwiML fragment instructing Twilio what to say next. Recordings are captured by Twilio and pulled after the call via `fetch_transcript.py`; there is no real-time audio processing on the local machine. 10-call test execution.

## Data Flow

```
run_scenario.py / call_bot.py
  → Twilio REST API (call create, TwiML inline)
    → Agent at +1-805-439-8008 answers
      → Static TwiML plays sequentially (fixed timing)
        → Call ends, Twilio stores recording

smart_bot.py
  → ngrok tunnel → Flask /answer
    → Agent answers → Twilio streams SpeechResult to /respond
      → Keyword matcher selects next state
        → New TwiML returned, Gather listens again
          → Loop until confirm state → Hangup

fetch_transcript.py
  → Twilio REST API → download MP3 → logs/recording_<SID>.mp3
```

The static and dynamic modes represent two generations of the bot. Static mode revealed the timing sensitivity of the agent's verification gate; dynamic mode was built to respond to actual agent utterances rather than assumed timing, making it resilient to variable agent response latency. Both modes record both sides of the call, so agent behavior is auditable from the MP3 regardless of which mode was used.
