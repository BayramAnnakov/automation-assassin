"""
Situation Fingerprinting System
Creates rich, interpretable descriptions of work situations without judgment
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import re


@dataclass
class WorkSituation:
    """
    Represents a work situation without judgment
    Just facts that AI can interpret
    """
    # Core context
    timestamp: datetime
    primary_app: str
    primary_content: Optional[str]
    
    # Action context
    recent_action: Optional[str]  # What just happened
    next_action: Optional[str]  # What happened next
    action_duration: float  # How long the action took
    
    # Environmental context
    other_apps_open: List[str]
    browser_tabs: List[str]
    time_context: Dict[str, Any]
    
    # Behavioral signals
    switching_pattern: str  # rapid, moderate, slow
    attention_pattern: str  # focused, divided, scattered
    return_pattern: bool  # Did they come back quickly?
    
    # Content signals
    content_type: str  # work, entertainment, communication, mixed
    content_relationship: str  # related, unrelated, partially-related
    
    # System signals
    system_state: Dict[str, Any]  # CPU usage, memory, active processes
    
    def describe(self) -> str:
        """Generate human-readable description"""
        desc = f"At {self.timestamp.strftime('%H:%M')}, "
        desc += f"user in {self.primary_app}"
        
        if self.primary_content:
            desc += f" ({self.primary_content[:30]}...)"
        
        if self.recent_action:
            desc += f", after {self.recent_action}"
        
        if self.switching_pattern == "rapid":
            desc += ", rapidly switching"
        elif self.attention_pattern == "divided":
            desc += ", with divided attention"
        
        return desc
    
    def to_ai_prompt(self) -> str:
        """Create prompt for AI interpretation"""
        prompt = "Interpret this work situation:\n\n"
        prompt += f"Time: {self.timestamp.strftime('%A %H:%M')}\n"
        prompt += f"Current app: {self.primary_app}\n"
        
        if self.primary_content:
            prompt += f"Working on: {self.primary_content}\n"
        
        if self.recent_action:
            prompt += f"Just did: {self.recent_action}\n"
        
        if self.other_apps_open:
            prompt += f"Also open: {', '.join(self.other_apps_open[:5])}\n"
        
        prompt += f"Switching pattern: {self.switching_pattern}\n"
        prompt += f"Attention: {self.attention_pattern}\n"
        
        if self.return_pattern:
            prompt += "User quickly returned to previous app\n"
        
        prompt += "\nIs this productive behavior? What's likely happening?"
        
        return prompt


class SituationFingerprinter:
    """
    Creates detailed situation fingerprints without making judgments
    Provides rich context for AI interpretation
    """
    
    def __init__(self):
        self.situation_cache = {}
        self.pattern_library = self._initialize_pattern_library()
    
    def _initialize_pattern_library(self) -> Dict:
        """Initialize pattern recognition library (hints, not rules)"""
        return {
            'waiting_signals': [
                'claude_processing',
                'build_running',
                'test_executing',
                'deployment_active',
                'render_in_progress',
                'upload_pending',
                'query_running',
                'compilation_active'
            ],
            'productive_signals': [
                'consistent_app_group',
                'deep_sessions',
                'related_content',
                'goal_oriented_sequence'
            ],
            'stress_signals': [
                'rapid_shallow_switches',
                'no_completion_pattern',
                'comfort_app_seeking',
                'irregular_timing'
            ]
        }
    
    def fingerprint_situation(self, 
                            current_app: str,
                            current_content: Optional[str],
                            recent_events: List[Dict],
                            system_state: Optional[Dict] = None) -> WorkSituation:
        """
        Create a detailed fingerprint of the current work situation
        """
        
        # Analyze recent events
        recent_action = self._extract_recent_action(recent_events)
        next_action = self._predict_next_action(recent_events)
        action_duration = self._calculate_action_duration(recent_events)
        
        # Analyze environment
        other_apps = self._extract_other_apps(recent_events)
        browser_tabs = self._extract_browser_tabs(current_content, recent_events)
        time_context = self._create_time_context()
        
        # Analyze behavior
        switching_pattern = self._analyze_switching_pattern(recent_events)
        attention_pattern = self._analyze_attention_pattern(recent_events)
        return_pattern = self._detect_return_pattern(recent_events)
        
        # Analyze content
        content_type = self._categorize_content_type(current_content, current_app)
        content_relationship = self._analyze_content_relationship(recent_events)
        
        # System state
        if not system_state:
            system_state = self._get_basic_system_state()
        
        situation = WorkSituation(
            timestamp=datetime.now(),
            primary_app=current_app,
            primary_content=current_content,
            recent_action=recent_action,
            next_action=next_action,
            action_duration=action_duration,
            other_apps_open=other_apps,
            browser_tabs=browser_tabs,
            time_context=time_context,
            switching_pattern=switching_pattern,
            attention_pattern=attention_pattern,
            return_pattern=return_pattern,
            content_type=content_type,
            content_relationship=content_relationship,
            system_state=system_state
        )
        
        # Cache for pattern recognition
        cache_key = f"{current_app}:{datetime.now().hour}"
        self.situation_cache[cache_key] = situation
        
        return situation
    
    def _extract_recent_action(self, events: List[Dict]) -> Optional[str]:
        """Extract the most recent significant action"""
        if not events:
            return None
        
        recent = events[-1] if events else None
        if not recent:
            return None
        
        # Look for action indicators
        if 'action' in recent:
            return recent['action']
        
        # Infer from app switches
        if 'from_app' in recent and 'to_app' in recent:
            from_app = recent['from_app']
            
            # Check for waiting patterns
            if 'IDE' in from_app or 'Code' in from_app:
                for signal in self.pattern_library['waiting_signals']:
                    if signal in str(recent.get('metadata', {})).lower():
                        return f"initiated_{signal}"
            
            return f"switched_from_{from_app}"
        
        return None
    
    def _predict_next_action(self, events: List[Dict]) -> Optional[str]:
        """Predict likely next action based on patterns"""
        if len(events) < 3:
            return None
        
        # Look for repetitive patterns
        recent_apps = [e.get('to_app', '') for e in events[-5:] if 'to_app' in e]
        if len(recent_apps) >= 3:
            # Check for A-B-A pattern
            if recent_apps[-3] == recent_apps[-1]:
                return f"likely_return_to_{recent_apps[-2]}"
        
        return None
    
    def _calculate_action_duration(self, events: List[Dict]) -> float:
        """Calculate duration of recent action"""
        if not events:
            return 0.0
        
        recent = events[-1]
        return recent.get('duration', 0.0)
    
    def _extract_other_apps(self, events: List[Dict]) -> List[str]:
        """Extract other apps that are open"""
        apps = set()
        
        # Look at recent events (last 10 minutes)
        for event in events[-50:]:
            if 'from_app' in event:
                apps.add(event['from_app'])
            if 'to_app' in event:
                apps.add(event['to_app'])
        
        return list(apps)
    
    def _extract_browser_tabs(self, content: Optional[str], events: List[Dict]) -> List[str]:
        """Extract browser tab information"""
        tabs = []
        
        if content and 'http' in content.lower():
            tabs.append(content)
        
        # Look for browser-related content in recent events
        for event in events[-10:]:
            if 'content' in event and event['content']:
                if 'http' in event['content'].lower() or 'www' in event['content'].lower():
                    tabs.append(event['content'])
        
        # Deduplicate while preserving order
        seen = set()
        unique_tabs = []
        for tab in tabs:
            if tab not in seen:
                seen.add(tab)
                unique_tabs.append(tab)
        
        return unique_tabs[:10]  # Limit to 10 most recent
    
    def _create_time_context(self) -> Dict[str, Any]:
        """Create temporal context"""
        now = datetime.now()
        
        return {
            'time': now.strftime('%H:%M'),
            'day': now.strftime('%A'),
            'hour': now.hour,
            'period': self._get_time_period(now.hour),
            'is_weekend': now.weekday() >= 5,
            'is_evening': now.hour >= 18,
            'is_late_night': now.hour >= 22 or now.hour < 5
        }
    
    def _get_time_period(self, hour: int) -> str:
        """Categorize time period"""
        if 5 <= hour < 9:
            return "early_morning"
        elif 9 <= hour < 12:
            return "morning"
        elif 12 <= hour < 14:
            return "lunch"
        elif 14 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 20:
            return "evening"
        elif 20 <= hour < 23:
            return "late_evening"
        else:
            return "night"
    
    def _analyze_switching_pattern(self, events: List[Dict]) -> str:
        """Analyze the switching pattern"""
        if len(events) < 3:
            return "insufficient_data"
        
        # Count switches in last 5 minutes
        recent_switches = len([e for e in events[-20:] if 'to_app' in e])
        
        if recent_switches > 15:
            return "rapid"
        elif recent_switches > 8:
            return "moderate"
        elif recent_switches > 3:
            return "occasional"
        else:
            return "minimal"
    
    def _analyze_attention_pattern(self, events: List[Dict]) -> str:
        """Analyze attention distribution"""
        if not events:
            return "unknown"
        
        # Look at session durations
        durations = [e.get('duration', 0) for e in events[-10:] if 'duration' in e]
        if not durations:
            return "unknown"
        
        avg_duration = sum(durations) / len(durations)
        
        if avg_duration > 300:  # > 5 minutes average
            return "focused"
        elif avg_duration > 60:  # > 1 minute average
            return "moderate"
        elif avg_duration > 10:  # > 10 seconds average
            return "divided"
        else:
            return "scattered"
    
    def _detect_return_pattern(self, events: List[Dict]) -> bool:
        """Detect if user returns to apps quickly"""
        if len(events) < 3:
            return False
        
        # Check for A→B→A pattern in last 3 events
        recent = events[-3:]
        if len(recent) == 3:
            if 'to_app' in recent[0] and 'to_app' in recent[2]:
                return recent[0]['to_app'] == recent[2]['to_app']
        
        return False
    
    def _categorize_content_type(self, content: Optional[str], app: str) -> str:
        """Categorize content type (flexible, not rigid)"""
        if not content and not app:
            return "unknown"
        
        combined = f"{app} {content or ''}".lower()
        
        # These are hints for AI, not rigid rules
        if any(x in combined for x in ['youtube', 'netflix', 'video', 'watch', 'movie']):
            return "entertainment"
        elif any(x in combined for x in ['code', 'ide', 'github', 'terminal', 'localhost']):
            return "development"
        elif any(x in combined for x in ['slack', 'teams', 'discord', 'telegram', 'whatsapp']):
            return "communication"
        elif any(x in combined for x in ['docs', 'sheets', 'word', 'excel', 'notion']):
            return "documentation"
        elif any(x in combined for x in ['gmail', 'outlook', 'mail']):
            return "email"
        else:
            return "mixed"
    
    def _analyze_content_relationship(self, events: List[Dict]) -> str:
        """Analyze if content across apps is related"""
        if len(events) < 2:
            return "unknown"
        
        # Extract content types from recent events
        content_types = []
        for event in events[-5:]:
            if 'content' in event or 'to_app' in event:
                content_type = self._categorize_content_type(
                    event.get('content'),
                    event.get('to_app', '')
                )
                content_types.append(content_type)
        
        # Check consistency
        unique_types = set(content_types)
        if len(unique_types) == 1:
            return "highly_related"
        elif len(unique_types) == 2:
            return "partially_related"
        else:
            return "unrelated"
    
    def _get_basic_system_state(self) -> Dict[str, Any]:
        """Get basic system state (would be enhanced with real system data)"""
        return {
            'timestamp': datetime.now().isoformat(),
            'inferred_load': 'normal',  # Would use actual CPU/memory data
            'active_process_count': 'unknown'
        }
    
    def compare_situations(self, situation1: WorkSituation, situation2: WorkSituation) -> float:
        """
        Compare two situations for similarity (0-1 score)
        Useful for pattern matching and learning
        """
        similarity_score = 0.0
        weights = {
            'app': 0.2,
            'content_type': 0.15,
            'time_context': 0.15,
            'switching_pattern': 0.15,
            'attention_pattern': 0.15,
            'content_relationship': 0.1,
            'return_pattern': 0.1
        }
        
        # Compare apps
        if situation1.primary_app == situation2.primary_app:
            similarity_score += weights['app']
        
        # Compare content types
        if situation1.content_type == situation2.content_type:
            similarity_score += weights['content_type']
        
        # Compare time context
        if situation1.time_context['period'] == situation2.time_context['period']:
            similarity_score += weights['time_context'] * 0.5
        if situation1.time_context['is_weekend'] == situation2.time_context['is_weekend']:
            similarity_score += weights['time_context'] * 0.5
        
        # Compare patterns
        if situation1.switching_pattern == situation2.switching_pattern:
            similarity_score += weights['switching_pattern']
        
        if situation1.attention_pattern == situation2.attention_pattern:
            similarity_score += weights['attention_pattern']
        
        if situation1.content_relationship == situation2.content_relationship:
            similarity_score += weights['content_relationship']
        
        if situation1.return_pattern == situation2.return_pattern:
            similarity_score += weights['return_pattern']
        
        return similarity_score
    
    def get_situation_insights(self, situation: WorkSituation) -> Dict[str, Any]:
        """
        Get insights about a situation (for AI context)
        """
        insights = {
            'description': situation.describe(),
            'key_signals': [],
            'possible_interpretations': []
        }
        
        # Identify key signals
        if situation.switching_pattern == "rapid":
            insights['key_signals'].append("rapid_switching")
        
        if situation.return_pattern:
            insights['key_signals'].append("quick_return_pattern")
        
        if situation.attention_pattern == "scattered":
            insights['key_signals'].append("scattered_attention")
        elif situation.attention_pattern == "focused":
            insights['key_signals'].append("deep_focus")
        
        if situation.time_context['is_evening'] and situation.content_type == "entertainment":
            insights['key_signals'].append("evening_entertainment")
        
        # Suggest possible interpretations (AI will refine)
        if situation.recent_action and any(signal in situation.recent_action for signal in self.pattern_library['waiting_signals']):
            insights['possible_interpretations'].append("productive_waiting")
        
        if situation.switching_pattern == "rapid" and situation.attention_pattern == "scattered":
            insights['possible_interpretations'].append("possible_cognitive_overload")
        
        if situation.time_context['is_late_night'] and situation.content_type == "entertainment":
            insights['possible_interpretations'].append("intentional_multitasking")
        
        return insights