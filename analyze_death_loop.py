#!/usr/bin/env python3
"""
Deep Analysis of Safari ↔ Telegram Death Loop
Provides detailed context about what's happening in these switches
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from urllib.parse import urlparse
import json

class DeathLoopAnalyzer:
    """Analyzes death loops in detail"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.screentime_db = self.base_path / "tests" / "fixtures" / "screentime_test.db"
        self.safari_db = self.base_path / "tests" / "fixtures" / "safari_history.db"
        self.chrome_db = self.base_path / "tests" / "fixtures" / "chrome_history.db"
        
    def analyze_safari_telegram_loop(self, days=30):
        """Analyze the Safari ↔ Telegram death loop in detail"""
        
        print("=" * 80)
        print("🔍 DEEP DIVE: Safari ↔ Telegram Death Loop Analysis")
        print("=" * 80)
        
        # 1. Get all app switches involving Safari and Telegram
        switches = self.get_app_switches(days)
        safari_telegram_switches = self.filter_safari_telegram(switches)
        
        print(f"\n📊 Basic Statistics (Last {days} days):")
        print(f"  • Total Safari ↔ Telegram switches: {len(safari_telegram_switches)}")
        print(f"  • Average per day: {len(safari_telegram_switches) / days:.1f}")
        print(f"  • Average per hour (assuming 10 active hours): {len(safari_telegram_switches) / (days * 10):.1f}")
        
        # 2. Analyze timing patterns
        self.analyze_timing_patterns(safari_telegram_switches)
        
        # 3. Analyze session durations
        self.analyze_session_durations(safari_telegram_switches)
        
        # 4. Get browser context - what websites are visited
        self.analyze_browser_context(safari_telegram_switches)
        
        # 5. Identify specific patterns
        self.identify_patterns(safari_telegram_switches)
        
        # 6. Root cause hypothesis
        self.generate_hypothesis(safari_telegram_switches)
        
    def get_app_switches(self, days):
        """Get all app switching data"""
        conn = sqlite3.connect(str(self.screentime_db))
        
        # Calculate date range
        MACOS_EPOCH_OFFSET = 978307200
        end_timestamp = datetime.now().timestamp() - MACOS_EPOCH_OFFSET
        start_timestamp = end_timestamp - (days * 86400)
        
        query = """
        SELECT 
            ZSTARTDATE as start_time,
            ZENDDATE as end_time,
            ZVALUESTRING as app_name,
            (ZENDDATE - ZSTARTDATE) as duration
        FROM ZOBJECT 
        WHERE ZSTREAMNAME = '/app/usage'
            AND ZSTARTDATE >= ?
            AND ZSTARTDATE <= ?
            AND ZVALUESTRING IS NOT NULL
        ORDER BY ZSTARTDATE
        """
        
        df = pd.read_sql_query(query, conn, params=(start_timestamp, end_timestamp))
        conn.close()
        
        # Convert timestamps
        df['start_time'] = df['start_time'].apply(lambda x: datetime.fromtimestamp(x + MACOS_EPOCH_OFFSET))
        df['end_time'] = df['end_time'].apply(lambda x: datetime.fromtimestamp(x + MACOS_EPOCH_OFFSET))
        
        # Find switches
        switches = []
        for i in range(len(df) - 1):
            curr = df.iloc[i]
            next_app = df.iloc[i + 1]
            
            # If apps switched within 5 seconds, it's a switch
            time_gap = (next_app['start_time'] - curr['end_time']).total_seconds()
            if time_gap < 5:
                switches.append({
                    'from_app': curr['app_name'],
                    'to_app': next_app['app_name'],
                    'switch_time': curr['end_time'],
                    'from_duration': curr['duration'],
                    'to_duration': next_app['duration'],
                    'hour': curr['end_time'].hour,
                    'weekday': curr['end_time'].weekday()
                })
        
        return switches
    
    def filter_safari_telegram(self, switches):
        """Filter for Safari ↔ Telegram switches"""
        safari_telegram = []
        
        for switch in switches:
            if ('Safari' in switch['from_app'] and 'Telegram' in switch['to_app']) or \
               ('Telegram' in switch['from_app'] and 'Safari' in switch['to_app']):
                safari_telegram.append(switch)
        
        return safari_telegram
    
    def analyze_timing_patterns(self, switches):
        """Analyze when these switches happen"""
        print("\n⏰ Timing Analysis:")
        
        # Hour distribution
        hours = Counter(s['hour'] for s in switches)
        peak_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print("  Peak switching hours:")
        for hour, count in peak_hours:
            bar = "█" * (count // 2)
            print(f"    {hour:02d}:00 {bar} {count} switches")
        
        # Weekday distribution
        weekdays = Counter(s['weekday'] for s in switches)
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        print("\n  By day of week:")
        for day, count in sorted(weekdays.items()):
            bar = "█" * (count // 5)
            print(f"    {day_names[day]:3} {bar} {count} switches")
    
    def analyze_session_durations(self, switches):
        """Analyze how long each app is used before switching"""
        print("\n⏱️ Session Duration Analysis:")
        
        safari_durations = []
        telegram_durations = []
        
        for switch in switches:
            if 'Safari' in switch['from_app']:
                safari_durations.append(switch['from_duration'])
            else:
                telegram_durations.append(switch['from_duration'])
        
        if safari_durations:
            print(f"  Safari sessions before switching:")
            print(f"    • Average: {sum(safari_durations)/len(safari_durations):.1f} seconds")
            print(f"    • Median: {sorted(safari_durations)[len(safari_durations)//2]:.1f} seconds")
            print(f"    • Shortest: {min(safari_durations):.1f} seconds")
            print(f"    • Longest: {max(safari_durations):.1f} seconds")
        
        if telegram_durations:
            print(f"\n  Telegram sessions before switching:")
            print(f"    • Average: {sum(telegram_durations)/len(telegram_durations):.1f} seconds")
            print(f"    • Median: {sorted(telegram_durations)[len(telegram_durations)//2]:.1f} seconds")
            print(f"    • Shortest: {min(telegram_durations):.1f} seconds")
            print(f"    • Longest: {max(telegram_durations):.1f} seconds")
    
    def analyze_browser_context(self, switches):
        """Analyze what websites are visited during these switches"""
        print("\n🌐 Browser Context Analysis:")
        
        # Load Safari history
        conn = sqlite3.connect(str(self.safari_db))
        
        query = """
        SELECT url, visit_count
        FROM history_items
        ORDER BY visit_count DESC
        LIMIT 100
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Categorize URLs
        categories = defaultdict(list)
        domains = Counter()
        
        for _, row in df.iterrows():
            url = row['url']
            title = ''
            
            if url:
                domain = urlparse(url).netloc
                domains[domain] += row['visit_count']
                
                # Categorize
                if 'github.com' in domain:
                    categories['Development'].append(url)
                elif 'stackoverflow.com' in domain:
                    categories['Development'].append(url)
                elif 'twitter.com' in domain or 'x.com' in domain:
                    categories['Social Media'].append(url)
                elif 'youtube.com' in domain:
                    categories['Entertainment'].append(url)
                elif 'gmail.com' in domain or 'mail.google' in domain:
                    categories['Communication'].append(url)
                elif 'localhost' in domain or '127.0.0.1' in domain:
                    categories['Local Development'].append(url)
                elif 'claude.ai' in domain or 'anthropic.com' in domain:
                    categories['AI Tools'].append(url)
                elif 'news' in domain or 'reddit.com' in domain:
                    categories['News/Forums'].append(url)
                else:
                    categories['Other'].append(url)
        
        print("  Top domains visited (by frequency):")
        for domain, count in list(domains.most_common(10)):
            if domain:  # Skip empty domains
                print(f"    • {domain}: {count} visits")
        
        print("\n  Activity categories:")
        for category, urls in sorted(categories.items()):
            print(f"    • {category}: {len(urls)} unique pages")
            # Show sample URL
            if urls and len(urls) > 0:
                sample = urls[0][:60] + "..." if len(urls[0]) > 60 else urls[0]
                print(f"      Example: {sample}")
    
    def identify_patterns(self, switches):
        """Identify specific behavioral patterns"""
        print("\n🎯 Behavioral Patterns Identified:")
        
        # Quick check pattern (< 10 seconds in Telegram)
        quick_checks = [s for s in switches if 'Telegram' in s['from_app'] and s['from_duration'] < 10]
        if quick_checks:
            print(f"  • Quick message checks: {len(quick_checks)} times")
            print(f"    (Opening Telegram for < 10 seconds, likely checking for new messages)")
        
        # Research interruption pattern (long Safari session interrupted)
        long_safari = [s for s in switches if 'Safari' in s['from_app'] and s['from_duration'] > 120]
        if long_safari:
            print(f"  • Research interruptions: {len(long_safari)} times")
            print(f"    (Safari sessions > 2 minutes interrupted by Telegram)")
        
        # Rapid switching (multiple switches within 1 minute)
        rapid_switches = []
        for i in range(len(switches) - 1):
            if (switches[i+1]['switch_time'] - switches[i]['switch_time']).total_seconds() < 60:
                rapid_switches.append(switches[i])
        
        if rapid_switches:
            print(f"  • Rapid switching episodes: {len(rapid_switches)} times")
            print(f"    (Multiple switches within 60 seconds - high distraction state)")
        
        # Morning routine pattern (first hour of day)
        morning = [s for s in switches if s['hour'] in [8, 9, 10]]
        if morning:
            print(f"  • Morning routine switches: {len(morning)} times")
            print(f"    (Happening during typical morning hours)")
    
    def generate_hypothesis(self, switches):
        """Generate hypothesis about the root cause"""
        print("\n💡 Root Cause Hypothesis:")
        
        # Calculate metrics
        safari_switches = [s for s in switches if 'Safari' in s['from_app']]
        telegram_switches = [s for s in switches if 'Telegram' in s['from_app']]
        
        avg_safari_duration = sum(s['from_duration'] for s in safari_switches) / len(safari_switches) if safari_switches else 0
        avg_telegram_duration = sum(s['from_duration'] for s in telegram_switches) / len(telegram_switches) if telegram_switches else 0
        
        print("\n  Based on the analysis, this pattern likely represents:")
        
        if avg_telegram_duration < 30:
            print("  ✓ FOMO-driven message checking")
            print("    - Quick Telegram checks (< 30s average)")
            print("    - Fear of missing important messages")
            print("    - Interrupting focused work to stay connected")
        
        if avg_safari_duration > 60:
            print("\n  ✓ Research/work interrupted by social needs")
            print("    - Productive Safari sessions being interrupted")
            print("    - Social connection seeking during cognitive load")
            print("    - Using Telegram as a mental break from complex tasks")
        
        # Time-based patterns
        work_hours = [s for s in switches if 9 <= s['hour'] <= 18]
        if len(work_hours) > len(switches) * 0.7:
            print("\n  ✓ Work-time distraction pattern")
            print("    - 70%+ happening during work hours")
            print("    - Mixing personal communication with work tasks")
            print("    - Possible remote work isolation compensation")
        
        print("\n📝 Recommended Interventions:")
        print("  1. Batch Processing: Check Telegram at scheduled times (e.g., every 2 hours)")
        print("  2. Focus Mode: Use macOS Focus mode to silence Telegram during deep work")
        print("  3. Window Management: Keep both apps open side-by-side to reduce switching")
        print("  4. Notification Tuning: Disable non-urgent Telegram notifications")
        print("  5. Pomodoro Integration: Check messages only during Pomodoro breaks")

if __name__ == "__main__":
    analyzer = DeathLoopAnalyzer()
    analyzer.analyze_safari_telegram_loop(days=30)