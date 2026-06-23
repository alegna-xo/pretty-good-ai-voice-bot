# State Log — Pretty Good AI Voice Bot

## Project Objective
Build a Python automated voice bot that places outbound calls to +1-805-439-8008, simulates realistic patient conversations (bot acts as patient calling a medical AI agent), records each call, generates transcripts, and produces a structured bug report identifying issues in the target AI agent.

## Current Phase
PRE-IMPLEMENTATION — awaiting architecture approval

## Status
- [ ] Phase 1: Core call loop (Twilio + Flask + ngrok + Claude)
- [ ] Phase 2: Transcription pipeline + 10 scenarios
- [ ] Phase 3: Bug analysis, reports, README

## Key Decisions (pending approval)
- Telephony: Twilio
- Conversation AI: Claude claude-sonnet-4-6 (Anthropic SDK)
- Transcription: OpenAI Whisper API
- Server: Flask + ngrok (for Twilio webhooks)
- Target number: +1-805-439-8008

## Last Updated
2026-06-23
