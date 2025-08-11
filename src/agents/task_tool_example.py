"""
Example of proper Claude Code SDK sub-agent usage with Task tool
This demonstrates how to use the Task tool with subagent_type for true modularity
"""

# Example of how the orchestrator would use the Task tool to spawn sub-agents
# This is the proper way to achieve modularity with Claude Code SDK

PATTERN_DETECTIVE_TASK = """
Task tool configuration:
{
    "subagent_type": "pattern-detective",
    "description": "Analyze Screen Time patterns",
    "prompt": '''
        You are a specialized Pattern Detective agent.
        
        Your unique capabilities:
        - Deep knowledge of macOS knowledgeC.db structure
        - Advanced SQL analysis for death loop detection
        - Temporal pattern recognition algorithms
        - Context switching cost calculation
        
        Available tools: Read, Bash, Grep, Write
        
        Task: Analyze the Screen Time database at {db_path} and find:
        1. Death loops (A→B→A patterns with <10s gaps)
        2. Temporal patterns (peak distraction times)
        3. App clusters (frequently used together)
        4. Context switching severity
        
        Use direct SQL queries on ZOBJECT table where ZSTREAMNAME='/app/usage'.
        Remember macOS timestamp offset: 978307200.
        
        Return structured JSON with all discovered patterns.
    '''
}
"""

INTERVENTION_ARCHITECT_TASK = """
Task tool configuration:
{
    "subagent_type": "intervention-architect",
    "description": "Design creative productivity interventions",
    "prompt": '''
        You are a specialized Intervention Architect.
        
        Your unique capabilities:
        - Behavioral psychology expertise
        - Hammerspoon automation knowledge
        - UX design for non-intrusive interventions
        - Progressive intervention strategies
        
        Available tools: Write, WebSearch
        
        Given these patterns: {patterns}
        
        Design creative interventions that are:
        1. Beyond simple blocking (use redirects, gamification, etc.)
        2. Progressive (gentle → firm)
        3. Context-aware (work vs personal time)
        4. Psychologically informed
        
        Consider:
        - Smart redirects to productive alternatives
        - Achievement systems and gamification
        - Breathing exercises during switches
        - Pomodoro with rewards
        - Social accountability
        
        Return JSON array of intervention objects.
    '''
}
"""

CODE_GENERATOR_TASK = """
Task tool configuration:
{
    "subagent_type": "code-generator", 
    "description": "Generate Hammerspoon Lua automations",
    "prompt": '''
        You are a specialized Code Generator for Hammerspoon.
        
        Your unique capabilities:
        - Hammerspoon Lua API mastery
        - macOS system event handling
        - State management and persistence
        - Beautiful, functional code patterns
        
        Available tools: Write, Read, Edit
        
        Interventions to implement: {interventions}
        
        Generate complete Hammerspoon code with:
        1. Elegant Lua patterns (metatables, coroutines)
        2. User-friendly notifications
        3. State persistence across reloads
        4. Configurable settings
        5. Debug mode
        
        Create modular files:
        - init.lua (entry point)
        - death_loop_killer.lua
        - focus_guardian.lua
        - progress_tracker.lua
        - config.lua
        
        Use hs.application.watcher, hs.timer, hs.notify creatively.
    '''
}
"""

IMPACT_ANALYST_TASK = """
Task tool configuration:
{
    "subagent_type": "impact-analyst",
    "description": "Calculate intervention ROI",
    "prompt": '''
        You are a specialized Impact Analyst.
        
        Your unique capabilities:
        - Productivity research knowledge
        - Context switching cost models (23 min avg)
        - Flow state economics
        - Behavioral change statistics
        
        Available tools: WebSearch
        
        Patterns: {patterns}
        Interventions: {interventions}
        
        Calculate realistic impact:
        1. Time savings (daily/weekly/yearly)
        2. Productivity boost percentage
        3. Mental energy preservation
        4. Stress reduction
        5. Financial impact
        6. Quality of life improvements
        
        Assume:
        - 70% compliance rate
        - 30-day gradual improvement
        - Compound intervention effects
        
        Return JSON with metrics and key benefits.
    '''
}
"""

# Example of how the orchestrator would call these
ORCHESTRATOR_FLOW = """
# In the orchestrator's analyze method:

async def analyze_with_subagents(self):
    # Phase 1: Pattern Detection
    patterns = await self.query_with_task(
        task_type="pattern-detective",
        prompt=PATTERN_DETECTIVE_TASK.format(db_path=self.db_path)
    )
    
    # Phase 2: Intervention Design  
    interventions = await self.query_with_task(
        task_type="intervention-architect",
        prompt=INTERVENTION_ARCHITECT_TASK.format(patterns=patterns)
    )
    
    # Phase 3: Code Generation
    code = await self.query_with_task(
        task_type="code-generator",
        prompt=CODE_GENERATOR_TASK.format(interventions=interventions)
    )
    
    # Phase 4: Impact Analysis
    impact = await self.query_with_task(
        task_type="impact-analyst",
        prompt=IMPACT_ANALYST_TASK.format(
            patterns=patterns,
            interventions=interventions
        )
    )
    
    return {
        'patterns': patterns,
        'interventions': interventions,
        'code': code,
        'impact': impact
    }
"""

# Key benefits of this approach:
KEY_BENEFITS = """
✅ TRUE MODULARITY through Task tool
- Each sub-agent has isolated context
- No tool confusion between agents
- Specialized system prompts per agent
- Clean separation of concerns

✅ SPECIALIZED CAPABILITIES
- Pattern Detective: SQL, data analysis, pattern recognition
- Intervention Architect: Psychology, UX, creative solutions
- Code Generator: Lua, Hammerspoon, state management
- Impact Analyst: ROI, productivity metrics, research

✅ TOOL ISOLATION
- Pattern Detective: Read, Bash, Grep, Write (for database analysis)
- Intervention Architect: Write, WebSearch (for research)
- Code Generator: Write, Read, Edit (for code generation)
- Impact Analyst: WebSearch (for productivity research)

✅ CLEAR COMMUNICATION
- Structured JSON between agents
- Well-defined interfaces
- No context pollution
- Predictable data flow
"""

if __name__ == "__main__":
    print("="*70)
    print("CLAUDE CODE SDK SUB-AGENT ARCHITECTURE")
    print("Using Task tool for true modularity")
    print("="*70)
    print("\nSub-agents defined:")
    print("1. pattern-detective - Analyzes Screen Time data")
    print("2. intervention-architect - Designs creative interventions")
    print("3. code-generator - Creates Hammerspoon automations")
    print("4. impact-analyst - Calculates ROI and benefits")
    print("\nEach agent has:")
    print("- Specialized knowledge domain")
    print("- Specific tool access")
    print("- Isolated context")
    print("- Clear responsibilities")
    print("\n" + KEY_BENEFITS)