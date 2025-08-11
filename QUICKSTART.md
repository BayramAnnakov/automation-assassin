# 🚀 Automation Assassin - Quick Start Guide

Get your personalized productivity interventions running in 5 minutes!

## Prerequisites

- **macOS** (required for Screen Time data)
- **Python 3.9+** 
- **Homebrew** (for installing Hammerspoon)

## Step 1: Setup (1 minute)

```bash
# Clone the repository
git clone https://github.com/yourusername/automation-assassin
cd automation-assassin

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Step 2: Copy Your Data (1 minute)

This copies your Screen Time data for analysis (stays local on your machine):

```bash
# Easy way - use our script
./copy_my_data.sh

# OR manually copy your data
mkdir -p user_data
cp ~/Library/Application\ Support/Knowledge/knowledgeC.db ./user_data/screentime.db

# Optional: Add browser history for better insights
cp ~/Library/Safari/History.db ./user_data/safari_history.db
cp ~/Library/Application\ Support/Google/Chrome/Default/History ./user_data/chrome_history.db
```

## Step 3: Analyze Your Patterns (1 minute)

Discover your shocking app-switching statistics:

```bash
python analyze_my_patterns.py
```

You'll see output like:
```
😱 Holy s***! You switched apps 10,888 times in 7 days!
⚡ 68.2% were bounce-backs (accidents)
💀 Your #1 death loop: Cursor → Safari (4136 times)
⏰ Time lost to context switching: 21.3 hours/week

✅ Full report saved to: my_analysis/report.md
```

Open `my_analysis/report.md` to see your detailed productivity analysis.

## Step 4: Generate Your Interventions (1 minute)

Create personalized Hammerspoon scripts based on YOUR patterns:

```bash
python generate_my_interventions.py
```

This creates:
- `my_interventions/complete_setup.lua` - Your complete intervention suite
- Individual components for customization

## Step 5: Install Interventions (1 minute)

### Install Hammerspoon

```bash
# Install Hammerspoon (macOS automation tool)
brew install --cask hammerspoon

# OR download from https://www.hammerspoon.org/
```

### Deploy Your Interventions

```bash
# Use our installer script
./install_interventions.sh

# OR manually install
cp my_interventions/complete_setup.lua ~/.hammerspoon/init.lua
```

### Grant Permissions

Hammerspoon needs permissions to work:

1. Open **System Preferences → Privacy & Security → Accessibility**
2. Add Hammerspoon (click the + and select from Applications)
3. Open **System Preferences → Privacy & Security → Screen Recording** 
4. Add Hammerspoon (for window management)

### Reload Configuration

- Click the Hammerspoon icon in your menu bar
- Select "Reload Config"
- OR press `Cmd+Ctrl+R` with Hammerspoon open

## ✅ You're Done!

Your personalized interventions are now active. Try these:

### Test Your Hotkeys

| Hotkey | Action |
|--------|--------|
| **Cmd+Shift+S** | Arrange your top 3 apps in split-screen |
| **Cmd+Shift+F** | Focus mode (70% main app) |
| **Cmd+Shift+D** | Show your productivity stats |
| **Cmd+Shift+G** | Toggle AI processing mode |
| **Cmd+Shift+B** | Toggle bounce protection |

### Test Bounce Protection

1. Switch between two apps rapidly with Cmd+Tab
2. You should see "⚡ Bounce detected!" alerts
3. After 3 bounces, you'll get a suggestion to use split-screen

### Check Your Stats

Press `Cmd+Shift+D` anytime to see:
- Current switches vs your baseline
- Bounce rate improvement
- Time saved

## 📊 Understanding Your Results

### Your Analysis Report

Open `my_analysis/report.md` to see:
- Total app switches and patterns
- Your specific "death loops"
- Time and money lost to context switching
- MCP automation opportunities

### Expected Improvements

Based on typical results:
- **Week 1**: 50% reduction in bounces
- **Week 2**: 30% reduction in total switches
- **Month 1**: 2-3 hours/day saved

## 🛠️ Customization

### Adjust Sensitivity

Edit `~/.hammerspoon/init.lua`:

```lua
-- Change bounce detection threshold (default: 1.0 seconds)
if timeSinceLastSwitch < 2.0 then  -- More lenient

-- Change window layout percentages
w = screen.w * 0.6  -- Give main app 60% instead of 50%
```

### Add More Apps

Your interventions are generated for your top 3 apps. To add more:

1. Edit `~/.hammerspoon/init.lua`
2. Add your app to the layout functions
3. Reload Hammerspoon

## ❓ Troubleshooting

### "No Screen Time data found!"

- Make sure Screen Time is enabled: System Preferences → Screen Time
- Try copying manually: `cp ~/Library/Application\ Support/Knowledge/knowledgeC.db ./user_data/screentime.db`

### Hotkeys Not Working

- Grant Accessibility permissions to Hammerspoon
- Check for conflicts with other apps using same hotkeys
- Try reloading: Click Hammerspoon → Reload Config

### Windows Not Moving

- Grant Screen Recording permission to Hammerspoon
- Make sure the apps are actually running
- Check app names match (e.g., "Google Chrome" not "Chrome")

### Stats Show 0

- Stats start fresh from installation
- Give it a few hours to collect meaningful data
- Your baseline is saved for comparison

## 🚀 Next Steps

1. **Use it for a day** - Let the interventions work
2. **Check your stats** - Press Cmd+Shift+D to see improvements
3. **Adjust as needed** - Customize layouts and thresholds
4. **Install MCP servers** - For even more automation (see report)

## 📚 Learn More

- [Full Documentation](README.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Creating Custom Interventions](docs/INTERVENTIONS.md)
- [API Reference](docs/API.md)

## 💡 Pro Tips

1. **AI Mode**: Press `Cmd+Shift+G` before triggering AI generation to switch apps guilt-free
2. **Evening Mode**: High switch times often happen 9-11 PM - interventions are stronger then
3. **Zen Mode**: Hide all apps except your main one with custom hotkeys
4. **Track Progress**: Check stats daily to stay motivated

---

**Questions?** Open an issue on GitHub
**Success story?** Share your before/after stats!

Remember: The goal isn't zero app switches - it's eliminating unnecessary ones and making necessary ones efficient.