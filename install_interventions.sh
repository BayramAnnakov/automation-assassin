#!/bin/bash

# Install your personalized interventions to Hammerspoon
# Run this after generate_my_interventions.py

echo "═══════════════════════════════════════════════════════════"
echo "🔨 Automation Assassin - Intervention Installation"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if interventions exist
if [ ! -d "my_interventions" ]; then
    echo "❌ No interventions found!"
    echo "Please run 'python generate_my_interventions.py' first"
    exit 1
fi

# Check if Hammerspoon is installed
if [ ! -d "/Applications/Hammerspoon.app" ]; then
    echo "❌ Hammerspoon not installed!"
    echo ""
    echo "To install Hammerspoon:"
    echo "  brew install --cask hammerspoon"
    echo ""
    echo "Or download from: https://www.hammerspoon.org/"
    exit 1
fi

# Create Hammerspoon config directory if it doesn't exist
if [ ! -d ~/.hammerspoon ]; then
    echo "📁 Creating Hammerspoon config directory..."
    mkdir -p ~/.hammerspoon
fi

# Backup existing config if it exists
if [ -f ~/.hammerspoon/init.lua ]; then
    echo "💾 Backing up existing Hammerspoon config..."
    cp ~/.hammerspoon/init.lua ~/.hammerspoon/init.lua.backup.$(date +%Y%m%d_%H%M%S)
    echo "  ✅ Backup saved"
fi

# Install the complete setup
echo "📦 Installing your personalized interventions..."
cp my_interventions/complete_setup.lua ~/.hammerspoon/init.lua
echo "  ✅ Interventions installed"

# Create a reference directory for individual components
echo "📚 Copying individual components for reference..."
mkdir -p ~/.hammerspoon/automation_assassin_components
cp my_interventions/*.lua ~/.hammerspoon/automation_assassin_components/
echo "  ✅ Components saved to ~/.hammerspoon/automation_assassin_components/"

# Reload Hammerspoon config
echo ""
echo "🔄 Reloading Hammerspoon configuration..."
if command -v hs &> /dev/null; then
    hs -c "hs.reload()"
    echo "  ✅ Configuration reloaded via CLI"
else
    echo "  ⚠️  Please reload manually:"
    echo "     • Click Hammerspoon icon in menu bar"
    echo "     • Select 'Reload Config'"
    echo "     OR press Cmd+Ctrl+R with Hammerspoon open"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Installation Complete!"
echo ""
echo "🎯 YOUR PERSONAL HOTKEYS:"
echo "  • Cmd+Shift+S : Smart split-screen layout"
echo "  • Cmd+Shift+F : Focused layout (70% main app)"
echo "  • Cmd+Shift+G : AI processing mode (no bounce warnings)"
echo "  • Cmd+Shift+B : Toggle bounce protection"
echo "  • Cmd+Shift+D : Show your productivity stats"
echo "  • Cmd+Shift+I : Show AI wait statistics"
echo ""
echo "🧪 TEST YOUR SETUP:"
echo "  1. Try Cmd+Tab quickly between apps"
echo "     → Should see bounce warnings"
echo "  2. Press Cmd+Shift+S"
echo "     → Apps should arrange in split-screen"
echo "  3. Press Cmd+Shift+D"
echo "     → Should see your statistics"
echo ""
echo "📊 TRACKING YOUR PROGRESS:"
echo "  Stats reset when you install, so give it a few hours"
echo "  to see meaningful improvements over your baseline."
echo ""
echo "⚙️  PERMISSIONS:"
echo "  If hotkeys don't work, grant Hammerspoon:"
echo "  • System Preferences → Privacy → Accessibility"
echo "  • System Preferences → Privacy → Screen Recording"
echo "═══════════════════════════════════════════════════════════"