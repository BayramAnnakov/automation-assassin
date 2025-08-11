"""
Coaching Intervention System - Orchestrates educational and behavioral interventions
Provides coaching, education, and insights rather than just blocking
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

from ..core.root_cause_analyzer import RootCauseAnalyzer, RootCauseType
from .learning_generator import LearningGenerator

class InterventionLevel(Enum):
    """User's chosen intervention level"""
    INSIGHTS_ONLY = 1  # Just explain behaviors
    GENTLE_COACHING = 2  # Suggestions and alternatives  
    ACTIVE_LEARNING = 3  # Tutorials and skill building
    COMPREHENSIVE = 4  # Full coaching + education + tools

@dataclass
class CoachingIntervention:
    """Represents a coaching intervention"""
    pattern: str
    root_cause: str
    intervention_type: str  # 'educational', 'behavioral', 'coaching', 'insight'
    content: str
    delivery_method: str  # 'notification', 'email', 'interactive', 'passive'
    urgency: str  # 'immediate', 'daily', 'weekly'
    user_action_required: bool

class CoachingInterventionSystem:
    """
    Orchestrates educational and coaching interventions
    Focuses on understanding and education over blocking
    """
    
    def __init__(self, intervention_level: InterventionLevel = InterventionLevel.GENTLE_COACHING):
        self.intervention_level = intervention_level
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.learning_generator = LearningGenerator()
        self.intervention_history = []
        self.user_preferences = {}
        
    def generate_intervention(self, pattern_data: Dict, 
                            browser_context: Optional[Dict] = None) -> CoachingIntervention:
        """
        Generate appropriate intervention based on pattern and user preferences
        
        Args:
            pattern_data: Pattern information
            browser_context: Browser history context
            
        Returns:
            CoachingIntervention with content and delivery method
        """
        
        # Analyze root cause
        analysis = self.root_cause_analyzer.analyze_pattern(pattern_data, browser_context)
        primary_cause = analysis.primary_cause
        
        # Generate intervention based on level and cause
        if self.intervention_level == InterventionLevel.INSIGHTS_ONLY:
            return self._generate_insight_intervention(analysis, pattern_data)
        elif self.intervention_level == InterventionLevel.GENTLE_COACHING:
            return self._generate_coaching_intervention(analysis, pattern_data)
        elif self.intervention_level == InterventionLevel.ACTIVE_LEARNING:
            return self._generate_learning_intervention(analysis, pattern_data, browser_context)
        else:  # COMPREHENSIVE
            return self._generate_comprehensive_intervention(analysis, pattern_data, browser_context)
    
    def _generate_insight_intervention(self, analysis, pattern_data: Dict) -> CoachingIntervention:
        """Generate insight-only intervention"""
        
        pattern_str = f"{pattern_data.get('app_a')} ↔ {pattern_data.get('app_b')}"
        
        content = f"""
💡 **Pattern Insight: {pattern_str}**

**What's happening:** {analysis.surface_behavior}

**Why it's happening:** {analysis.primary_cause.description}

**The psychology:** {analysis.primary_cause.psychological_explanation}

No action required - just awareness.
"""
        
        return CoachingIntervention(
            pattern=pattern_str,
            root_cause=analysis.primary_cause.cause_type.value,
            intervention_type="insight",
            content=content,
            delivery_method="passive",
            urgency="weekly",
            user_action_required=False
        )
    
    def _generate_coaching_intervention(self, analysis, pattern_data: Dict) -> CoachingIntervention:
        """Generate gentle coaching intervention"""
        
        pattern_str = f"{pattern_data.get('app_a')} ↔ {pattern_data.get('app_b')}"
        cause_type = analysis.primary_cause.cause_type
        
        # Get coaching message based on root cause
        if cause_type == RootCauseType.STRESS_RESPONSE:
            content = self._coach_stress_response(pattern_data)
        elif cause_type == RootCauseType.EMOTIONAL_REGULATION:
            content = self._coach_emotional_regulation(pattern_data)
        elif cause_type == RootCauseType.KNOWLEDGE_GAP:
            content = self._coach_knowledge_gap(pattern_data, analysis)
        else:
            content = self._coach_generic(pattern_data, analysis)
        
        return CoachingIntervention(
            pattern=pattern_str,
            root_cause=cause_type.value,
            intervention_type="coaching",
            content=content,
            delivery_method="notification",
            urgency="daily",
            user_action_required=False
        )
    
    def _generate_learning_intervention(self, analysis, pattern_data: Dict, 
                                      browser_context: Optional[Dict]) -> CoachingIntervention:
        """Generate active learning intervention"""
        
        pattern_str = f"{pattern_data.get('app_a')} ↔ {pattern_data.get('app_b')}"
        cause_type = analysis.primary_cause.cause_type
        
        if cause_type == RootCauseType.KNOWLEDGE_GAP:
            # Generate learning path
            search_history = []
            if browser_context:
                search_history = [h.get('title', '') for h in browser_context.get('history', [])]
            
            knowledge_gap = self._identify_knowledge_gap(search_history)
            learning_path = self.learning_generator.generate_intervention(
                knowledge_gap, search_history
            )
            
            # Get first module
            first_module = learning_path.modules[0]
            
            content = f"""
📚 **Learning Intervention: Master {knowledge_gap}**

You've searched for this {len(search_history)} times. Let's fix that permanently!

**Today's Module:** {first_module.title}
**Time:** {first_module.estimated_time} minutes
**Objective:** {first_module.objective}

{first_module.content[:500]}...

[Click to start interactive lesson]
"""
        else:
            # Non-knowledge interventions
            content = self._generate_skill_building_content(analysis, pattern_data)
        
        return CoachingIntervention(
            pattern=pattern_str,
            root_cause=cause_type.value,
            intervention_type="educational",
            content=content,
            delivery_method="interactive",
            urgency="immediate",
            user_action_required=True
        )
    
    def _generate_comprehensive_intervention(self, analysis, pattern_data: Dict,
                                           browser_context: Optional[Dict]) -> CoachingIntervention:
        """Generate comprehensive intervention with all elements"""
        
        pattern_str = f"{pattern_data.get('app_a')} ↔ {pattern_data.get('app_b')}"
        cause_type = analysis.primary_cause.cause_type
        
        # Combine insights, coaching, and learning
        content = f"""
🎯 **Comprehensive Intervention: {pattern_str}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **INSIGHT**
{analysis.primary_cause.psychological_explanation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💭 **COACHING**
{self._get_coaching_content(cause_type, pattern_data)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 **EDUCATION**
{self._get_educational_content(cause_type, pattern_data, browser_context)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ **TOOLS**
{self._get_tool_suggestions(cause_type, pattern_data)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **ACTION PLAN**
1. Understand the pattern (5 min) ✓
2. Try alternative behavior (today)
3. Complete learning module (this week)
4. Track progress (ongoing)

[Start Guided Journey →]
"""
        
        return CoachingIntervention(
            pattern=pattern_str,
            root_cause=cause_type.value,
            intervention_type="comprehensive",
            content=content,
            delivery_method="interactive",
            urgency="immediate",
            user_action_required=True
        )
    
    def _coach_stress_response(self, pattern_data: Dict) -> str:
        """Coaching for stress-induced patterns"""
        
        app_a = pattern_data.get('app_a')
        app_b = pattern_data.get('app_b')
        
        return f"""
🧠 **Stress Pattern Detected: {app_a} ↔ {app_b}**

Your rapid switching is a stress response. Your brain is saying "I need a break!"

**Right now, try this:**
1. Push your chair back
2. Take 3 deep breaths
3. Name 3 things you can see
4. Return when ready

**Long-term alternatives:**
• Pomodoro timer (25 min work, 5 min break)
• Standing desk breaks
• Background music for focus
• Task chunking (break big problems into smaller ones)

**Why this works:** Planned breaks prevent emergency escapes.

💡 Next time you feel the urge to switch, pause and ask: "What do I really need right now?"
"""
    
    def _coach_emotional_regulation(self, pattern_data: Dict) -> str:
        """Coaching for emotional regulation patterns"""
        
        app_b = pattern_data.get('app_b')
        
        return f"""
😊 **Emotional Pattern: Seeking Comfort in {app_b}**

You're not procrastinating - you're managing emotions. This is human, not weakness.

**What's really happening:**
Big task → Anxiety → Brain seeks comfort → {app_b}

**The 2-Minute Miracle:**
1. Set timer for 2 minutes
2. Just open the task (no pressure to do more)
3. Often, starting removes the anxiety
4. If not, take a real break after 2 minutes

**Alternative comfort sources:**
• Quick walk (changes brain chemistry)
• Tea/coffee ritual (mindful pause)
• Favorite song (3-minute reset)
• Text a friend (connection without scrolling)

**Remember:** The task isn't as scary as your brain thinks. You've done hard things before.
"""
    
    def _coach_knowledge_gap(self, pattern_data: Dict, analysis) -> str:
        """Coaching for knowledge gaps"""
        
        topic = analysis.primary_cause.learning_opportunity or "this concept"
        
        return f"""
📚 **Knowledge Opportunity: Master {topic} Forever**

You keep searching because you haven't built the mental model yet. Let's fix that!

**Quick win (2 minutes):**
Write down what you DO know about {topic}. You know more than you think!

**Build understanding (10 minutes):**
1. Find the simplest explanation
2. Explain it to a rubber duck
3. Identify what's still fuzzy
4. Focus learning on fuzzy parts only

**Lock it in (ongoing):**
• Create YOUR examples (not copy-paste)
• Use it 3 times this week
• Teach someone else (or write a blog post)

**Why searching doesn't work:** 
Each search is isolated. Your brain needs connections, not fragments.

📝 Would you like a personalized learning plan for {topic}?
"""
    
    def _coach_generic(self, pattern_data: Dict, analysis) -> str:
        """Generic coaching message"""
        
        return f"""
💡 **Understanding Your Pattern**

{analysis.primary_cause.psychological_explanation}

**Three questions to explore:**
1. What triggers this pattern?
2. What need does it meet?
3. What would a better alternative look like?

**Experiment this week:**
Try one small change and observe what happens. No judgment, just curiosity.

Remember: Patterns exist for reasons. Understanding 'why' leads to sustainable change.
"""
    
    def _identify_knowledge_gap(self, search_history: List[str]) -> str:
        """Identify the main knowledge gap from searches"""
        
        # Simple keyword extraction (in production, use NLP)
        common_terms = {}
        for search in search_history:
            words = search.lower().split()
            for word in words:
                if len(word) > 4:  # Skip short words
                    common_terms[word] = common_terms.get(word, 0) + 1
        
        if common_terms:
            # Return most common term
            return max(common_terms, key=common_terms.get)
        
        return "technical concept"
    
    def _generate_skill_building_content(self, analysis, pattern_data: Dict) -> str:
        """Generate skill-building content for non-knowledge interventions"""
        
        return f"""
🛠️ **Skill Building: Better {pattern_data.get('app_a')} Workflow**

Your pattern suggests room for workflow improvement.

**This week's focus:** Keyboard shortcuts
• Learn 3 new shortcuts for {pattern_data.get('app_a')}
• Practice until automatic
• Save 10+ clicks per day

**Next week:** Automation basics
• Identify repetitive tasks
• Learn one automation tool
• Automate one workflow

**Goal:** Reduce friction, increase flow.

[Start Skill Builder →]
"""
    
    def _get_coaching_content(self, cause_type: RootCauseType, pattern_data: Dict) -> str:
        """Get coaching content for comprehensive intervention"""
        
        coaching_map = {
            RootCauseType.STRESS_RESPONSE: "Your brain needs planned breaks, not emergency escapes.",
            RootCauseType.KNOWLEDGE_GAP: "Let's move this from Google to your permanent memory.",
            RootCauseType.EMOTIONAL_REGULATION: "This isn't laziness - it's emotional management.",
            RootCauseType.SKILL_DEFICIT: "You're working harder than necessary. Let's work smarter.",
            RootCauseType.BIOLOGICAL_RHYTHM: "Work with your natural energy, not against it."
        }
        
        return coaching_map.get(cause_type, "Every pattern has a purpose. Let's understand yours.")
    
    def _get_educational_content(self, cause_type: RootCauseType, pattern_data: Dict,
                                browser_context: Optional[Dict]) -> str:
        """Get educational content for comprehensive intervention"""
        
        if cause_type == RootCauseType.KNOWLEDGE_GAP:
            return "Complete learning path available: 4 modules, 7 days to mastery."
        elif cause_type == RootCauseType.SKILL_DEFICIT:
            return "Workflow optimization course: Learn shortcuts and automation."
        else:
            return "Behavioral science mini-course: Understand your brain's patterns."
    
    def _get_tool_suggestions(self, cause_type: RootCauseType, pattern_data: Dict) -> str:
        """Get tool suggestions for comprehensive intervention"""
        
        suggestions = {
            RootCauseType.STRESS_RESPONSE: "• Pomodoro timer\n• Breathing app\n• Break reminder",
            RootCauseType.KNOWLEDGE_GAP: "• Spaced repetition app\n• Personal wiki\n• Cheat sheet generator",
            RootCauseType.EMOTIONAL_REGULATION: "• Task breakdown tool\n• Motivation tracker\n• Progress visualizer",
            RootCauseType.SKILL_DEFICIT: "• Macro recorder\n• Shortcut trainer\n• Workflow automator"
        }
        
        return suggestions.get(cause_type, "• Pattern tracker\n• Habit builder\n• Progress journal")
    
    def deliver_intervention(self, intervention: CoachingIntervention) -> bool:
        """
        Deliver intervention to user
        
        Args:
            intervention: The intervention to deliver
            
        Returns:
            Success boolean
        """
        
        # Log intervention
        self.intervention_history.append({
            'timestamp': datetime.now().isoformat(),
            'pattern': intervention.pattern,
            'root_cause': intervention.root_cause,
            'type': intervention.intervention_type,
            'delivered': True
        })
        
        # In production, this would:
        # - Show notification
        # - Send email
        # - Open interactive module
        # - Update dashboard
        
        print(f"\n{'='*60}")
        print(f"INTERVENTION: {intervention.pattern}")
        print(f"Type: {intervention.intervention_type}")
        print(f"Delivery: {intervention.delivery_method}")
        print(f"{'='*60}")
        print(intervention.content)
        print(f"{'='*60}\n")
        
        return True
    
    def get_intervention_history(self) -> List[Dict]:
        """Get history of delivered interventions"""
        return self.intervention_history
    
    def set_user_preference(self, preference: str, value: any):
        """Set user preference for interventions"""
        self.user_preferences[preference] = value
    
    def adjust_intervention_level(self, new_level: InterventionLevel):
        """Adjust intervention level based on user feedback"""
        self.intervention_level = new_level