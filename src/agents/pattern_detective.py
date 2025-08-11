"""
Pattern Detective - Intelligent Pattern Analysis for Screen Time Data
Analyzes real knowledgeC.db to detect death loops and productivity patterns
"""

import os
import sqlite3
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from pathlib import Path

@dataclass
class DeathLoop:
    """Represents a death loop pattern"""
    app_a: str
    app_b: str
    occurrences: int
    total_time_lost: float
    avg_gap_seconds: float
    severity_score: float
    peak_hours: List[int]
    work_hour_percentage: float

@dataclass
class TemporalPattern:
    """Represents time-based usage patterns"""
    hour: int
    session_count: int
    avg_duration: float
    pattern_type: str  # 'peak_distraction', 'deep_work', 'transition'
    apps_involved: List[str]

class PatternDetective:
    """
    Intelligent pattern detection directly from knowledgeC.db
    No assumptions - learns from actual user data
    """
    
    # macOS reference date: January 1, 2001
    MACOS_EPOCH_OFFSET = 978307200
    
    def __init__(self, db_path: str):
        """Initialize with path to knowledgeC.db copy"""
        self.db_path = db_path
        self.connection = None
        self.patterns = {
            'death_loops': [],
            'temporal_patterns': [],
            'app_clusters': [],
            'context_switches': []
        }
        
    def connect(self) -> bool:
        """Connect to the database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            return False
    
    def analyze_all_patterns(self, days: int = 7) -> Dict:
        """
        Comprehensive pattern analysis
        Returns all discovered patterns with severity scores
        """
        if not self.connection:
            if not self.connect():
                return {}
        
        # Analyze death loops
        death_loops = self.detect_death_loops(days)
        self.patterns['death_loops'] = death_loops
        
        # Analyze temporal patterns
        temporal = self.analyze_temporal_patterns(days)
        self.patterns['temporal_patterns'] = temporal
        
        # Detect app clusters
        clusters = self.detect_app_clusters(days)
        self.patterns['app_clusters'] = clusters
        
        # Calculate context switches
        switches = self.calculate_context_switches(days)
        self.patterns['context_switches'] = switches
        
        return self.patterns
    
    def detect_death_loops(self, days: int = 7) -> List[DeathLoop]:
        """
        Detect death loops with sophisticated analysis
        Finds A→B→A patterns and more complex cycles
        """
        # Calculate date range
        end_timestamp = datetime.now().timestamp() - self.MACOS_EPOCH_OFFSET
        start_timestamp = end_timestamp - (days * 86400)
        
        # Query for rapid app switches (gap <= 10 seconds)
        query = """
        WITH app_sequences AS (
            SELECT 
                a.ZVALUESTRING as app1,
                b.ZVALUESTRING as app2,
                a.ZENDDATE as end1,
                b.ZSTARTDATE as start2,
                (b.ZSTARTDATE - a.ZENDDATE) as gap_seconds,
                CAST(strftime('%H', datetime(a.ZSTARTDATE + 978307200, 'unixepoch', 'localtime')) AS INTEGER) as hour,
                a.ZSTARTDATE as start_time
            FROM ZOBJECT a
            JOIN ZOBJECT b ON b.ZSTARTDATE >= a.ZENDDATE 
                AND b.ZSTARTDATE <= a.ZENDDATE + 10
            WHERE a.ZSTREAMNAME = '/app/usage' 
                AND b.ZSTREAMNAME = '/app/usage'
                AND a.ZVALUESTRING IS NOT NULL 
                AND b.ZVALUESTRING IS NOT NULL
                AND a.Z_PK <> b.Z_PK
                AND a.ZSTARTDATE >= ?
                AND a.ZSTARTDATE <= ?
        )
        SELECT 
            app1,
            app2,
            COUNT(*) as occurrences,
            AVG(gap_seconds) as avg_gap,
            SUM(gap_seconds) as total_gap_time,
            GROUP_CONCAT(DISTINCT hour) as hours
        FROM app_sequences
        WHERE gap_seconds >= 0
        GROUP BY app1, app2
        HAVING COUNT(*) >= 5
        ORDER BY occurrences DESC
        """
        
        cursor = self.connection.execute(query, (start_timestamp, end_timestamp))
        rows = cursor.fetchall()
        
        death_loops = []
        
        # Process results and find bidirectional patterns
        pattern_pairs = {}
        
        for row in rows:
            app1, app2 = row['app1'], row['app2']
            
            # Create normalized pattern key (alphabetical order)
            pattern_key = tuple(sorted([app1, app2]))
            
            if pattern_key not in pattern_pairs:
                pattern_pairs[pattern_key] = {
                    'forward': {'count': 0, 'gap': 0, 'hours': []},
                    'backward': {'count': 0, 'gap': 0, 'hours': []},
                    'total_time': 0
                }
            
            # Determine direction
            if app1 == pattern_key[0]:
                direction = 'forward'
            else:
                direction = 'backward'
            
            pattern_pairs[pattern_key][direction]['count'] = row['occurrences']
            pattern_pairs[pattern_key][direction]['gap'] = row['avg_gap']
            pattern_pairs[pattern_key][direction]['hours'] = [
                int(h) for h in row['hours'].split(',') if h
            ] if row['hours'] else []
            pattern_pairs[pattern_key]['total_time'] += row['total_gap_time']
        
        # Create DeathLoop objects for bidirectional patterns
        for (app_a, app_b), data in pattern_pairs.items():
            # Only consider true death loops (bidirectional)
            if data['forward']['count'] > 0 and data['backward']['count'] > 0:
                total_occurrences = data['forward']['count'] + data['backward']['count']
                
                # Combine hours from both directions
                all_hours = data['forward']['hours'] + data['backward']['hours']
                hour_counts = Counter(all_hours)
                peak_hours = [h for h, _ in hour_counts.most_common(3)]
                
                # Calculate work hour percentage (9 AM - 6 PM)
                work_hours = [h for h in all_hours if 9 <= h <= 18]
                work_percentage = (len(work_hours) / len(all_hours) * 100) if all_hours else 0
                
                # Calculate severity score
                severity = self._calculate_severity(
                    occurrences=total_occurrences,
                    time_lost=data['total_time'],
                    work_percentage=work_percentage,
                    app_a=app_a,
                    app_b=app_b
                )
                
                death_loops.append(DeathLoop(
                    app_a=self._clean_app_name(app_a),
                    app_b=self._clean_app_name(app_b),
                    occurrences=total_occurrences,
                    total_time_lost=data['total_time'],
                    avg_gap_seconds=(data['forward']['gap'] + data['backward']['gap']) / 2,
                    severity_score=severity,
                    peak_hours=peak_hours,
                    work_hour_percentage=work_percentage
                ))
        
        # Sort by severity
        death_loops.sort(key=lambda x: x.severity_score, reverse=True)
        
        return death_loops
    
    def analyze_temporal_patterns(self, days: int = 7) -> List[TemporalPattern]:
        """
        Analyze usage patterns by time of day
        Identifies peak distraction times and deep work periods
        """
        end_timestamp = datetime.now().timestamp() - self.MACOS_EPOCH_OFFSET
        start_timestamp = end_timestamp - (days * 86400)
        
        query = """
        SELECT 
            CAST(strftime('%H', datetime(ZSTARTDATE + 978307200, 'unixepoch', 'localtime')) AS INTEGER) as hour,
            COUNT(*) as session_count,
            AVG(ZENDDATE - ZSTARTDATE) as avg_duration,
            GROUP_CONCAT(DISTINCT ZVALUESTRING) as apps
        FROM ZOBJECT
        WHERE ZSTREAMNAME = '/app/usage'
            AND ZVALUESTRING IS NOT NULL
            AND ZSTARTDATE >= ?
            AND ZSTARTDATE <= ?
        GROUP BY hour
        ORDER BY hour
        """
        
        cursor = self.connection.execute(query, (start_timestamp, end_timestamp))
        rows = cursor.fetchall()
        
        temporal_patterns = []
        
        # Calculate statistics for pattern classification
        all_durations = [row['avg_duration'] for row in rows]
        avg_duration = np.mean(all_durations) if all_durations else 30
        
        all_sessions = [row['session_count'] for row in rows]
        avg_sessions = np.mean(all_sessions) if all_sessions else 50
        
        for row in rows:
            hour = row['hour']
            sessions = row['session_count']
            duration = row['avg_duration']
            apps = row['apps'].split(',')[:5] if row['apps'] else []
            
            # Classify pattern type
            if duration < avg_duration * 0.5 and sessions > avg_sessions * 1.5:
                pattern_type = 'peak_distraction'
            elif duration > avg_duration * 1.5 and sessions < avg_sessions:
                pattern_type = 'deep_work'
            else:
                pattern_type = 'transition'
            
            temporal_patterns.append(TemporalPattern(
                hour=hour,
                session_count=sessions,
                avg_duration=duration,
                pattern_type=pattern_type,
                apps_involved=[self._clean_app_name(app) for app in apps]
            ))
        
        return temporal_patterns
    
    def detect_app_clusters(self, days: int = 7) -> List[Dict]:
        """
        Detect apps that are frequently used together
        Helps understand workflow vs distraction clusters
        """
        end_timestamp = datetime.now().timestamp() - self.MACOS_EPOCH_OFFSET
        start_timestamp = end_timestamp - (days * 86400)
        
        # Find apps used within 60-second windows
        query = """
        WITH app_pairs AS (
            SELECT 
                a.ZVALUESTRING as app1,
                b.ZVALUESTRING as app2,
                COUNT(*) as co_occurrences
            FROM ZOBJECT a
            JOIN ZOBJECT b ON ABS(a.ZSTARTDATE - b.ZSTARTDATE) <= 60
            WHERE a.ZSTREAMNAME = '/app/usage' 
                AND b.ZSTREAMNAME = '/app/usage'
                AND a.ZVALUESTRING IS NOT NULL 
                AND b.ZVALUESTRING IS NOT NULL
                AND a.ZVALUESTRING < b.ZVALUESTRING
                AND a.ZSTARTDATE >= ?
                AND a.ZSTARTDATE <= ?
            GROUP BY a.ZVALUESTRING, b.ZVALUESTRING
            HAVING COUNT(*) >= 10
        )
        SELECT * FROM app_pairs
        ORDER BY co_occurrences DESC
        LIMIT 20
        """
        
        cursor = self.connection.execute(query, (start_timestamp, end_timestamp))
        rows = cursor.fetchall()
        
        # Build clusters using graph-like approach
        clusters = []
        app_connections = defaultdict(set)
        
        for row in rows:
            app1 = self._clean_app_name(row['app1'])
            app2 = self._clean_app_name(row['app2'])
            app_connections[app1].add(app2)
            app_connections[app2].add(app1)
        
        # Find connected components (clusters)
        visited = set()
        
        for app in app_connections:
            if app not in visited:
                cluster = self._dfs_cluster(app, app_connections, visited)
                if len(cluster) >= 2:
                    clusters.append({
                        'apps': list(cluster),
                        'size': len(cluster),
                        'type': self._classify_cluster(cluster)
                    })
        
        return clusters
    
    def calculate_context_switches(self, days: int = 7) -> Dict:
        """
        Calculate the mental overhead of context switching
        Measures productivity loss from frequent app switches
        """
        end_timestamp = datetime.now().timestamp() - self.MACOS_EPOCH_OFFSET
        start_timestamp = end_timestamp - (days * 86400)
        
        query = """
        SELECT 
            COUNT(*) as total_switches,
            AVG(ZENDDATE - ZSTARTDATE) as avg_session_duration,
            COUNT(DISTINCT DATE(ZSTARTDATE + 978307200, 'unixepoch', 'localtime')) as days_active,
            MIN(ZENDDATE - ZSTARTDATE) as min_duration,
            MAX(ZENDDATE - ZSTARTDATE) as max_duration
        FROM ZOBJECT
        WHERE ZSTREAMNAME = '/app/usage'
            AND ZVALUESTRING IS NOT NULL
            AND ZSTARTDATE >= ?
            AND ZSTARTDATE <= ?
        """
        
        cursor = self.connection.execute(query, (start_timestamp, end_timestamp))
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        # Calculate context switch metrics
        switches_per_day = row['total_switches'] / row['days_active'] if row['days_active'] > 0 else 0
        
        # Estimate productivity loss (research shows ~23 minutes to refocus after interruption)
        # We'll use a scaled version based on session duration
        refocus_penalty = min(23 * 60, row['avg_session_duration'] * 0.25)  # 25% of session time
        daily_loss_seconds = switches_per_day * refocus_penalty
        
        return {
            'total_switches': row['total_switches'],
            'switches_per_day': switches_per_day,
            'avg_session_duration': row['avg_session_duration'],
            'min_session': row['min_duration'],
            'max_session': row['max_duration'],
            'estimated_daily_loss_minutes': daily_loss_seconds / 60,
            'context_switch_severity': self._rate_context_switch_severity(switches_per_day)
        }
    
    def get_pattern_insights(self) -> Dict:
        """
        Generate actionable insights from discovered patterns
        Returns prioritized recommendations
        """
        insights = {
            'critical_death_loops': [],
            'peak_distraction_times': [],
            'productivity_recommendations': [],
            'estimated_time_savings': 0
        }
        
        # Analyze death loops
        if self.patterns['death_loops']:
            top_loops = self.patterns['death_loops'][:3]
            for loop in top_loops:
                insights['critical_death_loops'].append({
                    'pattern': f"{loop.app_a} ↔ {loop.app_b}",
                    'daily_occurrences': loop.occurrences / 7,  # Assuming 7 days of data
                    'time_lost_minutes': loop.total_time_lost / 60,
                    'recommendation': self._generate_intervention(loop)
                })
                insights['estimated_time_savings'] += loop.total_time_lost / 60
        
        # Analyze temporal patterns
        if self.patterns['temporal_patterns']:
            distraction_hours = [
                p for p in self.patterns['temporal_patterns'] 
                if p.pattern_type == 'peak_distraction'
            ]
            for pattern in distraction_hours[:3]:
                insights['peak_distraction_times'].append({
                    'hour': f"{pattern.hour:02d}:00",
                    'session_count': pattern.session_count,
                    'avg_duration': pattern.avg_duration,
                    'apps': pattern.apps_involved[:3]
                })
        
        # Generate recommendations
        insights['productivity_recommendations'] = self._generate_recommendations()
        
        return insights
    
    def _calculate_severity(self, occurrences: int, time_lost: float, 
                           work_percentage: float, app_a: str, app_b: str) -> float:
        """Calculate severity score for a death loop"""
        # Base score from frequency
        frequency_score = min(100, occurrences / 10)
        
        # Time impact score
        time_score = min(100, time_lost / 60)  # Convert to minutes
        
        # Work hour impact
        work_impact = work_percentage / 100 * 50  # Max 50 points for work time
        
        # App type penalty
        distraction_apps = ['safari', 'chrome', 'telegram', 'twitter', 'discord']
        app_penalty = 0
        for app in [app_a.lower(), app_b.lower()]:
            for distraction in distraction_apps:
                if distraction in app:
                    app_penalty += 10
                    break
        
        # Combine scores
        severity = (frequency_score * 0.3 + 
                   time_score * 0.3 + 
                   work_impact * 0.2 + 
                   app_penalty * 0.2)
        
        return min(100, severity)
    
    def _clean_app_name(self, bundle_id: str) -> str:
        """Convert bundle ID to readable app name"""
        if not bundle_id:
            return "Unknown"
        
        # Extract meaningful part from bundle ID
        mappings = {
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
            'com.google.chrome.for.testing': 'Chrome Test'
        }
        
        return mappings.get(bundle_id, bundle_id.split('.')[-1].title())
    
    def _dfs_cluster(self, app: str, connections: Dict, visited: set) -> set:
        """Depth-first search to find app clusters"""
        cluster = {app}
        visited.add(app)
        
        for connected_app in connections[app]:
            if connected_app not in visited:
                cluster.update(self._dfs_cluster(connected_app, connections, visited))
        
        return cluster
    
    def _classify_cluster(self, apps: set) -> str:
        """Classify a cluster of apps"""
        # Simple classification based on app names
        work_keywords = ['zoom', 'code', 'terminal', 'xcode', 'figma']
        communication_keywords = ['slack', 'teams', 'telegram', 'messages', 'discord']
        browser_keywords = ['safari', 'chrome', 'firefox']
        
        app_lower = [app.lower() for app in apps]
        
        work_count = sum(1 for app in app_lower for keyword in work_keywords if keyword in app)
        comm_count = sum(1 for app in app_lower for keyword in communication_keywords if keyword in app)
        browser_count = sum(1 for app in app_lower for keyword in browser_keywords if keyword in app)
        
        if work_count >= 2:
            return 'work_cluster'
        elif comm_count >= 2:
            return 'communication_cluster'
        elif browser_count >= 1:
            return 'browsing_cluster'
        else:
            return 'mixed_cluster'
    
    def _rate_context_switch_severity(self, switches_per_day: float) -> str:
        """Rate the severity of context switching"""
        if switches_per_day < 50:
            return 'low'
        elif switches_per_day < 100:
            return 'moderate'
        elif switches_per_day < 200:
            return 'high'
        else:
            return 'critical'
    
    def _generate_intervention(self, loop: DeathLoop) -> str:
        """Generate intervention recommendation for a death loop"""
        if loop.severity_score > 80:
            return f"Block {loop.app_b} for 5 minutes after using {loop.app_a}"
        elif loop.severity_score > 60:
            return f"Add 3-second delay before switching from {loop.app_a} to {loop.app_b}"
        elif loop.severity_score > 40:
            return f"Show reminder when switching between {loop.app_a} and {loop.app_b}"
        else:
            return f"Track and visualize time spent in this loop"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate overall productivity recommendations"""
        recommendations = []
        
        # Based on death loops
        if self.patterns['death_loops']:
            top_loop = self.patterns['death_loops'][0]
            recommendations.append(
                f"Your biggest death loop ({top_loop.app_a} ↔ {top_loop.app_b}) "
                f"happens {top_loop.occurrences} times per week. "
                f"Breaking this pattern could save {top_loop.total_time_lost/60:.0f} minutes weekly."
            )
        
        # Based on temporal patterns
        distraction_hours = [
            p.hour for p in self.patterns.get('temporal_patterns', [])
            if p.pattern_type == 'peak_distraction'
        ]
        if distraction_hours:
            recommendations.append(
                f"Your peak distraction times are {', '.join(f'{h:02d}:00' for h in distraction_hours[:3])}. "
                f"Consider scheduling deep work outside these hours."
            )
        
        # Based on context switches
        if self.patterns.get('context_switches'):
            switches = self.patterns['context_switches']
            if switches['context_switch_severity'] in ['high', 'critical']:
                recommendations.append(
                    f"You switch apps {switches['switches_per_day']:.0f} times per day, "
                    f"potentially losing {switches['estimated_daily_loss_minutes']:.0f} minutes to refocusing. "
                    f"Try batching similar tasks together."
                )
        
        return recommendations
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


