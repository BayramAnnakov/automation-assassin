"""
Smart Intervention Generator - Context-Aware Automation Solutions
Generates Hammerspoon automations and suggests MCP servers based on patterns
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

class InterventionType(Enum):
    """Types of interventions available"""
    HAMMERSPOON_WINDOW = "hammerspoon_window"
    HAMMERSPOON_BLOCK = "hammerspoon_block"
    HAMMERSPOON_HOTKEY = "hammerspoon_hotkey"
    HAMMERSPOON_FOCUS = "hammerspoon_focus"
    HAMMERSPOON_NOTIFY = "hammerspoon_notify"
    MCP_SERVER = "mcp_server"
    HYBRID = "hybrid"

@dataclass
class Intervention:
    """Represents a single intervention"""
    name: str
    type: InterventionType
    description: str
    implementation: str  # Actual code or instructions
    difficulty: str  # 'easy', 'medium', 'hard'
    effectiveness: int  # 1-10 scale
    requirements: List[str]
    
@dataclass
class MCPSuggestion:
    """MCP server suggestion"""
    name: str
    purpose: str
    installation: str
    configuration: str
    search_query: str  # For finding more info

class SmartInterventionGenerator:
    """
    Generates context-aware interventions focusing on Hammerspoon
    with MCP suggestions for advanced automation needs
    """
    
    def __init__(self):
        self.hammerspoon_templates = self._load_hammerspoon_templates()
        self.mcp_registry = self._load_mcp_registry()
        
    def _load_hammerspoon_templates(self) -> Dict:
        """Load Hammerspoon code templates"""
        return {
            'window_testing_layout': '''
-- Testing Layout: {app_a} and {app_b} side-by-side
testingLayout = function()
    local app1 = hs.application.find("{app_a}")
    local app2 = hs.application.find("{app_b}")
    
    if app1 and app2 then
        -- Get screen dimensions
        local screen = hs.screen.mainScreen()
        local screenFrame = screen:frame()
        
        -- Position apps side-by-side
        app1:mainWindow():setFrame(hs.geometry.rect(
            screenFrame.x, 
            screenFrame.y, 
            screenFrame.w / 2, 
            screenFrame.h
        ))
        
        app2:mainWindow():setFrame(hs.geometry.rect(
            screenFrame.x + screenFrame.w / 2, 
            screenFrame.y, 
            screenFrame.w / 2, 
            screenFrame.h
        ))
        
        hs.notify.new({{
            title = "Testing Layout Active",
            informativeText = "{app_a} | {app_b}",
            soundName = hs.notify.defaultNotificationSound
        }}):send()
    else
        hs.alert.show("Apps not found for testing layout")
    end
end

-- Bind to hotkey
hs.hotkey.bind({{"cmd", "shift"}}, "T", testingLayout)

-- Auto-arrange when switching between apps
testingWatcher = hs.application.watcher.new(function(appName, eventType, appObject)
    if eventType == hs.application.watcher.activated then
        if appName == "{app_a}" or appName == "{app_b}" then
            -- Auto-arrange after a short delay
            hs.timer.doAfter(0.5, testingLayout)
        end
    end
end)
testingWatcher:start()
''',
            
            'progressive_block': '''
-- Progressive App Blocking: {app_to_block}
blockingState = {{
    violations = 0,
    lastViolation = 0,
    blocked = false
}}

-- Delay progression: 3s → 5s → 10s → 5min block
delayProgression = {{3, 5, 10, 300}}

function getDelay()
    local index = math.min(blockingState.violations + 1, #delayProgression)
    return delayProgression[index]
end

-- Monitor app activation
blockWatcher = hs.application.watcher.new(function(appName, eventType, appObject)
    if eventType == hs.application.watcher.activated and appName == "{app_to_block}" then
        local currentTime = os.time()
        
        -- Check if coming from productive app
        local lastApp = hs.application.frontmostApplication()
        if lastApp and lastApp:name() == "{productive_app}" then
            
            -- Check time since last violation
            if currentTime - blockingState.lastViolation < 60 then
                blockingState.violations = blockingState.violations + 1
            else
                blockingState.violations = 1
            end
            
            blockingState.lastViolation = currentTime
            local delay = getDelay()
            
            if delay >= 300 then
                -- Full block for 5 minutes
                hs.notify.new({{
                    title = "⛔ App Blocked",
                    informativeText = "{app_to_block} blocked for 5 minutes",
                    soundName = hs.notify.defaultNotificationSound
                }}):send()
                
                appObject:hide()
                blockingState.blocked = true
                
                -- Unblock after 5 minutes
                hs.timer.doAfter(300, function()
                    blockingState.blocked = false
                    blockingState.violations = 0
                    hs.notify.new({{
                        title = "✅ Block Lifted",
                        informativeText = "{app_to_block} is now accessible",
                    }}):send()
                end)
            else
                -- Progressive delay
                hs.notify.new({{
                    title = "⚠️ Death Loop Detected",
                    informativeText = string.format("Delaying {app_to_block} for %d seconds", delay),
                    soundName = hs.notify.defaultNotificationSound
                }}):send()
                
                -- Hide app and show after delay
                appObject:hide()
                hs.timer.doAfter(delay, function()
                    local productiveApp = hs.application.find("{productive_app}")
                    if productiveApp then
                        productiveApp:activate()
                    end
                end)
            end
        end
    end
end)
blockWatcher:start()
''',
            
            'smart_hotkeys': '''
-- Smart Hotkeys for {workflow_type} Workflow
-- Quick actions to reduce manual switching

-- 1. Quick Browser Refresh & Console
hs.hotkey.bind({{"cmd", "shift"}}, "R", function()
    local browser = hs.application.find("{browser}")
    if browser then
        browser:activate()
        hs.eventtap.keyStroke({{"cmd"}}, "r")  -- Refresh
        hs.timer.doAfter(0.1, function()
            hs.eventtap.keyStroke({{"cmd", "alt"}}, "j")  -- Dev tools
        end)
    end
end)

-- 2. Quick IDE Focus
hs.hotkey.bind({{"cmd", "shift"}}, "E", function()
    local ide = hs.application.find("{ide}")
    if ide then
        ide:activate()
        -- Focus on editor
        hs.eventtap.keyStroke({{"cmd"}}, "1")
    end
end)

-- 3. Smart Tab Cycling
local testUrls = {{
    "http://localhost:3000",
    "http://localhost:3000/test",
    "http://localhost:3000/api",
}}
local currentUrlIndex = 1

hs.hotkey.bind({{"cmd"}}, "`", function()
    local browser = hs.application.find("{browser}")
    if browser then
        browser:activate()
        -- Go to URL bar
        hs.eventtap.keyStroke({{"cmd"}}, "l")
        hs.timer.doAfter(0.1, function()
            -- Type URL
            hs.eventtap.keyStrokes(testUrls[currentUrlIndex])
            hs.eventtap.keyStroke({{"}}, "return")
            currentUrlIndex = (currentUrlIndex % #testUrls) + 1
        end)
    end
end)

-- 4. Quick Terminal Command
hs.hotkey.bind({{"cmd", "shift"}}, "T", function()
    local term = hs.application.find("Terminal")
    if not term then
        term = hs.application.find("iTerm2")
    end
    if term then
        term:activate()
        -- Run test command
        hs.eventtap.keyStrokes("npm test")
        hs.eventtap.keyStroke({{"}}, "return")
    end
end)
''',
            
            'focus_mode': '''
-- Deep Focus Mode with Smart Interruption Handling
focusMode = {{
    active = false,
    startTime = 0,
    duration = 1800,  -- 30 minutes default
    blockedApps = {{{blocked_apps}}},
    allowedBreaks = 2,
    breaksUsed = 0
}}

-- Menu bar indicator
focusMenuBar = hs.menubar.new()

function updateFocusMenu()
    if focusMode.active then
        local remaining = math.floor((focusMode.duration - (os.time() - focusMode.startTime)) / 60)
        focusMenuBar:setTitle("🎯 " .. remaining .. "m")
        focusMenuBar:setMenu({{
            {{title = "End Focus Session", fn = endFocusMode}},
            {{title = "Take Break (5 min)", fn = takeBreak, disabled = focusMode.breaksUsed >= focusMode.allowedBreaks}},
            {{title = "-"}},
            {{title = "Breaks used: " .. focusMode.breaksUsed .. "/" .. focusMode.allowedBreaks}}
        }})
    else
        focusMenuBar:setTitle("😴")
        focusMenuBar:setMenu({{
            {{title = "Start Focus Mode (30m)", fn = function() startFocusMode(1800) end}},
            {{title = "Start Focus Mode (60m)", fn = function() startFocusMode(3600) end}},
            {{title = "Start Focus Mode (90m)", fn = function() startFocusMode(5400) end}},
        }})
    end
end

function startFocusMode(duration)
    focusMode.active = true
    focusMode.startTime = os.time()
    focusMode.duration = duration or 1800
    focusMode.breaksUsed = 0
    
    -- Block distracting apps
    for _, appName in ipairs(focusMode.blockedApps) do
        local app = hs.application.find(appName)
        if app then app:kill() end
    end
    
    hs.notify.new({{
        title = "🎯 Focus Mode Active",
        informativeText = "Distractions blocked for " .. math.floor(duration/60) .. " minutes",
        soundName = hs.notify.defaultNotificationSound
    }}):send()
    
    -- Update menu bar
    updateFocusMenu()
    
    -- Set timer to end focus mode
    hs.timer.doAfter(duration, endFocusMode)
    
    -- Update menu bar every minute
    focusTimer = hs.timer.doEvery(60, updateFocusMenu)
end

function endFocusMode()
    focusMode.active = false
    
    hs.notify.new({{
        title = "✅ Focus Session Complete!",
        informativeText = "Great work! Take a break.",
        soundName = hs.notify.defaultNotificationSound
    }}):send()
    
    if focusTimer then
        focusTimer:stop()
    end
    
    updateFocusMenu()
end

function takeBreak()
    if focusMode.breaksUsed < focusMode.allowedBreaks then
        focusMode.breaksUsed = focusMode.breaksUsed + 1
        focusMode.active = false
        
        hs.notify.new({{
            title = "☕ Break Time",
            informativeText = "5 minute break. Focus resumes automatically.",
            soundName = hs.notify.defaultNotificationSound
        }}):send()
        
        -- Resume after 5 minutes
        hs.timer.doAfter(300, function()
            focusMode.active = true
            hs.notify.new({{
                title = "🎯 Back to Focus",
                informativeText = "Break over. Let's continue!",
                soundName = hs.notify.defaultNotificationSound
            }}):send()
            updateFocusMenu()
        end)
    end
end

-- Initialize menu
updateFocusMenu()

-- Hotkey for quick toggle
hs.hotkey.bind({{"cmd", "shift"}}, "F", function()
    if focusMode.active then
        endFocusMode()
    else
        startFocusMode(1800)
    end
end)
''',
            
            'smart_notifications': '''
-- Intelligent Notification Batching
notificationBatcher = {{
    queue = {{}},
    batchInterval = 1800,  -- 30 minutes
    enabled = true,
    urgentApps = {{}}  -- Apps that bypass batching
}}

-- Intercept notifications
hs.notify.watcher = hs.application.watcher.new(function(appName, eventType, appObject)
    if eventType == hs.application.watcher.activated then
        if notificationBatcher.enabled and shouldBatchApp(appName) then
            -- Add to queue instead of showing immediately
            table.insert(notificationBatcher.queue, {{
                app = appName,
                time = os.time(),
                count = 1
            }})
            
            -- Hide the app to prevent distraction
            appObject:hide()
            
            -- Show subtle indicator
            hs.alert.show("📬 Notification queued", 0.5)
        end
    end
end)

function shouldBatchApp(appName)
    local batchApps = {{{batch_apps}}}
    for _, app in ipairs(batchApps) do
        if appName:lower():find(app:lower()) then
            return true
        end
    end
    return false
end

-- Show batched notifications
function showBatchedNotifications()
    if #notificationBatcher.queue > 0 then
        local summary = "📬 Batched Notifications:\\n"
        local appCounts = {{}}
        
        for _, notif in ipairs(notificationBatcher.queue) do
            appCounts[notif.app] = (appCounts[notif.app] or 0) + 1
        end
        
        for app, count in pairs(appCounts) do
            summary = summary .. string.format("• %s: %d new\\n", app, count)
        end
        
        hs.notify.new({{
            title = "📬 Notification Batch",
            informativeText = summary,
            soundName = hs.notify.defaultNotificationSound,
            actionButtonTitle = "Review Now",
            hasActionButton = true
        }}):send()
        
        -- Clear queue
        notificationBatcher.queue = {{}}
    end
end

-- Timer for batch delivery
batchTimer = hs.timer.doEvery(notificationBatcher.batchInterval, showBatchedNotifications)

-- Hotkey to check notifications manually
hs.hotkey.bind({{"cmd", "shift"}}, "N", showBatchedNotifications)
'''
        }
    
    def _load_mcp_registry(self) -> Dict:
        """Load known MCP servers and their purposes"""
        return {
            'browser_automation': MCPSuggestion(
                name='mcp-playwright',
                purpose='Automate browser testing and interactions',
                installation='npm install -g @modelcontextprotocol/mcp-playwright',
                configuration='''
{
  "servers": {
    "playwright": {
      "command": "mcp-playwright",
      "args": ["--headless", "--timeout", "30000"],
      "env": {}
    }
  }
}''',
                search_query='MCP server Playwright browser automation testing'
            ),
            
            'note_consolidation': MCPSuggestion(
                name='mcp-obsidian',
                purpose='AI-powered note organization and linking',
                installation='npm install -g @modelcontextprotocol/mcp-obsidian',
                configuration='''
{
  "servers": {
    "obsidian": {
      "command": "mcp-obsidian",
      "args": ["--vault", "~/Documents/Obsidian"],
      "env": {}
    }
  }
}''',
                search_query='MCP server Obsidian note taking knowledge management'
            ),
            
            'communication': MCPSuggestion(
                name='mcp-slack-summary',
                purpose='Summarize and prioritize messages',
                installation='npm install -g @modelcontextprotocol/mcp-slack',
                configuration='''
{
  "servers": {
    "slack": {
      "command": "mcp-slack",
      "args": ["--summarize", "--priority-filter"],
      "env": {
        "SLACK_TOKEN": "xoxb-your-token"
      }
    }
  }
}''',
                search_query='MCP server Slack communication summarization'
            ),
            
            'code_analysis': MCPSuggestion(
                name='mcp-code-review',
                purpose='Automated code review and suggestions',
                installation='npm install -g @modelcontextprotocol/mcp-code',
                configuration='''
{
  "servers": {
    "code-review": {
      "command": "mcp-code",
      "args": ["--review", "--suggest"],
      "env": {}
    }
  }
}''',
                search_query='MCP server code review analysis suggestions'
            )
        }
    
    def generate_interventions(self, pattern_type: str, 
                              app_a: str, app_b: str,
                              context: Dict) -> List[Intervention]:
        """
        Generate a list of interventions for a specific pattern
        
        Args:
            pattern_type: Type of pattern detected
            app_a: First app in pattern
            app_b: Second app in pattern
            context: Additional context about the pattern
            
        Returns:
            List of intervention options
        """
        interventions = []
        
        # Generate based on pattern type
        if pattern_type == 'testing_workflow':
            interventions.extend(self._generate_testing_interventions(app_a, app_b))
        elif pattern_type == 'distraction_loop':
            interventions.extend(self._generate_distraction_interventions(app_a, app_b))
        elif pattern_type == 'research_workflow':
            interventions.extend(self._generate_research_interventions(app_a, app_b))
        elif pattern_type == 'communication_burst':
            interventions.extend(self._generate_communication_interventions(app_a, app_b))
        
        # Add universal interventions
        interventions.extend(self._generate_universal_interventions(app_a, app_b))
        
        return interventions
    
    def _generate_testing_interventions(self, ide: str, browser: str) -> List[Intervention]:
        """Generate interventions for testing workflows"""
        return [
            Intervention(
                name="Testing Window Layout",
                type=InterventionType.HAMMERSPOON_WINDOW,
                description=f"Automatically arrange {ide} and {browser} side-by-side for testing",
                implementation=self.hammerspoon_templates['window_testing_layout'].format(
                    app_a=ide, app_b=browser
                ),
                difficulty="easy",
                effectiveness=8,
                requirements=["Hammerspoon installed"]
            ),
            
            Intervention(
                name="Testing Hotkeys",
                type=InterventionType.HAMMERSPOON_HOTKEY,
                description="Quick browser refresh, console toggle, and test runner",
                implementation=self.hammerspoon_templates['smart_hotkeys'].format(
                    workflow_type="testing",
                    browser=browser,
                    ide=ide
                ),
                difficulty="easy",
                effectiveness=7,
                requirements=["Hammerspoon installed"]
            ),
            
            Intervention(
                name="Browser Automation MCP",
                type=InterventionType.MCP_SERVER,
                description="Automate browser testing with Playwright MCP",
                implementation=json.dumps({
                    'mcp': self.mcp_registry['browser_automation'].__dict__,
                    'usage': f'Automate testing between {ide} and {browser}'
                }, indent=2),
                difficulty="medium",
                effectiveness=9,
                requirements=["Node.js", "Claude Code MCP support"]
            )
        ]
    
    def _generate_distraction_interventions(self, productive_app: str, 
                                           distraction_app: str) -> List[Intervention]:
        """Generate interventions for distraction loops"""
        return [
            Intervention(
                name="Progressive App Blocking",
                type=InterventionType.HAMMERSPOON_BLOCK,
                description=f"Progressively block {distraction_app} when switching from {productive_app}",
                implementation=self.hammerspoon_templates['progressive_block'].format(
                    app_to_block=distraction_app,
                    productive_app=productive_app
                ),
                difficulty="easy",
                effectiveness=9,
                requirements=["Hammerspoon installed"]
            ),
            
            Intervention(
                name="Focus Mode",
                type=InterventionType.HAMMERSPOON_FOCUS,
                description="One-key focus mode that blocks all distractions",
                implementation=self.hammerspoon_templates['focus_mode'].format(
                    blocked_apps=f'"{distraction_app}", "Discord", "Telegram"'
                ),
                difficulty="easy",
                effectiveness=8,
                requirements=["Hammerspoon installed"]
            )
        ]
    
    def _generate_research_interventions(self, browser: str, 
                                        notes_app: str) -> List[Intervention]:
        """Generate interventions for research workflows"""
        return [
            Intervention(
                name="Research Layout",
                type=InterventionType.HAMMERSPOON_WINDOW,
                description=f"Split screen for {browser} and {notes_app}",
                implementation=self.hammerspoon_templates['window_testing_layout'].format(
                    app_a=browser, app_b=notes_app
                ),
                difficulty="easy",
                effectiveness=7,
                requirements=["Hammerspoon installed"]
            ),
            
            Intervention(
                name="Note Consolidation MCP",
                type=InterventionType.MCP_SERVER,
                description="AI-powered note organization",
                implementation=json.dumps({
                    'mcp': self.mcp_registry['note_consolidation'].__dict__,
                    'usage': f'Consolidate research from {browser} to {notes_app}'
                }, indent=2),
                difficulty="medium",
                effectiveness=8,
                requirements=["Node.js", "Obsidian or similar"]
            )
        ]
    
    def _generate_communication_interventions(self, work_app: str,
                                             comm_app: str) -> List[Intervention]:
        """Generate interventions for communication bursts"""
        return [
            Intervention(
                name="Notification Batching",
                type=InterventionType.HAMMERSPOON_NOTIFY,
                description=f"Batch {comm_app} notifications every 30 minutes",
                implementation=self.hammerspoon_templates['smart_notifications'].format(
                    batch_apps=f'"{comm_app}", "Slack", "Discord"'
                ),
                difficulty="medium",
                effectiveness=8,
                requirements=["Hammerspoon installed"]
            ),
            
            Intervention(
                name="Communication Summary MCP",
                type=InterventionType.MCP_SERVER,
                description="AI-powered message summarization",
                implementation=json.dumps({
                    'mcp': self.mcp_registry['communication'].__dict__,
                    'usage': f'Summarize {comm_app} messages while working in {work_app}'
                }, indent=2),
                difficulty="hard",
                effectiveness=7,
                requirements=["Node.js", "API tokens"]
            )
        ]
    
    def _generate_universal_interventions(self, app_a: str, app_b: str) -> List[Intervention]:
        """Generate interventions that work for any pattern"""
        return [
            Intervention(
                name="Usage Analytics",
                type=InterventionType.HAMMERSPOON_NOTIFY,
                description=f"Track and visualize time in {app_a} ↔ {app_b} pattern",
                implementation='''
-- Simple usage tracking
usageTracker = {
    patterns = {},
    startTime = os.time()
}

hs.application.watcher.new(function(appName, eventType, appObject)
    if eventType == hs.application.watcher.activated then
        local pattern = lastApp .. " → " .. appName
        usageTracker.patterns[pattern] = (usageTracker.patterns[pattern] or 0) + 1
        lastApp = appName
    end
end):start()

-- Daily report
hs.timer.doAt("18:00", "1d", function()
    local report = "Daily Usage Report:\\n"
    for pattern, count in pairs(usageTracker.patterns) do
        report = report .. pattern .. ": " .. count .. "\\n"
    end
    hs.notify.new({title = "Usage Report", informativeText = report}):send()
end)
''',
                difficulty="easy",
                effectiveness=5,
                requirements=["Hammerspoon installed"]
            )
        ]
    
    def rank_interventions(self, interventions: List[Intervention],
                          user_skill_level: str = "medium") -> List[Intervention]:
        """
        Rank interventions by effectiveness and user skill level
        
        Args:
            interventions: List of interventions to rank
            user_skill_level: 'beginner', 'medium', 'advanced'
            
        Returns:
            Sorted list of interventions
        """
        skill_weights = {
            'beginner': {'easy': 1.0, 'medium': 0.5, 'hard': 0.2},
            'medium': {'easy': 0.8, 'medium': 1.0, 'hard': 0.6},
            'advanced': {'easy': 0.6, 'medium': 0.9, 'hard': 1.0}
        }
        
        weights = skill_weights.get(user_skill_level, skill_weights['medium'])
        
        def score_intervention(intervention: Intervention) -> float:
            difficulty_weight = weights.get(intervention.difficulty, 0.5)
            return intervention.effectiveness * difficulty_weight
        
        return sorted(interventions, key=score_intervention, reverse=True)
    
    def generate_combined_config(self, selected_interventions: List[Intervention]) -> str:
        """
        Generate a combined Hammerspoon configuration from selected interventions
        
        Args:
            selected_interventions: List of interventions to combine
            
        Returns:
            Complete Hammerspoon configuration
        """
        config = '''-- Automation Assassin - Combined Configuration
-- Generated by Smart Intervention Generator
-- ==========================================

'''
        
        # Separate Hammerspoon and MCP interventions
        hammerspoon_interventions = [i for i in selected_interventions 
                                    if i.type != InterventionType.MCP_SERVER]
        mcp_interventions = [i for i in selected_interventions 
                           if i.type == InterventionType.MCP_SERVER]
        
        # Add Hammerspoon code
        for intervention in hammerspoon_interventions:
            config += f"-- {intervention.name}\n"
            config += f"-- {intervention.description}\n"
            config += intervention.implementation + "\n\n"
        
        # Add MCP setup instructions as comments
        if mcp_interventions:
            config += '''
-- ==========================================
-- MCP Server Setup Instructions
-- ==========================================
'''
            for intervention in mcp_interventions:
                config += f"-- {intervention.name}:\n"
                config += f"-- {intervention.description}\n"
                config += "-- Installation and setup:\n"
                for line in intervention.implementation.split('\n'):
                    config += f"-- {line}\n"
                config += "\n"
        
        return config