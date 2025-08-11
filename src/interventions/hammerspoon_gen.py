"""
Hammerspoon Automation Generator
Creates Lua scripts for macOS automation interventions
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class HammerspoonGenerator:
    """Generates Hammerspoon Lua scripts for productivity interventions"""
    
    def __init__(self, output_dir: str = "automations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_app_blocker(self, apps_to_block: List[str], 
                            work_hours: Dict[str, str] = None) -> str:
        """
        Generate script to block distracting apps during work hours
        
        Args:
            apps_to_block: List of app names to block
            work_hours: Dict with 'start' and 'end' times (24hr format)
        
        Returns:
            Path to generated Lua script
        """
        if not work_hours:
            work_hours = {'start': '09:00', 'end': '17:00'}
        
        script = f"""-- Automation Assassin: App Blocker
-- Blocks distracting apps during work hours
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

local blockedApps = {{
{self._format_lua_table(apps_to_block)}
}}

local workStart = "{work_hours['start']}"
local workEnd = "{work_hours['end']}"

-- Check if current time is within work hours
function isWorkTime()
    local currentTime = os.date("%H:%M")
    return currentTime >= workStart and currentTime <= workEnd
end

-- Kill blocked apps if they open during work time
appWatcher = hs.application.watcher.new(function(appName, eventType, appObject)
    if eventType == hs.application.watcher.activated then
        for _, blockedApp in ipairs(blockedApps) do
            if string.lower(appName) == string.lower(blockedApp) and isWorkTime() then
                hs.notify.new({{
                    title = "Automation Assassin",
                    informativeText = appName .. " blocked during work hours!",
                    soundName = "Funk"
                }}):send()
                
                -- Kill the app after notification
                hs.timer.doAfter(1, function()
                    appObject:kill()
                end)
                
                -- Log the block
                print("Blocked: " .. appName .. " at " .. os.date("%H:%M:%S"))
            end
        end
    end
end)

appWatcher:start()

-- Notify that blocker is active
hs.notify.new({{
    title = "Automation Assassin Active",
    informativeText = "Blocking " .. #blockedApps .. " distracting apps during work hours",
    soundName = "Hero"
}}):send()

