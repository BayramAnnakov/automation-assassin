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
    # Try copying Screen Time data with error handling
    if cp ~/Library/Application\ Support/Knowledge/knowledgeC.db ./user_data/screentime.db 2>/dev/null; then
        echo "  ✅ Screen Time data copied successfully"
        
        # Get file size
        size=$(du -h ./user_data/screentime.db | cut -f1)
        echo "  📊 Database size: $size"
    else
        echo "  ❌ Screen Time data access denied (macOS privacy protection)"
        echo "  💡 To enable Screen Time data access:"
        echo "     1. Open System Settings → Privacy & Security → Full Disk Access"
        echo "     2. Click the '+' button and add Terminal (or your terminal app)"
        echo "     3. Restart Terminal and run this script again"
        echo ""
        echo "  🔄 Alternative: Run this command to copy Screen Time data manually:"
        echo "     sudo cp ~/Library/Application\ Support/Knowledge/knowledgeC.db ./user_data/screentime.db"
        echo "     sudo chown $(whoami) ./user_data/screentime.db"
        echo ""
        echo "  ⚠️  Continuing without Screen Time data..."
    fi
else
    echo "  ❌ Screen Time database not found"
    echo "  Note: This requires macOS with Screen Time enabled"
    exit 1
fi

echo ""
echo "🌐 Copying browser history (optional)..."

# Safari history
if [ -f ~/Library/Safari/History.db ]; then
    # Try copying Safari history with error handling
    if cp ~/Library/Safari/History.db ./user_data/safari_history.db 2>/dev/null; then
        echo "  ✅ Safari history copied successfully"
    else
        echo "  ❌ Safari history access denied (macOS privacy protection)"
        echo "  💡 To enable Safari history access:"
        echo "     1. Open System Settings → Privacy & Security → Full Disk Access"
        echo "     2. Click the '+' button and add Terminal (or your terminal app)"
        echo "     3. Restart Terminal and run this script again"
        echo ""
        echo "  🔄 Alternative: Run this command to copy Safari history manually:"
        echo "     sudo cp ~/Library/Safari/History.db ./user_data/safari_history.db"
        echo "     sudo chown $(whoami) ./user_data/safari_history.db"
        echo ""
        echo "  ⚠️  Continuing without Safari history..."
    fi
else
    echo "  ⚠️  Safari history database not found"
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

# Microsoft Edge history
if [ -f ~/Library/Application\ Support/Microsoft\ Edge/Default/History ]; then
    cp ~/Library/Application\ Support/Microsoft\ Edge/Default/History ./user_data/edge_history.db
    echo "  ✅ Microsoft Edge history copied"
elif [ -d ~/Library/Application\ Support/Microsoft\ Edge ]; then
    # Check for other profile directories if Default doesn't exist
    edge_profile=$(ls ~/Library/Application\ Support/Microsoft\ Edge | grep -E "^Profile [0-9]+$|^Default$" | head -1)
    if [ -n "$edge_profile" ]; then
        if [ -f ~/Library/Application\ Support/Microsoft\ Edge/$edge_profile/History ]; then
            cp ~/Library/Application\ Support/Microsoft\ Edge/$edge_profile/History ./user_data/edge_history.db
            echo "  ✅ Microsoft Edge history copied (from $edge_profile)"
        else
            echo "  ⚠️  Microsoft Edge history file not found in $edge_profile (optional)"
        fi
    else
        echo "  ⚠️  Microsoft Edge profile not found (optional)"
    fi
else
    echo "  ⚠️  Microsoft Edge not installed (optional)"
fi

# Arc Browser history
if [ -f ~/Library/Application\ Support/Arc/User\ Data/Default/History ]; then
    cp ~/Library/Application\ Support/Arc/User\ Data/Default/History ./user_data/arc_history.db
    echo "  ✅ Arc Browser history copied"
elif [ -d ~/Library/Application\ Support/Arc/User\ Data ]; then
    # Check for other profile directories
    arc_profile=$(ls ~/Library/Application\ Support/Arc/User\ Data | grep -E "^Profile [0-9]+$|^Default$" | head -1)
    if [ -n "$arc_profile" ]; then
        if [ -f ~/Library/Application\ Support/Arc/User\ Data/$arc_profile/History ]; then
            cp ~/Library/Application\ Support/Arc/User\ Data/$arc_profile/History ./user_data/arc_history.db
            echo "  ✅ Arc Browser history copied (from $arc_profile)"
        else
            echo "  ⚠️  Arc Browser history file not found in $arc_profile (optional)"
        fi
    else
        echo "  ⚠️  Arc Browser profile not found (optional)"
    fi
else
    echo "  ⚠️  Arc Browser not installed (optional)"
fi

# Yandex Browser history
if [ -f ~/Library/Application\ Support/Yandex/YandexBrowser/Default/History ]; then
    cp ~/Library/Application\ Support/Yandex/YandexBrowser/Default/History ./user_data/yandex_history.db
    echo "  ✅ Yandex Browser history copied"
elif [ -d ~/Library/Application\ Support/Yandex/YandexBrowser ]; then
    # Check for other profile directories if Default doesn't exist
    yandex_profile=$(ls ~/Library/Application\ Support/Yandex/YandexBrowser | grep -E "^Profile [0-9]+$|^Default$" | head -1)
    if [ -n "$yandex_profile" ]; then
        if [ -f ~/Library/Application\ Support/Yandex/YandexBrowser/$yandex_profile/History ]; then
            cp ~/Library/Application\ Support/Yandex/YandexBrowser/$yandex_profile/History ./user_data/yandex_history.db
            echo "  ✅ Yandex Browser history copied (from $yandex_profile)"
        else
            echo "  ⚠️  Yandex Browser history file not found in $yandex_profile (optional)"
        fi
    else
        echo "  ⚠️  Yandex Browser profile not found (optional)"
    fi
