# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automation Assassin is an AI-powered intervention system that analyzes macOS Screen Time data to detect and prevent productivity-killing patterns. The system automatically generates and deploys interventions using Hammerspoon and Python.

## Architecture

### Core Components
- **Screen Time Data Analysis**: Accesses macOS knowledgeC.db to retrieve app usage history
- **Pattern Detection Engine**: Identifies "death loops" and repetitive app switching patterns
- **AI-Powered Pattern Analysis**: Uses Claude Code sub-agents for intelligent, context-aware pattern interpretation
- **Browser History Integration**: Augments app usage data with browser context for deeper understanding
- **Root Cause Analysis**: Identifies underlying reasons behind productivity patterns (stress, knowledge gaps, etc.)
- **Educational Intervention System**: Provides coaching and learning paths rather than just blocking behaviors
- **Intervention Generator**: Creates Hammerspoon automations, educational content, and coaching messages

### Data Sources
1. **Screen Time Database**: 
   - Location: `~/Library/Application Support/Knowledge/knowledgeC.db`
   - ZOBJECT table contains app usage data
   - Timestamps use macOS reference date (2001-01-01), requiring +978307200 for Unix epoch conversion
   - Filter by ZSTREAMNAME = '/app/usage' for app usage data

2. **Browser History**:
   - Safari: `~/Library/Safari/History.db`
   - Chrome: `~/Library/Application Support/Google/Chrome/Default/History`
   - Firefox: `~/Library/Application Support/Firefox/Profiles/*/places.sqlite`
   - Provides context for web-based activities and patterns

## Development Commands

### Python Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt
```

### Database Access
```bash
# Copy Screen Time database for analysis (read-only access)
cp ~/Library/Application\ Support/Knowledge/knowledgeC.db ./screentime_copy.db

# Query example
sqlite3 ./screentime_copy.db "SELECT DATETIME(ZSTARTDATE + 978307200, 'unixepoch', 'localtime'), ZVALUESTRING FROM ZOBJECT WHERE ZSTREAMNAME = '/app/usage' LIMIT 10;"
```

### Hammerspoon Testing
```bash
# Reload Hammerspoon configuration
hs -c "hs.reload()"

# Test intervention script
hs intervention_script.lua
```

## Technology Stack
- Python 3.9+ for main application logic
- SQLite for Screen Time database access
- Hammerspoon for macOS automation
- HTML/CSS/JavaScript for visualization
- Claude Code SDK for multi-agent orchestration
- pyobjc for macOS API integration

## AI Agents
The system uses specialized Claude Code sub-agents:

1. **pattern-interpreter**: Analyzes app switching patterns intelligently
2. **browser-context**: Interprets browser history without hardcoded categorization
3. **context-learner**: Builds user profiles and work patterns over time
4. **behavioral-coach**: Provides empathetic coaching and educational interventions

## Intervention System
The system offers four levels of intervention:

1. **Insights Only**: Explains behaviors without action requirements
2. **Gentle Coaching**: Provides suggestions and alternatives
3. **Active Learning**: Delivers tutorials and skill-building exercises
4. **Comprehensive**: Combines insights, coaching, education, and tools

Interventions address root causes:
- Knowledge gaps → Structured learning paths
- Stress responses → Stress management techniques
- Skill deficits → Workflow optimization training
- Emotional regulation → Task decomposition and anxiety management

## Key Implementation Notes

1. **Database Safety**: Always work with a copy of knowledgeC.db, never modify the original
2. **Timestamp Handling**: Remember to convert macOS timestamps (seconds since 2001-01-01) to Unix timestamps
3. **Hammerspoon Integration**: Generated Lua scripts should be compatible with Hammerspoon's API
4. **Privacy Consideration**: Screen Time and browser history data are sensitive - handle with appropriate care
5. **AI-Powered Analysis**: Pattern analysis uses Claude Code sub-agents for flexibility across user types
6. **Educational Focus**: System prioritizes understanding and education over blocking behaviors
7. **Root Cause Approach**: Interventions address underlying causes (stress, knowledge gaps) not just symptoms

## Demo Requirements
The system must demonstrate:
- Real Screen Time statistics visualization
- Live pattern detection from actual user data
- AI-powered pattern interpretation with browser context
- Educational interventions (tutorials, coaching messages)
- Root cause analysis of productivity patterns
- Working interventions (both blocking and educational)
- Generated automation code that functions correctly
- Measurable impact metrics (time saved, knowledge gained)
- use venv befor executing scripts