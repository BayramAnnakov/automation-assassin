#!/usr/bin/env python3
"""
Run Pattern Detective analysis on Screen Time data for the last 30 days
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.pattern_detective import PatternDetective
from datetime import datetime
import pandas as pd
import sqlite3

def analyze_screentime_data(db_path: str, days: int = 30):
    """Run comprehensive Screen Time analysis"""
    
    print("\n" + "="*80)
    print("🔍 PATTERN DETECTIVE - SCREEN TIME ANALYSIS")
    print(f"📅 Analyzing {days} days of data (Pacific Time)")
    print("="*80 + "\n")
    
    # Initialize Pattern Detective
    detective = PatternDetective(db_path)
    
    if not detective.connect():
        print("❌ Failed to connect to database")
        return
    
    # Get overall usage statistics first
    print("📊 Gathering usage statistics...\n")
    stats = get_usage_statistics(db_path, days)
    print_usage_statistics(stats)
    
    # Run pattern analysis
    print("\n🔍 Detecting patterns...")
    patterns = detective.analyze_all_patterns(days)
    
    # Get insights
    insights = detective.get_pattern_insights()
    
    # Print Death Loops
    if patterns['death_loops']:
        print("\n" + "="*80)
        print("🔄 DEATH LOOPS - REPETITIVE APP SWITCHING PATTERNS")
        print("="*80)
        
        for i, loop in enumerate(patterns['death_loops'][:10], 1):
            print(f"\n{i}. {loop.app_a} ↔ {loop.app_b}")
            print(f"   📈 Occurrences: {loop.occurrences} times")
            print(f"   ⏱️  Time lost: {loop.total_time_lost/60:.1f} minutes")
            print(f"   🎯 Severity: {loop.severity_score:.1f}/100")
            print(f"   ⏰ Peak hours: {', '.join(f'{h:02d}:00' for h in loop.peak_hours[:3])}")
            print(f"   💼 Work hours: {loop.work_hour_percentage:.1f}%")
    
    # Print Temporal Patterns
    if patterns['temporal_patterns']:
        print("\n" + "="*80)
        print("⏰ TEMPORAL PATTERNS BY HOUR")
        print("="*80)
        
        # Group by pattern type
        distraction_hours = []
        deep_work_hours = []
        
        for pattern in patterns['temporal_patterns']:
            if pattern.pattern_type == 'peak_distraction':
                distraction_hours.append(pattern)
            elif pattern.pattern_type == 'deep_work':
                deep_work_hours.append(pattern)
        
        if distraction_hours:
            print("\n🚨 Peak Distraction Times:")
            for pattern in sorted(distraction_hours, key=lambda x: x.session_count, reverse=True)[:5]:
                bar = "█" * int(pattern.session_count / 10)
                print(f"   {pattern.hour:02d}:00 {bar} {pattern.session_count} sessions")
                print(f"         Apps: {', '.join(pattern.apps_involved[:3])}")
        
        if deep_work_hours:
            print("\n✨ Deep Work Times:")
            for pattern in sorted(deep_work_hours, key=lambda x: x.avg_duration, reverse=True)[:5]:
                print(f"   {pattern.hour:02d}:00 - Avg session: {pattern.avg_duration:.1f}s")
    
    # Print App Clusters
    if patterns['app_clusters']:
        print("\n" + "="*80)
        print("🎯 APP CLUSTERS - FREQUENTLY USED TOGETHER")
        print("="*80)
        
        for i, cluster in enumerate(patterns['app_clusters'][:5], 1):
            print(f"\n{i}. {cluster['type'].replace('_', ' ').title()}:")
            print(f"   Apps: {', '.join(cluster['apps'][:6])}")
    
    # Print Context Switching
    if patterns['context_switches']:
        switches = patterns['context_switches']
        print("\n" + "="*80)
        print("🔀 CONTEXT SWITCHING ANALYSIS")
        print("="*80)
        print(f"\n📊 Total app switches: {switches['total_switches']:,}")
        print(f"📅 Switches per day: {switches['switches_per_day']:.0f}")
        print(f"⏱️  Average session: {switches['avg_session_duration']:.1f} seconds")
        print(f"🚨 Severity level: {switches['context_switch_severity'].upper()}")
        print(f"💸 Est. daily productivity loss: {switches['estimated_daily_loss_minutes']:.1f} minutes")
    
    # Print Insights and Recommendations
    if insights['productivity_recommendations']:
        print("\n" + "="*80)
        print("💡 PERSONALIZED RECOMMENDATIONS")
        print("="*80)
        for i, rec in enumerate(insights['productivity_recommendations'], 1):
            print(f"\n{i}. {rec}")
    
    # Print Summary
    print("\n" + "="*80)
    print("📈 IMPACT SUMMARY")
    print("="*80)
    
    total_time_lost = sum(loop.total_time_lost for loop in patterns['death_loops'][:10])
    print(f"\n⏱️  Time lost to top 10 death loops: {total_time_lost/60:.1f} minutes over {days} days")
    print(f"💰 Potential daily time savings: {total_time_lost/60/days:.1f} minutes")
    print(f"📊 Projected yearly savings: {total_time_lost/60/days*365:.0f} minutes ({total_time_lost/60/days*365/60:.1f} hours)")
    
    detective.close()
    
    return patterns, insights

def get_usage_statistics(db_path: str, days: int):
    """Get overall usage statistics"""
    conn = sqlite3.connect(db_path)
    
    # Calculate date range
    MACOS_EPOCH_OFFSET = 978307200
    end_timestamp = datetime.now().timestamp() - MACOS_EPOCH_OFFSET
    start_timestamp = end_timestamp - (days * 86400)
    
    # Query for top apps
    query = """
    SELECT 
        ZVALUESTRING as app_name,
        COUNT(*) as session_count,
        SUM(ZENDDATE - ZSTARTDATE) as total_seconds,
        AVG(ZENDDATE - ZSTARTDATE) as avg_session_seconds
    FROM ZOBJECT 
    WHERE ZSTREAMNAME = '/app/usage' 
        AND ZSTARTDATE >= ?
        AND ZSTARTDATE <= ?
        AND ZVALUESTRING IS NOT NULL
    GROUP BY ZVALUESTRING
    ORDER BY total_seconds DESC
    LIMIT 20
    """
    
    df = pd.read_sql_query(query, conn, params=(start_timestamp, end_timestamp))
    
    # Get daily usage
    daily_query = """
    SELECT 
        DATE(ZSTARTDATE + 978307200, 'unixepoch', 'localtime') as date,
        SUM(ZENDDATE - ZSTARTDATE) as daily_seconds
    FROM ZOBJECT 
    WHERE ZSTREAMNAME = '/app/usage' 
        AND ZSTARTDATE >= ?
        AND ZSTARTDATE <= ?
        AND ZVALUESTRING IS NOT NULL
    GROUP BY date
    """
    
    daily_df = pd.read_sql_query(daily_query, conn, params=(start_timestamp, end_timestamp))
    
    conn.close()
    
    return {
        'top_apps': df,
        'daily_usage': daily_df,
        'total_sessions': df['session_count'].sum(),
        'unique_apps': len(df)
    }

def print_usage_statistics(stats):
    """Print usage statistics"""
    
    # Clean app names
    app_name_map = {
        'com.apple.Safari': 'Safari',
        'com.google.Chrome': 'Chrome',
        'com.tdesktop.Telegram': 'Telegram',
        'com.todesktop.230313mzl4w4u92': 'Cursor IDE',
        'us.zoom.xos': 'Zoom',
        'com.apple.MobileSMS': 'Messages',
        'com.apple.TextEdit': 'TextEdit',
        'com.hnc.Discord': 'Discord',
        'com.apple.finder': 'Finder',
        'com.apple.TV': 'Apple TV',
        'com.apple.Preview': 'Preview',
        'com.apple.iWork.Keynote': 'Keynote',
        'com.google.chrome.for.testing': 'Chrome Test',
        'com.apple.Terminal': 'Terminal',
        'com.microsoft.VSCode': 'VS Code',
        'com.apple.mail': 'Mail',
        'com.spotify.client': 'Spotify',
        'com.apple.Notes': 'Notes',
        'com.notion.id': 'Notion',
        'com.obsidian.Obsidian': 'Obsidian',
        'com.figma.Desktop': 'Figma',
        'com.apple.systempreferences': 'System Preferences',
        'com.apple.ActivityMonitor': 'Activity Monitor'
    }
    
    print("📱 TOP APPS BY USAGE TIME")
    print("-" * 60)
    
    for idx, row in stats['top_apps'].head(15).iterrows():
        app_name = app_name_map.get(row['app_name'], row['app_name'].split('.')[-1].title())
        hours = row['total_seconds'] / 3600
        sessions = row['session_count']
        avg_minutes = row['avg_session_seconds'] / 60
        
        bar = "█" * int(hours / 2)  # Scale for display
        print(f"{idx+1:2}. {app_name[:25]:25} {bar} {hours:6.1f}h | {sessions:4} sessions | {avg_minutes:5.1f} min/session")
    
    # Daily statistics
    daily_avg = stats['daily_usage']['daily_seconds'].mean() / 3600
    daily_max = stats['daily_usage']['daily_seconds'].max() / 3600
    daily_min = stats['daily_usage']['daily_seconds'].min() / 3600
    
    print(f"\n📊 DAILY USAGE STATISTICS")
    print("-" * 60)
    print(f"Average: {daily_avg:.1f} hours/day")
    print(f"Maximum: {daily_max:.1f} hours")
    print(f"Minimum: {daily_min:.1f} hours")
    print(f"Total sessions: {stats['total_sessions']:,}")
    print(f"Unique apps: {stats['unique_apps']}")

if __name__ == "__main__":
    # Use the copied database
    db_path = os.path.join(os.path.dirname(__file__), "data", "screentime_data.db")
    
    # Analyze 30 days of data
    patterns, insights = analyze_screentime_data(db_path, days=30)