class PatternDetectiveOrchestrator:
    """
    Orchestrates pattern detection and generates reports
    """
    
    def __init__(self, db_path: str):
        self.detective = PatternDetective(db_path)
    
    def run_full_analysis(self, days: int = 7) -> Dict:
        """Run complete pattern analysis"""
        print(f"🔍 Analyzing {days} days of Screen Time data...")
        
        # Run analysis
        patterns = self.detective.analyze_all_patterns(days)
        
        # Get insights
        insights = self.detective.get_pattern_insights()
        
        # Generate report
        report = self.generate_report(patterns, insights)
        
        return {
            'patterns': patterns,
            'insights': insights,
            'report': report
        }
    
    def generate_report(self, patterns: Dict, insights: Dict) -> str:
        """Generate human-readable report"""
        report = []
        
        report.append("=" * 70)
        report.append("📊 PATTERN DETECTIVE REPORT")
        report.append("=" * 70)
        
        # Death loops section
        if patterns['death_loops']:
            report.append("\n🔄 DEATH LOOPS DETECTED")
            report.append("-" * 40)
            for i, loop in enumerate(patterns['death_loops'][:5], 1):
                report.append(
                    f"{i}. {loop.app_a} ↔ {loop.app_b}\n"
                    f"   Occurrences: {loop.occurrences}\n"
                    f"   Time lost: {loop.total_time_lost/60:.1f} minutes\n"
                    f"   Severity: {loop.severity_score:.1f}/100\n"
                    f"   Peak hours: {', '.join(f'{h:02d}:00' for h in loop.peak_hours)}"
                )
        
        # Temporal patterns section
        if patterns['temporal_patterns']:
            report.append("\n⏰ TEMPORAL PATTERNS")
            report.append("-" * 40)
            
            distraction_times = [p for p in patterns['temporal_patterns'] 
                               if p.pattern_type == 'peak_distraction']
            if distraction_times:
                report.append("Peak distraction times:")
                for pattern in distraction_times[:3]:
                    report.append(
                        f"  {pattern.hour:02d}:00 - {pattern.session_count} sessions, "
                        f"avg {pattern.avg_duration:.1f}s"
                    )
        
        # App clusters section
        if patterns['app_clusters']:
            report.append("\n🎯 APP CLUSTERS")
            report.append("-" * 40)
            for cluster in patterns['app_clusters'][:3]:
                report.append(
                    f"  {cluster['type']}: {', '.join(cluster['apps'][:4])}"
                )
        
        # Context switches section
        if patterns['context_switches']:
            switches = patterns['context_switches']
            report.append("\n🔀 CONTEXT SWITCHING")
            report.append("-" * 40)
            report.append(
                f"  Switches per day: {switches['switches_per_day']:.0f}\n"
                f"  Avg session: {switches['avg_session_duration']:.1f}s\n"
                f"  Daily loss: {switches['estimated_daily_loss_minutes']:.1f} minutes\n"
                f"  Severity: {switches['context_switch_severity']}"
            )
        
        # Insights section
        if insights['productivity_recommendations']:
            report.append("\n💡 RECOMMENDATIONS")
            report.append("-" * 40)
            for rec in insights['productivity_recommendations']:
                report.append(f"  • {rec}")
        
        # Summary
        report.append("\n" + "=" * 70)
        report.append(f"💰 POTENTIAL TIME SAVINGS: {insights.get('estimated_time_savings', 0):.0f} minutes/week")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def close(self):
        """Clean up resources"""
        self.detective.close()


if __name__ == "__main__":
    # Test with real data
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "screentime_data.db")
    
    if Path(db_path).exists():
        orchestrator = PatternDetectiveOrchestrator(db_path)
        results = orchestrator.run_full_analysis(days=7)
        
        print(results['report'])
        
        orchestrator.close()
    else:
        print(f"Database not found at {db_path}")
        print("Please copy your knowledgeC.db to the data directory")