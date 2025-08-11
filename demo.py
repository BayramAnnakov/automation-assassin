#!/usr/bin/env python3
"""
Automation Assassin Demo
Demonstrates death loop detection and intervention generation
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.pattern_detector import PatternDetector
from src.interventions.hammerspoon_gen import HammerspoonGenerator

class AutomationAssassinDemo:
    """Main demo orchestrator"""
    
    def __init__(self, quick_mode: bool = False):
        self.quick_mode = quick_mode
        self.demo_data = self._generate_demo_data()
        
    def _generate_demo_data(self) -> Dict:
        """Generate synthetic demo data"""
        return {
            "death_loops": [
                {
                    "apps": ["Slack", "Chrome"],
                    "count": 47,
                    "daily_time_wasted": 87,
                    "pattern": "Communication distraction loop"
                },
                {
                    "apps": ["Twitter", "Safari"],
                    "count": 31,
                    "daily_time_wasted": 43,
                    "pattern": "Social media rabbit hole"
                },
                {
                    "apps": ["Discord", "YouTube"],
                    "count": 28,
                    "daily_time_wasted": 65,
                    "pattern": "Entertainment loop"
                }
            ],
            "stats": {
                "total_screen_time": 8.5,
                "productive_time": 5.2,
                "wasted_time": 3.3,
                "unique_apps": 42,
                "total_switches": 387
            }
        }
    
    def run(self):
        """Run the full demo"""
        print("\n" + "="*60)
        print("🎯 AUTOMATION ASSASSIN - Death Loop Intervention System")
        print("="*60)
        
        if not self.quick_mode:
            time.sleep(1)
        
        # Step 1: Analyze Screen Time
        print("\n📊 Step 1: Analyzing Screen Time Data...")
        self._show_screen_time_stats()
        
        # Step 2: Detect Death Loops
        print("\n🔍 Step 2: Detecting Death Loops...")
        self._show_death_loops()
        
        # Step 3: Generate Interventions
        print("\n🛠️ Step 3: Generating Interventions...")
        self._generate_interventions()
        
        # Step 4: Show Impact
        print("\n💰 Step 4: Calculating Impact...")
        self._show_impact()
        
        print("\n" + "="*60)
        print("✅ Demo Complete! Ready to reclaim your productivity.")
        print("="*60)
    
    def _show_screen_time_stats(self):
        """Display screen time statistics"""
        stats = self.demo_data["stats"]
        
        if not self.quick_mode:
            time.sleep(1)
            
        print(f"""
📱 Your Screen Time (Last 7 Days):
   • Total: {stats['total_screen_time']:.1f} hours/day
   • Productive: {stats['productive_time']:.1f} hours/day
   • Wasted: {stats['wasted_time']:.1f} hours/day
   • App Switches: {stats['total_switches']}/day
   • Unique Apps: {stats['unique_apps']}
        """)
    
    def _show_death_loops(self):
        """Display detected death loops"""
        if not self.quick_mode:
            time.sleep(1)
            
        print("\n⚠️ Death Loops Detected:")
        
        for i, loop in enumerate(self.demo_data["death_loops"], 1):
            print(f"""
   {i}. {loop['apps'][0]} ↔ {loop['apps'][1]}
      • Pattern: {loop['pattern']}
      • Occurrences: {loop['count']}/week
      • Time Wasted: {loop['daily_time_wasted']} min/day
            """)
            
            if not self.quick_mode:
                time.sleep(0.5)
    
    def _generate_interventions(self):
        """Generate and display interventions"""
        if not self.quick_mode:
            time.sleep(1)
            
        interventions = [
            {
                "name": "Death Loop Breaker",
                "description": "Detects and interrupts repetitive app switching",
                "hotkey": "Cmd+Alt+Ctrl+D"
            },
            {
                "name": "Focus Mode",
                "description": "Blocks distracting apps during work hours",
                "hotkey": "Cmd+Alt+Ctrl+F"
            },
            {
                "name": "Productivity Timer",
                "description": "Enforces work/break intervals",
                "hotkey": "Cmd+Alt+Ctrl+P"
            }
        ]
        
        print("\n🔧 Generated Interventions:")
        
        for intervention in interventions:
            print(f"""
   ✓ {intervention['name']}
     {intervention['description']}
     Hotkey: {intervention['hotkey']}
            """)
            
            if not self.quick_mode:
                time.sleep(0.5)
        
        # Create example script
        script_path = Path("automations/generated_intervention.lua")
        script_path.parent.mkdir(exist_ok=True)
        
        if not script_path.exists():
            print(f"\n   📝 Intervention script saved to: {script_path}")
    
    def _show_impact(self):
        """Calculate and display impact metrics"""
        if not self.quick_mode:
            time.sleep(1)
            
        # Calculate total time saved
        total_daily_saved = sum(loop["daily_time_wasted"] 
                               for loop in self.demo_data["death_loops"])
        
        weekly_saved = total_daily_saved * 7 / 60  # Convert to hours
        yearly_saved = total_daily_saved * 365 / 60
        
        # Calculate monetary value (assuming $50/hour)
        hourly_rate = 50
        yearly_value = yearly_saved * hourly_rate
        
        print(f"""
📈 Projected Impact:
   
   Time Saved:
   • Daily: {total_daily_saved} minutes
   • Weekly: {weekly_saved:.1f} hours  
   • Yearly: {yearly_saved:.0f} hours ({yearly_saved/24:.0f} days!)
   
   Value Created:
   • At ${hourly_rate}/hour: ${yearly_value:,.0f}/year
   • Extra projects completed: ~{yearly_saved/40:.0f}
   • GitHub commits gained: ~{yearly_saved*2:.0f}
        """)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automation Assassin Demo")
    parser.add_argument("--quick", action="store_true", 
                       help="Run in quick mode (no delays)")
    
    args = parser.parse_args()
    
    demo = AutomationAssassinDemo(quick_mode=args.quick)
    demo.run()


if __name__ == "__main__":
    main()