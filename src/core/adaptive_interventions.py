"""
Adaptive Intervention System
Context-aware interventions that understand root causes
Provides educational, coaching, and tool-based interventions
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import random


class InterventionLevel(Enum):
    """Intervention intensity levels"""
    INSIGHT = "insight"  # Just information
    GENTLE = "gentle"  # Soft suggestion
    COACHING = "coaching"  # Active guidance
    EDUCATIONAL = "educational"  # Learning opportunity
    TOOL = "tool"  # Automation/blocking
    COMPREHENSIVE = "comprehensive"  # Multiple approaches


class RootCause(Enum):
    """Root causes of productivity patterns"""
    PRODUCTIVE_WAITING = "productive_waiting"
    INTENTIONAL_MULTITASK = "intentional_multitask"
    KNOWLEDGE_GAP = "knowledge_gap"
    STRESS_RESPONSE = "stress_response"
    COGNITIVE_OVERLOAD = "cognitive_overload"
    SOCIAL_NEED = "social_need"
    ENERGY_MANAGEMENT = "energy_management"
    WORKFLOW_INEFFICIENCY = "workflow_inefficiency"
    HABIT_FORMATION = "habit_formation"
    EXTERNAL_INTERRUPT = "external_interrupt"


@dataclass
class Intervention:
    """A specific intervention"""
    id: str
    level: InterventionLevel
    root_cause: RootCause
    title: str
    description: str
    action_required: bool
    automation_code: Optional[str] = None  # Hammerspoon/script
    educational_content: Optional[str] = None
    coaching_message: Optional[str] = None
    metrics_to_track: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    duration_minutes: int = 0  # How long intervention should run
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'level': self.level.value,
            'root_cause': self.root_cause.value,
            'title': self.title,
            'description': self.description,
            'action_required': self.action_required,
            'expected_outcome': self.expected_outcome
        }


@dataclass
class InterventionPlan:
    """A plan combining multiple interventions"""
    plan_id: str
    created_at: datetime
    root_causes: List[RootCause]
    interventions: List[Intervention]
    priority: str  # high, medium, low
    user_context: Dict[str, Any]
    success_criteria: List[str]
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        summary = f"Intervention Plan ({self.priority} priority)\n"
        summary += f"Addressing: {', '.join(rc.value for rc in self.root_causes)}\n"
        summary += f"Interventions: {len(self.interventions)}\n"
        for i, intervention in enumerate(self.interventions, 1):
            summary += f"  {i}. {intervention.title} ({intervention.level.value})\n"
        return summary


class AdaptiveInterventionSystem:
    """
    Creates context-aware interventions based on root causes
    Adapts to user preferences and effectiveness
    """
    
    def __init__(self):
        self.intervention_library = self._build_intervention_library()
        self.active_interventions = {}
        self.intervention_history = []
        self.effectiveness_scores = {}  # Track what works
        self.user_preferences = {
            'preferred_level': InterventionLevel.GENTLE,
            'learning_style': 'practical',  # practical, theoretical, visual
            'automation_comfort': 0.7,  # 0-1, how comfortable with automation
            'interruption_tolerance': 0.5  # 0-1, how much interruption is ok
        }
        
    def _build_intervention_library(self) -> Dict[RootCause, List[Intervention]]:
        """Build library of interventions for each root cause"""
        
        library = {
            RootCause.PRODUCTIVE_WAITING: [
                Intervention(
                    id="pw_insight_1",
                    level=InterventionLevel.INSIGHT,
                    root_cause=RootCause.PRODUCTIVE_WAITING,
                    title="Productive Waiting Detected",
                    description="You're efficiently using wait time while AI/tools process. Great job!",
                    action_required=False,
                    expected_outcome="User awareness of productive behavior"
                ),
                Intervention(
                    id="pw_tool_1",
                    level=InterventionLevel.TOOL,
                    root_cause=RootCause.PRODUCTIVE_WAITING,
                    title="Smart Wait Timer",
                    description="Shows estimated completion time for common wait triggers",
                    action_required=False,
                    automation_code="""
