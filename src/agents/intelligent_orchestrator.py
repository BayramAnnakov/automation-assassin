"""
Intelligent Agent Coordinator for Automation Assassin
Orchestrates specialized sub-agents using Claude Code's standard sub-agent system
"""

from typing import Dict, List
import json

class IntelligentAgentCoordinator:
    """
    Coordinates multiple specialized sub-agents for comprehensive death loop analysis
    Uses Claude Code's standard sub-agent discovery in .claude/agents/
    """
    
    def __init__(self):
        self.analysis_results = {}
        self.interventions = []
        self.automation_code = {}
        
    def get_pattern_detective_task(self, db_path: str, days: int = 30) -> Dict:
        """
        Generate Task configuration for Pattern Detective sub-agent
        Claude Code will automatically find this agent in .claude/agents/
        """
        return {
            'subagent_type': 'pattern-detective',
            'description': 'Analyze Screen Time patterns',
            'prompt': f"""
            Analyze the Screen Time database at {db_path} for the last {days} days.
            
            Focus on:
            1. Death loops (rapid app switching patterns)
            2. Temporal patterns (peak distraction times)
            3. Context switching metrics
            4. App clusters
            
            Use Python with sqlite3 to query the database.
            Remember the macOS timestamp offset (978307200).
            
            Return a comprehensive report with actionable insights.
            """
        }
    
    def get_context_learner_task(self, patterns: Dict) -> Dict:
        """
        Generate Task configuration for Context Learner sub-agent
        """
        return {
            'subagent_type': 'context-learner',
            'description': 'Learn user context',
            'prompt': f"""
            Based on these discovered patterns:
            {json.dumps(patterns, indent=2)}
            
            Learn and classify:
            1. User's profession and work style
            2. Productive vs distraction apps for THIS user
            3. Optimal work schedule
            4. Workflow patterns
            
            Return a detailed user profile.
            """
        }
    
    def get_intervention_architect_task(self, patterns: Dict, context: Dict = None) -> Dict:
        """
        Generate Task configuration for Intervention Architect sub-agent
        """
        prompt_context = f"""
        Design creative interventions for these patterns:
        {json.dumps(patterns, indent=2)}
        """
        
        if context:
            prompt_context += f"""
            
            User context:
            {json.dumps(context, indent=2)}
            """
        
        return {
            'subagent_type': 'intervention-architect',
            'description': 'Design interventions',
            'prompt': prompt_context + """
            
            Create 5-10 interventions that are:
            1. Progressive (gentle → firm)
            2. Psychologically effective
            3. User-friendly
            4. Creative (beyond simple blocking)
            
            Return a list of intervention strategies.
            """
        }
    
    def get_code_generator_task(self, interventions: List[Dict]) -> Dict:
        """
        Generate Task configuration for Code Generator sub-agent
        """
        return {
            'subagent_type': 'code-generator',
            'description': 'Generate Hammerspoon code',
            'prompt': f"""
            Generate Hammerspoon Lua code for these interventions:
            {json.dumps(interventions, indent=2)}
            
            Create a complete, working init.lua that:
            1. Implements each intervention
            2. Includes user notifications
            3. Tracks statistics
            4. Has configurable settings
            
            Return the complete Hammerspoon configuration.
            """
        }
    
    def get_impact_analyst_task(self, patterns: Dict, interventions: List[Dict]) -> Dict:
        """
        Generate Task configuration for Impact Analyst sub-agent
        """
        return {
            'subagent_type': 'impact-analyst',
            'description': 'Calculate impact',
            'prompt': f"""
            Calculate the impact of these interventions:
            
            Patterns found:
            {json.dumps(patterns, indent=2)}
            
            Interventions designed:
            {json.dumps(interventions, indent=2)}
            
            Calculate:
            1. Time saved (daily/weekly/yearly)
            2. Productivity improvement %
            3. ROI in hours and dollars
            4. Quality of life improvements
            
            Return a comprehensive impact report.
            """
        }
    
    def get_orchestration_sequence(self) -> List[Dict]:
        """
        Return the recommended sequence for orchestrating sub-agents
        These agents are automatically discovered from .claude/agents/
        """
        return [
            {
                'phase': 1,
                'agent': 'pattern-detective',
                'purpose': 'Analyze Screen Time data',
                'description': 'Finds death loops and productivity patterns'
            },
            {
                'phase': 2,
                'agent': 'context-learner',
                'purpose': 'Understand user context',
                'description': 'Learns work patterns and app classification'
            },
            {
                'phase': 3,
                'agent': 'intervention-architect',
                'purpose': 'Design interventions',
                'description': 'Creates personalized behavior change strategies'
            },
            {
                'phase': 4,
                'agent': 'code-generator',
                'purpose': 'Generate automation',
                'description': 'Creates Hammerspoon Lua scripts'
            },
            {
                'phase': 5,
                'agent': 'impact-analyst',
                'purpose': 'Calculate impact',
                'description': 'Measures time savings and ROI'
            }
        ]
    
    def example_orchestration(self):
        """
        Example of how to orchestrate the full workflow
        """
        print("""
        # Example Orchestration with Claude Code Sub-Agents
        
        ## Step 1: Analyze patterns
        ```python
        task_config = coordinator.get_pattern_detective_task('data/screentime.db', 30)
        patterns = Task(**task_config)
        ```
        
        ## Step 2: Learn context
        ```python
        task_config = coordinator.get_context_learner_task(patterns)
        context = Task(**task_config)
        ```
        
        ## Step 3: Design interventions
        ```python
        task_config = coordinator.get_intervention_architect_task(patterns, context)
        interventions = Task(**task_config)
        ```
        
        ## Step 4: Generate code
        ```python
        task_config = coordinator.get_code_generator_task(interventions)
        automation = Task(**task_config)
        ```
        
        ## Step 5: Calculate impact
        ```python
        task_config = coordinator.get_impact_analyst_task(patterns, interventions)
        impact = Task(**task_config)
        ```
        
        Note: Claude Code automatically discovers agents from .claude/agents/
        No manual registration needed!
        """)
    
    def available_agents(self) -> List[str]:
        """
        List available sub-agents (discovered from .claude/agents/)
        """
        return [
            'pattern-detective',
            'context-learner',
            'intervention-architect',
            'code-generator',
            'impact-analyst'
        ]