print("App Blocker loaded - Monitoring " .. #blockedApps .. " apps")
"""
        
        # Save script
        script_path = self.output_dir / "app_blocker.lua"
        script_path.write_text(script)
        print(f"✅ Generated app blocker: {script_path}")
        
        return str(script_path)
    
    def generate_death_loop_breaker(self, death_loops: List[Dict],
                                   switch_threshold: int = 30) -> str:
        """
        Generate script to detect and break death loops in real-time
        
        Args:
            death_loops: List of death loop patterns to monitor
            switch_threshold: Max seconds between switches to trigger intervention
        
        Returns:
            Path to generated Lua script
        """
        script = f"""-- Automation Assassin: Death Loop Breaker
-- Detects and breaks repetitive app switching patterns
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

local deathLoops = {{
{self._format_death_loops(death_loops)}
}}

local switchThreshold = {switch_threshold}  -- seconds
local lastApp = nil
local lastSwitchTime = nil
local switchCount = {{}}

-- Monitor app switches
appWatcher = hs.application.watcher.new(function(appName, eventType, appObject)
    if eventType == hs.application.watcher.activated then
        local currentTime = os.time()
        
        -- Check for rapid switching
        if lastApp and lastSwitchTime then
            local timeSinceSwitch = currentTime - lastSwitchTime
            
            if timeSinceSwitch <= switchThreshold then
                -- Track switch pattern
                local pattern = lastApp .. " → " .. appName
                switchCount[pattern] = (switchCount[pattern] or 0) + 1
                
                -- Check if this is a death loop
                for _, loop in ipairs(deathLoops) do
                    if (loop.app_a == lastApp and loop.app_b == appName) or
                       (loop.app_b == lastApp and loop.app_a == appName) then
                        
                        -- Death loop detected!
                        if switchCount[pattern] >= 3 then
                            -- Intervention: Hide all windows and show warning
                            hs.alert.show("⚠️ DEATH LOOP DETECTED! ⚠️\\n\\n" ..
                                        "You're stuck in " .. pattern .. "\\n" ..
                                        "Take a 2-minute break!", 10)
                            
                            -- Force a break by hiding all windows
                            hs.timer.doAfter(1, function()
                                hs.eventtap.keyStroke({{"cmd"}}, "h")  -- Hide current app
                                hs.application.launchOrFocus("Finder")  -- Focus Finder
                            end)
                            
                            -- Reset counter
                            switchCount[pattern] = 0
                            
                            -- Log the intervention
                            print("Death loop broken: " .. pattern .. " at " .. os.date("%H:%M:%S"))
                        end
                    end
                end
            else
                -- Reset if too much time passed
                switchCount = {{}}
            end
        end
        
        lastApp = appName
        lastSwitchTime = currentTime
    end
end)

appWatcher:start()

hs.notify.new({{
    title = "Death Loop Breaker Active",
    informativeText = "Monitoring " .. #deathLoops .. " problematic patterns",
    soundName = "Glass"
}}):send()

print("Death Loop Breaker loaded - Monitoring patterns")
"""
        
        # Save script
        script_path = self.output_dir / "death_loop_breaker.lua"
        script_path.write_text(script)
        print(f"✅ Generated death loop breaker: {script_path}")
        
        return str(script_path)
    
    def generate_focus_mode(self, allowed_apps: List[str],
                           focus_duration_minutes: int = 25) -> str:
        """
        Generate Pomodoro-style focus mode script
        
        Args:
            allowed_apps: Apps allowed during focus time
            focus_duration_minutes: Duration of focus session
        
        Returns:
            Path to generated Lua script
        """
        script = f"""-- Automation Assassin: Focus Mode
-- Enforces deep focus sessions with app restrictions
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

local allowedApps = {{
{self._format_lua_table(allowed_apps)}
}}

local focusDuration = {focus_duration_minutes} * 60  -- Convert to seconds
local focusActive = false
local focusTimer = nil

-- Start focus session
function startFocus()
    focusActive = true
    local endTime = os.date("%H:%M", os.time() + focusDuration)
    
    hs.alert.show("🎯 FOCUS MODE ACTIVE\\n\\nSession ends at " .. endTime, 5)
    
    -- Hide all non-essential apps
    for _, app in ipairs(hs.application.runningApplications()) do
        local appName = app:name()
        local isAllowed = false
        
        for _, allowed in ipairs(allowedApps) do
            if string.lower(appName) == string.lower(allowed) then
                isAllowed = true
                break
            end
        end
        
        if not isAllowed then
            app:hide()
        end
    end
    
    -- Set timer to end focus
    focusTimer = hs.timer.doAfter(focusDuration, function()
        endFocus()
    end)
end

-- End focus session
function endFocus()
    focusActive = false
    
    hs.alert.show("✅ FOCUS SESSION COMPLETE!\\n\\nGreat work! Take a 5-minute break.", 10)
    
    -- Play completion sound
    hs.sound.getByName("Glass"):play()
    
    -- Show all hidden apps
    for _, app in ipairs(hs.application.runningApplications()) do
        app:unhide()
    end
end

-- Monitor app switches during focus
appWatcher = hs.application.watcher.new(function(appName, eventType, appObject)
    if focusActive and eventType == hs.application.watcher.activated then
        local isAllowed = false
        
        for _, allowed in ipairs(allowedApps) do
            if string.lower(appName) == string.lower(allowed) then
                isAllowed = true
                break
            end
        end
        
        if not isAllowed then
            hs.notify.new({{
                title = "Focus Mode",
                informativeText = appName .. " not allowed during focus!",
                soundName = "Funk"
            }}):send()
            
            -- Switch back to an allowed app
            if #allowedApps > 0 then
                hs.application.launchOrFocus(allowedApps[1])
            end
        end
    end
end)

-- Hotkey to toggle focus mode
hs.hotkey.bind({{"cmd", "alt", "ctrl"}}, "F", function()
    if focusActive then
        endFocus()
        if focusTimer then focusTimer:stop() end
    else
        startFocus()
    end
end)

appWatcher:start()

hs.notify.new({{
    title = "Focus Mode Ready",
    informativeText = "Press Cmd+Alt+Ctrl+F to start focus session",
    soundName = "Hero"
}}):send()

print("Focus Mode loaded - Press Cmd+Alt+Ctrl+F to activate")
"""
        
        # Save script
        script_path = self.output_dir / "focus_mode.lua"
        script_path.write_text(script)
        print(f"✅ Generated focus mode: {script_path}")
        
        return str(script_path)
    
    def generate_break_reminder(self, work_minutes: int = 50,
                               break_minutes: int = 10) -> str:
        """
        Generate script for break reminders and screen time limits
        
        Args:
            work_minutes: Minutes to work before break
            break_minutes: Duration of break
        
        Returns:
            Path to generated Lua script
        """
        script = f"""-- Automation Assassin: Break Reminder
-- Enforces regular breaks to prevent burnout
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

local workMinutes = {work_minutes}
local breakMinutes = {break_minutes}
local sessionCount = 0

-- Schedule break reminder
function scheduleBreak()
    hs.timer.doAfter(workMinutes * 60, function()
        sessionCount = sessionCount + 1
        
        -- Force break after 3 sessions
        local forceBreak = (sessionCount % 3 == 0)
        
        if forceBreak then
            -- Lock screen for forced break
            hs.alert.show("⏰ MANDATORY BREAK TIME!\\n\\nScreen locking in 10 seconds...\\n" ..
                        "You've worked for " .. (sessionCount * workMinutes) .. " minutes", 10)
            
            hs.timer.doAfter(10, function()
                hs.caffeinate.lockScreen()
            end)
        else
            -- Regular break reminder
            hs.dialog.blockAlert(
                "Time for a Break!",
                "You've been working for " .. workMinutes .. " minutes.\\n\\n" ..
                "Take a " .. breakMinutes .. "-minute break to:\\n" ..
                "• Stand up and stretch\\n" ..
                "• Rest your eyes\\n" ..
                "• Hydrate\\n\\n" ..
                "Your productivity depends on regular breaks!",
                "Start Break",
                "Snooze 5 min"
            )
        end
        
        -- Schedule next reminder
        scheduleBreak()
    end)
end

-- Start the break reminder system
scheduleBreak()

hs.notify.new({{
    title = "Break Reminder Active",
    informativeText = "Reminders every " .. workMinutes .. " minutes",
    soundName = "Glass"
}}):send()

print("Break Reminder loaded - Work: " .. workMinutes .. "min, Break: " .. breakMinutes .. "min")
"""
        
        # Save script
        script_path = self.output_dir / "break_reminder.lua"
        script_path.write_text(script)
        print(f"✅ Generated break reminder: {script_path}")
        
        return str(script_path)
    
    def generate_master_config(self, scripts: List[str]) -> str:
        """
        Generate master Hammerspoon config that loads all interventions
        
        Args:
            scripts: List of script paths to include
        
        Returns:
            Path to init.lua config file
        """
        script = f"""-- Automation Assassin: Master Configuration
-- Loads all productivity interventions
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

print("="..string.rep("=", 50))
print("AUTOMATION ASSASSIN - PRODUCTIVITY INTERVENTION SYSTEM")
print("="..string.rep("=", 50))

-- Load intervention modules
local interventions = {{
{self._format_script_requires(scripts)}
}}

-- Display loaded interventions
hs.alert.show("🚀 AUTOMATION ASSASSIN ACTIVATED\\n\\n" ..
            #interventions .. " interventions loaded\\n" ..
            "Your productivity is now protected!", 5)

-- Dashboard hotkey (Cmd+Alt+Ctrl+D)
hs.hotkey.bind({{"cmd", "alt", "ctrl"}}, "D", function()
    local stats = "📊 AUTOMATION ASSASSIN DASHBOARD\\n\\n" ..
                 "Active Interventions: " .. #interventions .. "\\n" ..
                 "Session Time: " .. os.date("%H:%M:%S") .. "\\n\\n" ..
                 "Hotkeys:\\n" ..
                 "• Cmd+Alt+Ctrl+F: Toggle Focus Mode\\n" ..
                 "• Cmd+Alt+Ctrl+D: Show Dashboard\\n" ..
                 "• Cmd+Alt+Ctrl+R: Reload Config"
    
    hs.alert.show(stats, 10)
end)

-- Reload config hotkey (Cmd+Alt+Ctrl+R)
hs.hotkey.bind({{"cmd", "alt", "ctrl"}}, "R", function()
    hs.reload()
end)

-- Notify on config reload
hs.notify.new({{
    title = "Automation Assassin",
    informativeText = "Configuration loaded successfully",
    soundName = "Hero"
}}):send()

print("All interventions loaded successfully!")
print("="..string.rep("=", 50))
"""
        
        # Save as init.lua for Hammerspoon
        script_path = self.output_dir / "init.lua"
        script_path.write_text(script)
        print(f"✅ Generated master config: {script_path}")
        
        return str(script_path)
    
    def _format_lua_table(self, items: List[str]) -> str:
        """Format Python list as Lua table entries"""
        formatted = []
        for item in items:
            formatted.append(f'    "{item}"')
        return ',\n'.join(formatted)
    
    def _format_death_loops(self, loops: List[Dict]) -> str:
        """Format death loop patterns for Lua"""
        formatted = []
        for loop in loops:
            formatted.append(f"""    {{
        app_a = "{loop.get('app_a', '')}",
        app_b = "{loop.get('app_b', '')}",
        score = {loop.get('score', 0)}
    }}""")
        return ',\n'.join(formatted)
    
    def _format_script_requires(self, scripts: List[str]) -> str:
        """Format script paths as Lua require statements"""
        formatted = []
        for script in scripts:
            # Extract module name from path
            module_name = Path(script).stem
            formatted.append(f'    "{module_name}"')
        return ',\n'.join(formatted)


if __name__ == "__main__":
    # Test the generator
    generator = HammerspoonGenerator()
    
    # Generate sample interventions
    print("\n🔧 Generating Hammerspoon Interventions...")
    print("=" * 50)
    
    # App blocker
    blocker = generator.generate_app_blocker(
        apps_to_block=["Twitter", "Facebook", "Instagram", "TikTok", "Reddit"],
        work_hours={'start': '09:00', 'end': '17:00'}
    )
    
    # Death loop breaker
    death_loops = [
        {'app_a': 'Slack', 'app_b': 'Chrome', 'score': 45.2},
        {'app_a': 'Twitter', 'app_b': 'Safari', 'score': 38.7}
    ]
    loop_breaker = generator.generate_death_loop_breaker(death_loops)
    
    # Focus mode
    focus = generator.generate_focus_mode(
        allowed_apps=["VS Code", "Terminal", "Xcode", "Documentation"],
        focus_duration_minutes=25
    )
    
    # Break reminder
    breaks = generator.generate_break_reminder(work_minutes=50, break_minutes=10)
    
    # Master config
    master = generator.generate_master_config([blocker, loop_breaker, focus, breaks])
    
    print(f"\n✅ All interventions generated in {generator.output_dir}/")
    print("\nTo deploy:")
    print(f"1. Copy {master} to ~/.hammerspoon/init.lua")
    print("2. Reload Hammerspoon configuration")
    print("3. Interventions will activate automatically")