-- Hammerspoon: Smart Wait Timer
waitTimer = {}
waitTimer.active = {}

function waitTimer:start(app, action, duration)
    local alert = hs.alert.show(
        string.format("⏱️ %s: ~%ds remaining", action, duration),
        {textSize=14, radius=8},
        duration
    )
    self.active[app] = {alert=alert, start=os.time()}
end

function waitTimer:checkApp()
    local app = hs.application.frontmostApplication():name()
    if app == "Code" or app == "Terminal" then
        -- Detect wait triggers
        local win = hs.window.focusedWindow()
        if win then
            local title = win:title()
            if string.find(title, "Claude") then
                self:start(app, "AI Processing", 30)
            elseif string.find(title, "build") then
                self:start(app, "Build", 45)
            end
        end
    end
end

-- Check every 5 seconds
hs.timer.doEvery(5, function() waitTimer:checkApp() end)
""",
                    expected_outcome="Better awareness of wait durations"
                )
            ],
            
            RootCause.COGNITIVE_OVERLOAD: [
                Intervention(
                    id="co_coaching_1",
                    level=InterventionLevel.COACHING,
                    root_cause=RootCause.COGNITIVE_OVERLOAD,
                    title="Cognitive Load Check",
                    description="High switching velocity detected. Time for a mental reset?",
                    action_required=True,
                    coaching_message="""
Your switching patterns suggest cognitive overload. Let's reset:

1. Take 3 deep breaths
2. Write down your current top 3 priorities
3. Close all unnecessary tabs and apps
4. Focus on one task for the next 25 minutes

Remember: Multitasking feels productive but often isn't.
""",
                    expected_outcome="Reduced switching velocity by 50%"
                ),
                Intervention(
                    id="co_educational_1",
                    level=InterventionLevel.EDUCATIONAL,
                    root_cause=RootCause.COGNITIVE_OVERLOAD,
                    title="Understanding Cognitive Load",
                    description="Learn why rapid switching hurts productivity",
                    action_required=False,
                    educational_content="""
# The Science of Task Switching

Research shows that each task switch costs 25 minutes of focused time.
Your brain needs time to load context, and rapid switching prevents deep thinking.

## Quick Exercise:
1. Count your open browser tabs
2. Close all but 3 most important
3. Notice the mental relief

## Your Pattern:
- You switch apps every {avg_switch_time} seconds
- This costs you {lost_time} minutes per day
- Top trigger: {top_trigger}

## Try This:
- Batch similar tasks together
- Use time blocks for different activity types
- Check messages at set times, not continuously
""",
                    expected_outcome="Understanding leads to behavior change"
                )
            ],
            
            RootCause.STRESS_RESPONSE: [
                Intervention(
                    id="sr_gentle_1",
                    level=InterventionLevel.GENTLE,
                    root_cause=RootCause.STRESS_RESPONSE,
                    title="Stress Pattern Detected",
                    description="Your app switching suggests stress. Want a quick break?",
                    action_required=False,
                    coaching_message="Stress switching detected. Try: 5 minutes away from screen, short walk, or breathing exercise.",
                    expected_outcome="Stress reduction"
                ),
                Intervention(
                    id="sr_comprehensive_1",
                    level=InterventionLevel.COMPREHENSIVE,
                    root_cause=RootCause.STRESS_RESPONSE,
                    title="Stress Management Toolkit",
                    description="Complete stress intervention program",
                    action_required=True,
                    coaching_message="Let's address the stress pattern comprehensively.",
                    educational_content="""
# Stress Switching Pattern

You're using app switching as a stress response. Common but ineffective.

## Immediate Actions:
1. Step away from computer for 5 minutes
2. Do box breathing (4-4-4-4)
3. Write down what's causing stress

