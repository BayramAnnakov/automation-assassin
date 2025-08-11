#!/usr/bin/env python3
"""
Automation Assassin - Automated Demo (Non-Interactive)
Simulates user responses for demonstration purposes
"""

import os
import sys
import asyncio

# Add parent directory to path to import the interactive demo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the interactive demo module
from demo_interactive_streaming import (
    InteractiveOrchestrator, RealDataLoader, UserInteractionManager,
    StreamEvent, Pattern, UserProfile, RootCauseType, InterventionType
)


class AutoUserInteractionManager(UserInteractionManager):
    """Automated version that simulates user responses"""
    
    def __init__(self, days_analyzed: int = 30):
        super().__init__(days_analyzed)
    
    async def get_intervention_preferences(self, root_cause: RootCauseType, pattern: Pattern) -> list:
        """Simulate choosing intervention preferences"""
        print(f"\n{'='*60}")
        print(f"🔍 Root Cause Analysis Complete")
        print(f"   Pattern: {pattern.apps[0]} ↔ {pattern.apps[1]}")
        print(f"   Root Cause: {root_cause.value.replace('_', ' ').title()}")
        
        # Map root causes to appropriate intervention types
        intervention_map = {
            RootCauseType.STRESS_RESPONSE: [InterventionType.STRESS_MANAGEMENT, InterventionType.GENTLE_NUDGE],
            RootCauseType.KNOWLEDGE_GAP: [InterventionType.EDUCATION, InterventionType.SKILL_BUILDING],
            RootCauseType.HABIT_FORMATION: [InterventionType.GENTLE_NUDGE, InterventionType.AUTOMATION],
            RootCauseType.COGNITIVE_OVERLOAD: [InterventionType.AUTOMATION, InterventionType.ENVIRONMENTAL],
            RootCauseType.EMOTIONAL_REGULATION: [InterventionType.COACHING, InterventionType.STRESS_MANAGEMENT],
        }
        
        selected = intervention_map.get(root_cause, [InterventionType.GENTLE_NUDGE])
        
        print(f"\n[AUTOMATED] Selecting interventions based on root cause:")
        for itype in selected:
            print(f"  → {itype.value.replace('_', ' ').title()}")
        
        return selected
    
    async def get_user_info(self) -> UserProfile:
        """Simulate getting user info"""
        print("\n[AUTOMATED] Simulating user responses...")
        print("  → Profession: Software Developer")
        print("  → Work style: Deep focus with collaboration")
        print("  → Productive apps: Cursor IDE, Terminal, GitHub")
        print("  → Distraction apps: Twitter, YouTube, Discord")
        print("  → Optimal hours: 9-11am, 2-4pm")
        print("  → Stress indicators: Rapid app switching, social media loops")
        
        return UserProfile(
            profession="Software Developer",
            work_style="Deep focus with collaboration",
            confidence=0.9,
            productive_apps=["Cursor IDE", "Terminal", "GitHub Desktop", "VS Code", "Chrome"],
            distraction_apps=["Twitter", "YouTube", "Discord", "Reddit"],
            optimal_hours=[9, 10, 11, 14, 15, 16],
            stress_indicators=["rapid_switching", "social_media_loops", "documentation_searches"]
        )
    
    async def get_pattern_context(self, pattern: Pattern) -> str:
        """Simulate providing context for a pattern"""
        print(f"\n[AUTOMATED] Providing context for pattern: {' ↔ '.join(pattern.apps[:2])}")
        
        # Simulate different contexts based on apps
        contexts = {
            ("Chrome", "Notes"): "Taking notes while researching documentation",
            ("Safari", "Notes"): "Documenting findings from web research",
            ("Slack", "Chrome"): "Looking up information during team discussions",
            ("Cursor IDE", "Chrome"): "Searching for coding solutions and documentation",
            ("Safari", "Slack"): "Sharing links with team members",
            ("Notes", "Cursor IDE"): "Implementing ideas from notes",
        }
        
        # Get key for lookup
        key = tuple(pattern.apps[:2])
        reverse_key = tuple(reversed(pattern.apps[:2]))
        
        context = contexts.get(key) or contexts.get(reverse_key) or "Context switching due to unclear task"
        print(f"  → Context: {context}")
        
        return context
    
    def choose_intervention(self, interventions: list) -> list:
        """Simulate choosing interventions"""
        print("\n[AUTOMATED] Selecting interventions...")
        
        # Select first 3 interventions or all if less than 3
        selected = interventions[:min(3, len(interventions))]
        
        for i, intervention in enumerate(selected, 1):
            print(f"  → Selected {i}: {intervention.get('type', 'unknown')}")
        
        return selected
    
    def approve_automation(self, code: str) -> bool:
        """Simulate approving automation"""
        print("\n[AUTOMATED] Reviewing generated Hammerspoon code...")
        print(f"  → Code length: {len(code)} characters")
        print(f"  → Lines: {len(code.splitlines())}")
        print("  → Decision: APPROVED for demonstration")
        
        return True


