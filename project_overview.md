# Automation Assassin - Hackathon Project

## Mission
Build an AI-powered intervention system that analyzes macOS Screen Time data, detects productivity-killing patterns, and automatically generates/deploys interventions using Hammerspoon and Python.

## Core Features
1. Access and analyze macOS Screen Time data from knowledgeC.db
2. Detect "death loops" (repetitive app switching patterns)
3. Verify context (productive vs procrastination)
4. Generate Hammerspoon automations for window management
5. Create Python scripts for interventions
6. Live demo showing real data and interventions

## Technical Stack
- Python 3.9+ (main application)
- SQLite (accessing Screen Time database)
- Hammerspoon (macOS automation)
- HTML/CSS/JavaScript (visualization)
- Claude Code SDK for mutli-agent orchestration
- macOS APIs via pyobjc

## Demo Requirements (2.5 minutes)
- Show real Screen Time statistics
- Detect actual patterns from user's data
- Demonstrate live intervention (blocking apps)
- Generate working automation code
- Show measurable impact (time saved)

## Key Differentiator
Zero cold start - uses existing Screen Time history for instant value