## Long-term Solutions:
- Break large tasks into smaller ones
- Use Pomodoro technique
- Schedule worry time
""",
                    automation_code="""
-- Stress break reminder
hs.timer.doAfter(25*60, function()
    hs.alert.show("Time for a stress break! 🧘", 3)
    hs.openURL("focus://focus?minutes=5")
end)
""",
                    expected_outcome="Reduced stress-driven switching"
                )
            ],
            
            RootCause.WORKFLOW_INEFFICIENCY: [
                Intervention(
                    id="wi_tool_1",
                    level=InterventionLevel.TOOL,
                    root_cause=RootCause.WORKFLOW_INEFFICIENCY,
                    title="Window Layout Optimizer",
                    description="Arrange windows to reduce switching",
                    action_required=False,
                    automation_code="""
-- Hammerspoon: Smart Window Layout
function arrangeForProductivity()
    local screens = hs.screen.allScreens()
    local mainScreen = screens[1]
    local rect = mainScreen:frame()
    
    -- Put browser on left half
    local browser = hs.application.get("Safari") or hs.application.get("Chrome")
    if browser then
        local win = browser:mainWindow()
        if win then
            win:setFrame({x=rect.x, y=rect.y, w=rect.w/2, h=rect.h})
        end
    end
    
    -- Put communication on right half
    local telegram = hs.application.get("Telegram")
    if telegram then
        local win = telegram:mainWindow()
        if win then
            win:setFrame({x=rect.x+rect.w/2, y=rect.y, w=rect.w/2, h=rect.h})
        end
    end
    
    hs.alert.show("Windows arranged for productivity! 🖥️")
end

hs.hotkey.bind({"cmd", "shift"}, "L", arrangeForProductivity)
""",
                    expected_outcome="Reduced switching by 30%"
                ),
                Intervention(
                    id="wi_educational_1",
                    level=InterventionLevel.EDUCATIONAL,
                    root_cause=RootCause.WORKFLOW_INEFFICIENCY,
                    title="Workflow Optimization Guide",
                    description="Learn to structure your digital workspace",
                    action_required=True,
                    educational_content="""
# Optimizing Your Digital Workflow

Your switching patterns show workflow inefficiencies. Let's fix that.

## Window Management:
- Use split screen for related apps
- Virtual desktops for different contexts
- Keyboard shortcuts over mouse clicking

## App Organization:
- Group related apps together
- Close unused apps
- Use app launchers (Spotlight, Alfred)

## Your Specific Issues:
- You switch between {app1} and {app2} {count} times/day
- Average gap: {gap} seconds
- Solution: Keep both visible simultaneously
""",
                    expected_outcome="Improved workflow efficiency"
                )
            ],
            
            RootCause.INTENTIONAL_MULTITASK: [
                Intervention(
                    id="im_insight_1",
                    level=InterventionLevel.INSIGHT,
                    root_cause=RootCause.INTENTIONAL_MULTITASK,
                    title="Multitasking Style Recognized",
                    description="Your parallel processing style is working for you!",
                    action_required=False,
                    expected_outcome="Validation of work style"
                ),
                Intervention(
                    id="im_tool_1",
                    level=InterventionLevel.TOOL,
                    root_cause=RootCause.INTENTIONAL_MULTITASK,
                    title="Multitask Mode Optimizer",
                    description="Enhance your natural multitasking style",
                    action_required=False,
                    automation_code="""
-- Multitask Mode
multitaskMode = {}
multitaskMode.active = false

function multitaskMode:toggle()
    self.active = not self.active
    if self.active then
        -- Reduce interruptions
        hs.execute("defaults write com.apple.dock notification-always-show-image -bool false")
        hs.alert.show("Multitask Mode ON 🎯")
        
        -- Set up side-by-side windows
        arrangeForMultitasking()
    else
        hs.execute("defaults write com.apple.dock notification-always-show-image -bool true")
        hs.alert.show("Multitask Mode OFF")
    end
