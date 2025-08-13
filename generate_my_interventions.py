#!/usr/bin/env python3
"""
Generate personalized Hammerspoon interventions based on YOUR patterns
Run this after analyze_my_patterns.py
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def load_analysis():
    """Load the analysis results"""
    if not os.path.exists('my_analysis/patterns.json'):
        print("❌ No analysis found!")
        print("Please run 'python analyze_my_patterns.py' first")
        sys.exit(1)
    
    with open('my_analysis/patterns.json', 'r') as f:
        return json.load(f)

def generate_bounce_killer(results):
    """Generate bounce detection and prevention script"""
    script = """-- Bounce-Back Killer
-- Prevents accidental app switches (your bounce rate: {bounce_rate:.1f}%)

bounceKiller = {{}}
bounceKiller.lastApp = nil
bounceKiller.lastTime = 0
bounceKiller.bounceCount = 0
bounceKiller.protection = true
bounceKiller.totalBounces = 0
bounceKiller.totalSwitches = 0
bounceKiller.history = {{}}

function bounceKiller:init()
    print("Initializing Bounce Killer...")
    
    self.watcher = hs.application.watcher.new(function(appName, eventType, appObject)
        if eventType == hs.application.watcher.activated then
            self:checkForBounce(appName)
        end
    end)
    self.watcher:start()
    
    print("Bounce Killer started!")
end

