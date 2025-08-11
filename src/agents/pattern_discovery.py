"""
Intelligent Pattern Discovery Agent
Discovers productivity patterns without any hardcoded rules or assumptions
Uses Claude's intelligence to understand patterns unique to each user
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime, timedelta
import pandas as pd
from claude_code_sdk import query, ClaudeCodeOptions
from claude_code_sdk.types import AssistantMessage, ResultMessage

class IntelligentPatternDiscovery:
    """
    Discovers patterns using AI intelligence, not fixed algorithms
    Adapts to any user type and finds patterns unique to them
    """
    
    def __init__(self):
        self.session_id = None
        self.discovered_patterns = []
        
    async def discover_all_patterns(self, usage_data: pd.DataFrame, 
                                   user_context: Dict = None) -> Dict:
        """
        Discover ALL types of patterns that affect productivity
        Not limited to any specific pattern type
        """
        
        patterns = {
            'behavioral_patterns': [],
            'temporal_patterns': [],
            'contextual_patterns': [],
            'psychological_patterns': [],
            'workflow_disruptions': [],
            'hidden_inefficiencies': []
        }
        
        # Discover behavioral patterns
        behavioral = await self.discover_behavioral_patterns(usage_data, user_context)
        patterns['behavioral_patterns'] = behavioral
        
        # Discover temporal patterns
        temporal = await self.discover_temporal_patterns(usage_data, user_context)
        patterns['temporal_patterns'] = temporal
        
        # Discover contextual patterns
        contextual = await self.discover_contextual_patterns(usage_data, user_context)
        patterns['contextual_patterns'] = contextual
        
        # Discover psychological patterns
        psychological = await self.discover_psychological_patterns(usage_data, user_context)
        patterns['psychological_patterns'] = psychological
        
        # Discover workflow disruptions
        disruptions = await self.discover_workflow_disruptions(usage_data, user_context)
        patterns['workflow_disruptions'] = disruptions
        
        # Discover hidden inefficiencies
        hidden = await self.discover_hidden_inefficiencies(usage_data, user_context)
        patterns['hidden_inefficiencies'] = hidden
        
        return patterns
    
    async def discover_behavioral_patterns(self, data: pd.DataFrame, 
                                          context: Dict = None) -> List[Dict]:
        """
        Discover behavioral patterns unique to this user
        No assumptions about what's good or bad
        """
        options = ClaudeCodeOptions(
            permission_mode="bypassPermissions",
            max_turns=5,
            system_prompt="""You are a behavioral pattern analyst.

Discover behavioral patterns in app usage data without assumptions.
Don't categorize apps as 'productive' or 'distracting' - learn from the data.

Look for:
- Repetitive behaviors that might indicate habits (good or bad)
- Avoidance patterns (what the user seems to avoid)
- Compulsive patterns (irresistible app checks)
- Reward-seeking patterns
- Stress responses in app usage
- Flow state interruptions