end

hs.hotkey.bind({"cmd", "shift"}, "M", function() multitaskMode:toggle() end)
""",
                    expected_outcome="Enhanced multitasking efficiency"
                )
            ]
        }
        
        # Add more root causes...
        for root_cause in RootCause:
            if root_cause not in library:
                library[root_cause] = [
                    Intervention(
                        id=f"{root_cause.value}_default",
                        level=InterventionLevel.INSIGHT,
                        root_cause=root_cause,
                        title=f"Pattern: {root_cause.value.replace('_', ' ').title()}",
                        description=f"We've identified a {root_cause.value} pattern",
                        action_required=False,
                        expected_outcome="User awareness"
                    )
                ]
        
        return library
    
    def create_intervention_plan(self, 
                                root_causes: List[RootCause],
                                user_context: Dict[str, Any],
                                urgency: str = "medium") -> InterventionPlan:
        """Create a personalized intervention plan"""
        
        interventions = []
        
        for root_cause in root_causes:
            if root_cause in self.intervention_library:
                available = self.intervention_library[root_cause]
                
                # Select intervention based on user preferences
                selected = self._select_intervention(available, user_context)
                if selected:
                    interventions.append(selected)
        
        # Sort by effectiveness if we have historical data
        interventions = self._sort_by_effectiveness(interventions)
        
        # Create success criteria
        success_criteria = self._generate_success_criteria(root_causes, user_context)
        
        plan = InterventionPlan(
            plan_id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            created_at=datetime.now(),
            root_causes=root_causes,
            interventions=interventions,
            priority=urgency,
            user_context=user_context,
            success_criteria=success_criteria
        )
        
        # Store plan
        self.active_interventions[plan.plan_id] = plan
        
        return plan
    
    def _select_intervention(self, available: List[Intervention], 
                           context: Dict[str, Any]) -> Optional[Intervention]:
        """Select best intervention based on context and preferences"""
        
        # Filter by user preferences
        preferred_level = self.user_preferences['preferred_level']
        
        # Try to find intervention matching preferred level
        matches = [i for i in available if i.level == preferred_level]
        
        if not matches:
            # Fall back to any intervention
            matches = available
        
        # Consider effectiveness scores
        if self.effectiveness_scores:
            matches.sort(key=lambda i: self.effectiveness_scores.get(i.id, 0.5), reverse=True)
        
        return matches[0] if matches else None
    
    def _sort_by_effectiveness(self, interventions: List[Intervention]) -> List[Intervention]:
        """Sort interventions by historical effectiveness"""
        
        return sorted(interventions, 
                     key=lambda i: self.effectiveness_scores.get(i.id, 0.5), 
                     reverse=True)
    
    def _generate_success_criteria(self, root_causes: List[RootCause], 
                                  context: Dict[str, Any]) -> List[str]:
        """Generate measurable success criteria"""
        
        criteria = []
        
        if RootCause.COGNITIVE_OVERLOAD in root_causes:
            criteria.append("Reduce switching velocity by 40%")
            criteria.append("Increase average session duration to >5 minutes")
        
        if RootCause.PRODUCTIVE_WAITING in root_causes:
            criteria.append("Maintain productive waiting patterns")
            criteria.append("No intervention needed - pattern is healthy")
        
        if RootCause.STRESS_RESPONSE in root_causes:
            criteria.append("Reduce stress-driven switches by 50%")
            criteria.append("Implement regular break schedule")
        
        if RootCause.WORKFLOW_INEFFICIENCY in root_causes:
            criteria.append("Reduce repetitive app switches by 30%")
            criteria.append("Implement better window management")
        
        return criteria if criteria else ["Improve overall productivity metrics"]
    
    def execute_intervention(self, intervention: Intervention) -> Dict[str, Any]:
        """Execute a specific intervention"""
        
        result = {
            'intervention_id': intervention.id,
            'executed_at': datetime.now().isoformat(),
            'success': False,
            'message': ''
        }
        
        try:
            # Execute based on level
            if intervention.level == InterventionLevel.INSIGHT:
                # Just show message
                result['message'] = intervention.description
                result['success'] = True
                
            elif intervention.level == InterventionLevel.GENTLE:
                # Show coaching message
                result['message'] = intervention.coaching_message or intervention.description
                result['success'] = True
                
            elif intervention.level == InterventionLevel.COACHING:
                # Provide coaching
                result['coaching'] = intervention.coaching_message
                result['action_required'] = intervention.action_required
                result['success'] = True
                
            elif intervention.level == InterventionLevel.EDUCATIONAL:
                # Provide education
                result['content'] = intervention.educational_content
                result['success'] = True
                
            elif intervention.level == InterventionLevel.TOOL:
                # Deploy automation
                if intervention.automation_code:
                    result['code'] = intervention.automation_code
                    result['instructions'] = "Add this code to your Hammerspoon config"
                    result['success'] = True
                    
            elif intervention.level == InterventionLevel.COMPREHENSIVE:
                # Multiple components
                components = []
                if intervention.coaching_message:
                    components.append({'type': 'coaching', 'content': intervention.coaching_message})
                if intervention.educational_content:
                    components.append({'type': 'education', 'content': intervention.educational_content})
                if intervention.automation_code:
                    components.append({'type': 'automation', 'content': intervention.automation_code})
                result['components'] = components
                result['success'] = True
            
            # Track execution
            self.intervention_history.append({
                'intervention': intervention,
                'result': result,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def record_effectiveness(self, intervention_id: str, effectiveness: float):
        """Record how effective an intervention was (0-1)"""
        
        # Update rolling average
        if intervention_id in self.effectiveness_scores:
            old_score = self.effectiveness_scores[intervention_id]
            # Weighted average: 70% old, 30% new
            self.effectiveness_scores[intervention_id] = old_score * 0.7 + effectiveness * 0.3
        else:
            self.effectiveness_scores[intervention_id] = effectiveness
    
    def adapt_to_user(self, feedback: Dict[str, Any]):
        """Adapt system based on user feedback"""
        
        if 'preferred_level' in feedback:
            self.user_preferences['preferred_level'] = InterventionLevel[feedback['preferred_level'].upper()]
        
        if 'automation_comfort' in feedback:
            self.user_preferences['automation_comfort'] = feedback['automation_comfort']
        
        if 'interruption_tolerance' in feedback:
            self.user_preferences['interruption_tolerance'] = feedback['interruption_tolerance']
        
        if 'learning_style' in feedback:
            self.user_preferences['learning_style'] = feedback['learning_style']
    
    def get_active_plans(self) -> List[InterventionPlan]:
        """Get all active intervention plans"""
        return list(self.active_interventions.values())
    
    def get_intervention_stats(self) -> Dict:
        """Get statistics about interventions"""
        
        total_executed = len(self.intervention_history)
        if total_executed == 0:
            return {'message': 'No interventions executed yet'}
        
        by_level = {}
        by_root_cause = {}
        successful = 0
        
        for record in self.intervention_history:
            intervention = record['intervention']
            result = record['result']
            
            # Count by level
            level = intervention.level.value
            by_level[level] = by_level.get(level, 0) + 1
            
            # Count by root cause
            cause = intervention.root_cause.value
            by_root_cause[cause] = by_root_cause.get(cause, 0) + 1
            
            # Count successful
            if result['success']:
                successful += 1
        
        # Get most effective interventions
        most_effective = sorted(
            self.effectiveness_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_executed': total_executed,
            'success_rate': successful / total_executed * 100,
            'by_level': by_level,
            'by_root_cause': by_root_cause,
            'most_effective': most_effective,
            'user_preferences': self.user_preferences,
            'active_plans': len(self.active_interventions)
        }