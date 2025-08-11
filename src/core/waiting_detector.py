"""
Waiting Pattern Detector
Identifies productive waiting periods and suggests appropriate activities
Learns from user behavior without hardcoding specific tools
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import json


@dataclass
class WaitingContext:
    """Context about a waiting period"""
    trigger_app: str
    trigger_action: str
    expected_duration: float  # seconds
    confidence: float  # 0-1
    actual_duration: Optional[float] = None
    fill_activity: Optional[str] = None
    was_productive: Optional[bool] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WaitingPattern:
    """Learned waiting pattern"""
    trigger: str  # app:action combination
    durations: List[float]  # Historical durations
    fill_activities: List[str]  # What user does while waiting
    success_rate: float  # How often waiting was productive
    
    @property
    def average_duration(self) -> float:
        return statistics.mean(self.durations) if self.durations else 0
    
    @property
    def median_duration(self) -> float:
        return statistics.median(self.durations) if self.durations else 0
    
    @property
    def duration_variance(self) -> float:
        return statistics.stdev(self.durations) if len(self.durations) > 1 else 0


@dataclass
class ActivitySuggestion:
    """Suggested activity for a waiting period"""
    activity_type: str
    specific_apps: List[str]
    duration_range: Tuple[float, float]  # min, max seconds
    rationale: str
    examples: List[str]


class WaitingDetector:
    """
    Detects and optimizes productive waiting periods
    Learns from behavior, doesn't hardcode specific tools
    """
    
    def __init__(self):
        self.waiting_patterns = {}  # key: trigger, value: WaitingPattern
        self.current_waits = {}  # Active waiting periods
        self.activity_library = self._init_activity_library()
        self.user_preferences = defaultdict(list)
        self.learning_enabled = True
        
    def _init_activity_library(self) -> Dict[str, ActivitySuggestion]:
        """Initialize library of activities for different wait durations"""
        return {
            'micro': ActivitySuggestion(
                activity_type='glance',
                specific_apps=['notification_center'],
                duration_range=(0, 5),
                rationale='Too short to context switch',
                examples=['Check notification badges', 'Glance at clock']
            ),
            'mini': ActivitySuggestion(
                activity_type='quick_check',
                specific_apps=['messages', 'email_preview'],
                duration_range=(5, 30),
                rationale='Perfect for quick status checks',
                examples=['Read Slack message', 'Check email subject lines']
            ),
            'short': ActivitySuggestion(
                activity_type='quick_task',
                specific_apps=['messages', 'notes'],
                duration_range=(30, 120),
                rationale='Enough time for a quick response',
                examples=['Reply to message', 'Add quick note', 'Review todo']
            ),
            'medium': ActivitySuggestion(
                activity_type='secondary_task',
                specific_apps=['browser', 'documentation'],
                duration_range=(120, 300),
                rationale='Time for meaningful secondary work',
                examples=['Read article section', 'Code review', 'Email draft']
            ),
            'long': ActivitySuggestion(
                activity_type='context_switch',
                specific_apps=['any'],
                duration_range=(300, float('inf')),
                rationale='Worth full context switch',
                examples=['Different project', 'Deep work on other task']
            )
        }
    
    def detect_waiting_trigger(self, app: str, action: str, context: Dict) -> Optional[WaitingContext]:
        """
        Detect if an action will trigger a waiting period
        """
        
        # Check for explicit waiting indicators (learned, not hardcoded)
        waiting_indicators = self._extract_waiting_indicators(app, action, context)
        
        if not waiting_indicators:
            return None
        
        # Create trigger key
        trigger_key = f"{app}:{action}"
        
        # Check if we've seen this pattern before
        if trigger_key in self.waiting_patterns:
            pattern = self.waiting_patterns[trigger_key]
            expected_duration = pattern.median_duration
            confidence = self._calculate_confidence(pattern)
        else:
            # New pattern - make educated guess
            expected_duration = self._estimate_duration(action, context)
            confidence = 0.3  # Low confidence for new patterns
        
        waiting_context = WaitingContext(
            trigger_app=app,
            trigger_action=action,
            expected_duration=expected_duration,
            confidence=confidence,
            metadata=context
        )
        
        # Track active wait
        self.current_waits[trigger_key] = {
            'context': waiting_context,
            'start_time': datetime.now()
        }
        
        return waiting_context
    
    def _extract_waiting_indicators(self, app: str, action: str, context: Dict) -> List[str]:
        """Extract indicators that suggest waiting (learned from patterns)"""
        indicators = []
        
        action_lower = action.lower()
        
        # These are initial hints - system learns more over time
        waiting_keywords = [
            # Development
            'build', 'compile', 'test', 'deploy', 'install', 'update',
            'generate', 'process', 'analyze', 'run', 'execute',
            # AI/ML
            'claude', 'gpt', 'ai', 'model', 'training', 'inference',
            # Creative
            'render', 'export', 'encode', 'convert', 'compress',
            # Data
            'query', 'fetch', 'load', 'import', 'sync', 'backup',
            # Communication
            'send', 'upload', 'download', 'transfer'
        ]
        
        for keyword in waiting_keywords:
            if keyword in action_lower:
                indicators.append(f"keyword_{keyword}")
        
        # Check context for additional signals
        if context:
            # File size operations
            if 'file_size' in context and context['file_size'] > 1000000:  # > 1MB
                indicators.append('large_file_operation')
            
            # Network operations
            if 'network_operation' in context:
                indicators.append('network_wait')
            
            # Previous behavior
            if 'switch_after' in context and context['switch_after']:
                indicators.append('historical_switch_pattern')
        
        return indicators
    
    def _estimate_duration(self, action: str, context: Dict) -> float:
        """Estimate wait duration for new patterns"""
        
        action_lower = action.lower()
        
        # Initial estimates (will be refined through learning)
        if 'ai' in action_lower or 'claude' in action_lower or 'gpt' in action_lower:
            return 30.0  # AI responses typically 10-60s
        elif 'build' in action_lower or 'compile' in action_lower:
            return 45.0  # Builds vary widely
        elif 'test' in action_lower:
            return 60.0  # Test suites vary
        elif 'deploy' in action_lower:
            return 180.0  # Deployments typically longer
        elif 'render' in action_lower or 'export' in action_lower:
            return 120.0  # Media operations
        elif 'query' in action_lower:
            return 10.0  # Database queries
        else:
            return 15.0  # Default guess
    
    def _calculate_confidence(self, pattern: WaitingPattern) -> float:
        """Calculate confidence in duration prediction"""
        
        if not pattern.durations:
            return 0.0
        
        # Factors affecting confidence
        sample_size = len(pattern.durations)
        variance = pattern.duration_variance
        avg_duration = pattern.average_duration
        
        # More samples = higher confidence
        size_factor = min(1.0, sample_size / 20)
        
        # Lower variance = higher confidence
        if avg_duration > 0:
            variance_factor = max(0, 1 - (variance / avg_duration))
        else:
            variance_factor = 0
        
        # Recent consistency
        if len(pattern.durations) >= 3:
            recent = pattern.durations[-3:]
            recent_variance = statistics.stdev(recent) if len(recent) > 1 else 0
            recent_avg = statistics.mean(recent)
            if recent_avg > 0:
                consistency_factor = max(0, 1 - (recent_variance / recent_avg))
            else:
                consistency_factor = 0
        else:
            consistency_factor = 0.5
        
        # Weighted confidence
        confidence = (size_factor * 0.3 + 
                     variance_factor * 0.4 + 
                     consistency_factor * 0.3)
        
        return min(1.0, max(0.0, confidence))
    
    def record_wait_completion(self, app: str, action: str, actual_duration: float, 
                              fill_activity: Optional[str] = None, 
                              was_productive: bool = True):
        """Record completion of a waiting period for learning"""
        
        trigger_key = f"{app}:{action}"
        
        # Update or create pattern
        if trigger_key not in self.waiting_patterns:
            self.waiting_patterns[trigger_key] = WaitingPattern(
                trigger=trigger_key,
                durations=[],
                fill_activities=[],
                success_rate=1.0
            )
        
        pattern = self.waiting_patterns[trigger_key]
        
        # Update pattern data
        pattern.durations.append(actual_duration)
        if fill_activity:
            pattern.fill_activities.append(fill_activity)
        
        # Keep only recent data (last 50 observations)
        if len(pattern.durations) > 50:
            pattern.durations = pattern.durations[-50:]
        if len(pattern.fill_activities) > 50:
            pattern.fill_activities = pattern.fill_activities[-50:]
        
        # Update success rate
        if len(pattern.durations) > 1:
            success_count = sum(1 for _ in pattern.fill_activities if was_productive)
            pattern.success_rate = success_count / len(pattern.fill_activities) if pattern.fill_activities else 1.0
        
        # Remove from active waits
        if trigger_key in self.current_waits:
            del self.current_waits[trigger_key]
        
        # Learn user preferences
        if fill_activity and was_productive:
            duration_category = self._categorize_duration(actual_duration)
            self.user_preferences[duration_category].append(fill_activity)
    
    def _categorize_duration(self, duration: float) -> str:
        """Categorize duration into activity types"""
        for category, suggestion in self.activity_library.items():
            if suggestion.duration_range[0] <= duration < suggestion.duration_range[1]:
                return category
        return 'long'
    
    def suggest_activity(self, waiting_context: WaitingContext) -> ActivitySuggestion:
        """Suggest appropriate activity for waiting period"""
        
        duration = waiting_context.expected_duration
        category = self._categorize_duration(duration)
        base_suggestion = self.activity_library[category]
        
        # Personalize based on user preferences
        if category in self.user_preferences and self.user_preferences[category]:
            # Get most common activities for this duration
            from collections import Counter
            activity_counts = Counter(self.user_preferences[category])
            preferred_apps = [app for app, _ in activity_counts.most_common(3)]
            
            # Create personalized suggestion
            return ActivitySuggestion(
                activity_type=base_suggestion.activity_type,
                specific_apps=preferred_apps,
                duration_range=base_suggestion.duration_range,
                rationale=f"Based on your patterns: {base_suggestion.rationale}",
                examples=[f"You often: {app}" for app in preferred_apps[:2]]
            )
        
        return base_suggestion
    
    def get_active_waits(self) -> List[Tuple[str, WaitingContext, float]]:
        """Get all active waiting periods with elapsed time"""
        active = []
        now = datetime.now()
        
        for trigger_key, wait_info in self.current_waits.items():
            context = wait_info['context']
            elapsed = (now - wait_info['start_time']).total_seconds()
            active.append((trigger_key, context, elapsed))
        
        return active
    
    def predict_wait_end(self, trigger_key: str) -> Optional[Tuple[float, float]]:
        """Predict when a wait will end (remaining_time, confidence)"""
        
        if trigger_key not in self.current_waits:
            return None
        
        wait_info = self.current_waits[trigger_key]
        context = wait_info['context']
        elapsed = (datetime.now() - wait_info['start_time']).total_seconds()
        
        remaining = max(0, context.expected_duration - elapsed)
        
        return (remaining, context.confidence)
    
    def analyze_waiting_patterns(self) -> Dict[str, Any]:
        """Analyze overall waiting patterns"""
        
        analysis = {
            'total_patterns': len(self.waiting_patterns),
            'total_wait_time': 0,
            'productive_wait_percentage': 0,
            'common_triggers': [],
            'optimal_activities': {},
            'learning_insights': []
        }
        
        if not self.waiting_patterns:
            return analysis
        
        # Calculate total wait time
        total_duration = sum(
            sum(pattern.durations) 
            for pattern in self.waiting_patterns.values()
        )
        analysis['total_wait_time'] = total_duration
        
        # Calculate productive percentage
        productive_patterns = [
            p for p in self.waiting_patterns.values() 
            if p.success_rate > 0.7
        ]
        analysis['productive_wait_percentage'] = (
            len(productive_patterns) / len(self.waiting_patterns) * 100
        )
        
        # Find common triggers
        sorted_patterns = sorted(
            self.waiting_patterns.items(),
            key=lambda x: len(x[1].durations),
            reverse=True
        )
        
        analysis['common_triggers'] = [
            {
                'trigger': trigger,
                'avg_duration': pattern.average_duration,
                'frequency': len(pattern.durations),
                'success_rate': pattern.success_rate
            }
            for trigger, pattern in sorted_patterns[:5]
        ]
        
        # Optimal activities by duration
        for category in self.activity_library:
            if category in self.user_preferences:
                from collections import Counter
                counts = Counter(self.user_preferences[category])
                if counts:
                    analysis['optimal_activities'][category] = counts.most_common(1)[0][0]
        
        # Learning insights
        if len(self.waiting_patterns) > 5:
            analysis['learning_insights'].append(
                f"Identified {len(self.waiting_patterns)} unique waiting patterns"
            )
        
        # Find patterns with high variance (unpredictable)
        high_variance = [
            trigger for trigger, pattern in self.waiting_patterns.items()
            if pattern.duration_variance > pattern.average_duration * 0.5
            and len(pattern.durations) > 3
        ]
        
        if high_variance:
            analysis['learning_insights'].append(
                f"Unpredictable waits: {', '.join(high_variance[:3])}"
            )
        
        return analysis
    
    def export_patterns(self) -> str:
        """Export learned patterns for sharing/backup"""
        
        export_data = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'patterns': {},
            'preferences': dict(self.user_preferences)
        }
        
        for trigger, pattern in self.waiting_patterns.items():
            export_data['patterns'][trigger] = {
                'average_duration': pattern.average_duration,
                'median_duration': pattern.median_duration,
                'sample_count': len(pattern.durations),
                'success_rate': pattern.success_rate,
                'common_activities': list(set(pattern.fill_activities))[:5]
            }
        
        return json.dumps(export_data, indent=2)
    
    def import_patterns(self, json_data: str):
        """Import patterns from export"""
        
        data = json.loads(json_data)
        
        # Import patterns
        for trigger, pattern_data in data.get('patterns', {}).items():
            if trigger not in self.waiting_patterns:
                self.waiting_patterns[trigger] = WaitingPattern(
                    trigger=trigger,
                    durations=[pattern_data['median_duration']] * min(5, pattern_data.get('sample_count', 1)),
                    fill_activities=pattern_data.get('common_activities', []),
                    success_rate=pattern_data.get('success_rate', 0.8)
                )
        
        # Import preferences
        for category, activities in data.get('preferences', {}).items():
            self.user_preferences[category].extend(activities)