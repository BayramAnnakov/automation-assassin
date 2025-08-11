#!/usr/bin/env python3
"""
Extract real Screen Time and browser history data for testing
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agents.pattern_detective import PatternDetective
from core.browser_history_reader import BrowserHistoryReader
from core.pattern_detector import PatternDetector

def extract_real_patterns():
    """Extract real app switching patterns from Screen Time database"""
    
    print("Extracting real Screen Time patterns...")
    
    # Copy the database first
    os.system("cp ~/Library/Application\\ Support/Knowledge/knowledgeC.db /tmp/screentime_test.db 2>/dev/null")
    
    if not os.path.exists("/tmp/screentime_test.db"):
        print("Could not access Screen Time database")
        return None
        
    # Use Pattern Detective to find real patterns
    detective = PatternDetective("/tmp/screentime_test.db")
    
    # Get recent patterns (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    patterns = detective.find_death_loops(
        start_date=start_date,
        end_date=end_date,
        min_occurrences=10
    )
    
    # Extract top patterns
    real_patterns = []
    for pattern in patterns[:5]:  # Top 5 patterns
        real_patterns.append({
            "app_a": pattern.app_a,
            "app_b": pattern.app_b,
            "occurrences": pattern.occurrences,
            "avg_gap_seconds": pattern.avg_gap_seconds,
            "total_time_lost": pattern.total_time_lost,
            "work_hour_percentage": pattern.work_hour_percentage,
            "peak_hours": pattern.peak_hours
        })
    
    print(f"Found {len(real_patterns)} real patterns")
    return real_patterns

def extract_real_browser_history():
    """Extract real browser history data"""
    
    print("Extracting real browser history...")
    
    reader = BrowserHistoryReader()
    browser_data = {}
    
    # Try to get Safari history
    try:
        safari_history = reader.get_browser_context(
            "safari",
            datetime.now() - timedelta(hours=2),
            datetime.now()
        )
        if safari_history:
            browser_data["safari"] = safari_history
            print(f"Found {len(safari_history)} Safari history items")
    except Exception as e:
        print(f"Could not get Safari history: {e}")
    
    # Try to get Chrome history
    try:
        chrome_history = reader.get_browser_context(
            "chrome",
            datetime.now() - timedelta(hours=2),
            datetime.now()
        )
        if chrome_history:
            browser_data["chrome"] = chrome_history
            print(f"Found {len(chrome_history)} Chrome history items")
    except Exception as e:
        print(f"Could not get Chrome history: {e}")
    
    return browser_data

def create_real_test_data():
    """Create test data file with real user data"""
    
    print("\n=== Extracting Real User Data for Testing ===\n")
    
    # Extract patterns
    patterns = extract_real_patterns()
    
    # Extract browser history
    browser_history = extract_real_browser_history()
    
    # Combine into test data
    test_data = {
        "patterns": patterns or [],
        "browser_history": browser_history or {},
        "extraction_time": datetime.now().isoformat(),
        "user_profile": {
            "profession": "detected_from_apps",  # Will be detected by agents
            "work_hours": "9-17",  # Default assumption
            "peak_productivity": "10-12"  # Default assumption
        }
    }
    
    # Save to file
    output_path = Path(__file__).parent / "fixtures" / "real_user_data.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(test_data, f, indent=2, default=str)
    
    print(f"\nSaved real test data to {output_path}")
    
    # Print summary
    print("\n=== Data Summary ===")
    print(f"Patterns found: {len(test_data['patterns'])}")
    if test_data['patterns']:
        print("\nTop patterns:")
        for i, p in enumerate(test_data['patterns'][:3], 1):
            print(f"  {i}. {p['app_a']} ↔ {p['app_b']} ({p['occurrences']} times)")
    
    print(f"\nBrowser history:")
    for browser, history in test_data['browser_history'].items():
        print(f"  {browser}: {len(history)} items")
    
    return test_data

if __name__ == "__main__":
    data = create_real_test_data()
    
    # Clean up temp file
    if os.path.exists("/tmp/screentime_test.db"):
        os.remove("/tmp/screentime_test.db")