else
    echo "  ⚠️  Yandex Browser not installed (optional)"
fi

# Brave Browser history
if [ -f ~/Library/Application\ Support/BraveSoftware/Brave-Browser/Default/History ]; then
    cp ~/Library/Application\ Support/BraveSoftware/Brave-Browser/Default/History ./user_data/brave_history.db
    echo "  ✅ Brave Browser history copied"
elif [ -d ~/Library/Application\ Support/BraveSoftware/Brave-Browser ]; then
    # Check for other profile directories
    brave_profile=$(ls ~/Library/Application\ Support/BraveSoftware/Brave-Browser | grep -E "^Profile [0-9]+$|^Default$" | head -1)
    if [ -n "$brave_profile" ]; then
        if [ -f ~/Library/Application\ Support/BraveSoftware/Brave-Browser/$brave_profile/History ]; then
            cp ~/Library/Application\ Support/BraveSoftware/Brave-Browser/$brave_profile/History ./user_data/brave_history.db
            echo "  ✅ Brave Browser history copied (from $brave_profile)"
        else
            echo "  ⚠️  Brave Browser history file not found in $brave_profile (optional)"
        fi
    else
        echo "  ⚠️  Brave Browser profile not found (optional)"
    fi
else
    echo "  ⚠️  Brave Browser not installed (optional)"
fi

# Opera Browser history
if [ -f ~/Library/Application\ Support/com.operasoftware.Opera/History ]; then
    cp ~/Library/Application\ Support/com.operasoftware.Opera/History ./user_data/opera_history.db
    echo "  ✅ Opera Browser history copied"
else
    echo "  ⚠️  Opera Browser not found (optional)"
fi

# Vivaldi Browser history
if [ -f ~/Library/Application\ Support/Vivaldi/Default/History ]; then
    cp ~/Library/Application\ Support/Vivaldi/Default/History ./user_data/vivaldi_history.db
    echo "  ✅ Vivaldi Browser history copied"
elif [ -d ~/Library/Application\ Support/Vivaldi ]; then
    # Check for other profile directories
    vivaldi_profile=$(ls ~/Library/Application\ Support/Vivaldi | grep -E "^Profile [0-9]+$|^Default$" | head -1)
    if [ -n "$vivaldi_profile" ]; then
        if [ -f ~/Library/Application\ Support/Vivaldi/$vivaldi_profile/History ]; then
            cp ~/Library/Application\ Support/Vivaldi/$vivaldi_profile/History ./user_data/vivaldi_history.db
            echo "  ✅ Vivaldi Browser history copied (from $vivaldi_profile)"
        else
            echo "  ⚠️  Vivaldi Browser history file not found in $vivaldi_profile (optional)"
        fi
    else
        echo "  ⚠️  Vivaldi Browser profile not found (optional)"
    fi
else
    echo "  ⚠️  Vivaldi Browser not installed (optional)"
fi

# Orion Browser history (WebKit-based by Kagi)
if [ -f ~/Library/Application\ Support/Orion/Defaults/history ]; then
    cp ~/Library/Application\ Support/Orion/Defaults/history ./user_data/orion_history.db
    echo "  ✅ Orion Browser history copied"
else
    echo "  ⚠️  Orion Browser not found (optional)"
fi

# Dia Browser history (Chromium-based by The Browser Company)
# Note: Dia uses similar structure to Arc with "User Data" directory
dia_main_path="$HOME/Library/Application Support/Dia/User Data/Default/History"
if [ -f "$dia_main_path" ]; then
    cp "$dia_main_path" ./user_data/dia_history.db
    echo "  ✅ Dia Browser history copied"
elif [ -d "$HOME/Library/Application Support/Dia/User Data" ]; then
    # Check for other profiles
    for profile_dir in "$HOME/Library/Application Support/Dia/User Data"/*; do
        if [ -d "$profile_dir" ] && [ -f "$profile_dir/History" ]; then
            profile_name=$(basename "$profile_dir")
            cp "$profile_dir/History" ./user_data/dia_history.db
            echo "  ✅ Dia Browser history copied (from $profile_name)"
            break
        fi
    done
else
    echo "  ⚠️  Dia Browser not found (optional)"
fi

# Comet Browser history (Chromium-based by Perplexity)
if [ -f ~/Library/Application\ Support/Comet/Default/History ]; then
    cp ~/Library/Application\ Support/Comet/Default/History ./user_data/comet_history.db
    echo "  ✅ Comet Browser history copied"
elif [ -d ~/Library/Application\ Support/Comet ]; then
    # Check for other profile directories
    comet_profile=$(ls ~/Library/Application\ Support/Comet | grep -E "^Profile [0-9]+$|^Default$" | head -1)
    if [ -n "$comet_profile" ]; then
        if [ -f ~/Library/Application\ Support/Comet/$comet_profile/History ]; then
            cp ~/Library/Application\ Support/Comet/$comet_profile/History ./user_data/comet_history.db
            echo "  ✅ Comet Browser history copied (from $comet_profile)"
        else
            echo "  ⚠️  Comet Browser history file not found in $comet_profile (optional)"
        fi
    else
        echo "  ⚠️  Comet Browser profile not found (optional)"
    fi
else
    echo "  ⚠️  Comet Browser not found (optional)"
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
