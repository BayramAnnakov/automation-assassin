"""
Pattern Context Analyzer - AI-Powered Pattern Classification
Uses AI sub-agents to intelligently analyze app switching patterns
Now enhanced with browser history context for better accuracy
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
from .browser_history_reader import BrowserHistoryReader

@dataclass
class PatternContext:
    """Contextual information about a pattern from AI analysis"""
    pattern_type: str  # Main classification from AI
    confidence: float  # 0-100
    reasoning: str
    indicators: List[str]
    suggested_interventions: List[str]
    alternative_hypotheses: List[Dict]
    is_productive: bool
    
class PatternContextAnalyzer:
    """
    Flexible pattern analyzer that delegates to AI for intelligent interpretation.
    Works for any user type - developers, designers, writers, traders, students, etc.
    """
    
    def __init__(self, user_profile: Optional[Dict] = None):
        """
        Initialize with optional user profile from context-learner
        
        Args:
            user_profile: Pre-loaded user profile from context-learner agent
        """
        self.user_profile = user_profile or self._get_default_profile()
        self.analysis_cache = {}
        self.browser_reader = BrowserHistoryReader()
        
    def _get_default_profile(self) -> Dict:
        """Get a default user profile when none is provided"""
        return {
            'profession': 'unknown',
            'productive_apps': [],
            'distraction_apps': [],
            'work_hours': '9-17',
            'peak_productivity': '10-12',
            'common_workflows': []
        }
    
    def analyze_pattern(self, app_a: str, app_b: str, 
                       occurrences: int, avg_gap_seconds: float,
                       total_time_lost: float = 0,
                       work_hour_percentage: float = 50,
                       peak_hours: Optional[List[int]] = None) -> PatternContext:
        """
        Analyze a pattern using AI pattern-interpreter agent
        
        Args:
            app_a: First app in the pattern
            app_b: Second app in the pattern
            occurrences: Number of times this pattern occurred
            avg_gap_seconds: Average time between switches
            total_time_lost: Total time in this pattern (seconds)
            work_hour_percentage: Percentage during work hours
            peak_hours: Hours when pattern is most common
            
        Returns:
            PatternContext with AI-generated classification
        """
        
        # Create cache key
        cache_key = f"{app_a}|{app_b}|{datetime.now().hour}"
        
        # Check cache (valid for 1 hour)
        if cache_key in self.analysis_cache:
            cached = self.analysis_cache[cache_key]
            if cached.get('timestamp', 0) > datetime.now().timestamp() - 3600:
                return self._parse_ai_response(cached['response'])
        
        # Prepare input for AI agent
        current_hour = datetime.now().hour
        
        # Get browser context if one of the apps is a browser
        browser_context = self._get_browser_context(app_a, app_b)
        
        pattern_data = {
            'pattern': {
                'app_a': app_a,
                'app_b': app_b,
                'occurrences': occurrences,
                'avg_gap_seconds': avg_gap_seconds,
                'total_time_lost': total_time_lost,
                'work_hour_percentage': work_hour_percentage,
                'peak_hours': peak_hours or [],
                'current_hour': current_hour
            },
            'user_profile': self.user_profile,
            'browser_context': browser_context  # Add browser history context
        }
        
        # Call pattern-interpreter agent (simulated here - in production would use Task tool)
        ai_response = self._call_pattern_interpreter(pattern_data)
        
        # Cache the response
        self.analysis_cache[cache_key] = {
            'response': ai_response,
            'timestamp': datetime.now().timestamp()
        }
        
        return self._parse_ai_response(ai_response)
    
    def _get_browser_context(self, app_a: str, app_b: str) -> Optional[Dict]:
        """
        Get browser history context if one of the apps is a browser
        
        Args:
            app_a: First app
            app_b: Second app
            
        Returns:
            Browser context dictionary or None
        """
        browsers = ['safari', 'chrome', 'firefox', 'brave', 'edge']
        
        # Check if either app is a browser
        browser_app = None
        for app in [app_a, app_b]:
            if any(browser in app.lower() for browser in browsers):
                browser_app = app
                break
        
        if not browser_app:
            return None
            
        # Get browser history for recent window
        try:
            context = self.browser_reader.get_pattern_browser_context(
                app_a=app_a,
                app_b=app_b,
                pattern_time=datetime.now(),
                window_minutes=10
            )
            return context if context else None
        except Exception as e:
            print(f"Could not get browser context: {e}")
            return None
    
    def _call_pattern_interpreter(self, pattern_data: Dict) -> Dict:
        """
        Call the pattern-interpreter AI agent
        
        In production, this would use the Task tool to invoke the agent.
        For now, returns a simulated response structure.
        
        Args:
            pattern_data: Pattern and user profile data
            
        Returns:
            AI agent's analysis response
        """
        
        # In production:
        # from claude_code import Task
        # response = Task(
        #     subagent_type="pattern-interpreter",
        #     description="Analyze app switching pattern",
        #     prompt=json.dumps(pattern_data)
        # )
        
        # Simulated intelligent response based on pattern characteristics
        app_a = pattern_data['pattern']['app_a']
        app_b = pattern_data['pattern']['app_b']
        avg_gap = pattern_data['pattern']['avg_gap_seconds']
        current_hour = pattern_data['pattern']['current_hour']
        browser_context = pattern_data.get('browser_context', {})
        
        # Enhanced AI reasoning with browser context
        if browser_context and (browser_context.get('history') or browser_context.get('top_domains')):
            # Analyze browser history for better classification
            domains = browser_context.get('top_domains', [])
            
            # Check for development patterns
            if any('localhost' in d['domain'] for d in domains):
                primary_type = 'testing_workflow'
                confidence = 90
                reasoning = "Local development detected - testing web application"
                is_productive = True
            # Check for documentation/learning
            elif any('stackoverflow' in d['domain'] or 'docs' in d['domain'] for d in domains):
                primary_type = 'debugging' if 'stackoverflow' in str(domains) else 'research'
                confidence = 85
                reasoning = f"Accessing technical documentation and Q&A sites"
                is_productive = True
            # Check for social media
            elif any(social in str(domains).lower() for social in ['reddit', 'twitter', 'facebook']):
                primary_type = 'distraction' if current_hour < 17 else 'social_browsing'
                confidence = 75
                reasoning = f"Social media browsing {'during work hours' if current_hour < 17 else 'after hours'}"
                is_productive = False if current_hour < 17 else None
            else:
                # General browsing analysis
                primary_type = 'browsing'
                confidence = 60
                reasoning = f"General web browsing - {len(domains)} sites visited"
                is_productive = None
        elif avg_gap < 10:
            # Rapid switching suggests active workflow
            primary_type = 'testing_workflow' if 'browser' in app_b.lower() else 'active_workflow'
            confidence = 70
            reasoning = f"Rapid switching ({avg_gap:.1f}s average) suggests active {primary_type}"
            is_productive = True
        elif avg_gap < 30:
            # Medium switching could be reference checking
            primary_type = 'research' if 'browser' in app_b.lower() else 'reference_checking'
            confidence = 60
            reasoning = f"Medium-paced switching suggests {primary_type}"
            is_productive = True
        elif current_hour >= 21:
            # Late night patterns more likely distraction
            primary_type = 'distraction'
            confidence = 65
            reasoning = "Late evening pattern with slower switching suggests distraction"
            is_productive = False
        else:
            # Default to unknown for unusual patterns
            primary_type = 'unknown'
            confidence = 40
            reasoning = "Pattern requires more context to classify accurately"
            is_productive = None
        
        return {
            'primary_classification': {
                'type': primary_type,
                'confidence': confidence,
                'reasoning': reasoning,
                'indicators': [
                    f"Switching every {avg_gap:.1f} seconds on average",
                    f"Pattern occurs at {current_hour}:00",
                    f"Apps involved: {app_a} and {app_b}"
                ]
            },
            'alternative_hypotheses': [
                {
                    'type': 'distraction' if is_productive else 'productive_workflow',
                    'confidence': 100 - confidence,
                    'reasoning': 'Alternative interpretation based on context'
                }
            ],
            'workflow_legitimacy': {
                'is_productive': is_productive,
                'explanation': reasoning
            },
            'intervention_suggestions': self._generate_interventions(
                primary_type, app_a, app_b, is_productive
            )
        }
    
    def _parse_ai_response(self, ai_response: Dict) -> PatternContext:
        """
        Parse AI agent response into PatternContext
        
        Args:
            ai_response: Response from pattern-interpreter agent
            
        Returns:
            PatternContext object
        """
        primary = ai_response.get('primary_classification', {})
        legitimacy = ai_response.get('workflow_legitimacy', {})
        
        return PatternContext(
            pattern_type=primary.get('type', 'unknown'),
            confidence=primary.get('confidence', 50),
            reasoning=primary.get('reasoning', 'Pattern analysis in progress'),
            indicators=primary.get('indicators', []),
            suggested_interventions=ai_response.get('intervention_suggestions', []),
            alternative_hypotheses=ai_response.get('alternative_hypotheses', []),
            is_productive=legitimacy.get('is_productive', False)
        )
    
    def _generate_interventions(self, pattern_type: str, app_a: str, 
                               app_b: str, is_productive: bool) -> List[str]:
        """
        Generate intervention suggestions based on AI classification
        
        Args:
            pattern_type: AI-determined pattern type
            app_a: First app
            app_b: Second app
            is_productive: Whether pattern is productive
            
        Returns:
            List of intervention suggestions
        """
        
        if is_productive:
            # Support productive patterns
            return [
                f"hammerspoon:window_layout:Optimize {app_a} and {app_b} arrangement",
                f"hammerspoon:hotkey:Create quick-switch shortcut",
                f"mcp:workflow-automation:Automate repetitive actions between apps",
                f"hammerspoon:session:Save and restore {pattern_type} workspace"
            ]
        elif is_productive is False:
            # Intervene in unproductive patterns
            return [
                f"hammerspoon:progressive_block:Gradually restrict {app_b}",
                f"hammerspoon:awareness:Notify when entering this pattern",
                f"hammerspoon:delay:Add friction before switching to {app_b}",
                f"hammerspoon:alternative:Suggest productive alternative to {app_b}"
            ]
        else:
            # Monitor unclear patterns
            return [
                f"hammerspoon:analytics:Track time in this pattern",
                f"hammerspoon:prompt:Ask for clarification when pattern detected",
                f"manual:review:Review this pattern manually"
            ]
    
    def update_user_profile(self, profile_update: Dict):
        """
        Update user profile from context-learner
        
        Args:
            profile_update: New or updated user profile information
        """
        self.user_profile.update(profile_update)
        # Clear cache when profile updates
        self.analysis_cache = {}
    
    def batch_analyze(self, patterns: List[Dict]) -> List[tuple]:
        """
        Analyze multiple patterns
        
        Args:
            patterns: List of pattern dictionaries
            
        Returns:
            List of (pattern, context) tuples
        """
        results = []
        
        for pattern in patterns:
            context = self.analyze_pattern(
                app_a=pattern.get('app_a', ''),
                app_b=pattern.get('app_b', ''),
                occurrences=pattern.get('occurrences', 0),
                avg_gap_seconds=pattern.get('avg_gap_seconds', 30),
                total_time_lost=pattern.get('total_time_lost', 0),
                work_hour_percentage=pattern.get('work_hour_percentage', 50),
                peak_hours=pattern.get('peak_hours', [])
            )
            results.append((pattern, context))
        
        return results
    
    def get_pattern_summary(self, pattern_context: PatternContext) -> str:
        """
        Generate a human-friendly summary of the pattern analysis
        
        Args:
            pattern_context: Analyzed pattern context
            
        Returns:
            Formatted summary string
        """
        
        # Emoji map for different pattern types
        emoji_map = {
            'testing_workflow': '🧪',
            'research': '📚',
            'distraction': '🚨',
            'communication': '💬',
            'creative': '🎨',
            'monitoring': '📊',
            'active_workflow': '⚡',
            'reference_checking': '🔍',
            'unknown': '❓'
        }
        
        emoji = emoji_map.get(pattern_context.pattern_type, '📱')
        productivity = "✅ Productive" if pattern_context.is_productive else "⚠️ Unproductive"
        
        summary = f"{emoji} **{pattern_context.pattern_type.replace('_', ' ').title()}**\n"
        summary += f"Confidence: {pattern_context.confidence:.0f}%\n"
        summary += f"Status: {productivity}\n"
        summary += f"Reasoning: {pattern_context.reasoning}\n"
        
        if pattern_context.alternative_hypotheses:
            summary += "\nAlternative interpretations:\n"
            for alt in pattern_context.alternative_hypotheses[:2]:
                summary += f"  • {alt['type']}: {alt['confidence']:.0f}% confidence\n"
        
        if pattern_context.indicators:
            summary += "\nKey indicators:\n"
            for indicator in pattern_context.indicators[:3]:
                summary += f"  • {indicator}\n"
        
        return summary


class AIPatternAnalyzer:
    """
    Convenience class for direct AI pattern analysis
    """
    
    def __init__(self):
        self.analyzer = PatternContextAnalyzer()
    
    def analyze(self, app_a: str, app_b: str, **kwargs) -> Dict:
        """
        Simple interface for pattern analysis
        
        Returns dict with classification and suggestions
        """
        context = self.analyzer.analyze_pattern(app_a, app_b, **kwargs)
        
        return {
            'classification': context.pattern_type,
            'confidence': context.confidence,
            'is_productive': context.is_productive,
            'reasoning': context.reasoning,
            'interventions': context.suggested_interventions,
            'alternatives': context.alternative_hypotheses
        }