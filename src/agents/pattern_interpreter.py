"""
AI-Powered Pattern Interpreter
Uses Claude to interpret work patterns with user-specific context
No hardcoded rules - pure AI interpretation based on examples
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.intelligent_pattern_detector import SituationContext, SwitchEvent
from src.core.situation_fingerprint import WorkSituation
from src.core.waiting_detector import WaitingContext


@dataclass
class PatternInterpretation:
    """AI's interpretation of a work pattern"""
    situation_id: str
    interpretation: str
    productivity_assessment: str  # productive, neutral, concerning
    root_cause: Optional[str]
    intervention_needed: bool
    intervention_type: Optional[str]  # gentle, educational, blocking
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]


class PatternInterpreter:
    """
    AI-powered pattern interpreter
    Uses Claude to understand patterns based on user examples
    """
    
    def __init__(self, claude_client=None):
        self.claude_client = claude_client
        self.user_examples = []
        self.interpretation_cache = {}
        self.learning_mode = True
        
    def add_user_example(self, pattern: str, interpretation: str, 
                         is_productive: bool, context: Dict):
        """Add user-specific example for interpretation"""
        self.user_examples.append({
            'pattern': pattern,
            'interpretation': interpretation,
            'is_productive': is_productive,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
    def build_interpretation_prompt(self, situation: SituationContext, 
                                   work_situation: Optional[WorkSituation] = None,
                                   waiting_context: Optional[WaitingContext] = None) -> str:
        """Build prompt for AI interpretation"""
        
        prompt = """You are analyzing a knowledge worker's app switching pattern.
Your task is to interpret whether this behavior is productive, neutral, or concerning.
Consider multitasking, productive waiting, and different work styles.

USER-SPECIFIC CONTEXT AND EXAMPLES:
"""
        
        # Add user examples
        if self.user_examples:
            prompt += "\nThis user has provided these examples of their behavior:\n"
            for ex in self.user_examples[-5:]:  # Last 5 examples
                prompt += f"\nPattern: {ex['pattern']}\n"
                prompt += f"User's interpretation: {ex['interpretation']}\n"
                prompt += f"Productive: {'Yes' if ex['is_productive'] else 'No'}\n"
        
        # Add specific user behaviors we've learned
        prompt += """
KEY INSIGHTS ABOUT THIS USER:
- Watches videos/movies while working (intentional multitasking)
- Switches to Telegram/Browser while waiting for Claude Code/AI to process
- Safari ↔ Telegram pattern (185 times/month) is productive multitasking
- Works in evening hours with entertainment running
- Has rapid switching that looks like distraction but is actually productive waiting

CURRENT SITUATION TO ANALYZE:
"""
        
        # Add current situation details
        prompt += f"\nTimestamp: {situation.timestamp}"
        prompt += f"\nApp: {situation.active_app}"
        if situation.active_content:
            prompt += f"\nContent: {situation.active_content}"
        prompt += f"\nTime of day: {situation.time_of_day}"
        prompt += f"\nDay type: {situation.day_type}"
        prompt += f"\nEnergy level: {situation.energy_level}"
        prompt += f"\nSwitching velocity: {situation.switching_velocity:.1f} switches/min"
        prompt += f"\nSession depth: {situation.session_depth:.1f} seconds avg"
        prompt += f"\nBounce rate: {situation.bounce_rate:.1%}"
        
        if situation.waiting_indicators:
            prompt += f"\nWaiting indicators: {', '.join(situation.waiting_indicators)}"
        if situation.multitask_indicators:
            prompt += f"\nMultitask indicators: {', '.join(situation.multitask_indicators)}"
        
        # Add work situation if available
        if work_situation:
            prompt += f"\n\nAdditional context:"
            prompt += f"\n{work_situation.describe()}"
        
        # Add waiting context if available
        if waiting_context:
            prompt += f"\n\nWaiting context:"
            prompt += f"\nWaiting for: {waiting_context.trigger_action}"
            prompt += f"\nExpected duration: {waiting_context.expected_duration:.0f}s"
            prompt += f"\nConfidence: {waiting_context.confidence:.1%}"
        
        prompt += """

Please analyze this situation and provide:
1. INTERPRETATION: What is likely happening? (one sentence)
2. PRODUCTIVITY: Is this productive/neutral/concerning?
3. ROOT_CAUSE: What's driving this behavior?
4. INTERVENTION: Should we intervene? If yes, how?
5. CONFIDENCE: How confident are you? (0-100%)
6. REASONING: Brief explanation of your analysis

Remember:
- Rapid switching during AI processing is PRODUCTIVE (waiting)
- Evening entertainment + work is INTENTIONAL multitasking
- Quick app checks can be productive status monitoring
- Consider the user's specific patterns and preferences
"""
        
        return prompt
    
    async def interpret_pattern(self, situation: SituationContext,
                               work_situation: Optional[WorkSituation] = None,
                               waiting_context: Optional[WaitingContext] = None) -> PatternInterpretation:
        """Interpret a pattern using AI"""
        
        # Check cache first
        cache_key = situation.to_fingerprint()
        if cache_key in self.interpretation_cache:
            cached = self.interpretation_cache[cache_key]
            # Use cache if less than 1 hour old
            if (datetime.now() - cached['timestamp']).seconds < 3600:
                return cached['interpretation']
        
        # Build prompt
        prompt = self.build_interpretation_prompt(situation, work_situation, waiting_context)
        
        # Simulate AI response (would use actual Claude API in production)
        interpretation = await self._get_ai_interpretation(prompt, situation)
        
        # Cache the interpretation
        self.interpretation_cache[cache_key] = {
            'interpretation': interpretation,
            'timestamp': datetime.now()
        }
        
        return interpretation
    
    async def _get_ai_interpretation(self, prompt: str, situation: SituationContext) -> PatternInterpretation:
        """Get interpretation from AI (simulated for demo)"""
        
        # In production, this would call Claude API
        # For demo, we'll use intelligent heuristics based on learned patterns
        
        interpretation = self._apply_learned_patterns(situation)
        
        return PatternInterpretation(
            situation_id=situation.to_fingerprint(),
            interpretation=interpretation['interpretation'],
            productivity_assessment=interpretation['productivity'],
            root_cause=interpretation['root_cause'],
            intervention_needed=interpretation['intervention_needed'],
            intervention_type=interpretation['intervention_type'],
            confidence=interpretation['confidence'],
            reasoning=interpretation['reasoning'],
            metadata={'situation': situation.__dict__}
        )
    
    def _apply_learned_patterns(self, situation: SituationContext) -> Dict:
        """Apply learned patterns (demo implementation)"""
        
        # Check for productive waiting
        if situation.waiting_indicators:
            if 'waiting_for_ai_query' in situation.waiting_indicators or \
               'waiting_for_claude' in situation.waiting_indicators:
                return {
                    'interpretation': 'Productively filling time while waiting for AI/Claude Code to process',
                    'productivity': 'productive',
                    'root_cause': 'Async work - making use of processing delays',
                    'intervention_needed': False,
                    'intervention_type': None,
                    'confidence': 0.95,
                    'reasoning': 'User switches apps while waiting for AI, which is efficient time use'
                }
        
        # Check for evening multitasking
        if situation.time_of_day in ['evening', 'night'] and situation.multitask_indicators:
            if 'video_multitasking' in situation.multitask_indicators:
                return {
                    'interpretation': 'Intentional multitasking - watching video while working',
                    'productivity': 'productive',
                    'root_cause': 'Personal work style - parallel processing for engagement',
                    'intervention_needed': False,
                    'intervention_type': None,
                    'confidence': 0.9,
                    'reasoning': 'User intentionally watches videos while working in evening'
                }
        
        # Check for rapid but productive switching
        if situation.switching_velocity > 5 and situation.bounce_rate > 0.3:
            if situation.waiting_indicators or situation.multitask_indicators:
                return {
                    'interpretation': 'High-velocity productive switching between related tasks',
                    'productivity': 'productive',
                    'root_cause': 'Managing multiple async processes or conversations',
                    'intervention_needed': False,
                    'intervention_type': None,
                    'confidence': 0.85,
                    'reasoning': 'Rapid switching with purpose - managing parallel work streams'
                }
        
        # Check for actual distraction patterns
        if situation.switching_velocity > 10 and situation.energy_level == 'frantic':
            if not situation.waiting_indicators and not situation.multitask_indicators:
                return {
                    'interpretation': 'Possible attention fragmentation without clear purpose',
                    'productivity': 'concerning',
                    'root_cause': 'Cognitive overload or stress response',
                    'intervention_needed': True,
                    'intervention_type': 'gentle',
                    'confidence': 0.7,
                    'reasoning': 'Very rapid switching without waiting/multitask indicators'
                }
        
        # Check for deep focus
        if situation.session_depth > 300 and situation.switching_velocity < 1:
            return {
                'interpretation': 'Deep focus session with minimal distractions',
                'productivity': 'productive',
                'root_cause': 'Flow state or deep work',
                'intervention_needed': False,
                'intervention_type': None,
                'confidence': 0.95,
                'reasoning': 'Long sessions with low switching indicates deep focus'
            }
        
        # Default neutral assessment
        return {
            'interpretation': 'Normal work pattern - switching between tasks',
            'productivity': 'neutral',
            'root_cause': 'Regular task management',
            'intervention_needed': False,
            'intervention_type': None,
            'confidence': 0.6,
            'reasoning': 'No strong indicators of concern or exceptional productivity'
        }
    
    def learn_from_feedback(self, situation_id: str, user_feedback: str, was_accurate: bool):
        """Learn from user feedback on interpretations"""
        
        if situation_id in self.interpretation_cache:
            cached = self.interpretation_cache[situation_id]
            interpretation = cached['interpretation']
            
            # Store feedback for future learning
            self.user_examples.append({
                'pattern': f"Situation {situation_id}",
                'interpretation': user_feedback,
                'is_productive': was_accurate,
                'context': interpretation.metadata,
                'timestamp': datetime.now().isoformat()
            })
            
            # Clear cache entry to force re-interpretation with new knowledge
            del self.interpretation_cache[situation_id]
    
    def get_interpretation_summary(self) -> Dict:
        """Get summary of interpretations"""
        
        total = len(self.interpretation_cache)
        if total == 0:
            return {'message': 'No interpretations yet'}
        
        productive = sum(1 for c in self.interpretation_cache.values() 
                        if c['interpretation'].productivity_assessment == 'productive')
        concerning = sum(1 for c in self.interpretation_cache.values() 
                        if c['interpretation'].productivity_assessment == 'concerning')
        neutral = total - productive - concerning
        
        interventions_needed = sum(1 for c in self.interpretation_cache.values() 
                                 if c['interpretation'].intervention_needed)
        
        avg_confidence = sum(c['interpretation'].confidence for c in self.interpretation_cache.values()) / total
        
        return {
            'total_interpretations': total,
            'productive_percentage': productive / total * 100,
            'concerning_percentage': concerning / total * 100,
            'neutral_percentage': neutral / total * 100,
            'interventions_needed': interventions_needed,
            'average_confidence': avg_confidence,
            'user_examples_learned': len(self.user_examples)
        }
    
    def export_learning(self) -> str:
        """Export learned patterns for backup/sharing"""
        
        export_data = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'user_examples': self.user_examples,
            'interpretation_stats': self.get_interpretation_summary()
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_learning(self, json_data: str):
        """Import learned patterns"""
        
        data = json.loads(json_data)
        
        # Import user examples
        for example in data.get('user_examples', []):
            self.user_examples.append(example)
        
        # Clear cache to apply new learning
        self.interpretation_cache.clear()


class RealTimeInterpreter:
    """Real-time pattern interpretation with streaming updates"""
    
    def __init__(self, interpreter: PatternInterpreter):
        self.interpreter = interpreter
        self.active_interpretations = {}
        self.interpretation_queue = asyncio.Queue()
        
    async def process_situation_stream(self, situation: SituationContext):
        """Process situations in real-time"""
        
        # Add to queue for processing
        await self.interpretation_queue.put(situation)
        
        # Get interpretation
        interpretation = await self.interpreter.interpret_pattern(situation)
        
        # Store active interpretation
        self.active_interpretations[situation.to_fingerprint()] = {
            'situation': situation,
            'interpretation': interpretation,
            'timestamp': datetime.now()
        }
        
        # Clean old interpretations (older than 1 hour)
        cutoff = datetime.now()
        self.active_interpretations = {
            k: v for k, v in self.active_interpretations.items()
            if (cutoff - v['timestamp']).seconds < 3600
        }
        
        return interpretation
    
    def get_current_state(self) -> Dict:
        """Get current interpretation state"""
        
        if not self.active_interpretations:
            return {'status': 'No active interpretations'}
        
        # Get most recent interpretations
        recent = sorted(self.active_interpretations.values(), 
                       key=lambda x: x['timestamp'], 
                       reverse=True)[:5]
        
        return {
            'active_count': len(self.active_interpretations),
            'recent_interpretations': [
                {
                    'time': interp['timestamp'].strftime('%H:%M:%S'),
                    'app': interp['situation'].active_app,
                    'interpretation': interp['interpretation'].interpretation,
                    'productivity': interp['interpretation'].productivity_assessment,
                    'confidence': f"{interp['interpretation'].confidence:.0%}"
                }
                for interp in recent
            ]
        }