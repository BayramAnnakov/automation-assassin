"""
Death Loop Pattern Detector
Identifies productivity-killing app switching patterns in Screen Time data
"""

from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np

class DeathLoopDetector:
    """Detects and analyzes repetitive app switching patterns (death loops)"""
    
    def __init__(self):
        self.patterns = []
        self.loop_scores = {}
        self.context_classifications = {}
        
        # Define productive vs distracting apps
        self.productive_apps = {
            'vs code', 'xcode', 'terminal', 'github', 'intellij',
            'sublime', 'atom', 'vim', 'emacs', 'jupyter',
            'word', 'excel', 'powerpoint', 'pages', 'numbers', 'keynote',
            'notion', 'obsidian', 'roam', 'bear', 'notes',
            'figma', 'sketch', 'adobe', 'photoshop', 'illustrator'
        }
        
        self.distracting_apps = {
            'twitter', 'facebook', 'instagram', 'tiktok', 'youtube',
            'reddit', 'discord', 'twitch', 'netflix', 'disney',
            'hulu', 'prime video', 'spotify', 'apple music'
        }
        
        self.communication_apps = {
            'slack', 'teams', 'zoom', 'messages', 'whatsapp',
            'telegram', 'signal', 'mail', 'gmail', 'outlook'
        }
    
    def find_loops(self, usage_data: pd.DataFrame, 
                   min_loop_count: int = 3,
                   max_gap_seconds: int = 60) -> List[Dict]:
        """
        Find A→B→A death loop patterns in app usage data
        
        Args:
            usage_data: DataFrame with app usage sessions
            min_loop_count: Minimum occurrences to qualify as a pattern
            max_gap_seconds: Maximum seconds between switches
        
        Returns:
            List of death loop patterns with details
        """
        if usage_data.empty:
            return []
        
        # Sort by start time
        usage_data = usage_data.sort_values('start_time')
        
        # Track app sequences
        sequences = []
        loop_patterns = defaultdict(list)
        
        # Build sequences of rapid app switches
        for i in range(len(usage_data) - 1):
            current = usage_data.iloc[i]
            next_app = usage_data.iloc[i + 1]
            
            # Check if this is a rapid switch
            if next_app['start_time'] and current['end_time']:
                gap = (next_app['start_time'] - current['end_time']).total_seconds()
                
                if 0 <= gap <= max_gap_seconds:
                    sequences.append({
                        'from': current['app'],
                        'to': next_app['app'],
                        'time': current['end_time'],
                        'gap': gap,
                        'from_duration': current['duration_seconds'],
                        'to_duration': next_app['duration_seconds']
                    })
        
        # Identify A→B→A patterns
        for i in range(len(sequences) - 1):
            curr_seq = sequences[i]
            next_seq = sequences[i + 1]
            
            # Check if we have A→B followed by B→A
            if (curr_seq['from'] == next_seq['to'] and 
                curr_seq['to'] == next_seq['from']):
                
                pattern_key = tuple(sorted([curr_seq['from'], curr_seq['to']]))
                loop_patterns[pattern_key].append({
                    'app_a': curr_seq['from'],
                    'app_b': curr_seq['to'],
                    'time': curr_seq['time'],
                    'total_duration': (curr_seq['from_duration'] + 
                                     curr_seq['to_duration'] + 
                                     next_seq['to_duration']),
                    'switch_gaps': [curr_seq['gap'], next_seq['gap']]
                })
        
        # Filter and score patterns
        death_loops = []
        for pattern, occurrences in loop_patterns.items():
            if len(occurrences) >= min_loop_count:
                app_a, app_b = pattern
                
                # Calculate loop statistics
                total_time = sum(occ['total_duration'] for occ in occurrences)
                avg_duration = total_time / len(occurrences)
                frequency = len(occurrences)
                
                # Calculate loop score
                score = self.calculate_loop_score(
                    frequency=frequency,
                    avg_duration=avg_duration,
                    total_time=total_time,
                    app_a=app_a,
                    app_b=app_b
                )
                
                death_loops.append({
                    'pattern': f"{app_a} ↔ {app_b}",
                    'app_a': app_a,
                    'app_b': app_b,
                    'frequency': frequency,
                    'total_time_seconds': round(total_time, 2),
                    'total_time_minutes': round(total_time / 60, 2),
                    'avg_duration_seconds': round(avg_duration, 2),
                    'score': round(score, 2),
                    'context': self.classify_context(app_a, app_b),
                    'occurrences': occurrences[:5]  # Keep first 5 for examples
                })
        
        # Sort by score (highest first)
        death_loops.sort(key=lambda x: x['score'], reverse=True)
        
        self.patterns = death_loops
        return death_loops
    
    def calculate_loop_score(self, frequency: int, avg_duration: float,
                            total_time: float, app_a: str, app_b: str) -> float:
        """
        Calculate a score for how problematic a death loop is
        
        Higher score = more problematic pattern
        """
        # Base score from frequency and time
        base_score = frequency * np.log1p(total_time / 60)  # Log scale for time
        
        # Penalty for short durations (indicates restlessness)
        if avg_duration < 30:  # Less than 30 seconds average
            base_score *= 2.0
        elif avg_duration < 60:  # Less than 1 minute
            base_score *= 1.5
        
        # Context multiplier
        context = self.classify_context(app_a, app_b)
        
        if context == 'highly_distracting':
            base_score *= 3.0
        elif context == 'distracting':
            base_score *= 2.0
        elif context == 'mixed':
            base_score *= 1.5
        elif context == 'communication_loop':
            base_score *= 1.3
        else:  # productive
            base_score *= 0.5
        
        return base_score
    
    def classify_context(self, app_a: str, app_b: str) -> str:
        """
        Classify the context of an app switching pattern
        
        Returns:
            'productive', 'distracting', 'highly_distracting', 
            'mixed', or 'communication_loop'
        """
        app_a_lower = app_a.lower()
        app_b_lower = app_b.lower()
        
        # Check if both apps are in the same category
        a_productive = any(prod in app_a_lower for prod in self.productive_apps)
        b_productive = any(prod in app_b_lower for prod in self.productive_apps)
        
        a_distracting = any(dist in app_a_lower for dist in self.distracting_apps)
        b_distracting = any(dist in app_b_lower for dist in self.distracting_apps)
        
        a_communication = any(comm in app_a_lower for comm in self.communication_apps)
        b_communication = any(comm in app_b_lower for comm in self.communication_apps)
        
        # Classify based on combinations
        if a_distracting and b_distracting:
            return 'highly_distracting'
        elif a_productive and b_productive:
            return 'productive'
        elif a_communication and b_communication:
            return 'communication_loop'
        elif (a_distracting and not b_productive) or (b_distracting and not a_productive):
            return 'distracting'
        else:
            return 'mixed'
    
    def get_intervention_priority(self) -> List[Dict]:
        """
        Get death loops prioritized for intervention
        
        Returns loops that are most harmful to productivity
        """
        if not self.patterns:
            return []
        
        # Filter for problematic patterns
        problematic = [
            p for p in self.patterns 
            if p['context'] in ['highly_distracting', 'distracting', 'mixed']
            and p['score'] > 10  # Minimum score threshold
        ]
        
        # Add intervention recommendations
        for pattern in problematic:
            pattern['intervention'] = self._recommend_intervention(pattern)
        
        return problematic[:5]  # Top 5 for intervention
    
    def _recommend_intervention(self, pattern: Dict) -> Dict:
        """Generate intervention recommendation for a death loop"""
        app_a = pattern['app_a']
        app_b = pattern['app_b']
        context = pattern['context']
        
        intervention = {
            'type': '',
            'action': '',
            'expected_impact': ''
        }
        
        if context == 'highly_distracting':
            intervention['type'] = 'aggressive_block'
            intervention['action'] = f"Block both {app_a} and {app_b} during work hours"
            intervention['expected_impact'] = f"Save {pattern['total_time_minutes']:.0f} minutes/day"
        
        elif context == 'distracting':
            intervention['type'] = 'time_limit'
            intervention['action'] = f"Limit {app_a} and {app_b} to 15 min/hour"
            intervention['expected_impact'] = f"Reduce by {pattern['total_time_minutes']*0.7:.0f} minutes/day"
        
        elif context == 'mixed':
            intervention['type'] = 'focus_mode'
            intervention['action'] = f"Hide {app_a} when {app_b} is active"
            intervention['expected_impact'] = f"Reduce switches by {pattern['frequency']*0.5:.0f}/day"
        
        elif context == 'communication_loop':
            intervention['type'] = 'batch_check'
            intervention['action'] = f"Batch {app_a} and {app_b} checks to 3x/day"
            intervention['expected_impact'] = f"Save {pattern['total_time_minutes']*0.4:.0f} minutes/day"
        
        else:  # productive
            intervention['type'] = 'none'
            intervention['action'] = "No intervention needed"
            intervention['expected_impact'] = "Pattern is productive"
        
        return intervention
    
    def calculate_total_impact(self) -> Dict:
        """Calculate total potential time savings from interventions"""
        priority_patterns = self.get_intervention_priority()
        
        total_minutes_wasted = sum(p['total_time_minutes'] for p in priority_patterns)
        estimated_savings = sum(
            p['total_time_minutes'] * 0.6  # Assume 60% reduction
            for p in priority_patterns
        )
        
        return {
            'patterns_found': len(self.patterns),
            'problematic_patterns': len(priority_patterns),
            'daily_time_wasted_minutes': round(total_minutes_wasted, 1),
            'potential_daily_savings_minutes': round(estimated_savings, 1),
            'weekly_savings_hours': round(estimated_savings * 7 / 60, 1),
            'yearly_savings_hours': round(estimated_savings * 365 / 60, 1)
        }
    
    def generate_summary(self) -> str:
        """Generate human-readable summary of findings"""
        if not self.patterns:
            return "No death loops detected in your Screen Time data."
        
        impact = self.calculate_total_impact()
        priority = self.get_intervention_priority()
        
        summary = f"""
🔍 DEATH LOOP ANALYSIS COMPLETE
================================

📊 Overview:
• Found {impact['patterns_found']} repetitive patterns
• {impact['problematic_patterns']} require intervention
• Daily time in loops: {impact['daily_time_wasted_minutes']:.0f} minutes
• Potential savings: {impact['potential_daily_savings_minutes']:.0f} minutes/day

⚠️ Top Death Loops:
"""
        
        for i, pattern in enumerate(priority[:3], 1):
            summary += f"""
{i}. {pattern['pattern']}
   • Frequency: {pattern['frequency']}x/day
   • Time lost: {pattern['total_time_minutes']:.0f} min/day
   • Type: {pattern['context'].replace('_', ' ').title()}
   • Action: {pattern['intervention']['action']}
"""
        
        summary += f"""
💰 Potential Impact:
• Daily: Save {impact['potential_daily_savings_minutes']:.0f} minutes
• Weekly: Recover {impact['weekly_savings_hours']:.1f} hours
• Yearly: Gain {impact['yearly_savings_hours']:.0f} hours ({impact['yearly_savings_hours']/24:.1f} days!)
"""
        
        return summary


if __name__ == "__main__":
    # Test with sample data
    from screentime_reader import ScreenTimeReader
    
    print("🔍 Analyzing Death Loops...")
    print("=" * 50)
    
    # Get real data
    reader = ScreenTimeReader()
    if reader.connect():
        usage_data = reader.query_app_usage(days=7)
        
        # Detect patterns
        detector = DeathLoopDetector()
        patterns = detector.find_loops(usage_data)
        
        # Show summary
        print(detector.generate_summary())
        
        reader.close()