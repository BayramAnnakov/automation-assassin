#!/usr/bin/env python3
"""
Analyze real user data from copied databases
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agents.pattern_detective import PatternDetective
from core.browser_history_reader import BrowserHistoryReader

def analyze_real_patterns():
    """Extract and analyze real patterns from Screen Time database"""
    
    db_path = Path(__file__).parent / "fixtures" / "screentime_test.db"
    
    if not db_path.exists():
        print("Screen Time database not found")
        return []
    
    print("Analyzing real Screen Time patterns...")
    
    detective = PatternDetective(str(db_path))
    detective.connect()  # Establish connection
    
    # Get patterns from last 7 days
    patterns = detective.detect_death_loops(days=7)
    
    # Convert to dict format
    pattern_list = []
    for p in patterns[:10]:  # Top 10 patterns
        pattern_list.append({
            "app_a": p.app_a,
            "app_b": p.app_b,
            "occurrences": p.occurrences,
            "avg_gap_seconds": p.avg_gap_seconds,
            "total_time_lost": p.total_time_lost,
            "work_hour_percentage": p.work_hour_percentage,
            "peak_hours": p.peak_hours
        })
    
    return pattern_list

def analyze_browser_history():
    """Extract real browser history from copied databases"""
    
    browser_data = {}
    fixtures_path = Path(__file__).parent / "fixtures"
    
    # Analyze Safari
    safari_db = fixtures_path / "safari_history.db"
    if safari_db.exists():
        print("Analyzing Safari history...")
        try:
            conn = sqlite3.connect(str(safari_db))
            cursor = conn.cursor()
            
            # Get recent history
            query = """
            SELECT 
                hi.url,
                hv.title,
                hv.visit_time + 978307200 as unix_time
            FROM history_items hi
            JOIN history_visits hv ON hi.id = hv.history_item
            WHERE hv.visit_time > (strftime('%s', 'now') - 978307200 - 86400)
            ORDER BY hv.visit_time DESC
            LIMIT 100
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            safari_history = []
            for url, title, visit_time in results:
                safari_history.append({
                    "url": url,
                    "title": title or "No title",
                    "timestamp": datetime.fromtimestamp(visit_time).isoformat()
                })
            
            browser_data["safari"] = safari_history
            print(f"  Found {len(safari_history)} Safari history items")
            
            conn.close()
        except Exception as e:
            print(f"  Error reading Safari history: {e}")
    
    # Analyze Chrome
    chrome_db = fixtures_path / "chrome_history.db"
    if chrome_db.exists():
        print("Analyzing Chrome history...")
        try:
            conn = sqlite3.connect(str(chrome_db))
            cursor = conn.cursor()
            
            # Chrome uses microseconds since 1601-01-01
            query = """
            SELECT 
                url,
                title,
                last_visit_time
            FROM urls
            WHERE last_visit_time > (strftime('%s', 'now') * 1000000 + 11644473600000000 - 86400000000)
            ORDER BY last_visit_time DESC
            LIMIT 100
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            chrome_history = []
            for url, title, visit_time in results:
                # Convert Chrome timestamp
                unix_time = (visit_time / 1000000) - 11644473600
                chrome_history.append({
                    "url": url,
                    "title": title or "No title",
                    "timestamp": datetime.fromtimestamp(unix_time).isoformat()
                })
            
            browser_data["chrome"] = chrome_history
            print(f"  Found {len(chrome_history)} Chrome history items")
            
            conn.close()
        except Exception as e:
            print(f"  Error reading Chrome history: {e}")
    
    return browser_data

def extract_pattern_context(patterns, browser_data):
    """Create context-rich test cases from real data"""
    
    test_cases = []
    
    for pattern in patterns[:5]:  # Top 5 patterns
        # Find relevant browser history if one app is a browser
        browser_context = None
        browser_app = None
        
        for app in [pattern["app_a"], pattern["app_b"]]:
            if any(browser in app.lower() for browser in ["safari", "chrome", "firefox"]):
                browser_app = app
                break
        
        if browser_app and browser_data:
            # Get the most recent browser history
            if "safari" in browser_app.lower() and "safari" in browser_data:
                history = browser_data["safari"][:10]
            elif "chrome" in browser_app.lower() and "chrome" in browser_data:
                history = browser_data["chrome"][:10]
            else:
                history = []
            
            if history:
                # Extract domains and create context
                domains = {}
                for item in history:
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(item["url"]).netloc
                        domains[domain] = domains.get(domain, 0) + 1
                    except:
                        pass
                
                browser_context = {
                    "history": history[:5],  # Recent 5 items
                    "top_domains": [
                        {"domain": d, "visits": c} 
                        for d, c in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:3]
                    ]
                }
        
        test_case = {
            "pattern": pattern,
            "browser_context": browser_context,
            "current_hour": datetime.now().hour
        }
        
        test_cases.append(test_case)
    
    return test_cases

def save_real_test_data():
    """Main function to extract and save real test data"""
    
    print("\n=== Extracting Real User Data ===\n")
    
    # Extract patterns
    patterns = analyze_real_patterns()
    print(f"\nFound {len(patterns)} app switching patterns")
    
    if patterns:
        print("\nTop 5 patterns:")
        for i, p in enumerate(patterns[:5], 1):
            print(f"  {i}. {p['app_a']} ↔ {p['app_b']}")
            print(f"     Occurrences: {p['occurrences']}, Avg gap: {p['avg_gap_seconds']:.1f}s")
            print(f"     Work hours: {p['work_hour_percentage']:.0f}%, Peak: {p['peak_hours']}")
    
    # Extract browser history
    browser_data = analyze_browser_history()
    
    # Create test cases with context
    test_cases = extract_pattern_context(patterns, browser_data)
    
    # Save to file
    output_data = {
        "patterns": patterns,
        "browser_data": browser_data,
        "test_cases": test_cases,
        "extraction_time": datetime.now().isoformat()
    }
    
    output_path = Path(__file__).parent / "fixtures" / "real_user_data.json"
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n✅ Saved real test data to {output_path}")
    
    # Print sample browser context for verification
    if browser_data:
        print("\nSample browser history:")
        for browser, history in browser_data.items():
            if history:
                print(f"\n{browser.capitalize()} (recent 3):")
                for item in history[:3]:
                    print(f"  - {item['title'][:50]}...")
    
    return output_data

if __name__ == "__main__":
    data = save_real_test_data()
    print(f"\n📊 Ready to test with {len(data['patterns'])} real patterns!")