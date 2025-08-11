"""
Generate synthetic test data for Pattern Detective testing
Creates databases with known patterns for validation
"""

import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Tuple
import os
from pathlib import Path

class TestDataGenerator:
    """Generates synthetic Screen Time data with known patterns"""
    
    # macOS reference date
    MACOS_EPOCH_OFFSET = 978307200
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        
        # App pools for different personas
        self.developer_apps = [
            'com.microsoft.VSCode',
            'com.apple.Terminal',
            'com.google.Chrome',
            'com.apple.Safari',
            'com.github.desktop',
            'com.tinyspeck.slackmacgap',
            'com.tdesktop.Telegram',
            'com.spotify.client'
        ]
        
        self.designer_apps = [
            'com.figma.desktop',
            'com.adobe.Photoshop',
            'com.adobe.Illustrator',
            'com.apple.Safari',
            'com.pinterest.app',
            'com.instagram.app',
            'com.tinyspeck.slackmacgap',
            'com.dribbble.app'
        ]
        
        self.writer_apps = [
            'com.apple.Pages',
            'com.notion.app',
            'com.google.Chrome',
            'com.apple.Safari',
            'com.twitter.twitter-mac',
            'com.medium.app',
            'com.grammarly.app',
            'com.spotify.client'
        ]
    
    def create_database(self):
        """Create database with proper schema"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Drop table if exists
        cursor.execute("DROP TABLE IF EXISTS ZOBJECT")
        
        # Create ZOBJECT table
        cursor.execute("""
        CREATE TABLE ZOBJECT (
            Z_PK INTEGER PRIMARY KEY AUTOINCREMENT,
            Z_ENT INTEGER,
            Z_OPT INTEGER,
            ZUUIDHASH INTEGER,
            ZEVENT INTEGER,
            ZSOURCE INTEGER,
            ZSTARTDATE REAL,
            ZENDDATE REAL,
            ZVALUESTRING TEXT,
            ZSTREAMNAME TEXT,
            ZUUID TEXT UNIQUE
        )
        """)
        
        # Create indices for performance
        cursor.execute("CREATE INDEX idx_stream ON ZOBJECT(ZSTREAMNAME)")
        cursor.execute("CREATE INDEX idx_dates ON ZOBJECT(ZSTARTDATE, ZENDDATE)")
        cursor.execute("CREATE INDEX idx_app ON ZOBJECT(ZVALUESTRING)")
        
        self.connection.commit()
    
    def generate_death_loop_pattern(self, app_a: str, app_b: str, 
                                   base_time: float, frequency: int = 10,
                                   gap_seconds: int = 5) -> List[Tuple]:
        """Generate a death loop pattern between two apps"""
        records = []
        
        for i in range(frequency):
            time_offset = i * 120  # Every 2 minutes
            
            # App A session
            start_a = base_time + time_offset
            end_a = start_a + random.randint(10, 30)  # 10-30 second session
            records.append((
                None, None, None, None, None,
                start_a, end_a, app_a, '/app/usage',
                f'uuid_loop_{base_time}_{i}_a'
            ))
            
            # App B session (rapid switch)
            start_b = end_a + gap_seconds
            end_b = start_b + random.randint(10, 30)
            records.append((
                None, None, None, None, None,
                start_b, end_b, app_b, '/app/usage',
                f'uuid_loop_{base_time}_{i}_b'
            ))
            
            # Return to App A (completing the loop)
            start_a2 = end_b + gap_seconds
            end_a2 = start_a2 + random.randint(5, 15)
            records.append((
                None, None, None, None, None,
                start_a2, end_a2, app_a, '/app/usage',
                f'uuid_loop_{base_time}_{i}_a2'
            ))
        
        return records
    
    def generate_productive_session(self, app: str, base_time: float,
                                   duration_minutes: int = 60) -> List[Tuple]:
        """Generate a productive (long) session"""
        records = []
        
        start = base_time
        end = start + (duration_minutes * 60)
        
        records.append((
            None, None, None, None, None,
            start, end, app, '/app/usage',
            f'uuid_productive_{base_time}'
        ))
        
        return records
    
    def generate_doom_scrolling_pattern(self, apps: List[str], base_time: float,
                                       duration_minutes: int = 30) -> List[Tuple]:
        """Generate doom scrolling pattern (many short sessions)"""
        records = []
        current_time = base_time
        end_time = base_time + (duration_minutes * 60)
        
        while current_time < end_time:
            app = random.choice(apps)
            duration = random.randint(5, 20)  # Very short sessions
            
            records.append((
                None, None, None, None, None,
                current_time, current_time + duration,
                app, '/app/usage',
                f'uuid_doom_{current_time}'
            ))
            
            current_time += duration + random.randint(1, 5)  # Small gaps
        
        return records
    
    def generate_developer_persona(self, days: int = 7) -> List[Tuple]:
        """Generate usage pattern for a developer"""
        records = []
        base_time = datetime.now().timestamp() - self.MACOS_EPOCH_OFFSET
        
        for day in range(days):
            day_offset = day * 86400
            day_base = base_time - day_offset
            
            # Morning deep work (9 AM - 12 PM)
            morning_time = day_base - (15 * 3600)
            records.extend(self.generate_productive_session(
                'com.microsoft.VSCode', morning_time, 180
            ))
            
            # Death loop: VS Code ↔ Chrome (searching Stack Overflow)
            loop_time = day_base - (12 * 3600)
            records.extend(self.generate_death_loop_pattern(
                'com.microsoft.VSCode', 'com.google.Chrome',
                loop_time, frequency=15
            ))
            
            # Afternoon: Terminal work with Slack interruptions
            afternoon_time = day_base - (8 * 3600)
            records.extend(self.generate_death_loop_pattern(
                'com.apple.Terminal', 'com.tinyspeck.slackmacgap',
                afternoon_time, frequency=8, gap_seconds=10
            ))
            
            # Evening doom scrolling
            evening_time = day_base - (3 * 3600)
            records.extend(self.generate_doom_scrolling_pattern(
                ['com.apple.Safari', 'com.tdesktop.Telegram', 'com.google.Chrome'],
                evening_time, duration_minutes=45
            ))
        
        return records
    
    def generate_designer_persona(self, days: int = 7) -> List[Tuple]:
        """Generate usage pattern for a designer"""
        records = []
        base_time = datetime.now().timestamp() - self.MACOS_EPOCH_OFFSET
        
        for day in range(days):
            day_offset = day * 86400
            day_base = base_time - day_offset
            
            # Morning design work
            morning_time = day_base - (14 * 3600)
            records.extend(self.generate_productive_session(
                'com.figma.desktop', morning_time, 120
            ))
            
            # Inspiration loop: Figma ↔ Pinterest ↔ Dribbble
            inspiration_time = day_base - (11 * 3600)
            records.extend(self.generate_death_loop_pattern(
                'com.figma.desktop', 'com.pinterest.app',
                inspiration_time, frequency=12
            ))
            records.extend(self.generate_death_loop_pattern(
                'com.pinterest.app', 'com.dribbble.app',
                inspiration_time + 600, frequency=8
            ))
            
            # Afternoon Photoshop work
            afternoon_time = day_base - (7 * 3600)
            records.extend(self.generate_productive_session(
                'com.adobe.Photoshop', afternoon_time, 90
            ))
            
            # Social media break (Instagram)
            social_time = day_base - (5 * 3600)
            records.extend(self.generate_doom_scrolling_pattern(
                ['com.instagram.app', 'com.apple.Safari'],
                social_time, duration_minutes=20
            ))
        
        return records
    
    def generate_edge_cases(self) -> List[Tuple]:
        """Generate edge case scenarios for testing"""
        records = []
        base_time = datetime.now().timestamp() - self.MACOS_EPOCH_OFFSET
        
        # Zero-second gap switches
        for i in range(5):
            start = base_time - (i * 100)
            records.append((
                None, None, None, None, None,
                start, start + 10, 'com.app.one', '/app/usage',
                f'uuid_zero_{i}_1'
            ))
            # Immediate switch (0 gap)
            records.append((
                None, None, None, None, None,
                start + 10, start + 20, 'com.app.two', '/app/usage',
                f'uuid_zero_{i}_2'
            ))
        
        # Midnight crossing
        midnight = base_time - (base_time % 86400)  # Start of day
        records.append((
            None, None, None, None, None,
            midnight - 300, midnight + 300,  # 5 min before to 5 min after
            'com.midnight.app', '/app/usage',
            'uuid_midnight'
        ))
        
        # Very long session (8 hours)
        records.append((
            None, None, None, None, None,
            base_time - 30000, base_time - 1200,
            'com.long.session', '/app/usage',
            'uuid_long'
        ))
        
        # Rapid fire switches (stress test)
        rapid_start = base_time - 10000
        for i in range(100):
            app = f'com.rapid.app{i % 3}'
            records.append((
                None, None, None, None, None,
                rapid_start + i * 2, rapid_start + i * 2 + 1,
                app, '/app/usage',
                f'uuid_rapid_{i}'
            ))
        
        return records
    
    def insert_records(self, records: List[Tuple]):
        """Insert records into database"""
        cursor = self.connection.cursor()
        
        cursor.executemany("""
        INSERT INTO ZOBJECT (
            Z_ENT, Z_OPT, ZUUIDHASH, ZEVENT, ZSOURCE,
            ZSTARTDATE, ZENDDATE, ZVALUESTRING, ZSTREAMNAME, ZUUID
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        
        self.connection.commit()
    
    def generate_complete_test_database(self, personas: List[str] = None):
        """Generate complete test database with multiple personas"""
        if personas is None:
            personas = ['developer', 'designer']
        
        self.create_database()
        
        all_records = []
        
        if 'developer' in personas:
            print("Generating developer persona...")
            all_records.extend(self.generate_developer_persona())
        
        if 'designer' in personas:
            print("Generating designer persona...")
            all_records.extend(self.generate_designer_persona())
        
        # Always add edge cases
        print("Adding edge cases...")
        all_records.extend(self.generate_edge_cases())
        
        # Shuffle to simulate real usage
        random.shuffle(all_records)
        
        print(f"Inserting {len(all_records)} records...")
        self.insert_records(all_records)
        
        print(f"Test database created at: {self.db_path}")
        print(f"Total records: {len(all_records)}")
        
        # Print statistics
        self.print_statistics()
    
    def print_statistics(self):
        """Print database statistics"""
        cursor = self.connection.cursor()
        
        # Total records
        cursor.execute("SELECT COUNT(*) FROM ZOBJECT WHERE ZSTREAMNAME = '/app/usage'")
        total = cursor.fetchone()[0]
        
        # Unique apps
        cursor.execute("SELECT COUNT(DISTINCT ZVALUESTRING) FROM ZOBJECT WHERE ZSTREAMNAME = '/app/usage'")
        apps = cursor.fetchone()[0]
        
        # Date range
        cursor.execute("""
        SELECT 
            datetime(MIN(ZSTARTDATE) + 978307200, 'unixepoch', 'localtime'),
            datetime(MAX(ZENDDATE) + 978307200, 'unixepoch', 'localtime')
        FROM ZOBJECT WHERE ZSTREAMNAME = '/app/usage'
        """)
        date_range = cursor.fetchone()
        
        print("\n=== Database Statistics ===")
        print(f"Total sessions: {total}")
        print(f"Unique apps: {apps}")
        print(f"Date range: {date_range[0]} to {date_range[1]}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


def main():
    """Generate test databases"""
    # Create fixtures directory if it doesn't exist
    fixtures_dir = Path(__file__).parent
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate different test databases
    databases = [
        ('test_developer.db', ['developer']),
        ('test_designer.db', ['designer']),
        ('test_mixed.db', ['developer', 'designer']),
    ]
    
    for db_name, personas in databases:
        db_path = fixtures_dir / db_name
        print(f"\n{'='*50}")
        print(f"Creating {db_name}...")
        print('='*50)
        
        generator = TestDataGenerator(str(db_path))
        generator.generate_complete_test_database(personas)
        generator.close()
    
    print("\n✅ All test databases created successfully!")


if __name__ == '__main__':
    main()