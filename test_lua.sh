#!/bin/bash

# Test Hammerspoon Lua Scripts
echo "🎯 Testing Automation Assassin Lua Scripts"
echo "=========================================="

# Check if Hammerspoon is installed
if ! command -v hs &> /dev/null; then
    echo "⚠️  Hammerspoon not installed!"
    echo "Install with: brew install --cask hammerspoon"
    exit 1
fi

echo "✅ Hammerspoon found"
echo ""

# Test the generated Lua scripts
echo "📝 Testing Lua scripts..."
echo ""

# Run the test script
if [ -f "test_hammerspoon.lua" ]; then
    echo "Running test suite..."
    hs test_hammerspoon.lua
else
    echo "❌ test_hammerspoon.lua not found"
    exit 1
fi

echo ""
echo "✨ Tests complete!"
echo ""
echo "To install the scripts:"
echo "  1. cp automations/*.lua ~/.hammerspoon/"
echo "  2. Add to ~/.hammerspoon/init.lua:"
echo ""
echo "     -- Automation Assassin"
echo "     local splitScreen = require('split_screen_optimizer')"
echo "     local focusMode = require('focus_mode')"
echo ""
echo "     -- Hotkeys"
echo "     hs.hotkey.bind({'cmd', 'alt'}, 'F', focusMode.toggle)"
echo "     hs.hotkey.bind({'cmd', 'alt'}, 'S', splitScreen.arrange)"
echo ""
echo "  3. Reload Hammerspoon (menubar icon → Reload Config)"