Be specific to THIS user's behavior."""
        )
        
        # Prepare data for analysis
        data_summary = self._prepare_behavioral_data(data)
        
        prompt = f"""Analyze these app usage behaviors:

{data_summary}

User Context: {context if context else 'General user'}

Discover behavioral patterns that affect productivity.
Don't make generic assumptions. Learn from THIS user's specific behaviors.
What patterns do you see that they might not even realize?"""
        
        patterns = []
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, 'text'):
                        discovered = self._extract_patterns(block.text, 'behavioral')
                        patterns.extend(discovered)
            
            if isinstance(message, ResultMessage):
                self.session_id = message.session_id
                break
        
        return patterns
    
    async def discover_temporal_patterns(self, data: pd.DataFrame,
                                        context: Dict = None) -> List[Dict]:
        """
        Discover time-based patterns specific to this user
        """
        options = ClaudeCodeOptions(
            permission_mode="bypassPermissions",
            max_turns=5,
            continue_conversation=True,
            resume=self.session_id,
            system_prompt="""You are a temporal pattern analyst.

Discover time-based patterns that affect productivity:
- Peak performance times vs actual work times
- Energy dips and their app usage correlations
- Weekend vs weekday patterns
- Morning routine inefficiencies
- End-of-day wind-down issues
- Lunch break patterns
- Meeting aftermath patterns

Look for misalignments between natural rhythms and actual usage."""
        )
        
        data_summary = self._prepare_temporal_data(data)
        
        prompt = f"""Analyze these temporal patterns:

{data_summary}

Find time-based inefficiencies and opportunities.
When does this user lose productivity? When could they gain it?"""
        
        patterns = []
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, 'text'):
                        discovered = self._extract_patterns(block.text, 'temporal')
                        patterns.extend(discovered)
            
            if isinstance(message, ResultMessage):
                break
        
        return patterns
    
    async def discover_contextual_patterns(self, data: pd.DataFrame,
                                          context: Dict = None) -> List[Dict]:
        """
        Discover context-switching and environmental patterns
        """
        options = ClaudeCodeOptions(
            permission_mode="bypassPermissions",
            max_turns=5,
            continue_conversation=True,
            resume=self.session_id,
            system_prompt="""You are a context pattern analyst.

Discover patterns related to context and environment:
- Context switching costs (mental overhead)
- App clustering (which apps are used together)
- Task fragmentation patterns
- Deep work interruptions
- Collaboration vs solo work patterns
- Project switching patterns

Understand the hidden costs of switching contexts."""
        )
        
        data_summary = self._prepare_contextual_data(data)
        
        prompt = f"""Analyze context switching patterns:

{data_summary}

What context switches are costly for this user?
What app combinations indicate deep work vs shallow work?"""
        
        patterns = []
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, 'text'):
                        discovered = self._extract_patterns(block.text, 'contextual')
                        patterns.extend(discovered)
            
            if isinstance(message, ResultMessage):
                break
        
        return patterns
    
    async def discover_psychological_patterns(self, data: pd.DataFrame,
                                             context: Dict = None) -> List[Dict]:
        """
        Discover psychological and emotional patterns in usage
        """
        options = ClaudeCodeOptions(
            permission_mode="bypassPermissions",
            max_turns=5,
            continue_conversation=True,
            resume=self.session_id,
            system_prompt="""You are a psychological pattern analyst.

Discover psychological patterns in app usage:
- Procrastination signatures
- Anxiety-driven app checking
- Dopamine-seeking behaviors
- Perfectionism patterns (over-editing, over-checking)
- Impostor syndrome indicators
- Burnout warning signs
- Motivation cycles

Be empathetic and insightful."""
        )
        
        data_summary = self._prepare_psychological_data(data)
        
        prompt = f"""Analyze psychological patterns in usage:

{data_summary}

What emotional or psychological patterns affect productivity?
What behaviors suggest stress, anxiety, or other states?"""
        
        patterns = []
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, 'text'):
                        discovered = self._extract_patterns(block.text, 'psychological')
                        patterns.extend(discovered)
            
            if isinstance(message, ResultMessage):
                break
        
        return patterns
    
    async def discover_workflow_disruptions(self, data: pd.DataFrame,
                                           context: Dict = None) -> List[Dict]:
        """
        Discover what disrupts this user's workflow
        """
        options = ClaudeCodeOptions(
            permission_mode="bypassPermissions",
            max_turns=5,
            continue_conversation=True,
            resume=self.session_id,
            system_prompt="""You are a workflow analyst.

Identify workflow disruptions:
- What breaks their flow state?
- What causes task abandonment?
- What creates decision fatigue?
- What causes priority confusion?
- What leads to incomplete work?

Focus on disruption patterns, not individual events."""
        )
        
        data_summary = self._prepare_workflow_data(data)
        
        prompt = f"""Analyze workflow disruption patterns:

{data_summary}

What systematically disrupts this user's productivity?
What patterns prevent them from completing important work?"""
        
        patterns = []
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, 'text'):
                        discovered = self._extract_patterns(block.text, 'disruption')
                        patterns.extend(discovered)
            
            if isinstance(message, ResultMessage):
                break
        
        return patterns
    
    async def discover_hidden_inefficiencies(self, data: pd.DataFrame,
                                            context: Dict = None) -> List[Dict]:
        """
        Discover inefficiencies the user doesn't realize exist
        """
        options = ClaudeCodeOptions(
            permission_mode="bypassPermissions",
            max_turns=5,
            continue_conversation=True,
            resume=self.session_id,
            system_prompt="""You are an efficiency analyst.

Find hidden inefficiencies:
- Micro-procrastinations (small time losses)
- Tool switching overhead
- Duplicate effort patterns
- Suboptimal app choices for tasks
- Missing automation opportunities
- Unnecessary complexity patterns

Find the subtle time wasters."""
        )
        
        data_summary = self._prepare_efficiency_data(data)
        
        prompt = f"""Find hidden inefficiencies:

{data_summary}

What small inefficiencies add up to big productivity losses?
What patterns could be optimized that the user doesn't notice?"""
        
        patterns = []
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, 'text'):
                        discovered = self._extract_patterns(block.text, 'inefficiency')
                        patterns.extend(discovered)
            
            if isinstance(message, ResultMessage):
                break
        
        return patterns
    
    def _prepare_behavioral_data(self, data: pd.DataFrame) -> str:
        """Prepare behavioral data summary for AI analysis"""
        summary = []
        
        if not data.empty:
            # App switching frequency
            summary.append("App Switching Patterns:")
            if 'app' in data.columns:
                app_switches = data['app'].value_counts().head(10)
                for app, count in app_switches.items():
                    summary.append(f"  {app}: {count} sessions")
            
            # Session durations
            if 'duration_seconds' in data.columns:
                summary.append(f"\nSession Durations:")
                summary.append(f"  Average: {data['duration_seconds'].mean():.1f}s")
                summary.append(f"  Shortest: {data['duration_seconds'].min():.1f}s")
                summary.append(f"  Longest: {data['duration_seconds'].max():.1f}s")
        
        return "\n".join(summary)
    
    def _prepare_temporal_data(self, data: pd.DataFrame) -> str:
        """Prepare temporal data summary"""
        summary = []
        
        if not data.empty and 'start_time' in data.columns:
            # Extract hour patterns
            data['hour'] = pd.to_datetime(data['start_time']).dt.hour
            hourly_usage = data.groupby('hour').size()
            
            summary.append("Hourly Usage Patterns:")
            for hour, count in hourly_usage.items():
                summary.append(f"  {hour:02d}:00 - {count} sessions")
            
            # Day of week patterns
            data['day'] = pd.to_datetime(data['start_time']).dt.day_name()
            daily_usage = data.groupby('day').size()
            
            summary.append("\nDaily Patterns:")
            for day, count in daily_usage.items():
                summary.append(f"  {day}: {count} sessions")
        
        return "\n".join(summary)
    
    def _prepare_contextual_data(self, data: pd.DataFrame) -> str:
        """Prepare context switching data"""
        summary = []
        
        if not data.empty:
            # Analyze app sequences
            summary.append("App Transition Patterns:")
            
            # Create transition matrix
            if len(data) > 1:
                transitions = []
                for i in range(len(data) - 1):
                    if 'app' in data.columns:
                        from_app = data.iloc[i]['app']
                        to_app = data.iloc[i + 1]['app']
                        transitions.append(f"{from_app} → {to_app}")
                
                # Count transitions
                from collections import Counter
                transition_counts = Counter(transitions)
                
                for transition, count in transition_counts.most_common(10):
                    summary.append(f"  {transition}: {count} times")
        
        return "\n".join(summary)
    
    def _prepare_psychological_data(self, data: pd.DataFrame) -> str:
        """Prepare data for psychological analysis"""
        summary = []
        
        if not data.empty:
            # Rapid app checks (potential anxiety)
            if 'duration_seconds' in data.columns:
                rapid_checks = data[data['duration_seconds'] < 10]
                summary.append(f"Rapid Checks (<10s): {len(rapid_checks)} sessions")
                
                if 'app' in rapid_checks.columns:
                    rapid_apps = rapid_checks['app'].value_counts().head(5)
                    summary.append("Most rapidly checked apps:")
                    for app, count in rapid_apps.items():
                        summary.append(f"  {app}: {count} times")
            
            # Late night usage (potential insomnia/anxiety)
            if 'start_time' in data.columns:
                data['hour'] = pd.to_datetime(data['start_time']).dt.hour
                late_night = data[(data['hour'] >= 23) | (data['hour'] <= 2)]
                summary.append(f"\nLate night usage (11pm-2am): {len(late_night)} sessions")
        
        return "\n".join(summary)
    
    def _prepare_workflow_data(self, data: pd.DataFrame) -> str:
        """Prepare workflow disruption data"""
        summary = []
        
        if not data.empty:
            # Long sessions followed by short ones (potential disruption)
            if 'duration_seconds' in data.columns:
                summary.append("Session Length Variations:")
                
                for i in range(len(data) - 1):
                    curr_duration = data.iloc[i]['duration_seconds']
                    next_duration = data.iloc[i + 1]['duration_seconds']
                    
                    if curr_duration > 600 and next_duration < 30:  # Long then short
                        if 'app' in data.columns:
                            summary.append(f"  Disruption: {data.iloc[i]['app']} "
                                         f"({curr_duration:.0f}s) → "
                                         f"{data.iloc[i+1]['app']} ({next_duration:.0f}s)")
        
        return "\n".join(summary[:20])  # Limit output
    
    def _prepare_efficiency_data(self, data: pd.DataFrame) -> str:
        """Prepare efficiency analysis data"""
        summary = []
        
        if not data.empty:
            # Multiple short sessions of same app (inefficient)
            if 'app' in data.columns and 'duration_seconds' in data.columns:
                short_sessions = data[data['duration_seconds'] < 30]
                app_fragments = short_sessions['app'].value_counts()
                
                summary.append("Fragmented App Usage (<30s sessions):")
                for app, count in app_fragments.head(10).items():
                    if count > 5:  # Multiple fragments
                        summary.append(f"  {app}: {count} fragments")
        
        return "\n".join(summary)
    
    def _extract_patterns(self, text: str, pattern_type: str) -> List[Dict]:
        """Extract patterns from AI response"""
        patterns = []
        
        lines = text.split('\n')
        current_pattern = None
        
        for line in lines:
            # Look for pattern indicators
            if any(indicator in line.lower() for indicator in 
                   ['pattern', 'behavior', 'tendency', 'habit', 'repeatedly']):
                
                if current_pattern:
                    patterns.append(current_pattern)
                
                current_pattern = {
                    'type': pattern_type,
                    'description': line.strip(),
                    'details': [],
                    'severity': self._assess_severity(line)
                }
            elif current_pattern and line.strip():
                # Add details to current pattern
                current_pattern['details'].append(line.strip())
        
        # Add last pattern
        if current_pattern:
            patterns.append(current_pattern)
        
        return patterns
    
    def _assess_severity(self, text: str) -> str:
        """Assess pattern severity from description"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['severe', 'major', 'significant', 'critical']):
            return 'high'
        elif any(word in text_lower for word in ['moderate', 'notable', 'concerning']):
            return 'medium'
        else:
            return 'low'


class PatternInsightGenerator:
    """
    Generates actionable insights from discovered patterns
    """
    
    def __init__(self):
        self.discovery_agent = IntelligentPatternDiscovery()
    
    async def generate_insights(self, usage_data: pd.DataFrame,
                               user_context: Dict = None) -> Dict:
        """
        Generate comprehensive insights from pattern analysis
        """
        print("🔬 Discovering patterns with AI intelligence...")
        
        # Discover all patterns
        patterns = await self.discovery_agent.discover_all_patterns(
            usage_data, user_context
        )
        
        # Generate insights
        insights = {
            'key_findings': [],
            'priority_issues': [],
            'quick_wins': [],
            'long_term_improvements': [],
            'personalized_recommendations': []
        }
        
        # Analyze patterns for insights
        insights = await self._analyze_for_insights(patterns, user_context)
        
        return {
            'patterns': patterns,
            'insights': insights
        }
    
    async def _analyze_for_insights(self, patterns: Dict, 
                                   context: Dict = None) -> Dict:
        """
        Convert patterns into actionable insights
        """
        options = ClaudeCodeOptions(
            permission_mode="bypassPermissions",
            max_turns=5,
            system_prompt="""You are an insight generator.