class AutoInteractiveOrchestrator(InteractiveOrchestrator):
    """Automated version of the orchestrator"""
    
    def __init__(self, verbose: bool = False, days: int = 30):
        super().__init__(verbose, days=days)
        # Replace interaction manager with automated version
        self.interaction_manager = AutoUserInteractionManager(days_analyzed=days)
    
    async def run(self):
        """Run automated analysis"""
        try:
            print(f"\n{self.bold_color}🎯 Automation Assassin - Automated Demo{self.reset_color}")
            print(f"{self.dim_color}Non-interactive demonstration with simulated user responses{self.reset_color}")
            
            # Phase 1: Load real data
            print(f"\n{self.bold_color}━━━ Phase 1: Loading Real Data (Last {self.days_analyzed} Days) ━━━{self.reset_color}")
            print()
            
            if self.data_loader.using_fixtures:
                print("📁 Using test fixture databases")
                print()
            
            screentime_data = self.data_loader.load_screentime_7_days()
            browser_data = self.data_loader.load_browser_history_7_days()
            
            print(f"📊 Screen Time Analysis:")
            print(f"  ✓ {screentime_data.get('total_records', 0):,} records from last {self.days_analyzed} days")
            if screentime_data.get('top_apps'):
                top_apps_str = ", ".join(screentime_data['top_apps'][:5])
                print(f"  ✓ Top apps: {top_apps_str}")
            
            print(f"\n🌐 Browser History Analysis:")
            print(f"  ✓ {browser_data.get('total_visits', 0):,} visits analyzed")
            
            if browser_data.get('categories'):
                print(f"\n  Category breakdown:")
                for category, percentage in browser_data['categories'].items():
                    bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
                    print(f"    {category:15} {bar} {percentage:.1f}%")
            
            # Phase 2: Pattern detection
            print(f"\n{self.bold_color}━━━ Phase 2: AI-Powered Pattern Detection ━━━{self.reset_color}")
            print()
            
            # Combine data for pattern detection
            combined_data = {
                'screentime': screentime_data,
                'browser': browser_data
            }
            
            # Detect patterns with streaming
            await self.detect_patterns_streaming(combined_data)
            
            # Phase 3: User profiling  
            print(f"\n{self.bold_color}━━━ Phase 3: User Profile Building ━━━{self.reset_color}")
            print()
            
            self.user_profile = await self.interaction_manager.get_user_info()
            await self.learn_context_streaming()
            
            # Phase 4: Root cause analysis
            print(f"\n{self.bold_color}━━━ Phase 4: Root Cause Analysis ━━━{self.reset_color}")
            print()
            
            await self.analyze_root_causes()
            
            # Phase 5: Generate interventions
            print(f"\n{self.bold_color}━━━ Phase 5: Holistic Intervention Design ━━━{self.reset_color}")
            print()
            
            await self.design_interventions_interactive()
            
            # Phase 6: Review and deploy
            print(f"\n{self.bold_color}━━━ Phase 6: Review and Deployment ━━━{self.reset_color}")
            print()
            
            # Call parent's review_and_deploy but intercept inputs
            selected = self.interaction_manager.choose_intervention(self.interventions)
            
            if selected:
                print("\n🔨 Generating Hammerspoon automation...")
                code = self.generate_hammerspoon_code(selected)
                
                if self.interaction_manager.approve_automation(code):
                    # Save to file
                    output_path = "automation_assassin_generated.lua"
                    with open(output_path, 'w') as f:
                        f.write(code)
                    
                    print(f"\n✅ Automation saved to: {output_path}")
                    print(f"   To deploy: cp {output_path} ~/.hammerspoon/")
                    print(f"   Then reload: hs -c 'hs.reload()'")
                    
                    # Save key insights
                    insights_path = "automation_assassin_insights.json"
                    insights = {
                        'patterns': len(self.patterns),
                        'user_profile': self.user_profile.profession if self.user_profile else 'Unknown',
                        'interventions': len(selected),
                        'root_causes': list(set(p.root_cause.value for p in self.patterns if p.root_cause))
                    }
                    
                    import json
                    with open(insights_path, 'w') as f:
                        json.dump(insights, f, indent=2)
                    
                    print(f"   Insights saved to: {insights_path}")
                else:
                    print("\n⚠️ Automation not approved")
            
            # Print summary
            self.print_summary()
            
            print(f"\n{self.bold_color}✨ Automated demo complete!{self.reset_color}")
            print("\nKey features demonstrated:")
            print("  ✓ Real 7-day Screen Time data analysis")
            print("  ✓ AI-powered pattern detection") 
            print("  ✓ Root cause identification")
            print("  ✓ Holistic intervention design")
            print("  ✓ Automated Hammerspoon code generation")
            
        except Exception as e:
            print(f"\n❌ Error during automated demo: {e}")
            import traceback
            traceback.print_exc()
            raise


async def main():
    """Main entry point for automated demo"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automation Assassin - Automated Demo",
        epilog="This demo runs without user interaction, simulating responses."
    )
    
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    
    args = parser.parse_args()
    
    # Check for SDK
    try:
        from claude_code_sdk import query, ClaudeCodeOptions
    except ImportError:
        print("❌ Please install claude-code-sdk first:")
        print("   pip install claude-code-sdk")
        sys.exit(1)
    
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not found")
        print("Please ensure .env file exists with: ANTHROPIC_API_KEY=your-key")
        sys.exit(1)
    
    orchestrator = AutoInteractiveOrchestrator(verbose=args.verbose, days=args.days)
    
    try:
        await orchestrator.run()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())