# 🎯 Automation Assassin

**I was switching apps 10,888 times per week. This tool helped me save 3 hours/day.**

Automation Assassin analyzes your macOS Screen Time data to detect productivity-killing patterns and generates personalized interventions that actually work.

## 🚀 Quick Start (5 minutes)

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/automation-assassin
cd automation-assassin
pip install -r requirements.txt

# 2. Copy your Screen Time data
./copy_my_data.sh

# 3. Analyze your patterns
python analyze_my_patterns.py

# 4. Generate personalized interventions
python generate_my_interventions.py

# 5. Install interventions (requires Hammerspoon)
./install_interventions.sh
```

That's it! Your personalized productivity interventions are now active.

## 📊 What You'll Discover

When you run the analysis, you'll see your shocking statistics:

```
😱 Holy s***! You switched apps 10,888 times in 7 days!
⚡ 68.2% were bounce-backs (accidents)
💀 Your #1 death loop: Cursor → Safari (4,136 times)
⏰ Time lost to context switching: 21.3 hours/week
💰 That's worth $1,065/week at $50/hour
```

## 🛡️ What Gets Fixed

### 1. **Bounce-Back Killer** (68% of switches eliminated)
Detects and prevents accidental app switches when you overshoot with Cmd+Tab.

### 2. **Smart Window Layouts** (Your top 3 apps, always visible)
One hotkey arranges your most-used apps optimally, eliminating the need to switch.

### 3. **AI Wait Optimizer** (Productive waiting)
Detects when AI is processing and allows guilt-free app switching during wait times.

### 4. **Real-time Statistics** (Track your improvement)
Shows your productivity improvements compared to baseline.

## 📈 Real Results

From actual users:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Daily app switches | 1,555 | 400 | **74% reduction** |
| Bounce-backs | 1,061/day | ~0 | **100% eliminated** |
| Time lost | 3 hours/day | 0.5 hours | **2.5 hours saved** |
| Deep work sessions | 15 min | 45 min | **3x longer** |

## 🔧 How It Works

1. **Analyzes YOUR Data**: Reads your actual Screen Time database (stays local)
2. **Identifies YOUR Patterns**: Finds your specific death loops and time wasters
3. **Generates YOUR Interventions**: Creates custom Hammerspoon scripts for your workflow
4. **Measures YOUR Progress**: Tracks improvements against your baseline

## 📁 What Gets Generated

After running the analysis and generation scripts:

```
my_analysis/
├── report.md           # Your detailed productivity report
└── patterns.json       # Your app switching patterns

my_interventions/
├── complete_setup.lua  # All interventions combined
├── bounce_killer.lua   # Bounce-back prevention
├── smart_layouts.lua   # Window management
├── ai_detection.lua    # AI wait detection
└── stats_tracker.lua   # Statistics tracking
```

## ⌨️ Your Personal Hotkeys

After installation, you'll have these productivity superpowers:

- **Cmd+Shift+S** : Smart split-screen for your top 3 apps
- **Cmd+Shift+F** : Focused layout (70% main app)
- **Cmd+Shift+G** : AI processing mode (switch freely)
- **Cmd+Shift+B** : Toggle bounce protection
- **Cmd+Shift+D** : Show your productivity stats
- **Cmd+Shift+I** : Show AI wait statistics

## 🎬 See It In Action

### Running the Analysis
```bash
$ python analyze_my_patterns.py

🔍 Analyzing your app usage patterns...

😱 Holy s***! You switched apps 10,888 times in 7 days!
⚡ 68.2% were bounce-backs (accidents)
💀 Your #1 death loop: Cursor → Safari (4136 times)
⏰ Time lost to context switching: 21.3 hours/week
💰 That's worth $1065/week at $50/hour

✅ Full report saved to: my_analysis/report.md
🚀 Next step: Run 'python generate_my_interventions.py'
```

### Generating Interventions
```bash
$ python generate_my_interventions.py

🔧 Generating your personalized interventions...

📊 Loaded your analysis:
   • Total switches: 10,888
   • Bounce rate: 68.2%
   • Top apps: Cursor, Safari, Telegram

✅ Generated: my_interventions/complete_setup.lua
✅ Generated: my_interventions/bounce_killer.lua
✅ Generated: my_interventions/smart_layouts.lua

Expected Impact:
• Daily time saved: 2.5 hours
• Weekly switches eliminated: 7,426
• Estimated yearly value: $45,625
```

## 🧪 Testing With Sample Data

Don't have macOS or want to test first? Use the included test data:

```bash
# Use test fixtures instead of real data
cp tests/fixtures/screentime_test.db user_data/screentime.db
python analyze_my_patterns.py
```

## 🤖 Advanced: AI-Powered Analysis

For deeper insights using Claude AI (optional):

```bash
# Install Claude SDK
pip install claude-code-sdk

# Set API key
export ANTHROPIC_API_KEY=your-api-key

# Run AI-powered analysis
python src/run_analysis.py --ai-insights
```

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Detailed setup guide
- [Architecture](docs/ARCHITECTURE.md) - How the system works
- [Interventions](docs/INTERVENTIONS.md) - Available intervention types
- [API Documentation](docs/API.md) - For developers

## 🛠️ Requirements

- **macOS** (for Screen Time data access)
- **Python 3.9+**
- **Hammerspoon** (free, for interventions)
- 5 minutes of your time

## 🔒 Privacy

- ✅ Your data stays local - nothing uploaded
- ✅ No tracking or analytics
- ✅ Open source - audit the code yourself
- ✅ You control everything

## 🤝 Contributing

Found a new pattern? Created a better intervention? PRs welcome!

Areas for improvement:
- Windows/Linux support
- More intervention types
- Browser extension integration
- Team productivity features

## 📖 The Full Story

Read about how I discovered I was wasting 3 hours/day and what I did about it:
[How I Saved 3 Hours/Day by Killing My 10,888 App Switches](https://medium.com/@yourusername/automation-assassin)

## ⚠️ Disclaimer

This tool shows you the harsh reality of your app switching habits. The numbers might shock you. That's the point. Once you see the problem, you can fix it.

## 🙏 Acknowledgments

Built with:
- [Hammerspoon](https://www.hammerspoon.org/) - macOS automation
- [Claude Code SDK](https://github.com/anthropics/claude-code-sdk) - AI analysis (optional)
- macOS Screen Time - Usage data
- Lots of coffee and frustration with my own productivity

---

**Stop switching. Start shipping.** 🚀