Convert discovered patterns into actionable insights.
Prioritize by impact and ease of implementation.
Be specific and personalized."""
        )
        
        prompt = f"""Generate insights from these patterns:

{self._summarize_patterns(patterns)}

User Context: {context if context else 'General user'}

Create:
1. Key findings (top 3-5 discoveries)
2. Priority issues to address
3. Quick wins (easy improvements)
4. Long-term improvements
5. Personalized recommendations"""
        
        insights = {}
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, 'text'):
                        insights = self._parse_insights(block.text)
            
            if isinstance(message, ResultMessage):
                break
        
        return insights
    
    def _summarize_patterns(self, patterns: Dict) -> str:
        """Summarize patterns for insight generation"""
        summary = []
        
        for category, pattern_list in patterns.items():
            if pattern_list:
                summary.append(f"\n{category.replace('_', ' ').title()}:")
                for pattern in pattern_list[:3]:  # Top 3 per category
                    summary.append(f"  - {pattern.get('description', 'Pattern')}")
        
        return "\n".join(summary)
    
    def _parse_insights(self, text: str) -> Dict:
        """Parse insights from AI response"""
        insights = {
            'key_findings': [],
            'priority_issues': [],
            'quick_wins': [],
            'long_term_improvements': [],
            'personalized_recommendations': []
        }
        
        current_section = None
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Identify sections
            if 'key finding' in line_lower:
                current_section = 'key_findings'
            elif 'priority' in line_lower:
                current_section = 'priority_issues'
            elif 'quick win' in line_lower:
                current_section = 'quick_wins'
            elif 'long' in line_lower and 'term' in line_lower:
                current_section = 'long_term_improvements'
            elif 'recommend' in line_lower:
                current_section = 'personalized_recommendations'
            
            # Add content to current section
            elif current_section and line.strip() and not line.startswith('#'):
                insights[current_section].append(line.strip().lstrip('-').strip())
        
        return insights


if __name__ == "__main__":
    # Test the pattern discovery
    async def test():
        # Create sample data
        import numpy as np
        
        # Generate realistic usage data
        apps = ['VS Code', 'Chrome', 'Slack', 'Terminal', 'Figma', 'Spotify', 'Twitter']
        
        data = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(500):
            app = np.random.choice(apps)
            start = base_time + timedelta(minutes=np.random.randint(0, 10080))
            duration = np.random.exponential(120) if app in ['VS Code', 'Figma'] else np.random.exponential(30)
            
            data.append({
                'app': app,
                'start_time': start,
                'end_time': start + timedelta(seconds=duration),
                'duration_seconds': duration
            })
        
        df = pd.DataFrame(data)
        
        # Test pattern discovery
        generator = PatternInsightGenerator()
        
        user_context = {
            'profession': 'Software Developer',
            'work_hours': '9-6',
            'work_apps': ['VS Code', 'Terminal', 'Chrome'],
            'communication_apps': ['Slack']
        }
        
        result = await generator.generate_insights(df, user_context)
        
        # Display results
        print("\n" + "="*60)
        print("🔍 INTELLIGENT PATTERN DISCOVERY RESULTS")
        print("="*60)
        
        for category, patterns in result['patterns'].items():
            if patterns:
                print(f"\n{category.replace('_', ' ').title()}:")
                for pattern in patterns[:2]:
                    print(f"  • {pattern['description']}")
        
        print("\n📊 Key Insights:")
        for insight in result['insights'].get('key_findings', [])[:3]:
            print(f"  • {insight}")
        
        return result
    
    import asyncio
    asyncio.run(test())