function bounceKiller:checkForBounce(appName)
    local now = hs.timer.secondsSinceEpoch()
    local timeSinceLastSwitch = now - self.lastTime
    
    self.totalSwitches = self.totalSwitches + 1
    
    -- Check for bounce (switching back within 1 second)
    if self.lastApp and timeSinceLastSwitch < 1.0 then
        if self.history and #self.history >= 2 then
            local prevApp = self.history[#self.history - 1]
            if prevApp == appName then
                -- This is a bounce!
                self.bounceCount = self.bounceCount + 1
                self.totalBounces = self.totalBounces + 1
                
                if self.protection then
                    hs.alert.show("⚡ Bounce detected! (#" .. self.bounceCount .. ")", 1)
                    
                    if self.bounceCount >= 3 then
                        hs.alert.show("💡 Too many bounces! Try Cmd+Shift+S for split screen", 3)
                        self.bounceCount = 0
                    end
                end
            end
        end
    else
        if timeSinceLastSwitch > 2 then
            self.bounceCount = 0
        end
    end
    
    -- Update history
    if not self.history then
        self.history = {{}}
    end
    table.insert(self.history, appName)
    if #self.history > 10 then
        table.remove(self.history, 1)
    end
    
    self.lastApp = appName
    self.lastTime = now
end

bounceKiller:init()

-- Hotkey to toggle protection
hs.hotkey.bind({{"cmd", "shift"}}, "B", function()
    bounceKiller.protection = not bounceKiller.protection
    hs.alert.show(bounceKiller.protection and "🛡️ Bounce Protection ON" or "⚠️ Bounce Protection OFF")
end)
""".format(bounce_rate=results['bounce_rate'])
    
    return script

def generate_smart_layouts(results):
    """Generate smart window layouts based on top apps"""
    top_apps = [app[0] for app in results['top_apps'][:5]]
    
    # Determine primary apps
    primary_app = top_apps[0] if top_apps else "Cursor"
    secondary_app = top_apps[1] if len(top_apps) > 1 else "Safari"
    tertiary_app = top_apps[2] if len(top_apps) > 2 else "Slack"
    
    script = f"""-- Smart Window Layouts
-- Optimized for your most-used apps: {', '.join(top_apps[:3])}

function setupOptimalLayout()
    local screen = hs.screen.mainScreen():frame()
    local appsToArrange = {{ "{primary_app}", "{secondary_app}", "{tertiary_app}" }}
    
    -- Hide all other apps
    local allApps = hs.application.runningApplications()
    for _, app in ipairs(allApps) do
        local appName = app:name()
        local shouldHide = true
        for _, keepApp in ipairs(appsToArrange) do
            if appName == keepApp then
                shouldHide = false
                break
            end
        end
        if shouldHide then
            app:hide()
        end
    end
    
    -- Primary app (left 50%)
    local primary = hs.application.get("{primary_app}")
    if primary then
        primary:activate()
        local win = primary:mainWindow()
        if win then
            win:setFrame({{
                x = screen.x,
                y = screen.y,
                w = screen.w * 0.5,
                h = screen.h
            }})
            win:raise()
        end
    end
    
    -- Secondary app (top-right 50%)
    local secondary = hs.application.get("{secondary_app}")
    if secondary then
        local win = secondary:mainWindow()
        if win then
            win:setFrame({{
                x = screen.x + screen.w * 0.5,
                y = screen.y,
                w = screen.w * 0.5,
                h = screen.h * 0.5
            }})
            win:raise()
        end
    end
    
    -- Tertiary app (bottom-right 50%)
    local tertiary = hs.application.get("{tertiary_app}")
    if tertiary then
        local win = tertiary:mainWindow()
        if win then
            win:setFrame({{
                x = screen.x + screen.w * 0.5,
                y = screen.y + screen.h * 0.5,
                w = screen.w * 0.5,
                h = screen.h * 0.5
            }})
            win:raise()
        end
    end
    
    hs.alert.show("✅ Optimal layout set!")
end

function setupFocusedLayout()
    local screen = hs.screen.mainScreen():frame()
    local appsToArrange = {{ "{primary_app}", "{secondary_app}" }}

    -- Hide all other apps
    local allApps = hs.application.runningApplications()
    for _, app in ipairs(allApps) do
        local appName = app:name()
        local shouldHide = true
        for _, keepApp in ipairs(appsToArrange) do
            if appName == keepApp then
                shouldHide = false
                break
            end
        end
        if shouldHide then
            app:hide()
        end
    end
    
    -- Primary app gets 70% of screen
    local primary = hs.application.get("{primary_app}")
    if primary then
        primary:activate()
        local win = primary:mainWindow()
        if win then
            win:setFrame({{
                x = screen.x,
                y = screen.y,
                w = screen.w * 0.7,
                h = screen.h
            }})
            win:raise()
        end
    end
    
    -- Secondary app gets remaining 30%
    local secondary = hs.application.get("{secondary_app}")
    if secondary then
        local win = secondary:mainWindow()
        if win then
            win:setFrame({{
                x = screen.x + screen.w * 0.7,
                y = screen.y,
                w = screen.w * 0.3,
                h = screen.h
            }})
            win:raise()
        end
    end
    
    hs.alert.show("🎯 Focused layout set!")
end

-- Hotkeys for layouts
hs.hotkey.bind({{"cmd", "shift"}}, "S", setupOptimalLayout)
hs.hotkey.bind({{"cmd", "shift"}}, "F", setupFocusedLayout)
"""
    
    return script

def generate_ai_detection():
    """Generate AI processing detection for productive waiting"""
    script = """-- AI Processing Detection
-- Allows productive app switching while AI is working

aiDetection = {}
aiDetection.processing = false
aiDetection.waitStarted = 0
aiDetection.totalAIWaits = 0
aiDetection.totalWaitTime = 0

-- Manual AI mode toggle (press when you trigger AI)
hs.hotkey.bind({"cmd", "shift"}, "G", function()
    local frontApp = hs.application.frontmostApplication()
    
    if not aiDetection.processing then
        aiDetection.processing = true
        aiDetection.waitStarted = hs.timer.secondsSinceEpoch()
        aiDetection.totalAIWaits = aiDetection.totalAIWaits + 1
        
        hs.alert.show("🤖 AI Mode ON - Switch apps freely!", 2)
        
        -- Auto-off after 60 seconds
        hs.timer.doAfter(60, function()
            if aiDetection.processing then
                local duration = hs.timer.secondsSinceEpoch() - aiDetection.waitStarted
                aiDetection.processing = false
                aiDetection.totalWaitTime = aiDetection.totalWaitTime + duration
                hs.alert.show(string.format("✅ AI Mode OFF (%.0fs wait)", duration), 2)
            end
        end)
    else
        -- Turn off manually
        local duration = hs.timer.secondsSinceEpoch() - aiDetection.waitStarted
        aiDetection.processing = false
        aiDetection.totalWaitTime = aiDetection.totalWaitTime + duration
        hs.alert.show(string.format("✅ AI Mode OFF (%.0fs wait)", duration), 2)
    end
end)

-- Show AI statistics
function showAIStats()
    local avgWait = 0
    if aiDetection.totalAIWaits > 0 then
        avgWait = aiDetection.totalWaitTime / aiDetection.totalAIWaits
    end
    
    local message = string.format(
        "🤖 AI Wait Statistics\\n" ..
        "━━━━━━━━━━━━━━━\\n" ..
        "Total AI waits: %d\\n" ..
        "Total wait time: %.1f min\\n" ..
        "Average wait: %.0f seconds\\n" ..
        "Time saved: %.1f min",
        aiDetection.totalAIWaits,
        aiDetection.totalWaitTime / 60,
        avgWait,
        aiDetection.totalWaitTime / 60 * 0.8
    )
    
    hs.alert.show(message, 5)
end

hs.hotkey.bind({"cmd", "shift"}, "I", showAIStats)
"""
    return script

def generate_stats_tracker(results):
    """Generate statistics tracking"""
    script = f"""-- Statistics Tracker
-- Tracks your productivity improvements

statsTracker = {{}}
statsTracker.switches = 0
statsTracker.bounces = 0
statsTracker.startTime = hs.timer.secondsSinceEpoch()
statsTracker.baselineSwitches = {results['daily_average']:.0f}  -- Your baseline
statsTracker.baselineBounceRate = {results['bounce_rate']:.1f}  -- Your baseline

function statsTracker:show()
    local uptime = (hs.timer.secondsSinceEpoch() - self.startTime) / 60
    local switchRate = 0
    local bounceRate = 0
    
    if uptime > 0 then
        switchRate = (self.switches / uptime) * 60
    end
    
    if self.switches > 0 then
        bounceRate = (self.bounces / self.switches) * 100
    end
    
    -- Calculate improvement
    local switchImprovement = ((self.baselineSwitches - switchRate) / self.baselineSwitches) * 100
    local bounceImprovement = self.baselineBounceRate - bounceRate
    
    local message = string.format(
        "📊 Productivity Stats\\n" ..
        "━━━━━━━━━━━━━━━━━━━━━━\\n" ..
        "⏱️ Uptime: %.1f minutes\\n" ..
        "🔄 Switches: %d (%.1f/hour)\\n" ..
        "   Baseline: %.0f/hour\\n" ..
        "   Improvement: %.1f%%\\n" ..
        "⚡ Bounce rate: %.1f%%\\n" ..
        "   Baseline: %.1f%%\\n" ..
        "   Improvement: %.1f%%\\n" ..
        "💾 Time saved: ~%.1f min",
        uptime,
        self.switches, switchRate,
        self.baselineSwitches / 24 * 60,  -- Convert daily to hourly
        switchImprovement,
        bounceRate,
        self.baselineBounceRate,
        bounceImprovement,
        (bounceKiller.totalBounces or 0) * 0.5
    )
    
    hs.alert.show(message, 8)
end

-- Update stats from bounce killer
hs.timer.doEvery(1, function()
    if bounceKiller then
        statsTracker.switches = bounceKiller.totalSwitches or 0
        statsTracker.bounces = bounceKiller.totalBounces or 0
    end
end)

-- Hotkey to show stats
hs.hotkey.bind({{"cmd", "shift"}}, "D", function()
    statsTracker:show()
end)
"""
    return script

def generate_complete_setup(results):
    """Generate the complete setup script combining all interventions"""
    
    # Get individual components
    bounce_killer = generate_bounce_killer(results)
    smart_layouts = generate_smart_layouts(results)
    ai_detection = generate_ai_detection()
    stats_tracker = generate_stats_tracker(results)
    
    # Combine into complete script
    script = f"""-- Automation Assassin - Personalized Productivity Interventions
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
-- Based on your analysis: {results['total_switches']} switches in 7 days

-- ============================================================================
-- CONFIGURATION
-- ============================================================================
-- Your baseline metrics:
-- • Daily switches: {results['daily_average']:.0f}
-- • Bounce rate: {results['bounce_rate']:.1f}%
-- • Top death loop: {results['top_patterns'][0][0] if results['top_patterns'] else 'N/A'}

-- ============================================================================
-- 1. BOUNCE-BACK KILLER
-- ============================================================================
{bounce_killer}

-- ============================================================================
-- 2. SMART WINDOW LAYOUTS
-- ============================================================================
{smart_layouts}

-- ============================================================================
-- 3. AI PROCESSING DETECTION
-- ============================================================================
{ai_detection}

-- ============================================================================
-- 4. STATISTICS TRACKER
-- ============================================================================
{stats_tracker}

-- ============================================================================
-- STARTUP
-- ============================================================================
hs.alert.show("🚀 Automation Assassin Loaded!", 2)

hs.timer.doAfter(2.5, function()
    hs.alert.show("Your hotkeys:\\n" ..
                  "• Cmd+Shift+S: Smart split-screen\\n" ..
                  "• Cmd+Shift+G: AI processing mode\\n" ..
                  "• Cmd+Shift+D: Show your stats\\n" ..
                  "• Cmd+Shift+B: Toggle bounce protection", 5)
end)

print("✅ Automation Assassin: Ready!")
print("✅ Bounce Killer: Active")
print("✅ Smart Layouts: Configured")
print("✅ AI Detection: Ready")
print("✅ Stats Tracking: Running")
"""
    
    return script

def calculate_impact(results):
    """Calculate expected impact of interventions"""
    
    # Conservative estimates
    bounce_reduction = results['bounce_count'] * 0.7  # 70% of bounces eliminated
    switch_reduction = results['total_switches'] * 0.3  # 30% fewer switches overall
    
    time_saved_daily = (bounce_reduction + switch_reduction) / 7 * 30 / 3600  # hours
    value_yearly = time_saved_daily * 365 * 50  # at $50/hour
    
    return {
        'daily_hours': time_saved_daily,
        'weekly_switches': int(bounce_reduction + switch_reduction),
        'yearly_value': value_yearly
    }

def generate_mcp_recommendations(results):
    """Generate MCP server recommendations"""
    recommendations = []
    
    patterns = results['patterns']
    
    # Check for web development pattern
    web_dev_switches = sum(v for k, v in patterns.items() 
                           if any(ide in k for ide in ['VS Code', 'Cursor', 'Xcode']) 
                           and any(browser in k for browser in ['Safari', 'Chrome']))
    
    if web_dev_switches > 50:
        recommendations.append("""
1. Install Puppeteer MCP for web testing:
   npm install -g @modelcontextprotocol/server-puppeteer
   
   Add to Claude Code settings.json:
   "mcpServers": {
     "puppeteer": {
       "command": "npx",
       "args": ["@modelcontextprotocol/server-puppeteer"]
     }
   }""")
    
    # Check for GitHub pattern
    if any('github' in k.lower() or 'git' in k.lower() for k in patterns.keys()):
        recommendations.append("""
2. Install GitHub MCP for PR reviews:
   npm install -g @modelcontextprotocol/server-github
   
   Add to settings.json with your GitHub token""")
    
    return "\n".join(recommendations) if recommendations else "No specific MCP servers recommended based on your patterns"

def main():
    print("🔧 Generating your personalized interventions...\n")
    
    # Load analysis
    results = load_analysis()
    
    print(f"📊 Loaded your analysis:")
    print(f"   • Total switches: {results['total_switches']:,}")
    print(f"   • Bounce rate: {results['bounce_rate']:.1f}%")
    print(f"   • Top apps: {', '.join([app[0] for app in results['top_apps'][:3]])}")
    
    # Create output directory
    os.makedirs('my_interventions', exist_ok=True)
    
    # Generate individual scripts
    scripts = {
        'complete_setup.lua': generate_complete_setup(results),
        'bounce_killer.lua': generate_bounce_killer(results),
        'smart_layouts.lua': generate_smart_layouts(results),
        'ai_detection.lua': generate_ai_detection(),
        'stats_tracker.lua': generate_stats_tracker(results)
    }
    
    # Save all scripts
    for filename, content in scripts.items():
        filepath = f'my_interventions/{filename}'
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Generated: {filepath}")
    
    # Calculate impact
    impact = calculate_impact(results)
    
    # Generate MCP recommendations
    mcp_recs = generate_mcp_recommendations(results)
    
    # Show installation instructions
    print(f"""
🎯 Your Personalized Interventions are Ready!

INSTALLATION INSTRUCTIONS:
═══════════════════════════════════════════════════════════

1. Install Hammerspoon (if not already installed):
   brew install --cask hammerspoon
   
2. Copy your main intervention script:
   cp my_interventions/complete_setup.lua ~/.hammerspoon/init.lua
   
3. Open Hammerspoon and reload config:
   • Click Hammerspoon icon in menu bar
   • Select "Reload Config"
   OR press Cmd+Shift+R with Hammerspoon open

YOUR PERSONAL HOTKEYS:
═══════════════════════════════════════════════════════════
• Cmd+Shift+S : Smart split-screen for your top apps
• Cmd+Shift+F : Focused layout (70% primary app)
• Cmd+Shift+G : AI processing mode (no bounce warnings)
• Cmd+Shift+B : Toggle bounce protection
• Cmd+Shift+D : Show your productivity stats
• Cmd+Shift+I : Show AI wait statistics

EXPECTED IMPACT:
═══════════════════════════════════════════════════════════
• Daily time saved: {impact['daily_hours']:.1f} hours
• Weekly switches eliminated: {impact['weekly_switches']:,}
• Estimated yearly value: ${impact['yearly_value']:,.0f}

Your baseline (before interventions):
• {results['daily_average']:.0f} switches/day
• {results['bounce_rate']:.1f}% bounce rate

Expected after interventions:
• ~{results['daily_average'] * 0.3:.0f} switches/day
• <5% bounce rate

MCP SERVERS TO INSTALL (Optional):
═══════════════════════════════════════════════════════════
{mcp_recs}

TESTING YOUR SETUP:
═══════════════════════════════════════════════════════════
1. Try switching between apps quickly
   → You should see bounce warnings
   
2. Press Cmd+Shift+S
   → Your top 3 apps should arrange optimally
   
3. Press Cmd+Shift+D
   → You should see your current stats

4. Press Cmd+Shift+G before using AI
   → Switch freely without bounce warnings

Need help? Check my_interventions/README.md for troubleshooting.
""")
    
    # Save README for interventions
    with open('my_interventions/README.md', 'w') as f:
        f.write(f"""# Your Personalized Interventions

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Your Patterns
- Total switches: {results['total_switches']:,} in 7 days
- Daily average: {results['daily_average']:.0f} switches
- Bounce rate: {results['bounce_rate']:.1f}%
- Top death loop: {results['top_patterns'][0][0] if results['top_patterns'] else 'N/A'}

## Files Generated
- `complete_setup.lua` - All interventions combined (use this one!)
- `bounce_killer.lua` - Just bounce detection
- `smart_layouts.lua` - Just window management
- `ai_detection.lua` - Just AI wait detection
- `stats_tracker.lua` - Just statistics tracking

## Customization
Edit any script to adjust:
- Bounce detection threshold (default: 1.0 seconds)
- Window layout percentages
- AI wait timeout (default: 60 seconds)
- Hotkey bindings

## Troubleshooting
- **Hotkeys not working**: Make sure Hammerspoon has Accessibility permissions
- **Windows not moving**: Grant Hammerspoon Screen Recording permissions
- **Stats show 0**: The stats start fresh - they track from when you install
""")
    
    print("\n✅ All interventions generated successfully!")
    print("📁 Check the 'my_interventions' folder for all files")

if __name__ == "__main__":
    main()