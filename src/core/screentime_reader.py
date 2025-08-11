"""
Screen Time Database Reader
Safely accesses and queries macOS knowledgeC.db for app usage data
"""

import sqlite3
import shutil
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from typing import List, Dict, Tuple, Optional

class ScreenTimeReader:
    """Reads and analyzes macOS Screen Time data from knowledgeC.db"""
    
    # macOS reference date: January 1, 2001
    MACOS_EPOCH_OFFSET = 978307200
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize with optional custom database path"""
        self.source_db = db_path or os.path.expanduser(
            "~/Library/Application Support/Knowledge/knowledgeC.db"
        )
        self.local_db = Path("data/screentime_copy.db")
        self.connection = None
        
    def copy_database(self) -> bool:
        """Safely copy the Screen Time database to local directory"""
        try:
            # Create data directory if it doesn't exist
            self.local_db.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy database
            shutil.copy2(self.source_db, self.local_db)
            print(f"✅ Database copied to {self.local_db}")
            return True
        except Exception as e:
            print(f"❌ Failed to copy database: {e}")
            return False
    
    def connect(self) -> bool:
        """Connect to the local database copy"""
        try:
            # Copy database if local copy doesn't exist
            if not self.local_db.exists():
                if not self.copy_database():
                    return False
            
            self.connection = sqlite3.connect(str(self.local_db))
            self.connection.row_factory = sqlite3.Row
            print("✅ Connected to Screen Time database")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def convert_timestamp(self, macos_timestamp: float) -> datetime:
        """Convert macOS timestamp to Python datetime"""
        if macos_timestamp:
            unix_timestamp = macos_timestamp + self.MACOS_EPOCH_OFFSET
            return datetime.fromtimestamp(unix_timestamp)
        return None
    
    def query_app_usage(self, days: int = 7) -> pd.DataFrame:
        """
        Query app usage data for the specified number of days
        Returns DataFrame with app usage sessions
        """
        if not self.connection:
            if not self.connect():
                return pd.DataFrame()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Convert to macOS timestamps
        start_timestamp = (start_date.timestamp() - self.MACOS_EPOCH_OFFSET)
        end_timestamp = (end_date.timestamp() - self.MACOS_EPOCH_OFFSET)
        
        query = """
        SELECT 
            ZSTARTDATE as start_time,
            ZENDDATE as end_time,
            ZVALUESTRING as app_bundle_id,
            (ZENDDATE - ZSTARTDATE) as duration_seconds
        FROM ZOBJECT
        WHERE ZSTREAMNAME = '/app/usage'
            AND ZSTARTDATE >= ?
            AND ZSTARTDATE <= ?
            AND ZVALUESTRING IS NOT NULL
        ORDER BY ZSTARTDATE DESC
        """
        
        try:
            cursor = self.connection.execute(query, (start_timestamp, end_timestamp))
            rows = cursor.fetchall()
            
            # Convert to DataFrame
            data = []
            for row in rows:
                data.append({
                    'start_time': self.convert_timestamp(row['start_time']),
                    'end_time': self.convert_timestamp(row['end_time']),
                    'app': self._clean_app_name(row['app_bundle_id']),
                    'bundle_id': row['app_bundle_id'],
                    'duration_seconds': row['duration_seconds']
                })
            
            df = pd.DataFrame(data)
            print(f"✅ Retrieved {len(df)} app usage records")
            return df
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return pd.DataFrame()
    
    def detect_rapid_switches(self, threshold_seconds: int = 30) -> List[Dict]:
        """
        Detect rapid app switching patterns (death loops)
        Returns list of switching patterns where user switches apps within threshold
        """
        df = self.query_app_usage(days=1)  # Start with 1 day for demo
        if df.empty:
            return []
        
        switches = []
        
        # Sort by start time
        df = df.sort_values('start_time')
        
        # Analyze consecutive app usage
        for i in range(len(df) - 1):
            current = df.iloc[i]
            next_app = df.iloc[i + 1]
            
            # Calculate time between app sessions
            gap = (next_app['start_time'] - current['end_time']).total_seconds()
            
            if gap < threshold_seconds and gap >= 0:
                switches.append({
                    'from_app': current['app'],
                    'to_app': next_app['app'],
                    'switch_time': current['end_time'],
                    'gap_seconds': gap,
                    'from_duration': current['duration_seconds'],
                    'to_duration': next_app['duration_seconds']
                })
        
        print(f"✅ Found {len(switches)} rapid switches")
        return switches
    
    def get_app_statistics(self, days: int = 7) -> Dict:
        """Get comprehensive app usage statistics"""
        df = self.query_app_usage(days=days)
        if df.empty:
            return {}
        
        # Group by app
        app_stats = df.groupby('app').agg({
            'duration_seconds': ['sum', 'mean', 'count']
        }).round(2)
        
        # Convert to dictionary
        stats = {}
        for app in app_stats.index:
            stats[app] = {
                'total_seconds': app_stats.loc[app, ('duration_seconds', 'sum')],
                'average_seconds': app_stats.loc[app, ('duration_seconds', 'mean')],
                'session_count': int(app_stats.loc[app, ('duration_seconds', 'count')]),
                'total_hours': round(app_stats.loc[app, ('duration_seconds', 'sum')] / 3600, 2)
            }
        
        # Sort by total time
        stats = dict(sorted(stats.items(), 
                          key=lambda x: x[1]['total_seconds'], 
                          reverse=True))
        
        return stats
    
    def get_top_distracting_apps(self, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Get top distracting apps based on usage patterns
        Returns list of (app_name, distraction_score) tuples
        """
        stats = self.get_app_statistics(days=7)
        
        # Define distracting app patterns
        distracting_keywords = [
            'twitter', 'facebook', 'instagram', 'tiktok', 'youtube',
            'reddit', 'discord', 'slack', 'messages', 'whatsapp',
            'telegram', 'safari', 'chrome', 'firefox', 'edge'
        ]
        
        distracting_apps = []
        for app, data in stats.items():
            app_lower = app.lower()
            
            # Check if app matches distracting patterns
            is_distracting = any(keyword in app_lower for keyword in distracting_keywords)
            
            if is_distracting:
                # Calculate distraction score
                # High session count + short average duration = higher distraction
                if data['average_seconds'] > 0:
                    distraction_score = (
                        data['session_count'] * 
                        (300 / data['average_seconds']) *  # Normalize by 5 minutes
                        (data['total_hours'] / 10)  # Weight by total time
                    )
                else:
                    distraction_score = 0
                
                distracting_apps.append((app, round(distraction_score, 2)))
        
        # Sort by distraction score
        distracting_apps.sort(key=lambda x: x[1], reverse=True)
        
        return distracting_apps[:limit]
    
    def _clean_app_name(self, bundle_id: str) -> str:
        """Convert bundle ID to readable app name"""
        if not bundle_id:
            return "Unknown"
        
        # Common bundle ID mappings
        mappings = {
            'com.apple.Safari': 'Safari',
            'com.google.Chrome': 'Chrome',
            'com.microsoft.VSCode': 'VS Code',
            'com.tinyspeck.slackmacgap': 'Slack',
            'com.apple.Terminal': 'Terminal',
            'com.apple.dt.Xcode': 'Xcode',
            'com.spotify.client': 'Spotify',
            'com.apple.mail': 'Mail',
            'com.apple.iCal': 'Calendar',
            'com.apple.Notes': 'Notes',
            'com.microsoft.teams': 'Teams',
            'us.zoom.xos': 'Zoom',
            'com.brave.Browser': 'Brave',
            'org.mozilla.firefox': 'Firefox',
            'com.microsoft.edgemac': 'Edge',
            'com.apple.MobileSMS': 'Messages',
            'net.whatsapp.WhatsApp': 'WhatsApp',
            'ru.keepcoder.Telegram': 'Telegram',
            'com.hnc.Discord': 'Discord',
            'com.facebook.archon': 'Messenger',
            'com.twitter.twitter-mac': 'Twitter'
        }
        
        # Check for known mapping
        if bundle_id in mappings:
            return mappings[bundle_id]
        
        # Try to extract app name from bundle ID
        parts = bundle_id.split('.')
        if len(parts) >= 2:
            # Get the last meaningful part
            app_name = parts[-1]
            # Capitalize first letter
            return app_name.replace('-', ' ').replace('_', ' ').title()
        
        return bundle_id
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("✅ Database connection closed")


if __name__ == "__main__":
    # Test the reader
    reader = ScreenTimeReader()
    
    if reader.connect():
        print("\n📊 App Usage Statistics (Last 7 Days)")
        print("=" * 50)
        
        stats = reader.get_app_statistics(days=7)
        for i, (app, data) in enumerate(list(stats.items())[:10], 1):
            print(f"{i}. {app}: {data['total_hours']}h "
                  f"({data['session_count']} sessions)")
        
        print("\n⚠️ Top Distracting Apps")
        print("=" * 50)
        
        distracting = reader.get_top_distracting_apps()
        for i, (app, score) in enumerate(distracting, 1):
            print(f"{i}. {app}: Score {score}")
        
        print("\n🔄 Recent Rapid Switches (Death Loops)")
        print("=" * 50)
        
        switches = reader.detect_rapid_switches(threshold_seconds=60)
        for i, switch in enumerate(switches[:10], 1):
            print(f"{i}. {switch['from_app']} → {switch['to_app']} "
                  f"(gap: {switch['gap_seconds']:.1f}s)")
        
        reader.close()