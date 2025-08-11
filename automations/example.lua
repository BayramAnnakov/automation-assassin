-- Example Hammerspoon Automation Script
-- This is a template for generated interventions

-- Death Loop Breaker Example
-- Detects and breaks repetitive app switching patterns

local deathLoopTimer = nil
local appHistory = {}
local PATTERN_THRESHOLD = 3
local INTERVENTION_DURATION = 60 -- seconds

-- Track app switches
function trackAppSwitch()
    local currentApp = hs.application.frontmostApplication():name()
    table.insert(appHistory, {
        app = currentApp,
        time = os.time()
    })
    
    -- Keep only last 10 switches
    if #appHistory > 10 then
        table.remove(appHistory, 1)
    end
    
    -- Check for death loop pattern
    checkForDeathLoop()
end

-- Check if user is in a death loop
function checkForDeathLoop()
    if #appHistory < 4 then return end
    
    -- Look for A->B->A->B pattern
    local lastFour = {}
    for i = #appHistory - 3, #appHistory do
        table.insert(lastFour, appHistory[i].app)
    end
    
    if lastFour[1] == lastFour[3] and 
       lastFour[2] == lastFour[4] and
       lastFour[1] ~= lastFour[2] then
        -- Death loop detected!
        triggerIntervention(lastFour[1], lastFour[2])
    end
end

-- Trigger intervention
function triggerIntervention(app1, app2)
    hs.notify.new({
        title = "⚠️ Death Loop Detected",
        informativeText = string.format(
            "You're switching between %s and %s repeatedly. " ..
            "Taking a %d second break.",
            app1, app2, INTERVENTION_DURATION
        ),
        soundName = "Submarine"
    }):send()
    
    -- Block the apps temporarily
    blockApps({app1, app2}, INTERVENTION_DURATION)
end

-- Block specific apps for a duration
function blockApps(apps, duration)
    for _, appName in ipairs(apps) do
        local app = hs.application.get(appName)
        if app then
            app:hide()
        end
    end
    
    -- Unblock after duration
    hs.timer.doAfter(duration, function()
        hs.notify.new({
            title = "✅ Break Complete",
            informativeText = "You can now return to work.",
            soundName = "Glass"
        }):send()
    end)
end

-- Focus Mode Example
local focusMode = false
local allowedApps = {"Code", "Terminal", "Safari", "Notes"}

function toggleFocusMode()
    focusMode = not focusMode
    
    if focusMode then
        hs.notify.new({
            title = "🎯 Focus Mode ON",
            informativeText = "Only productive apps allowed",
            soundName = "Hero"
        }):send()
        
        -- Hide all non-productive apps
        enforeceFocusMode()
    else
        hs.notify.new({
            title = "😌 Focus Mode OFF",
            informativeText = "All apps available",
            soundName = "Pop"
        }):send()
    end
end

function enforeceFocusMode()
    if not focusMode then return end
    
    local currentApp = hs.application.frontmostApplication():name()
    local isAllowed = false
    
    for _, allowedApp in ipairs(allowedApps) do
        if currentApp == allowedApp then
            isAllowed = true
            break
        end
    end
    
    if not isAllowed then
        hs.application.frontmostApplication():hide()
        hs.notify.new({
            title = "🚫 App Blocked",
            informativeText = currentApp .. " is not allowed in Focus Mode",
            soundName = "Funk"
        }):send()
    end
end

-- Productivity Timer
local workTimer = nil
local workDuration = 25 * 60 -- 25 minutes
local breakDuration = 5 * 60 -- 5 minutes

function startProductivityTimer()
    -- Work period
    hs.notify.new({
        title = "⏰ Work Sprint Started",
        informativeText = "Focus for 25 minutes",
        soundName = "Hero"
    }):send()
    
    workTimer = hs.timer.doAfter(workDuration, function()
        -- Break period
        hs.notify.new({
            title = "☕ Break Time!",
            informativeText = "Take a 5 minute break",
            soundName = "Glass"
        }):send()
        
        -- Restart cycle after break
        hs.timer.doAfter(breakDuration, startProductivityTimer)
    end)
end

-- Hotkey Bindings
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "F", toggleFocusMode)
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "P", startProductivityTimer)
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "R", function()
    hs.reload()
    hs.notify.new({
        title = "🔄 Config Reloaded",
        informativeText = "Hammerspoon configuration reloaded"
    }):send()
end)

-- App Watcher
appWatcher = hs.application.watcher.new(trackAppSwitch)
appWatcher:start()

-- Focus Mode Enforcer
if focusMode then
    focusModeTimer = hs.timer.doEvery(1, enforeceFocusMode)
end

-- Initialization
hs.notify.new({
    title = "🎯 Automation Assassin",
    informativeText = "Death loop protection active",
    soundName = "Hero"
}):send()

print("Automation Assassin loaded successfully")