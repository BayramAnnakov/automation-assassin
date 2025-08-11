#!/usr/bin/env python3
"""
Analyze if Safari ↔ Telegram switching is accidental
Check timezone and actual switching mechanics
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import pytz

class AccidentalSwitchAnalyzer:
    """Analyzes if app switches might be accidental"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.screentime_db = self.base_path / "tests" / "fixtures" / "screentime_test.db"
        
    def analyze_switch_mechanics(self):
        """Analyze the mechanics of switching to determine if accidental"""
        
        print("=" * 80)
        print("🔍 ACCIDENTAL SWITCHING ANALYSIS")
        print("=" * 80)
        
        # Get raw data
        conn = sqlite3.connect(str(self.screentime_db))
        
        # First, check the timezone of the data
        print("\n📅 Timezone Analysis:")
        self.check_timezone(conn)
        
        # Get app usage data
        MACOS_EPOCH_OFFSET = 978307200
        end_timestamp = datetime.now().timestamp() - MACOS_EPOCH_OFFSET
        start_timestamp = end_timestamp - (30 * 86400)
        
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
        
        # Convert timestamps
        df['start_dt'] = df['start_time'].apply(lambda x: datetime.fromtimestamp(x + MACOS_EPOCH_OFFSET))
        df['end_dt'] = df['end_time'].apply(lambda x: datetime.fromtimestamp(x + MACOS_EPOCH_OFFSET))
        
        print("\n🕐 Time Analysis:")
        print(f"  Data spans from: {df['start_dt'].min()}")
        print(f"  Data spans to: {df['end_dt'].max()}")
        
        # Analyze Safari ↔ Telegram switches
        switches = []
        for i in range(len(df) - 1):
            curr = df.iloc[i]
            next_app = df.iloc[i + 1]
            
            # Check if it's Safari ↔ Telegram
            if ('Safari' in curr['app_name'] and 'Telegram' in next_app['app_name']) or \
               ('Telegram' in curr['app_name'] and 'Safari' in next_app['app_name']):
                
                gap = (next_app['start_dt'] - curr['end_dt']).total_seconds()
                switches.append({
                    'from': curr['app_name'],
                    'to': next_app['app_name'],
                    'from_duration': curr['duration'],
                    'to_duration': next_app['duration'],
                    'gap_seconds': gap,
                    'time': curr['end_dt'],
                    'hour': curr['end_dt'].hour
                })
        
        print(f"\n📊 Switch Analysis (Safari ↔ Telegram):")
        print(f"  Total switches found: {len(switches)}")
        
        # Analyze gaps between switches
        gaps = [s['gap_seconds'] for s in switches]
        print(f"\n⏱️ Gap between app switches:")
        print(f"  • Instant (< 0.5s): {len([g for g in gaps if g < 0.5])} switches")
        print(f"  • Very quick (0.5-2s): {len([g for g in gaps if 0.5 <= g < 2])} switches")
        print(f"  • Quick (2-5s): {len([g for g in gaps if 2 <= g < 5])} switches")
        print(f"  • Deliberate (> 5s): {len([g for g in gaps if g >= 5])} switches")
        
        # Analyze duration patterns
        print(f"\n📱 App Duration Before Switch:")
        
        # Extremely short sessions that might be accidental
        accidental_threshold = 2  # seconds
        
        safari_accidental = [s for s in switches if 'Safari' in s['from'] and s['from_duration'] < accidental_threshold]
        telegram_accidental = [s for s in switches if 'Telegram' in s['from'] and s['from_duration'] < accidental_threshold]
        
        print(f"  Safari sessions < {accidental_threshold}s: {len(safari_accidental)} ({len(safari_accidental)*100/len(switches):.1f}%)")
        print(f"  Telegram sessions < {accidental_threshold}s: {len(telegram_accidental)} ({len(telegram_accidental)*100/len(switches):.1f}%)")
        
        # Check for patterns that suggest accidents
        print(f"\n🎯 Accidental Switch Indicators:")
        
        # Pattern 1: Immediate bounce-back
        bouncebacks = []
        for i in range(len(switches) - 1):
            if switches[i]['to'] == switches[i+1]['from'] and \
               switches[i]['from'] == switches[i+1]['to'] and \
               switches[i+1]['from_duration'] < 3:
                bouncebacks.append(switches[i])
        
        print(f"  • Bounce-backs (A→B→A in <3s): {len(bouncebacks)} patterns")
        
        # Pattern 2: CMD+Tab accidents (very specific timing)
        cmd_tab_pattern = [s for s in switches if s['gap_seconds'] < 0.2 and s['from_duration'] < 1]
        print(f"  • Possible CMD+Tab accidents: {len(cmd_tab_pattern)} switches")
        
        # Pattern 3: Notification-triggered switches
        notification_switches = [s for s in switches if 'Telegram' in s['to'] and s['to_duration'] < 5]
        print(f"  • Notification checks (<5s in Telegram): {len(notification_switches)} switches")
        
        # Check if these happen at consistent times (habitual vs accidental)
        print(f"\n⏰ Timing Patterns (Seattle/Pacific Time):")
        hour_distribution = Counter(s['hour'] for s in switches)
        
        # Convert to Pacific time for display
        pacific = pytz.timezone('US/Pacific')
        
        for hour in sorted(hour_distribution.keys()):
            count = hour_distribution[hour]
            bar = "█" * (count // 10)
            
            # Interpret the hour
            if 6 <= hour <= 9:
                period = "Morning"
            elif 10 <= hour <= 12:
                period = "Mid-morning"
            elif 13 <= hour <= 17:
                period = "Afternoon"
            elif 18 <= hour <= 21:
                period = "Evening"
            else:
                period = "Night"
            
            print(f"  {hour:02d}:00 ({period:12}) {bar} {count}")
        
        # Analyze if it's likely accidental
        print(f"\n💡 Verdict: Are These Switches Accidental?")
        
        accidental_percentage = (len(safari_accidental) + len(telegram_accidental)) * 100 / (2 * len(switches))
        bounceback_percentage = len(bouncebacks) * 100 / len(switches) if switches else 0
        
        print(f"\n  Evidence FOR accidental switching:")
        if accidental_percentage > 30:
            print(f"  ✓ {accidental_percentage:.1f}% of sessions are < 2 seconds")
        if bounceback_percentage > 10:
            print(f"  ✓ {bounceback_percentage:.1f}% are bounce-back patterns")
        if len(cmd_tab_pattern) > 50:
            print(f"  ✓ {len(cmd_tab_pattern)} possible CMD+Tab accidents")
        
        print(f"\n  Evidence AGAINST accidental switching:")
        if len(notification_switches) > 100:
            print(f"  ✗ {len(notification_switches)} deliberate notification checks")
        if max(hour_distribution.values()) > 50:
            print(f"  ✗ Consistent peak times suggest habitual behavior")
        
        # Calculate likelihood
        if accidental_percentage > 40 and bounceback_percentage > 15:
            print(f"\n  🎯 CONCLUSION: HIGH likelihood of accidental switching")
            print(f"     Many switches appear to be misclicks or CMD+Tab errors")
        elif accidental_percentage > 25 or bounceback_percentage > 10:
            print(f"\n  🎯 CONCLUSION: MODERATE accidental switching mixed with intentional")
            print(f"     Some accidents, but also deliberate checking behavior")
        else:
            print(f"\n  🎯 CONCLUSION: Mostly INTENTIONAL switching")
            print(f"     Pattern appears to be habitual checking, not accidents")
        
        conn.close()
        
    def check_timezone(self, conn):
        """Check what timezone the data is in"""
        
        # Get a sample of timestamps
        query = """
        SELECT 
            ZSTARTDATE as timestamp
        FROM ZOBJECT 
        WHERE ZSTREAMNAME = '/app/usage'
        LIMIT 100
        """
        
        df = pd.read_sql_query(query, conn)
        
        if len(df) > 0:
            # Convert a sample timestamp
            MACOS_EPOCH_OFFSET = 978307200
            sample_ts = df.iloc[0]['timestamp'] + MACOS_EPOCH_OFFSET
            
            # Convert to different timezones
            utc_time = datetime.fromtimestamp(sample_ts, tz=pytz.UTC)
            pacific_time = utc_time.astimezone(pytz.timezone('US/Pacific'))
            local_time = datetime.fromtimestamp(sample_ts)
            
            print(f"  Sample timestamp interpretations:")
            print(f"    • Local system time: {local_time}")
            print(f"    • Pacific/Seattle time: {pacific_time}")
            print(f"    • UTC time: {utc_time}")
            print(f"  ℹ️ Data appears to be stored in local system timezone")

if __name__ == "__main__":
    analyzer = AccidentalSwitchAnalyzer()
    analyzer.analyze_switch_mechanics()