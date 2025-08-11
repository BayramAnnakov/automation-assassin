#!/usr/bin/env python3
"""
Demo of the Intelligent Pattern Detection System
Shows how it understands productive waiting, multitasking, and real user patterns
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys
import json
from typing import List, Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from src.core.intelligent_pattern_detector import (
    IntelligentPatternDetector, SwitchEvent, SituationContext
)
from src.core.situation_fingerprint import SituationFingerprinter, WorkSituation
from src.core.waiting_detector import WaitingDetector
from src.agents.pattern_interpreter import PatternInterpreter, RealTimeInterpreter
from src.core.adaptive_interventions import (
    AdaptiveInterventionSystem, RootCause, InterventionLevel
)


class IntelligentSystemDemo:
    """Demo showing the evolution from simple to intelligent pattern detection"""
    
    def __init__(self):
        print("=" * 80)
        print("🧠 INTELLIGENT PATTERN DETECTION SYSTEM DEMO")
        print("=" * 80)
        
        # Initialize components
        self.detector = IntelligentPatternDetector()
        self.fingerprinter = SituationFingerprinter()
        self.waiting_detector = WaitingDetector()
        self.interpreter = PatternInterpreter()
        self.intervention_system = AdaptiveInterventionSystem()
        
        # Add user-specific examples based on our discoveries
        self._add_user_examples()
        
    def _add_user_examples(self):
        """Add the specific patterns we discovered about the user"""
        
        # Safari ↔ Telegram is productive multitasking
        self.interpreter.add_user_example(
            pattern="Safari ↔ Telegram rapid switching",
            interpretation="Checking messages while browsing - intentional multitasking",
            is_productive=True,
            context={'apps': ['Safari', 'Telegram'], 'frequency': 185}
        )
        
        # Waiting for Claude Code
        self.interpreter.add_user_example(
            pattern="IDE → Browser/Telegram while Claude processes",
            interpretation="Productive use of waiting time during AI processing",
            is_productive=True,
            context={'trigger': 'claude_code', 'wait_time': 30}
        )
        
        # Evening video multitasking
        self.interpreter.add_user_example(
            pattern="Prime Video + Work apps in evening",
            interpretation="Intentional parallel processing - video for engagement while working",
            is_productive=True,
            context={'time': 'evening', 'apps': ['Prime Video', 'Safari', 'Code']}
        )
        
        # Add to detector too
        self.detector.add_user_example(
            "safari_telegram_switch",
            "Productive multitasking pattern",
            {'count': 185, 'monthly': True}
        )
    
    async def run_demo(self):
        """Run the complete demo"""
        
        print("\n📚 PART 1: THE JOURNEY OF UNDERSTANDING")
        print("-" * 40)
        await self.show_evolution()
        
        print("\n🔍 PART 2: ANALYZING YOUR REAL PATTERNS")
        print("-" * 40)
        await self.analyze_real_patterns()
        
        print("\n🎯 PART 3: INTELLIGENT INTERVENTIONS")
        print("-" * 40)
        await self.demonstrate_interventions()
        
        print("\n📊 PART 4: SYSTEM SUMMARY")
        print("-" * 40)
        self.show_system_summary()
    
    async def show_evolution(self):
        """Show how our understanding evolved"""
        
        print("\n1️⃣ Initial Naive Interpretation:")
        print("   ❌ 'Safari ↔ Telegram 185 times = Death Loop'")
        print("   ❌ 'Rapid switching = Always bad'")
        print("   ❌ 'Need to block distracting apps'")
        
        print("\n2️⃣ First Discovery - Timing Analysis:")
        print("   🔍 99.6% of switches are < 0.5 seconds")
        print("   🔍 34% are bounce-backs (A→B→A)")
        print("   💡 'Maybe these are accidents or reflexes?'")
        
        print("\n3️⃣ Second Discovery - Context Matters:")
        print("   🔍 User watches videos while working (evening pattern)")
        print("   🔍 Switches happen while waiting for Claude Code")
        print("   💡 'This is intentional multitasking!'")
        
        print("\n4️⃣ Final Understanding - Productive Patterns:")
        print("   ✅ Safari ↔ Telegram = Productive multitasking")
        print("   ✅ Rapid switching during AI wait = Efficient time use")
        print("   ✅ Evening video + work = Personal productivity style")
        print("   ✅ Each person has unique productive patterns")
        
        await asyncio.sleep(0.5)
    
    async def analyze_real_patterns(self):
        """Analyze actual user patterns with the new system"""
        
        print("\n🎬 Simulating Your Actual Workflow...")
        
        # Simulate morning work session with Claude Code
        print("\n⏰ Morning: Working with Claude Code")
        
        # Start coding
        event1 = SwitchEvent(
            timestamp=datetime.now(),
            from_app="Desktop",
            to_app="VS Code",
            to_content="automation-assassin project",
            switch_duration=0.2,
            session_duration=0,
            prior_action=None
        )
        situation1 = self.detector.record_switch(event1)
        
        # Trigger Claude Code
        await asyncio.sleep(0.1)
        event2 = SwitchEvent(
            timestamp=datetime.now(),
            from_app="VS Code",
            to_app="VS Code",
            to_content="Claude Code processing...",
            switch_duration=0.1,
            session_duration=45,
            prior_action="ai_query: implement pattern detection"
        )
        situation2 = self.detector.record_switch(event2)
        
        # Switch to Telegram while waiting
        await asyncio.sleep(0.1)
        event3 = SwitchEvent(
            timestamp=datetime.now(),
            from_app="VS Code",
            to_app="Telegram",
            to_content="Work chat",
            switch_duration=0.3,
            session_duration=2,
            prior_action="waiting_for_claude"
        )
        situation3 = self.detector.record_switch(event3)
        
        # Quick Safari check
        await asyncio.sleep(0.1)
        event4 = SwitchEvent(
            timestamp=datetime.now(),
            from_app="Telegram",
            to_app="Safari",
            to_content="github.com",
            switch_duration=0.2,
            session_duration=8,
            prior_action=None
        )
        situation4 = self.detector.record_switch(event4)
        
        # Back to VS Code when Claude is done
        await asyncio.sleep(0.1)
        event5 = SwitchEvent(
            timestamp=datetime.now(),
            from_app="Safari",
            to_app="VS Code",
            to_content="Claude Code complete",
            switch_duration=0.4,
            session_duration=15,
            prior_action="claude_complete"
        )
        situation5 = self.detector.record_switch(event5)
        
        # Interpret the pattern
        print("\n🤖 AI Interpretation of Morning Pattern:")
        
        work_situation = self.fingerprinter.fingerprint_situation(
            "VS Code", "Claude Code processing",
            [event2.__dict__, event3.__dict__, event4.__dict__]
        )
        
        interpretation = await self.interpreter.interpret_pattern(
            situation3, work_situation
        )
        
        print(f"   Pattern: {interpretation.interpretation}")
        print(f"   Assessment: {interpretation.productivity_assessment.upper()}")
        print(f"   Root Cause: {interpretation.root_cause}")
        print(f"   Confidence: {interpretation.confidence:.0%}")
        
        # Evening multitasking pattern
        print("\n🌙 Evening: Multitasking Session")
        
        # Modify time for evening context
        evening_time = datetime.now().replace(hour=20)
        
        # Watching video while working
        event6 = SwitchEvent(
            timestamp=evening_time,
            from_app="Safari",
            to_app="Prime Video",
            to_content="Movie streaming",
            switch_duration=0.5,
            session_duration=120,
            prior_action=None
        )
        situation6 = self.detector.record_switch(event6)
        
        # Quick work check
        event7 = SwitchEvent(
            timestamp=evening_time + timedelta(seconds=30),
            from_app="Prime Video",
            to_app="Safari",
            to_content="Work documentation",
            switch_duration=0.3,
            session_duration=5,
            prior_action=None
        )
        situation7 = self.detector.record_switch(event7)
        
        # Back to video
        event8 = SwitchEvent(
            timestamp=evening_time + timedelta(seconds=35),
            from_app="Safari",
            to_app="Prime Video",
            to_content="Movie streaming",
            switch_duration=0.2,
            session_duration=10,
            prior_action=None
        )
        situation8 = self.detector.record_switch(event8)
        
        print("\n🤖 AI Interpretation of Evening Pattern:")
        
        evening_situation = self.fingerprinter.fingerprint_situation(
            "Prime Video", "Movie streaming",
            [event6.__dict__, event7.__dict__, event8.__dict__]
        )
        
        interpretation2 = await self.interpreter.interpret_pattern(
            situation7, evening_situation
        )
        
        print(f"   Pattern: {interpretation2.interpretation}")
        print(f"   Assessment: {interpretation2.productivity_assessment.upper()}")
        print(f"   Root Cause: {interpretation2.root_cause}")
        print(f"   Confidence: {interpretation2.confidence:.0%}")
        
        # Show pattern summary
        print("\n📈 Pattern Summary:")
        summary = self.detector.get_pattern_summary()
        if 'behavioral_metrics' in summary:
            metrics = summary['behavioral_metrics']
            print(f"   • Switching velocity: {metrics['avg_switching_velocity']:.1f} switches/min")
            print(f"   • Waiting patterns: {metrics['waiting_percentage']*100:.0f}% of time")
            print(f"   • Multitasking: {metrics['multitask_percentage']*100:.0f}% of time")
    
    async def demonstrate_interventions(self):
        """Show how interventions adapt to patterns"""
        
        print("\n🎯 Creating Adaptive Interventions...")
        
        # Productive waiting scenario
        print("\n✅ Scenario 1: Productive Waiting Pattern")
        plan1 = self.intervention_system.create_intervention_plan(
            root_causes=[RootCause.PRODUCTIVE_WAITING],
            user_context={'pattern': 'waiting_for_claude', 'frequency': 'high'},
            urgency="low"
        )
        
        print(f"   Intervention: {plan1.interventions[0].title}")
        print(f"   Level: {plan1.interventions[0].level.value}")
        print(f"   Action Required: {plan1.interventions[0].action_required}")
        
        if plan1.interventions[0].automation_code:
            print("   📝 Automation Available: Smart wait timer")
        
        # Cognitive overload scenario
        print("\n⚠️ Scenario 2: Cognitive Overload Pattern")
        
        # Set intervention preference
        self.intervention_system.user_preferences['preferred_level'] = InterventionLevel.COACHING
        
        plan2 = self.intervention_system.create_intervention_plan(
            root_causes=[RootCause.COGNITIVE_OVERLOAD],
            user_context={'switching_velocity': 12, 'session_depth': 5},
            urgency="high"
        )
        
        if plan2.interventions:
            intervention = plan2.interventions[0]
            print(f"   Intervention: {intervention.title}")
            print(f"   Level: {intervention.level.value}")
            
            if intervention.coaching_message:
                print(f"\n   📢 Coaching Message:")
                for line in intervention.coaching_message.split('\n')[:5]:
                    if line.strip():
                        print(f"      {line}")
        
        # Intentional multitasking
        print("\n🎭 Scenario 3: Intentional Multitasking")
        plan3 = self.intervention_system.create_intervention_plan(
            root_causes=[RootCause.INTENTIONAL_MULTITASK],
            user_context={'pattern': 'video_work', 'time': 'evening'},
            urgency="low"
        )
        
        if plan3.interventions:
            print(f"   Intervention: {plan3.interventions[0].title}")
            print(f"   Message: {plan3.interventions[0].description}")
        
        # Show intervention stats
        print("\n📊 Intervention System Stats:")
        stats = self.intervention_system.get_intervention_stats()
        if 'active_plans' in stats:
            print(f"   • Active plans: {stats['active_plans']}")
            print(f"   • Preferred level: {stats['user_preferences']['preferred_level'].value}")
            print(f"   • Automation comfort: {stats['user_preferences']['automation_comfort']:.0%}")
        else:
            print(f"   • System initialized and ready")
            print(f"   • 3 intervention plans created")
            print(f"   • Adapts to user preferences")
    
    def show_system_summary(self):
        """Show system capabilities summary"""
        
        print("\n🧠 INTELLIGENT SYSTEM CAPABILITIES:")
        print("\n   ✨ Multi-Dimensional Analysis:")
        print("      • Temporal (time of day, patterns)")
        print("      • Behavioral (velocity, depth, bounces)")
        print("      • Intentional (waiting, multitasking)")
        print("      • Environmental (background apps, context)")
        
        print("\n   🎯 Adaptive Understanding:")
        print("      • Learns from user examples")
        print("      • No hardcoded rules")
        print("      • Understands productive waiting")
        print("      • Recognizes intentional multitasking")
        
        print("\n   💡 Context-Aware Interventions:")
        print("      • Addresses root causes, not symptoms")
        print("      • Multiple intervention levels")
        print("      • Personalized to user preferences")
        print("      • Tracks effectiveness over time")
        
        print("\n   🚀 Key Innovations:")
        print("      • Productive waiting detection")
        print("      • Multitasking recognition")
        print("      • AI-powered interpretation")
        print("      • Educational focus over blocking")
        
        print("\n" + "=" * 80)
        print("✅ System ready for any knowledge worker!")
        print("🎯 Flexible, intelligent, and personalized")
        print("=" * 80)


async def main():
    """Run the demo"""
    demo = IntelligentSystemDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())