#!/usr/bin/env python3
"""
Main script to run death loop analysis using Claude Code SDK sub-agents
Demonstrates proper use of Task tool for multi-agent orchestration
"""

import asyncio
import json
from pathlib import Path
from agents.pattern_detective import PatternDetective
from agents.claude_orchestrator import ClaudeOrchestrator

def run_pattern_detective_directly():
    """
    Run the Pattern Detective module directly (without sub-agents)
    This is for testing the core functionality
    """
    print("\n" + "="*70)
    print("🔍 RUNNING PATTERN DETECTIVE DIRECTLY")
    print("="*70 + "\n")
    
    db_path = "data/knowledgeC_copy.db"
    
    if not Path(db_path).exists():
        print(f"❌ Database not found at {db_path}")
        return None
    
    detective = PatternDetective(db_path)
    detective.connect()
    
    # Analyze patterns
    patterns = detective.analyze_all_patterns(days=7)
    
    # Get insights
    insights = detective.get_pattern_insights()
    
    # Print summary
    print("📊 Analysis Results:")
    print(f"   Death loops found: {len(patterns.get('death_loops', []))}")
    print(f"   Temporal patterns: {len(patterns.get('temporal_patterns', []))}")
    print(f"   App clusters: {len(patterns.get('app_clusters', []))}")
    
    if patterns.get('death_loops'):
        top_loop = patterns['death_loops'][0]
        print(f"\n🔄 Top Death Loop:")
        print(f"   {top_loop.app_a} ↔ {top_loop.app_b}")
        print(f"   Occurrences: {top_loop.occurrences}")
        print(f"   Time lost: {top_loop.total_time_lost/60:.1f} minutes")
        print(f"   Severity: {top_loop.severity_score:.1f}/100")
    
    if patterns.get('context_switches'):
        switches = patterns['context_switches']
        print(f"\n🔀 Context Switching:")
        print(f"   Switches per day: {switches['switches_per_day']:.0f}")
        print(f"   Daily loss: {switches['estimated_daily_loss_minutes']:.1f} minutes")
        print(f"   Severity: {switches['context_switch_severity']}")
    
    detective.close()
    
    return patterns, insights

async def demonstrate_subagent_architecture():
    """
    Demonstrates the proper Claude Code SDK sub-agent architecture
    Shows how agents should be spawned via Task tool
    """
    print("\n" + "="*70)
    print("🤖 CLAUDE CODE SDK SUB-AGENT ARCHITECTURE")
    print("="*70 + "\n")
    
    orchestrator = ClaudeOrchestrator()
    
    # This demonstrates the structure - actual implementation would use Task tool
    db_path = "data/knowledgeC_copy.db"
    results = await orchestrator.analyze_death_loops(db_path, days=7)
    
    print("\n📝 Sub-Agent Prompts Generated:")
    print("   These prompts would be used with the Task tool")
    print("   to spawn specialized sub-agents\n")
    
    for phase, config in results.items():
        if isinstance(config, dict) and 'agent_type' in config:
            print(f"🎯 {config['agent_type']}:")
            print(f"   Description: {config['description']}")
            print(f"   Status: {config['status']}")
            print()
    
    return results

def generate_task_tool_examples():
    """
    Generate example Task tool invocations for sub-agents
    """
    print("\n" + "="*70)
    print("📦 TASK TOOL INVOCATION EXAMPLES")
    print("="*70 + "\n")
    
    examples = [
        {
            "tool": "Task",
            "parameters": {
                "subagent_type": "general-purpose",
                "description": "Analyze death loops",
                "prompt": """As the Pattern Detective sub-agent, analyze the Screen Time database at data/knowledgeC_copy.db. 
                Find death loops (rapid A→B→A app switches), temporal patterns, and context switching metrics. 
                Use SQL queries directly on the database (macOS timestamps need +978307200). 
                Return structured findings with severity scores."""
            }
        },
        {
            "tool": "Task",
            "parameters": {
                "subagent_type": "general-purpose",
                "description": "Learn user context",
                "prompt": """As the Context Learner sub-agent, analyze these patterns to understand the user's work style. 
                Determine their profession, productive vs unproductive apps for THEM specifically, 
                work schedule, and unique workflow characteristics. 
                Don't make generic assumptions - learn from their actual usage."""
            }
        },
        {
            "tool": "Task",
            "parameters": {
                "subagent_type": "general-purpose",
                "description": "Design interventions",
                "prompt": """As the Intervention Architect sub-agent, design personalized interventions. 
                Create smart nudges that don't break productive flow, use psychological principles, 
                and are technically implementable with Hammerspoon. 
                Be creative - think beyond simple app blocking."""
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"🎯 Example {i}: {example['parameters']['description']}")
        print(f"   Tool: {example['tool']}")
        print(f"   Subagent Type: {example['parameters']['subagent_type']}")
        print(f"   Prompt Preview: {example['parameters']['prompt'][:150]}...")
        print()
    
    return examples

def main():
    """
    Main execution function
    """
    print("🚀 AUTOMATION ASSASSIN - Death Loop Analysis")
    print("   Using Claude Code SDK Multi-Agent Architecture\n")
    
    # Step 1: Run Pattern Detective directly to verify functionality
    patterns, insights = run_pattern_detective_directly()
    
    if patterns:
        # Step 2: Demonstrate sub-agent architecture
        asyncio.run(demonstrate_subagent_architecture())
        
        # Step 3: Show Task tool examples
        examples = generate_task_tool_examples()
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE")
        print("="*70)
        print("\n💡 Key Insights:")
        print("   1. Pattern Detective found real death loops in your data")
        print("   2. Sub-agents are ready to be spawned via Task tool")
        print("   3. Each agent specializes in one aspect of the analysis")
        print("   4. Orchestration happens through Task tool invocations")
        print("\n🔗 Next Steps:")
        print("   Use the Task tool with the prompts above to spawn sub-agents")
        print("   Each agent will contribute its specialized analysis")
        print("   The orchestrator will coordinate and synthesize results")
    else:
        print("❌ No data found. Please ensure knowledgeC_copy.db exists in data/")

if __name__ == "__main__":
    main()