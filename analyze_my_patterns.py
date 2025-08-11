#!/usr/bin/env python3
"""
Analyze YOUR productivity patterns and generate personalized interventions
Run this after copying your Screen Time data with copy_my_data.sh
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_for_data():
    """Check if user has copied their Screen Time data"""
    if not os.path.exists('user_data/screentime.db'):
        print("❌ No Screen Time data found!")
        print("\nTo analyze your patterns, first copy your data:")
        print("  1. Run: ./copy_my_data.sh")
        print("     OR manually:")
        print("  2. cp ~/Library/Application\\ Support/Knowledge/knowledgeC.db ./user_data/screentime.db")
        print("\nOptionally add browser history:")
        print("  • Safari: cp ~/Library/Safari/History.db ./user_data/safari_history.db")
        print("  • Chrome: cp ~/Library/Application\\ Support/Google/Chrome/Default/History ./user_data/chrome_history.db")
        sys.exit(1)

def analyze_patterns(db_path, days=7):
    """Analyze app switching patterns from Screen Time database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Convert to macOS timestamp (seconds since 2001-01-01)
    start_timestamp = (start_date - datetime(2001, 1, 1)).total_seconds()
    end_timestamp = (end_date - datetime(2001, 1, 1)).total_seconds()
    
    # Query for app usage
    query = """
    SELECT 
        DATETIME(ZSTARTDATE + 978307200, 'unixepoch', 'localtime') as timestamp,
        ZVALUESTRING as app,
        ZSECONDSFROMGMT as duration
    FROM ZOBJECT 
    WHERE ZSTREAMNAME = '/app/usage'
    AND ZSTARTDATE BETWEEN ? AND ?
    ORDER BY ZSTARTDATE
    """
    
    cursor.execute(query, (start_timestamp, end_timestamp))
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        print("⚠️ No app usage data found in the last 7 days.")
        print("Your Screen Time database might be empty or from a different time period.")
        return None
    
    # Analyze switches
    switches = []
    last_app = None
    last_time = None
    bounce_count = 0
    patterns = defaultdict(int)
    app_usage = Counter()
    
    for record in records:
        timestamp = datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S')
        app = normalize_app_name(record[1])
        duration = record[2] if record[2] else 0
        
        app_usage[app] += 1
        
        if last_app and last_app != app:
            time_diff = (timestamp - last_time).total_seconds() if last_time else 0
            switches.append({
                'from': last_app,
                'to': app,
                'time': timestamp,
                'duration': time_diff
            })
            
            # Track patterns
            pattern_key = f"{last_app} → {app}"
            patterns[pattern_key] += 1
            
            # Detect bounces (quick back-and-forth)
            if time_diff < 1.0 and len(switches) > 1:
                if switches[-2]['from'] == app and switches[-2]['to'] == last_app:
                    bounce_count += 1
        
        last_app = app
        last_time = timestamp
    
    total_switches = len(switches)
    bounce_rate = (bounce_count / total_switches * 100) if total_switches > 0 else 0
    
    # Find death loops (most common patterns)
    top_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Calculate time lost
    hours_lost = total_switches * 30 / 3600  # 30 seconds per switch
    
    return {
        'total_switches': total_switches,
        'daily_average': total_switches / days,
        'bounce_count': bounce_count,
        'bounce_rate': bounce_rate,
        'top_patterns': top_patterns,
        'top_apps': app_usage.most_common(10),
        'hours_lost_per_week': hours_lost,
        'patterns': patterns,
        'switches': switches[:100]  # First 100 for analysis
    }

def normalize_app_name(app_name):
    """Normalize app names for consistency"""
    if not app_name:
        return "Unknown"
    
    # Common app name mappings
    mappings = {
        'com.apple.Safari': 'Safari',
        'com.google.Chrome': 'Chrome',
        'com.tinyspeck.slackmacgap': 'Slack',
        'com.microsoft.VSCode': 'VS Code',
        'com.todesktop.230313mzl4w4u92': 'Cursor',
        'com.apple.Terminal': 'Terminal',
        'com.telegram.desktop': 'Telegram',
        'com.spotify.client': 'Spotify',
    }
    
    for key, value in mappings.items():
        if key in app_name:
            return value
    
    # Extract readable name from bundle ID
    if '.' in app_name:
        parts = app_name.split('.')
        return parts[-1].replace('-', ' ').title()
    
    return app_name

def identify_mcp_opportunities(results):
    """Identify which MCP servers could help based on patterns"""
    opportunities = []
    
    patterns = results['patterns']
    top_apps = [app[0] for app in results['top_apps'][:5]]
    
    # Check for web testing pattern (IDE ↔ Browser)
    ide_apps = ['VS Code', 'Cursor', 'Xcode', 'IntelliJ']
    browser_apps = ['Safari', 'Chrome', 'Firefox', 'Edge']
    
    for ide in ide_apps:
        for browser in browser_apps:
            pattern1 = f"{ide} → {browser}"
            pattern2 = f"{browser} → {ide}"
            if patterns.get(pattern1, 0) + patterns.get(pattern2, 0) > 50:
                opportunities.append({
                    'name': 'Puppeteer MCP',
                    'pattern': f'{ide} ↔ {browser}',
                    'count': patterns.get(pattern1, 0) + patterns.get(pattern2, 0),
                    'time_saved': 15,  # minutes per day
                    'description': 'Automate web testing without switching to browser'
                })
                break
    
    # Check for Slack distraction
    if 'Slack' in top_apps:
        slack_switches = sum(v for k, v in patterns.items() if 'Slack' in k)
        if slack_switches > 30:
            opportunities.append({
                'name': 'Slack MCP',
                'pattern': 'Frequent Slack checks',
                'count': slack_switches,
                'time_saved': 20,
                'description': 'Batch Slack messages and reduce interruptions'
            })
    
    # Check for terminal pattern
    if 'Terminal' in top_apps:
        terminal_switches = sum(v for k, v in patterns.items() if 'Terminal' in k)
        if terminal_switches > 40:
            opportunities.append({
                'name': 'Filesystem MCP',
                'pattern': 'Terminal for logs/files',
                'count': terminal_switches,
                'time_saved': 10,
                'description': 'Stream logs and files directly in your IDE'
            })
    
    return opportunities

