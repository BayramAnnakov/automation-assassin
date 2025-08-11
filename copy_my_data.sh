#!/bin/bash

# Copy your Screen Time and browser history data for analysis
# This script helps you gather your productivity data safely

echo "═══════════════════════════════════════════════════════════"
echo "📊 Automation Assassin - Data Collection"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Create user_data directory
echo "📂 Creating user_data directory..."
mkdir -p user_data

# Copy Screen Time database
echo "📱 Copying Screen Time data..."
if [ -f ~/Library/Application\ Support/Knowledge/knowledgeC.db ]; then
    cp ~/Library/Application\ Support/Knowledge/knowledgeC.db ./user_data/screentime.db
    echo "  ✅ Screen Time data copied successfully"
    
    # Get file size
    size=$(du -h ./user_data/screentime.db | cut -f1)
    echo "  📊 Database size: $size"
else
    echo "  ❌ Screen Time database not found"
    echo "  Note: This requires macOS with Screen Time enabled"
    exit 1
fi

echo ""
echo "🌐 Copying browser history (optional)..."

# Safari history
if [ -f ~/Library/Safari/History.db ]; then
    cp ~/Library/Safari/History.db ./user_data/safari_history.db
    echo "  ✅ Safari history copied"
else
    echo "  ⚠️  Safari history not found (optional)"
fi

# Chrome history
if [ -f ~/Library/Application\ Support/Google/Chrome/Default/History ]; then
    cp ~/Library/Application\ Support/Google/Chrome/Default/History ./user_data/chrome_history.db
    echo "  ✅ Chrome history copied"
else
    echo "  ⚠️  Chrome history not found (optional)"
fi

# Firefox history
if [ -d ~/Library/Application\ Support/Firefox/Profiles ]; then
    firefox_profile=$(ls ~/Library/Application\ Support/Firefox/Profiles | grep default-release | head -1)
    if [ -n "$firefox_profile" ]; then
        if [ -f ~/Library/Application\ Support/Firefox/Profiles/$firefox_profile/places.sqlite ]; then
            cp ~/Library/Application\ Support/Firefox/Profiles/$firefox_profile/places.sqlite ./user_data/firefox_history.db
            echo "  ✅ Firefox history copied"
        fi
    else
        echo "  ⚠️  Firefox history not found (optional)"
    fi
else
    echo "  ⚠️  Firefox not installed (optional)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Data collection complete!"
echo ""
echo "📊 Next steps:"
echo "  1. Run: python analyze_my_patterns.py"
echo "     This will analyze your app usage patterns"
echo ""
echo "  2. Run: python generate_my_interventions.py"
echo "     This will create personalized automations"
echo ""
echo "🔒 Privacy note: Your data stays local - nothing is uploaded"
echo "═══════════════════════════════════════════════════════════"