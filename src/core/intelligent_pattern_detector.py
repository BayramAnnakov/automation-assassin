"""
Intelligent Pattern Detector v2.0
Multi-dimensional pattern analysis without hardcoded rules
Understands context, not just app switches
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import defaultdict, deque
import hashlib


class ContextDimension(Enum):
    """Dimensions of context we track"""
    TEMPORAL = "temporal"
    CONTENT = "content"
    BEHAVIORAL = "behavioral"
    ENVIRONMENTAL = "environmental"
    INTENTIONAL = "intentional"


@dataclass
class SwitchEvent:
    """Represents a single app/tab switch event"""
    timestamp: datetime
    from_app: str
    to_app: str
    from_content: Optional[str] = None  # Tab title, document name, etc.
    to_content: Optional[str] = None
    switch_duration: float = 0.0  # How long the switch took
    session_duration: float = 0.0  # How long in the 'from' app
    prior_action: Optional[str] = None  # What triggered the switch
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SituationContext:
    """Rich context about current situation"""
    timestamp: datetime
    active_app: str
    active_content: Optional[str]
    background_apps: List[str]
    recent_actions: List[str]  # Last 5 actions
    time_of_day: str  # morning, afternoon, evening, night
    day_type: str  # weekday, weekend
    energy_level: str  # inferred from switching patterns
    switching_velocity: float  # switches per minute
    session_depth: float  # average time in apps
    bounce_rate: float  # percentage of quick returns
    waiting_indicators: List[str]  # Signs of productive waiting
    multitask_indicators: List[str]  # Signs of intentional multitasking
    
    def to_fingerprint(self) -> str:
        """Create a unique fingerprint for this situation"""
        key_elements = [
            self.active_app,
            self.active_content or "",
            self.time_of_day,
            str(self.switching_velocity),
            ",".join(self.recent_actions[:3])
        ]
        return hashlib.md5("|".join(key_elements).encode()).hexdigest()[:12]


class PatternDimension:
    """Tracks patterns across different dimensions"""
    
    def __init__(self, dimension: ContextDimension):
        self.dimension = dimension
        self.patterns = defaultdict(list)
        self.statistics = defaultdict(float)
    
    def add_observation(self, key: str, value: Any):
        """Add an observation to this dimension"""
        self.patterns[key].append({
            'timestamp': datetime.now(),
            'value': value
        })
        
        # Keep only recent observations (last 1000)
        if len(self.patterns[key]) > 1000:
            self.patterns[key] = self.patterns[key][-1000:]
    
    def get_pattern_summary(self) -> Dict:
        """Summarize patterns in this dimension"""
        summary = {}
        for key, observations in self.patterns.items():
            if observations:
                summary[key] = {
                    'count': len(observations),
                    'recent': observations[-10:],  # Last 10
                    'frequency': len(observations) / max(1, len(self.patterns))
                }
        return summary


class IntelligentPatternDetector:
    """
    Detects patterns without hardcoded rules
    Captures multi-dimensional context for AI interpretation
    """
    
    def __init__(self):
        self.dimensions = {
            dim: PatternDimension(dim) 
            for dim in ContextDimension
        }
        self.switch_history = deque(maxlen=1000)
        self.situation_history = deque(maxlen=500)
        self.waiting_patterns = {}  # Learned waiting durations
        self.user_examples = []  # Examples from user behavior
        
    def record_switch(self, switch_event: SwitchEvent) -> SituationContext:
        """
        Record a switch event and build situation context
        """
        self.switch_history.append(switch_event)
        
        # Build current situation context
        situation = self._build_situation_context(switch_event)
        self.situation_history.append(situation)
        
        # Update dimensional patterns
        self._update_dimensions(switch_event, situation)
        
        # Detect waiting patterns
        self._detect_waiting_pattern(switch_event, situation)
        
        return situation
    
    def _build_situation_context(self, switch: SwitchEvent) -> SituationContext:
        """Build rich context about current situation"""
        
        # Time context
        hour = switch.timestamp.hour
        if 5 <= hour < 9:
            time_of_day = "morning"
        elif 9 <= hour < 12:
            time_of_day = "mid-morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        day_type = "weekday" if switch.timestamp.weekday() < 5 else "weekend"
        
        # Behavioral metrics
        recent_switches = [s for s in self.switch_history 
                          if s.timestamp > switch.timestamp - timedelta(minutes=5)]
        
        switching_velocity = len(recent_switches) / 5.0  # per minute
        
        # Session depth
        session_durations = [s.session_duration for s in recent_switches if s.session_duration > 0]
        session_depth = sum(session_durations) / len(session_durations) if session_durations else 0
        
        # Bounce rate (quick returns to previous app)
        bounces = self._count_bounces(recent_switches)
        bounce_rate = bounces / max(1, len(recent_switches))
        
        # Energy level inference
        if switching_velocity > 10:
            energy_level = "frantic"
        elif switching_velocity > 5:
            energy_level = "high"
        elif switching_velocity > 2:
            energy_level = "moderate"
        else:
            energy_level = "focused"
        
        # Waiting indicators
        waiting_indicators = self._detect_waiting_indicators(switch)
        
        # Multitasking indicators
        multitask_indicators = self._detect_multitask_indicators(switch)
        
        # Recent actions
        recent_actions = self._get_recent_actions()
        
        # Background apps (simplified - would need system integration)
        background_apps = self._infer_background_apps()
        
        return SituationContext(
            timestamp=switch.timestamp,
            active_app=switch.to_app,
            active_content=switch.to_content,
            background_apps=background_apps,
            recent_actions=recent_actions,
            time_of_day=time_of_day,
            day_type=day_type,
            energy_level=energy_level,
            switching_velocity=switching_velocity,
            session_depth=session_depth,
            bounce_rate=bounce_rate,
            waiting_indicators=waiting_indicators,
            multitask_indicators=multitask_indicators
        )
    
    def _count_bounces(self, switches: List[SwitchEvent]) -> int:
        """Count bounce-back patterns (A→B→A quickly)"""
        bounces = 0
        for i in range(len(switches) - 1):
            if i > 0:
                if switches[i-1].from_app == switches[i].to_app and \
                   switches[i].session_duration < 3:
                    bounces += 1
        return bounces
    
    def _detect_waiting_indicators(self, switch: SwitchEvent) -> List[str]:
        """Detect signs of productive waiting"""
        indicators = []
        
        # Check prior action
        if switch.prior_action:
            waiting_triggers = [
                'ai_query', 'claude', 'build', 'compile', 'test',
                'deploy', 'render', 'export', 'upload', 'download',
                'process', 'analyze', 'generate', 'install'
            ]
            
            for trigger in waiting_triggers:
                if trigger in switch.prior_action.lower():
                    indicators.append(f"waiting_for_{trigger}")
        
        # Check app combinations that suggest waiting
        if 'IDE' in switch.from_app and 'message' in switch.to_app.lower():
            indicators.append("ide_to_messaging_wait")
        
        # Check if this is a regular check pattern
        similar_switches = [s for s in list(self.switch_history)[-20:]
                           if s.from_app == switch.from_app and s.to_app == switch.to_app]
        if len(similar_switches) > 3:
            indicators.append("regular_check_pattern")
        
        return indicators
    
    def _detect_multitask_indicators(self, switch: SwitchEvent) -> List[str]:
        """Detect signs of intentional multitasking"""
        indicators = []
        
        # Video + work pattern
        if switch.from_content and switch.to_content:
            if any(vid in switch.from_content.lower() for vid in ['youtube', 'video', 'netflix', 'prime']):
                indicators.append("video_multitasking")
            elif any(vid in switch.to_content.lower() for vid in ['youtube', 'video', 'netflix', 'prime']):
                indicators.append("video_multitasking")
        
        # Evening multitasking
        if switch.timestamp.hour >= 20:
            indicators.append("evening_multitask")
        
        # Regular rotation pattern
        recent = list(self.switch_history)[-10:]
        if len(recent) > 5:
            apps = [s.to_app for s in recent]
            if len(set(apps)) <= 3 and len(apps) >= 6:
                indicators.append("regular_rotation")
        
        return indicators
    
    def _get_recent_actions(self) -> List[str]:
        """Get recent user actions"""
        actions = []
        for switch in list(self.switch_history)[-5:]:
            action = f"{switch.from_app}→{switch.to_app}"
            if switch.prior_action:
                action = f"{switch.prior_action}:{action}"
            actions.append(action)
        return actions
    
    def _infer_background_apps(self) -> List[str]:
        """Infer which apps are in background"""
        # Get apps used in last 10 minutes
        recent_time = datetime.now() - timedelta(minutes=10)
        recent_apps = set()
        
        for switch in self.switch_history:
            if switch.timestamp > recent_time:
                recent_apps.add(switch.from_app)
                recent_apps.add(switch.to_app)
        
        return list(recent_apps)
    
    def _update_dimensions(self, switch: SwitchEvent, situation: SituationContext):
        """Update pattern tracking across dimensions"""
        
        # Temporal dimension
        self.dimensions[ContextDimension.TEMPORAL].add_observation(
            situation.time_of_day,
            {'velocity': situation.switching_velocity, 'app': switch.to_app}
        )
        
        # Content dimension
        if switch.to_content:
            self.dimensions[ContextDimension.CONTENT].add_observation(
                self._categorize_content(switch.to_content),
                {'app': switch.to_app, 'duration': switch.session_duration}
            )
        
        # Behavioral dimension
        self.dimensions[ContextDimension.BEHAVIORAL].add_observation(
            situation.energy_level,
            {'bounce_rate': situation.bounce_rate, 'depth': situation.session_depth}
        )
        
        # Environmental dimension
        self.dimensions[ContextDimension.ENVIRONMENTAL].add_observation(
            f"{situation.day_type}_{situation.time_of_day}",
            {'apps': situation.background_apps}
        )
        
        # Intentional dimension
        intent_key = "waiting" if situation.waiting_indicators else "active"
        self.dimensions[ContextDimension.INTENTIONAL].add_observation(
            intent_key,
            {'pattern': f"{switch.from_app}→{switch.to_app}"}
        )
    
    def _categorize_content(self, content: str) -> str:
        """Categorize content type (without hardcoding)"""
        content_lower = content.lower()
        
        # These are hints, not rules - AI will interpret
        if any(x in content_lower for x in ['video', 'youtube', 'netflix', 'watch']):
            return "media"
        elif any(x in content_lower for x in ['.py', '.js', '.java', 'code', 'github']):
            return "development"
        elif any(x in content_lower for x in ['gmail', 'outlook', 'email']):
            return "communication"
        elif any(x in content_lower for x in ['docs', 'sheets', 'notion', 'word']):
            return "documentation"
        else:
            return "other"
    
    def _detect_waiting_pattern(self, switch: SwitchEvent, situation: SituationContext):
        """Learn waiting patterns from behavior"""
        if switch.prior_action and situation.waiting_indicators:
            key = f"{switch.from_app}:{switch.prior_action}"
            
            # Track how long user typically waits after this action
            if key not in self.waiting_patterns:
                self.waiting_patterns[key] = []
            
            self.waiting_patterns[key].append(switch.session_duration)
            
            # Keep only recent data
            if len(self.waiting_patterns[key]) > 50:
                self.waiting_patterns[key] = self.waiting_patterns[key][-50:]
    
    def get_pattern_summary(self) -> Dict:
        """Get summary of detected patterns for AI interpretation"""
        summary = {
            'dimensions': {},
            'waiting_patterns': {},
            'recent_situations': [],
            'behavioral_metrics': {}
        }
        
        # Dimensional summaries
        for dim_name, dimension in self.dimensions.items():
            summary['dimensions'][dim_name.value] = dimension.get_pattern_summary()
        
        # Waiting patterns
        for key, durations in self.waiting_patterns.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                summary['waiting_patterns'][key] = {
                    'average_wait': avg_duration,
                    'occurrences': len(durations)
                }
        
        # Recent situations (for context)
        for situation in list(self.situation_history)[-10:]:
            summary['recent_situations'].append({
                'fingerprint': situation.to_fingerprint(),
                'time': situation.time_of_day,
                'energy': situation.energy_level,
                'velocity': situation.switching_velocity,
                'waiting': bool(situation.waiting_indicators),
                'multitask': bool(situation.multitask_indicators)
            })
        
        # Overall behavioral metrics
        if self.situation_history:
            recent = list(self.situation_history)[-50:]
            summary['behavioral_metrics'] = {
                'avg_switching_velocity': sum(s.switching_velocity for s in recent) / len(recent),
                'avg_session_depth': sum(s.session_depth for s in recent) / len(recent),
                'avg_bounce_rate': sum(s.bounce_rate for s in recent) / len(recent),
                'waiting_percentage': len([s for s in recent if s.waiting_indicators]) / len(recent),
                'multitask_percentage': len([s for s in recent if s.multitask_indicators]) / len(recent)
            }
        
        return summary
    
    def add_user_example(self, pattern: str, interpretation: str, context: Dict):
        """Add user-specific example for AI to learn from"""
        self.user_examples.append({
            'pattern': pattern,
            'interpretation': interpretation,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_ai_context(self) -> str:
        """Get context string for AI interpretation"""
        context = "User behavior patterns:\n\n"
        
        # Add user examples
        for example in self.user_examples[-10:]:  # Last 10 examples
            context += f"Pattern: {example['pattern']}\n"
            context += f"Interpretation: {example['interpretation']}\n"
            context += f"Context: {json.dumps(example['context'], indent=2)}\n\n"
        
        # Add learned waiting patterns
        if self.waiting_patterns:
            context += "Learned waiting patterns:\n"
            for key, durations in list(self.waiting_patterns.items())[:10]:
                avg = sum(durations) / len(durations) if durations else 0
                context += f"- After '{key}': typically waits {avg:.1f} seconds\n"
            context += "\n"
        
        # Add behavioral summary
        summary = self.get_pattern_summary()
        if summary['behavioral_metrics']:
            context += "Behavioral metrics:\n"
            metrics = summary['behavioral_metrics']
            context += f"- Average switching velocity: {metrics['avg_switching_velocity']:.1f} switches/min\n"
            context += f"- Waiting patterns: {metrics['waiting_percentage']*100:.1f}% of switches\n"
            context += f"- Multitasking: {metrics['multitask_percentage']*100:.1f}% of time\n"
        
        return context