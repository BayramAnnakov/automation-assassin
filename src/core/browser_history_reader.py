"""
Browser History Reader - Extract browser history for pattern context
Reads Safari, Chrome, and Firefox history databases
"""

import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
import shutil
import tempfile

class BrowserHistoryReader:
    """
    Reads browser history from Safari, Chrome, and Firefox
    Provides context for app switching patterns
    """
    
    def __init__(self):
        self.browsers = self._detect_browsers()
        self.temp_dir = tempfile.mkdtemp()
        
    def _detect_browsers(self) -> Dict[str, Path]:
        """Detect installed browsers and their history database paths"""
        browsers = {}
        home = Path.home()
        
        # Safari
        safari_path = home / 'Library' / 'Safari' / 'History.db'
        if safari_path.exists():
            browsers['safari'] = safari_path
            
        # Chrome
        chrome_path = home / 'Library' / 'Application Support' / 'Google' / 'Chrome' / 'Default' / 'History'
        if chrome_path.exists():
            browsers['chrome'] = chrome_path
            
        # Chrome Canary
        canary_path = home / 'Library' / 'Application Support' / 'Google' / 'Chrome Canary' / 'Default' / 'History'
        if canary_path.exists():
            browsers['chrome_canary'] = canary_path
            
        # Firefox
        firefox_dir = home / 'Library' / 'Application Support' / 'Firefox' / 'Profiles'
        if firefox_dir.exists():
            for profile in firefox_dir.glob('*.default*'):
                places_db = profile / 'places.sqlite'
                if places_db.exists():
                    browsers['firefox'] = places_db
                    break
                    
        # Brave
        brave_path = home / 'Library' / 'Application Support' / 'BraveSoftware' / 'Brave-Browser' / 'Default' / 'History'
        if brave_path.exists():
            browsers['brave'] = brave_path
            
        return browsers
    
    def get_browser_context(self, browser_name: str, 
                           start_time: datetime, 
                           end_time: datetime) -> List[Dict]:
        """
        Get browser history for a specific time period
        
        Args:
            browser_name: Name of browser (safari, chrome, firefox)
            start_time: Start of time period
            end_time: End of time period
            
        Returns:
            List of visited URLs with metadata
        """
        browser_name_lower = browser_name.lower()
        
        # Map common browser names to our keys
        browser_map = {
            'safari': 'safari',
            'chrome': 'chrome',
            'google chrome': 'chrome',
            'firefox': 'firefox',
            'brave': 'brave',
            'chrome test': 'chrome',
            'chrome canary': 'chrome_canary'
        }
        
        browser_key = browser_map.get(browser_name_lower)
        if not browser_key or browser_key not in self.browsers:
            return []
            
        db_path = self.browsers[browser_key]
        
        # Copy database to temp location to avoid locks
        temp_db = Path(self.temp_dir) / f"{browser_key}_history.db"
        try:
            shutil.copy2(db_path, temp_db)
        except Exception as e:
            print(f"Could not copy browser history: {e}")
            return []
            
        # Read history based on browser type
        if browser_key in ['chrome', 'chrome_canary', 'brave']:
            return self._read_chrome_history(temp_db, start_time, end_time)
        elif browser_key == 'safari':
            return self._read_safari_history(temp_db, start_time, end_time)
        elif browser_key == 'firefox':
            return self._read_firefox_history(temp_db, start_time, end_time)
        else:
            return []
    
    def _read_chrome_history(self, db_path: Path, 
                           start_time: datetime, 
                           end_time: datetime) -> List[Dict]:
        """Read Chrome/Chromium-based browser history"""
        history = []
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Chrome uses microseconds since 1601-01-01
            chrome_epoch = datetime(1601, 1, 1)
            start_timestamp = int((start_time - chrome_epoch).total_seconds() * 1000000)
            end_timestamp = int((end_time - chrome_epoch).total_seconds() * 1000000)
            
            query = """
                SELECT url, title, visit_count, 
                       last_visit_time, 
                       (last_visit_time - ?) / 1000000 as duration_estimate
                FROM urls
                WHERE last_visit_time >= ? AND last_visit_time <= ?
                ORDER BY last_visit_time DESC
            """
            
            cursor.execute(query, (start_timestamp, start_timestamp, end_timestamp))
            
            for row in cursor.fetchall():
                url, title, visit_count, visit_time, duration = row
                
                # Parse domain from URL
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc or parsed.path
                except:
                    domain = url[:50]
                
                history.append({
                    'url': url,
                    'domain': domain,
                    'title': title or '',
                    'visit_count': visit_count,
                    'timestamp': datetime.fromtimestamp(
                        (visit_time - chrome_epoch.timestamp()) / 1000000
                    ).isoformat() if visit_time else None,
                    'duration_seconds': max(0, min(duration, 3600)) if duration else 30  # Cap at 1 hour
                })
            
            conn.close()
            
        except Exception as e:
            print(f"Error reading Chrome history: {e}")
            
        return history
    
    def _read_safari_history(self, db_path: Path, 
                           start_time: datetime, 
                           end_time: datetime) -> List[Dict]:
        """Read Safari history"""
        history = []
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Safari uses seconds since 2001-01-01
            safari_epoch = datetime(2001, 1, 1)
            start_timestamp = (start_time - safari_epoch).total_seconds()
            end_timestamp = (end_time - safari_epoch).total_seconds()
            
            query = """
                SELECT 
                    hi.url,
                    hi.title,
                    hv.visit_time,
                    hi.visit_count
                FROM history_items hi
                JOIN history_visits hv ON hi.id = hv.history_item
                WHERE hv.visit_time >= ? AND hv.visit_time <= ?
                ORDER BY hv.visit_time DESC
            """
            
            cursor.execute(query, (start_timestamp, end_timestamp))
            
            for row in cursor.fetchall():
                url, title, visit_time, visit_count = row
                
                # Parse domain
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc or parsed.path
                except:
                    domain = url[:50]
                
                history.append({
                    'url': url,
                    'domain': domain,
                    'title': title or '',
                    'visit_count': visit_count or 1,
                    'timestamp': datetime.fromtimestamp(
                        visit_time + safari_epoch.timestamp()
                    ).isoformat() if visit_time else None,
                    'duration_seconds': 30  # Safari doesn't store duration
                })
            
            conn.close()
            
        except Exception as e:
            print(f"Error reading Safari history: {e}")
            
        return history
    
    def _read_firefox_history(self, db_path: Path, 
                            start_time: datetime, 
                            end_time: datetime) -> List[Dict]:
        """Read Firefox history"""
        history = []
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Firefox uses microseconds since Unix epoch
            start_timestamp = int(start_time.timestamp() * 1000000)
            end_timestamp = int(end_time.timestamp() * 1000000)
            
            query = """
                SELECT 
                    p.url,
                    p.title,
                    h.visit_date,
                    p.visit_count
                FROM moz_places p
                JOIN moz_historyvisits h ON p.id = h.place_id
                WHERE h.visit_date >= ? AND h.visit_date <= ?
                ORDER BY h.visit_date DESC
            """
            
            cursor.execute(query, (start_timestamp, end_timestamp))
            
            for row in cursor.fetchall():
                url, title, visit_date, visit_count = row
                
                # Parse domain
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc or parsed.path
                except:
                    domain = url[:50]
                
                history.append({
                    'url': url,
                    'domain': domain,
                    'title': title or '',
                    'visit_count': visit_count or 1,
                    'timestamp': datetime.fromtimestamp(
                        visit_date / 1000000
                    ).isoformat() if visit_date else None,
                    'duration_seconds': 30  # Firefox doesn't store duration
                })
            
            conn.close()
            
        except Exception as e:
            print(f"Error reading Firefox history: {e}")
            
        return history
    
    def get_pattern_browser_context(self, app_a: str, app_b: str,
                                   pattern_time: datetime,
                                   window_minutes: int = 10) -> Dict:
        """
        Get browser context for a specific app switching pattern
        
        Args:
            app_a: First app in pattern
            app_b: Second app in pattern  
            pattern_time: When the pattern occurred
            window_minutes: Time window to analyze (default 10 minutes)
            
        Returns:
            Browser context with visited sites and AI-ready data
        """
        # Check if either app is a browser
        browsers = ['safari', 'chrome', 'firefox', 'brave', 'chrome test']
        
        browser_app = None
        for app in [app_a.lower(), app_b.lower()]:
            if any(browser in app for browser in browsers):
                browser_app = app
                break
                
        if not browser_app:
            return {}
            
        # Get history for time window
        start_time = pattern_time - timedelta(minutes=window_minutes)
        end_time = pattern_time + timedelta(minutes=window_minutes)
        
        history = self.get_browser_context(browser_app, start_time, end_time)
        
        if not history:
            return {}
            
        # Prepare context for AI analysis
        context = {
            'browser': browser_app,
            'time_window': f"{window_minutes} minutes",
            'sites_visited': len(history),
            'history': history[:20],  # Limit to 20 most recent
            'domains': list(set(h['domain'] for h in history)),
            'top_domains': self._get_top_domains(history),
            'page_titles': [h['title'] for h in history if h['title']][:10],
        }
        
        # Add summary statistics
        total_time = sum(h.get('duration_seconds', 30) for h in history)
        context['summary'] = {
            'total_sites': len(history),
            'unique_domains': len(context['domains']),
            'estimated_time_seconds': total_time,
            'average_time_per_site': total_time / len(history) if history else 0
        }
        
        return context
    
    def _get_top_domains(self, history: List[Dict], limit: int = 5) -> List[Dict]:
        """Get most visited domains with visit counts"""
        domain_counts = {}
        domain_time = {}
        
        for entry in history:
            domain = entry['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            domain_time[domain] = domain_time.get(domain, 0) + entry.get('duration_seconds', 30)
            
        # Sort by visit count
        sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'domain': domain,
                'visits': count,
                'time_seconds': domain_time.get(domain, 0)
            }
            for domain, count in sorted_domains[:limit]
        ]
    
    def cleanup(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()


class BrowserContextEnricher:
    """
    Enriches pattern data with browser history context
    """
    
    def __init__(self):
        self.reader = BrowserHistoryReader()
        
    def enrich_pattern(self, pattern: Dict) -> Dict:
        """
        Add browser context to a pattern
        
        Args:
            pattern: Pattern dictionary with app_a, app_b, etc.
            
        Returns:
            Pattern with added browser_context field
        """
        # Get browser context if applicable
        browser_context = self.reader.get_pattern_browser_context(
            app_a=pattern.get('app_a', ''),
            app_b=pattern.get('app_b', ''),
            pattern_time=datetime.now(),  # Would use actual pattern time
            window_minutes=10
        )
        
        if browser_context:
            pattern['browser_context'] = browser_context
            
        return pattern
    
    def get_browsing_summary(self, browser: str, days: int = 1) -> Dict:
        """
        Get summary of browsing patterns over time period
        
        Args:
            browser: Browser name
            days: Number of days to analyze
            
        Returns:
            Summary statistics and patterns
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        history = self.reader.get_browser_context(browser, start_time, end_time)
        
        if not history:
            return {'error': 'No history found'}
            
        # Analyze patterns
        domains = {}
        hourly_activity = {h: 0 for h in range(24)}
        
        for entry in history:
            # Count domains
            domain = entry['domain']
            domains[domain] = domains.get(domain, 0) + 1
            
            # Track hourly activity
            if entry.get('timestamp'):
                try:
                    hour = datetime.fromisoformat(entry['timestamp']).hour
                    hourly_activity[hour] += 1
                except:
                    pass
                    
        return {
            'total_visits': len(history),
            'unique_domains': len(domains),
            'top_domains': sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10],
            'peak_hours': sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:5],
            'time_period': f"{days} days"
        }