def generate_report(results):
    """Generate detailed markdown report"""
    if not results:
        return "No data to analyze."
    
    report = f"""# 📊 Your Productivity Analysis Report

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## 😱 The Shocking Truth

In the last 7 days, you:
- **Switched apps {results['total_switches']:,} times** ({results['daily_average']:.0f} per day)
- **{results['bounce_rate']:.1f}% were bounce-backs** (accidental switches)
- **Lost {results['hours_lost_per_week']:.1f} hours** to context switching

That's switching apps every **{86400 / results['daily_average']:.0f} seconds** during your work day!

## 💀 Your Death Loops

Your top app-switching patterns (these are killing your productivity):

"""
    
    for i, (pattern, count) in enumerate(results['top_patterns'], 1):
        daily = count / 7
        report += f"{i}. **{pattern}**: {count} times ({daily:.0f}/day)\n"
    
    report += f"""

## 📱 Most Used Apps

"""
    
    for i, (app, count) in enumerate(results['top_apps'][:10], 1):
        report += f"{i}. {app}: {count} switches\n"
    
    # Add MCP recommendations
    mcp_opps = identify_mcp_opportunities(results)
    if mcp_opps:
        report += f"""

## 🤖 Automation Opportunities

These MCP servers could eliminate your repetitive switches:

"""
        for opp in mcp_opps:
            report += f"""
### {opp['name']}
- **Pattern**: {opp['pattern']} ({opp['count']} times)
- **Time saved**: ~{opp['time_saved']} min/day
- **How it helps**: {opp['description']}
"""
    
    report += f"""

## 💰 The Cost

At $50/hour, your context switching costs you:
- **Daily**: ${results['hours_lost_per_week'] / 7 * 50:.0f}
- **Weekly**: ${results['hours_lost_per_week'] * 50:.0f}
- **Yearly**: ${results['hours_lost_per_week'] * 52 * 50:.0f}

## 🎯 Next Steps

1. Run `python generate_my_interventions.py` to create personalized automations
2. Install Hammerspoon and apply the interventions
3. Watch your productivity soar!

---

*Remember: The goal isn't to never switch apps, it's to eliminate unnecessary switches and make necessary ones more efficient.*
"""
    
    return report

def main():
    print("🔍 Analyzing your app usage patterns...\n")
    
    # Check for data
    check_for_data()
    
    # Analyze patterns
    results = analyze_patterns('user_data/screentime.db')
    
    if not results:
        print("❌ Could not analyze patterns. Check your Screen Time data.")
        sys.exit(1)
    
    # Show summary
    print(f"😱 Holy s***! You switched apps {results['total_switches']:,} times in 7 days!")
    print(f"⚡ {results['bounce_rate']:.1f}% were bounce-backs (accidents)")
    
    if results['top_patterns']:
        top_pattern = results['top_patterns'][0]
        print(f"💀 Your #1 death loop: {top_pattern[0]} ({top_pattern[1]} times)")
    
    print(f"⏰ Time lost to context switching: {results['hours_lost_per_week']:.1f} hours/week")
    print(f"💰 That's worth ${results['hours_lost_per_week'] * 50:.0f}/week at $50/hour")
    
    # Identify MCP opportunities
    mcp_opps = identify_mcp_opportunities(results)
    if mcp_opps:
        print("\n🤖 MCP servers that could help you:")
        for opp in mcp_opps[:3]:
            print(f"   • {opp['name']}: Save ~{opp['time_saved']} min/day")
    
    # Create output directory
    os.makedirs('my_analysis', exist_ok=True)
    
    # Save detailed report
    report = generate_report(results)
    with open('my_analysis/report.md', 'w') as f:
        f.write(report)
    
    # Save raw data for intervention generation
    with open('my_analysis/patterns.json', 'w') as f:
        # Convert to serializable format
        serializable_results = {
            'total_switches': results['total_switches'],
            'daily_average': results['daily_average'],
            'bounce_count': results['bounce_count'],
            'bounce_rate': results['bounce_rate'],
            'top_patterns': results['top_patterns'],
            'top_apps': results['top_apps'],
            'hours_lost_per_week': results['hours_lost_per_week'],
            'patterns': dict(results['patterns'])
        }
        json.dump(serializable_results, f, indent=2)
    
    print("\n✅ Full report saved to: my_analysis/report.md")
    print("📊 Raw data saved to: my_analysis/patterns.json")
    print("\n🚀 Next step: Run 'python generate_my_interventions.py' to create your personalized automations")

if __name__ == "__main__":
    main()