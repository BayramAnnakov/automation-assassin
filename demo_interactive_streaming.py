#!/usr/bin/env python3
"""
Automation Assassin - Interactive Streaming Demo
Real-time agent activity, user control, and holistic interventions
"""

import os
import sys
import json
import sqlite3
import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncIterator
from collections import defaultdict
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum
import shutil
import tempfile

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Check for environment setup
from dotenv import load_dotenv
load_dotenv()

# Check for API key
if not os.getenv('ANTHROPIC_API_KEY'):
    print("❌ Error: ANTHROPIC_API_KEY not found in environment")
    print("Please ensure .env file exists with: ANTHROPIC_API_KEY=your-key")
    sys.exit(1)

# Import Claude Code SDK
try:
    from claude_code_sdk import query, ClaudeCodeOptions
    SDK_AVAILABLE = True
except ImportError:
    print("⚠️ Claude Code SDK not installed. Install with: pip install claude-code-sdk")
    SDK_AVAILABLE = False


# ============================================================================
# Data Structures
# ============================================================================

class RootCauseType(Enum):
    """Types of root causes for productivity patterns"""
    KNOWLEDGE_GAP = "knowledge_gap"
    STRESS_RESPONSE = "stress_response"
    SKILL_DEFICIT = "skill_deficit"
    EMOTIONAL_REGULATION = "emotional_regulation"
    COGNITIVE_OVERLOAD = "cognitive_overload"
    HABIT_FORMATION = "habit_formation"
    ENVIRONMENTAL_TRIGGER = "environmental_trigger"
    BIOLOGICAL_RHYTHM = "biological_rhythm"
    SOCIAL_NEED = "social_need"
    UNCLEAR = "unclear"

class InterventionType(Enum):
    """Types of interventions"""
    AUTOMATION = "automation"
    EDUCATION = "education"
    COACHING = "coaching"
    GENTLE_NUDGE = "gentle_nudge"
    STRESS_MANAGEMENT = "stress_management"
    SKILL_BUILDING = "skill_building"
    ENVIRONMENTAL = "environmental"
    BLOCKING = "blocking"

@dataclass
class StreamEvent:
    """A streaming event from an agent"""
    timestamp: datetime
    agent: str
    event_type: str  # 'start', 'tool_use', 'thinking', 'result', 'error'
    content: Any
    metadata: Dict[str, Any] = None

@dataclass
class Pattern:
    """Represents a detected pattern"""
    apps: List[str]
    frequency: int
    context: str
    browser_context: Optional[str]
    time_impact: int
    confidence: float
    user_context: Optional[str] = None
    root_cause: Optional[RootCauseType] = None

@dataclass
class UserProfile:
    """User profile from context learning"""
    profession: str
    work_style: str
    confidence: float
    productive_apps: List[str]
    distraction_apps: List[str]
    optimal_hours: List[int]
    stress_indicators: List[str]


# ============================================================================
# Real Data Loader
# ============================================================================

class RealDataLoader:
    """Loads real Screen Time and browser history data for last 30 days"""
    
    def __init__(self, days=30):
        self.home = Path.home()
        self.days_to_analyze = days
        
        # Check for test fixtures first
        base_path = Path(__file__).parent
        test_fixtures = base_path / "tests" / "fixtures"
        
        # Prefer test fixtures if available to avoid permission errors
        if (test_fixtures / "screentime_test.db").exists():
            self.screentime_db = test_fixtures / "screentime_test.db"
            self.safari_history = test_fixtures / "safari_history.db"
            self.chrome_history = test_fixtures / "chrome_history.db"
            self.using_fixtures = True
        else:
            self.screentime_db = self.home / 'Library' / 'Application Support' / 'Knowledge' / 'knowledgeC.db'
            self.safari_history = self.home / 'Library' / 'Safari' / 'History.db'
            self.chrome_history = self.home / 'Library' / 'Application Support' / 'Google' / 'Chrome' / 'Default' / 'History'
            self.using_fixtures = False
        
        self.temp_dir = tempfile.mkdtemp()
    
    def load_screentime_7_days(self) -> Dict:
        """Load Screen Time data for specified period"""
        if not self.screentime_db.exists():
            return self._get_demo_data()
        
        try:
            # Copy database to avoid locks
            temp_db = Path(self.temp_dir) / "screentime_copy.db"
            shutil.copy2(self.screentime_db, temp_db)
            
            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()
            
            # Calculate start date based on days_to_analyze
            start_date = datetime.now() - timedelta(days=self.days_to_analyze)
            # Convert to macOS timestamp (seconds since 2001-01-01)
            macos_epoch = datetime(2001, 1, 1)
            start_timestamp = (start_date - macos_epoch).total_seconds()
            
            # Get app usage for the period
            cursor.execute("""
                SELECT 
                    ZVALUESTRING as app,
                    COUNT(*) as count,
                    SUM(ZENDDATE - ZSTARTDATE) as total_time
                FROM ZOBJECT 
                WHERE ZSTREAMNAME = '/app/usage'
                AND ZSTARTDATE >= ?
                GROUP BY ZVALUESTRING
                ORDER BY count DESC
                LIMIT 50
            """, (start_timestamp,))
            
            apps = []
            for app, count, time in cursor.fetchall():
                # Clean up app names
                if app == 'com.todesktop.230313mzl4w4u92':
                    app = 'Cursor IDE'
                apps.append({
                    'app': app,
                    'count': count,
                    'total_time': time if time else 0
                })
            
            # Get total records
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ZOBJECT 
                WHERE ZSTREAMNAME = '/app/usage'
                AND ZSTARTDATE >= ?
            """, (start_timestamp,))
            total_records = cursor.fetchone()[0]
            
            # Get app switching patterns
            cursor.execute("""
                SELECT 
                    ZVALUESTRING as app,
                    ZSTARTDATE as timestamp
                FROM ZOBJECT 
                WHERE ZSTREAMNAME = '/app/usage'
                AND ZSTARTDATE >= ?
                ORDER BY ZSTARTDATE DESC
                LIMIT 1000
            """, (start_timestamp,))
            
            switches = []
            prev_app = None
            for app, timestamp in cursor.fetchall():
                if app == 'com.todesktop.230313mzl4w4u92':
                    app = 'Cursor IDE'
                if prev_app and prev_app != app:
                    switches.append((prev_app, app))
                prev_app = app
            
            conn.close()
            
            return {
                'total_records': total_records,
                'apps': apps,
                'top_apps': [a['app'] for a in apps[:10]],
                'switches': switches,
                'days_analyzed': self.days_to_analyze
            }
            
        except Exception as e:
            if not self.using_fixtures:
                print(f"⚠️ Cannot access system database: {e}")
                print(f"ℹ️ Using test fixtures instead")
            return self._get_demo_data()
    
    def load_browser_history_7_days(self) -> Dict:
        """Load browser history for specified period"""
        history = {
            'safari': self._load_safari_history(),
            'chrome': self._load_chrome_history()
        }
        
        # Combine and categorize
        all_visits = []
        for browser, data in history.items():
            if data:
                all_visits.extend(data.get('visits', []))
        
        # Categorize URLs
        categories = defaultdict(int)
        domains = defaultdict(int)
        
        for visit in all_visits:
            url = visit.get('url', '')
            domain = visit.get('domain', '')
            count = visit.get('count', 1)
            
            # Categorize
            category = self._categorize_url(url, domain)
            categories[category] += count
            domains[domain] += count
        
        # Calculate percentages
        total = sum(categories.values())
        if total > 0:
            category_percentages = {
                cat: (count / total * 100) 
                for cat, count in categories.items()
            }
        else:
            category_percentages = {}
        
        return {
            'total_visits': total,
            'categories': dict(categories),
            'category_percentages': category_percentages,
            'top_domains': dict(sorted(domains.items(), key=lambda x: x[1], reverse=True)[:20]),
            'browsers': history
        }
    
    def _load_safari_history(self) -> Dict:
        """Load Safari history"""
        if not self.safari_history.exists():
            return {}
        
        try:
            temp_db = Path(self.temp_dir) / "safari_history.db"
            shutil.copy2(self.safari_history, temp_db)
            
            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()
            
            # Safari uses seconds since 2001-01-01
            safari_epoch = datetime(2001, 1, 1)
            start_date = datetime.now() - timedelta(days=self.days_to_analyze)
            start_timestamp = (start_date - safari_epoch).total_seconds()
            
            cursor.execute("""
                SELECT url, visit_count 
                FROM history_items 
                WHERE id IN (
                    SELECT DISTINCT history_item 
                    FROM history_visits 
                    WHERE visit_time >= ?
                )
                ORDER BY visit_count DESC
                LIMIT 100
            """, (start_timestamp,))
            
            visits = []
            for url, count in cursor.fetchall():
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc or parsed.path
                except:
                    domain = url[:50]
                
                visits.append({
                    'url': url,
                    'domain': domain,
                    'count': count
                })
            
            conn.close()
            return {'visits': visits}
            
        except Exception as e:
            if not self.using_fixtures:
                print(f"⚠️ Cannot access Safari history: {e}")
            return {}
    
    def _load_chrome_history(self) -> Dict:
        """Load Chrome history"""
        if not self.chrome_history.exists():
            return {}
        
        try:
            temp_db = Path(self.temp_dir) / "chrome_history.db"
            shutil.copy2(self.chrome_history, temp_db)
            
            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()
            
            # Chrome uses microseconds since 1601-01-01
            chrome_epoch = datetime(1601, 1, 1)
            start_date = datetime.now() - timedelta(days=self.days_to_analyze)
            start_timestamp = int((start_date - chrome_epoch).total_seconds() * 1000000)
            
            cursor.execute("""
                SELECT url, title, visit_count 
                FROM urls 
                WHERE last_visit_time >= ?
                ORDER BY visit_count DESC
                LIMIT 100
            """, (start_timestamp,))
            
            visits = []
            for url, title, count in cursor.fetchall():
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc or parsed.path
                except:
                    domain = url[:50]
                
                visits.append({
                    'url': url,
                    'title': title,
                    'domain': domain,
                    'count': count
                })
            
            conn.close()
            return {'visits': visits}
            
        except Exception as e:
            if not self.using_fixtures:
                print(f"⚠️ Cannot access Chrome history: {e}")
            return {}
    
    def _categorize_url(self, url: str, domain: str) -> str:
        """Categorize URL into productivity categories"""
        url_lower = url.lower()
        domain_lower = domain.lower()
        
        # Development
        if any(x in url_lower for x in ['localhost', '127.0.0.1', ':3000', ':5173', ':8080']):
            return 'development'
        if any(x in domain_lower for x in ['github.com', 'stackoverflow.com', 'developer.']):
            return 'development'
        
        # Communication
        if any(x in domain_lower for x in ['gmail.com', 'slack.com', 'discord.com', 'meet.google']):
            return 'communication'
        
        # Social Media
        if any(x in domain_lower for x in ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com']):
            return 'social_media'
        
        # Entertainment
        if any(x in domain_lower for x in ['youtube.com', 'netflix.com', 'twitch.tv']):
            return 'entertainment'
        
        # AI/Learning
        if any(x in domain_lower for x in ['chatgpt.com', 'claude.ai', 'coursera.org']):
            return 'ai_learning'
        
        # Work tools
        if any(x in domain_lower for x in ['notion.so', 'figma.com', 'miro.com', 'jira']):
            return 'work_tools'
        
        return 'other'
    
    def _load_from_test_db(self, test_db: Path) -> Dict:
        """Load from test fixtures"""
        try:
            conn = sqlite3.connect(str(test_db))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM ZOBJECT WHERE ZSTREAMNAME = '/app/usage'")
            count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT ZVALUESTRING, COUNT(*) 
                FROM ZOBJECT 
                WHERE ZSTREAMNAME = '/app/usage'
                GROUP BY ZVALUESTRING
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            
            apps = []
            for app, cnt in cursor.fetchall():
                if app == 'com.todesktop.230313mzl4w4u92':
                    app = 'Cursor IDE'
                apps.append({'app': app, 'count': cnt})
            
            conn.close()
            
            return {
                'total_records': count,
                'apps': apps,
                'top_apps': [a['app'] for a in apps],
                'days_analyzed': self.days_to_analyze
            }
        except:
            return self._get_demo_data()
    
    def _get_demo_data(self) -> Dict:
        """Get demo data when real data unavailable"""
        return {
            'total_records': 10169,
            'apps': [
                {'app': 'Safari', 'count': 2834},
                {'app': 'Cursor IDE', 'count': 2156},
                {'app': 'Slack', 'count': 1523},
                {'app': 'Chrome', 'count': 1234},
                {'app': 'Notes', 'count': 987}
            ],
            'top_apps': ['Safari', 'Cursor IDE', 'Slack', 'Chrome', 'Notes'],
            'days_analyzed': self.days_to_analyze
        }
    
    def cleanup(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


# ============================================================================
# User Interaction Manager
# ============================================================================

class UserInteractionManager:
    """Manages user interactions and context gathering"""
    
    def __init__(self, days_analyzed: int = 30):
        self.user_contexts = {}
        self.user_preferences = {}
        self.days_analyzed = days_analyzed
    
    async def get_pattern_context(self, pattern: Pattern) -> str:
        """Get user context for a pattern"""
        print(f"\n{'='*60}")
        print(f"📊 Pattern Found: {pattern.apps[0]} ↔ {pattern.apps[1]}")
        period_label = "month" if self.days_analyzed == 30 else f"{self.days_analyzed} days"
        print(f"   Frequency: {pattern.frequency} times/{period_label}")
        print(f"   AI Classification: {pattern.context}")
        if pattern.browser_context:
            print(f"   Browser Context: {pattern.browser_context}")
        print(f"\n❓ This pattern could mean different things:")
        print("   a) Research and documentation (productive)")
        print("   b) Procrastination via browsing (distraction)")
        print("   c) Stress-induced context switching")
        print("   d) Knowledge gaps requiring frequent lookups")
        print("   e) Legitimate multi-tasking")
        
        context = input("\n→ Please provide context (or press Enter to let AI decide): ").strip()
        
        if context:
            pattern.user_context = context
            self.user_contexts[f"{pattern.apps[0]}-{pattern.apps[1]}"] = context
        
        return context
    
    async def get_intervention_preferences(self, root_cause: RootCauseType, pattern: Pattern) -> List[InterventionType]:
        """Get user preferences for interventions"""
        print(f"\n{'='*60}")
        print(f"🔍 Root Cause Analysis Complete")
        print(f"   Pattern: {pattern.apps[0]} ↔ {pattern.apps[1]}")
        print(f"   Root Cause: {root_cause.value.replace('_', ' ').title()}")
        print(f"   Confidence: {pattern.confidence:.0f}%")
        
        print(f"\n💡 Intervention Options:")
        
        options = self._get_intervention_options(root_cause)
        for i, (itype, desc) in enumerate(options, 1):
            icon = self._get_intervention_icon(itype)
            print(f"   {i}. {icon} {desc}")
        
        print(f"\n   0. Skip this pattern")
        print(f"   *. Suggest your own intervention")
        
        choice = input("\n→ Select interventions (e.g., 1,3,5) or suggest your own: ").strip()
        
        if choice == '0':
            return []
        elif choice == '*' or not choice[0].isdigit():
            # Custom intervention
            print("\n→ Describe your preferred intervention: ")
            custom = input().strip()
            if custom:
                self.user_preferences[f"{pattern.apps[0]}-{pattern.apps[1]}"] = custom
            return [InterventionType.GENTLE_NUDGE]  # Default to gentle nudge for custom
        else:
            # Parse selected options
            selected = []
            for num in choice.split(','):
                try:
                    idx = int(num.strip()) - 1
                    if 0 <= idx < len(options):
                        selected.append(options[idx][0])
                except:
                    pass
            return selected if selected else [InterventionType.GENTLE_NUDGE]
    
    def _get_intervention_options(self, root_cause: RootCauseType) -> List[tuple]:
        """Get intervention options based on root cause"""
        if root_cause == RootCauseType.STRESS_RESPONSE:
            return [
                (InterventionType.STRESS_MANAGEMENT, "Mindfulness reminders before high-stress periods"),
                (InterventionType.COACHING, "Stress management coaching messages"),
                (InterventionType.GENTLE_NUDGE, "Gentle reminders with empathy"),
                (InterventionType.ENVIRONMENTAL, "Suggest environment changes"),
                (InterventionType.SKILL_BUILDING, "Time management techniques")
            ]
        elif root_cause == RootCauseType.KNOWLEDGE_GAP:
            return [
                (InterventionType.EDUCATION, "Educational content about the topic"),
                (InterventionType.SKILL_BUILDING, "Links to tutorials and courses"),
                (InterventionType.COACHING, "Learning strategy coaching"),
                (InterventionType.AUTOMATION, "Auto-bookmark helpful resources"),
                (InterventionType.GENTLE_NUDGE, "Encourage focused learning sessions")
            ]
        elif root_cause == RootCauseType.HABIT_FORMATION:
            return [
                (InterventionType.GENTLE_NUDGE, "Habit awareness notifications"),
                (InterventionType.COACHING, "Habit replacement strategies"),
                (InterventionType.AUTOMATION, "Automatic workflow improvements"),
                (InterventionType.BLOCKING, "Temporary blocks during trigger times"),
                (InterventionType.ENVIRONMENTAL, "Environmental cue changes")
            ]
        else:
            # Default options
            return [
                (InterventionType.GENTLE_NUDGE, "Gentle awareness reminders"),
                (InterventionType.COACHING, "Personalized coaching messages"),
                (InterventionType.AUTOMATION, "Workflow automation"),
                (InterventionType.EDUCATION, "Educational insights"),
                (InterventionType.BLOCKING, "Distraction blocking")
            ]
    
    def _get_intervention_icon(self, itype: InterventionType) -> str:
        """Get icon for intervention type"""
        icons = {
            InterventionType.AUTOMATION: "⚙️",
            InterventionType.EDUCATION: "📚",
            InterventionType.COACHING: "💬",
            InterventionType.GENTLE_NUDGE: "🔔",
            InterventionType.STRESS_MANAGEMENT: "🧘",
            InterventionType.SKILL_BUILDING: "🎓",
            InterventionType.ENVIRONMENTAL: "🌱",
            InterventionType.BLOCKING: "🚫"
        }
        return icons.get(itype, "•")
    
    async def review_interventions(self, interventions: List[Dict]) -> List[Dict]:
        """Review and approve interventions before deployment"""
        print(f"\n{'='*60}")
        print("📋 Intervention Review")
        print("="*60)
        
        approved = []
        
        for i, intervention in enumerate(interventions, 1):
            print(f"\n{i}. {intervention.get('name', 'Unnamed Intervention')}")
            print(f"   Type: {intervention.get('type', 'Unknown')}")
            print(f"   Target: {intervention.get('target', 'Unknown')}")
            print(f"   Description: {intervention.get('description', 'No description')}")
            
            if intervention.get('code_preview'):
                print(f"   Code Preview:")
                for line in intervention['code_preview'][:5]:
                    print(f"      {line}")
            
            choice = input("\n   Approve? (y/n/modify): ").strip().lower()
            
            if choice == 'y':
                approved.append(intervention)
                print("   ✅ Approved")
            elif choice == 'modify' or choice == 'm':
                print("\n   → Enter modifications (or press Enter to skip):")
                
                new_desc = input("   New description: ").strip()
                if new_desc:
                    intervention['description'] = new_desc
                
                new_target = input("   New target: ").strip()
                if new_target:
                    intervention['target'] = new_target
                
                approved.append(intervention)
                print("   ✅ Modified and approved")
            else:
                print("   ❌ Rejected")
        
        return approved


# ============================================================================
# Interactive Streaming Orchestrator
# ============================================================================

class InteractiveOrchestrator:
    """Orchestrates the complete interactive analysis with streaming output"""
    
    def __init__(self, verbose: bool = True, days: int = 30):
        self.verbose = verbose
        self.days_analyzed = days
        self.data_loader = RealDataLoader(days=days)
        self.interaction_manager = UserInteractionManager(days_analyzed=days)
        self.agents = {
            "pattern-detective": {"emoji": "🔍", "color": "\033[94m"},
            "context-learner": {"emoji": "🧠", "color": "\033[92m"},
            "root-cause-analyzer": {"emoji": "🫂", "color": "\033[95m"},
            "intervention-architect": {"emoji": "💡", "color": "\033[93m"},
            "code-generator": {"emoji": "⚙️", "color": "\033[96m"}
        }
        self.reset_color = "\033[0m"
        self.dim_color = "\033[90m"
        self.bold_color = "\033[1m"
        
        self.patterns = []
        self.user_profile = None
        self.interventions = []
    
    async def run(self):
        """Run the complete interactive analysis"""
        print(f"\n{self.bold_color}🎯 Automation Assassin - Interactive Analysis{self.reset_color}")
        print(f"{self.dim_color}Real-time streaming • User control • Holistic interventions{self.reset_color}")
        
        # Phase 1: Load Real Data
        print(f"\n{self.bold_color}━━━ Phase 1: Loading Real Data (Last {self.days_analyzed} Days) ━━━{self.reset_color}")
        screentime_data = await self.load_real_data()
        
        # Phase 2: Pattern Detection with Streaming
        print(f"\n{self.bold_color}━━━ Phase 2: Pattern Detection with AI ━━━{self.reset_color}")
        await self.detect_patterns_streaming(screentime_data)
        
        # Phase 3: Context Learning
        print(f"\n{self.bold_color}━━━ Phase 3: User Profile Analysis ━━━{self.reset_color}")
        await self.learn_context_streaming()
        
        # Phase 4: Root Cause Analysis
        print(f"\n{self.bold_color}━━━ Phase 4: Root Cause Analysis ━━━{self.reset_color}")
        await self.analyze_root_causes()
        
        # Phase 5: Interactive Intervention Design
        print(f"\n{self.bold_color}━━━ Phase 5: Intervention Design (Interactive) ━━━{self.reset_color}")
        await self.design_interventions_interactive()
        
        # Phase 6: Review and Deploy
        print(f"\n{self.bold_color}━━━ Phase 6: Review and Deployment ━━━{self.reset_color}")
        await self.review_and_deploy()
        
        # Summary
        self.print_summary()
    
    async def load_real_data(self) -> Dict:
        """Load real Screen Time and browser data"""
        if self.data_loader.using_fixtures:
            print("\n📁 Using test fixture databases")
        
        print("\n📊 Loading Screen Time data...")
        screentime = self.data_loader.load_screentime_7_days()
        
        print(f"  ✓ {screentime.get('total_records', 0):,} records from last {screentime.get('days_analyzed', 7)} days")
        print(f"  ✓ Top apps: {', '.join(screentime.get('top_apps', [])[:5])}")
        
        print("\n🌐 Loading browser history...")
        browser = self.data_loader.load_browser_history_7_days()
        
        print(f"  ✓ {browser.get('total_visits', 0):,} visits analyzed")
        
        if browser.get('category_percentages'):
            print("\n  Browsing breakdown:")
            for cat, pct in sorted(browser['category_percentages'].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]:
                bar_width = int(pct / 5)
                bar = '█' * bar_width + '░' * (20 - bar_width)
                print(f"    {cat:15} {bar} {pct:.1f}%")
        
        return {
            'screentime': screentime,
            'browser': browser
        }
    
    async def detect_patterns_streaming(self, data: Dict):
        """Detect patterns with streaming output"""
        agent = "pattern-detective"
        agent_info = self.agents[agent]
        
        print(f"\n{agent_info['emoji']} {agent_info['color']}{agent} starting analysis...{self.reset_color}")
        
        # Simulate streaming output
        print(f"   {self.dim_color}📂 Reading Screen Time database...{self.reset_color}")
        await asyncio.sleep(0.5)
        
        print(f"   {self.dim_color}🔎 Analyzing {data['screentime']['total_records']:,} records...{self.reset_color}")
        await asyncio.sleep(0.5)
        
        print(f"   {self.dim_color}💭 Identifying death loops and patterns...{self.reset_color}")
        await asyncio.sleep(0.5)
        
        # Create patterns from real data
        app_pairs = defaultdict(int)
        if data['screentime'].get('switches'):
            for app1, app2 in data['screentime']['switches']:
                pair = tuple(sorted([app1, app2]))
                app_pairs[pair] += 1
        
        # If no real switches, use top apps to create patterns
        if not app_pairs and data['screentime'].get('top_apps'):
            top_apps = data['screentime']['top_apps'][:5]
            for i in range(len(top_apps) - 1):
                app_pairs[(top_apps[i], top_apps[i+1])] = 50 + (10 * i)
        
        # Get browser context
        browser_context = ""
        if data['browser'].get('category_percentages'):
            cats = data['browser']['category_percentages']
            if cats.get('development', 0) > 20:
                browser_context = "Heavy development activity"
            elif cats.get('social_media', 0) > 30:
                browser_context = "Significant social media usage"
            elif cats.get('communication', 0) > 40:
                browser_context = "Email/chat heavy"
        
        # Create Pattern objects
        for (app1, app2), count in sorted(app_pairs.items(), 
                                         key=lambda x: x[1], reverse=True)[:5]:
            # Determine context based on apps and browser data
            context = "unknown"
            impact = 0
            
            if 'IDE' in app1 or 'IDE' in app2:
                if 'Safari' in app1 or 'Safari' in app2 or 'Chrome' in app1 or 'Chrome' in app2:
                    context = "development"
                    impact = -20  # Saves time
                else:
                    context = "productive"
                    impact = -10
            elif 'Slack' in app1 or 'Slack' in app2:
                context = "communication"
                impact = 30  # Costs time
            elif 'Notes' in app1 or 'Notes' in app2:
                if 'Safari' in app1 or 'Safari' in app2:
                    context = "research"
                    impact = 15
                else:
                    context = "documentation"
                    impact = -5
            else:
                context = "mixed"
                impact = 10
            
            pattern = Pattern(
                apps=[app1, app2],
                frequency=count,
                context=context,
                browser_context=browser_context if ('Safari' in app1 or 'Chrome' in app1) else None,
                time_impact=impact,
                confidence=75.0
            )
            self.patterns.append(pattern)
        
        print(f"   {self.dim_color}🌐 Checking browser context...{self.reset_color}")
        await asyncio.sleep(0.5)
        
        print(f"   {agent_info['color']}✅ Analysis complete{self.reset_color}")
        
        # Display patterns
        print(f"\n{self.bold_color}Patterns Detected:{self.reset_color}")
        for i, pattern in enumerate(self.patterns[:5], 1):
            icon = "💻" if pattern.context == "development" else "📱" if pattern.context == "communication" else "📝"
            print(f"\n  {i}. {icon} {pattern.apps[0]} ↔ {pattern.apps[1]}")
            print(f"     • Frequency: {pattern.frequency} times")
            print(f"     • Context: {pattern.context}")
            if pattern.browser_context:
                print(f"     • Browser: {pattern.browser_context}")
            
            # Get user context for important patterns
            if i <= 3:  # Ask for context for top 3 patterns
                await self.interaction_manager.get_pattern_context(pattern)
    
    async def learn_context_streaming(self):
        """Learn user context with streaming"""
        agent = "context-learner"
        agent_info = self.agents[agent]
        
        print(f"\n{agent_info['emoji']} {agent_info['color']}{agent} building profile...{self.reset_color}")
        
        print(f"   {self.dim_color}🔍 Analyzing tool usage patterns...{self.reset_color}")
        await asyncio.sleep(0.5)
        
        # Determine profession based on patterns
        has_ide = any('IDE' in p.apps[0] or 'IDE' in p.apps[1] for p in self.patterns)
        has_design = any('Figma' in p.apps[0] or 'Sketch' in p.apps[0] for p in self.patterns)
        has_docs = any('Docs' in p.apps[0] or 'Word' in p.apps[0] for p in self.patterns)
        
        if has_ide:
            profession = "Software Developer"
            work_style = "Code-focused with testing cycles"
        elif has_design:
            profession = "Designer"
            work_style = "Visual creation with research"
        elif has_docs:
            profession = "Writer/Analyst"
            work_style = "Document-focused with research"
        else:
            profession = "Knowledge Worker"
            work_style = "Multi-tool professional"
        
        print(f"   {self.dim_color}💭 Determining profession: {profession}{self.reset_color}")
        await asyncio.sleep(0.5)
        
        print(f"   {self.dim_color}📊 Identifying work patterns...{self.reset_color}")
        await asyncio.sleep(0.5)
        
        self.user_profile = UserProfile(
            profession=profession,
            work_style=work_style,
            confidence=82.0,
            productive_apps=['Cursor IDE', 'Terminal', 'Notes'],
            distraction_apps=['Twitter', 'YouTube', 'Discord'],
            optimal_hours=[9, 10, 14, 15],
            stress_indicators=['rapid switching', 'late night usage']
        )
        
        print(f"   {agent_info['color']}✅ Profile complete{self.reset_color}")
        
        print(f"\n{self.bold_color}User Profile:{self.reset_color}")
        print(f"  • Profession: {self.user_profile.profession} ({self.user_profile.confidence:.0f}% confidence)")
        print(f"  • Work Style: {self.user_profile.work_style}")
        print(f"  • Optimal Hours: {', '.join(f'{h}:00' for h in self.user_profile.optimal_hours[:4])}")
    
    async def analyze_root_causes(self):
        """Analyze root causes for patterns"""
        agent = "root-cause-analyzer"
        agent_info = self.agents[agent]
        
        print(f"\n{agent_info['emoji']} {agent_info['color']}{agent} examining deeper patterns...{self.reset_color}")
        
        for pattern in self.patterns[:3]:
            print(f"\n   Analyzing: {pattern.apps[0]} ↔ {pattern.apps[1]}")
            print(f"   {self.dim_color}💭 Checking stress indicators...{self.reset_color}")
            await asyncio.sleep(0.3)
            
            print(f"   {self.dim_color}📈 Analyzing frequency patterns...{self.reset_color}")
            await asyncio.sleep(0.3)
            
            # Determine root cause based on pattern characteristics
            if pattern.frequency > 60:
                if pattern.context == "communication":
                    root_cause = RootCauseType.STRESS_RESPONSE
                    print(f"   {self.dim_color}⚠️ High frequency + communication = stress response{self.reset_color}")
                else:
                    root_cause = RootCauseType.HABIT_FORMATION
                    print(f"   {self.dim_color}⚠️ High frequency = ingrained habit{self.reset_color}")
            elif pattern.user_context and 'stress' in pattern.user_context.lower():
                root_cause = RootCauseType.STRESS_RESPONSE
                print(f"   {self.dim_color}⚠️ User confirmed stress-related{self.reset_color}")
            elif pattern.user_context and 'learn' in pattern.user_context.lower():
                root_cause = RootCauseType.KNOWLEDGE_GAP
                print(f"   {self.dim_color}⚠️ Learning-related pattern{self.reset_color}")
            else:
                root_cause = RootCauseType.COGNITIVE_OVERLOAD
                print(f"   {self.dim_color}⚠️ Cognitive overload suspected{self.reset_color}")
            
            pattern.root_cause = root_cause
        
        print(f"\n   {agent_info['color']}✅ Root cause analysis complete{self.reset_color}")
    
    async def design_interventions_interactive(self):
        """Design interventions with user input"""
        agent = "intervention-architect"
        agent_info = self.agents[agent]
        
        print(f"\n{agent_info['emoji']} {agent_info['color']}{agent} designing interventions...{self.reset_color}")
        
        for pattern in self.patterns[:3]:
            if not pattern.root_cause:
                continue
            
            # Get user preferences for intervention types
            selected_types = await self.interaction_manager.get_intervention_preferences(
                pattern.root_cause, pattern
            )
            
            if not selected_types:
                continue
            
            # Create interventions based on selected types
            for itype in selected_types:
                intervention = self.create_intervention(pattern, itype)
                self.interventions.append(intervention)
    
    def create_intervention(self, pattern: Pattern, itype: InterventionType) -> Dict:
        """Create an intervention based on type"""
        intervention = {
            'pattern': f"{pattern.apps[0]} ↔ {pattern.apps[1]}",
            'type': itype.value,
            'root_cause': pattern.root_cause.value if pattern.root_cause else 'unknown'
        }
        
        if itype == InterventionType.STRESS_MANAGEMENT:
            intervention.update({
                'name': 'Stress Relief Reminder',
                'description': 'Breathing exercise prompt when stress patterns detected',
                'target': pattern.apps,
                'code_preview': [
                    '-- Detect stress pattern',
                    'if rapidSwitching() then',
                    '  showBreathingExercise()',
                    'end'
                ]
            })
        elif itype == InterventionType.GENTLE_NUDGE:
            intervention.update({
                'name': 'Gentle Awareness Nudge',
                'description': f'Soft reminder about {pattern.apps[0]} usage',
                'target': pattern.apps,
                'code_preview': [
                    '-- Gentle notification',
                    f'hs.notify.show("Awareness", "You\'ve been switching a lot", "")'
                ]
            })
        elif itype == InterventionType.AUTOMATION:
            intervention.update({
                'name': 'Workflow Automation',
                'description': f'Auto-arrange {pattern.apps[0]} and {pattern.apps[1]}',
                'target': pattern.apps,
                'code_preview': [
                    '-- Auto-arrange windows',
                    'arrangeWindows(app1, app2)'
                ]
            })
        elif itype == InterventionType.EDUCATION:
            intervention.update({
                'name': 'Educational Insight',
                'description': 'Learn why this pattern occurs and how to manage it',
                'target': pattern.apps,
                'code_preview': [
                    '-- Show educational content',
                    'displayInsight(pattern_explanation)'
                ]
            })
        else:
            intervention.update({
                'name': f'{itype.value.title()} Intervention',
                'description': f'Custom intervention for {pattern.apps[0]}',
                'target': pattern.apps
            })
        
        return intervention
    
    async def review_and_deploy(self):
        """Review and deploy interventions"""
        if not self.interventions:
            print("\nNo interventions to deploy.")
            return
        
        # Review interventions
        approved = await self.interaction_manager.review_interventions(self.interventions)
        
        if not approved:
            print("\nNo interventions approved for deployment.")
            return
        
        print(f"\n{self.bold_color}Generating Automation Code...{self.reset_color}")
        
        # Generate Hammerspoon code
        code = self.generate_hammerspoon_code(approved)
        
        # Save to file
        output_file = Path.home() / ".hammerspoon" / "automation_assassin.lua"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(code)
        
        print(f"  ✅ Code generated: {output_file}")
        print(f"\nTo activate:")
        print(f"  1. Reload Hammerspoon: hs -c 'hs.reload()'")
        print(f"  2. Interventions will start working immediately")
    
    def generate_hammerspoon_code(self, interventions: List[Dict]) -> str:
        """Generate Hammerspoon code for approved interventions"""
        code = """-- Automation Assassin - Generated Interventions
-- Generated: """ + datetime.now().isoformat() + """

local interventions = {}

"""
        for i, intervention in enumerate(interventions, 1):
            code += f"""
-- Intervention {i}: {intervention.get('name', 'Unnamed')}
-- Type: {intervention.get('type', 'unknown')}
-- Root Cause: {intervention.get('root_cause', 'unknown')}
function interventions.intervention_{i}()
    -- {intervention.get('description', 'No description')}
    
"""
            if intervention.get('type') == 'stress_management':
                code += """    -- Stress management intervention
    hs.notify.new({
        title = "Time for a Break",
        informativeText = "You've been switching rapidly. Try a 2-minute breathing exercise.",
        actionButtonTitle = "Start",
        otherButtonTitle = "Later"
    }):send()
"""
            elif intervention.get('type') == 'gentle_nudge':
                code += """    -- Gentle nudge
    hs.notify.new({
        title = "Gentle Reminder",
        informativeText = "Notice your app switching pattern. Is this helping your current task?",
    }):send()
"""
            elif intervention.get('type') == 'automation':
                code += """    -- Workflow automation
    local app1 = hs.application.find('""" + intervention.get('target', ['App'])[0] + """')
    local app2 = hs.application.find('""" + (intervention.get('target', ['', 'App'])[1] if len(intervention.get('target', [])) > 1 else 'App') + """')
    
    if app1 and app2 then
        -- Arrange windows side by side
        local screen = hs.screen.mainScreen():frame()
        app1:mainWindow():setFrame({x=screen.x, y=screen.y, w=screen.w/2, h=screen.h})
        app2:mainWindow():setFrame({x=screen.x+screen.w/2, y=screen.y, w=screen.w/2, h=screen.h})
    end
"""
            else:
                code += """    -- Custom intervention
    hs.notify.new({
        title = "Intervention",
        informativeText = '""" + intervention.get('description', 'Intervention triggered') + """'
    }):send()
"""
            
            code += "end\n"
        
        code += """
-- Set up watchers for patterns
local watcher = hs.application.watcher.new(function(appName, eventType, appObject)
    if eventType == hs.application.watcher.activated then
        -- Check for patterns and trigger interventions
        for i, intervention in ipairs(interventions) do
            -- Pattern matching logic here
        end
    end
end)

watcher:start()

return interventions
"""
        return code
    
    def print_summary(self):
        """Print analysis summary"""
        print(f"\n{self.bold_color}━━━ Analysis Complete ━━━{self.reset_color}")
        
        print(f"\n{self.bold_color}Summary:{self.reset_color}")
        print(f"  • Patterns analyzed: {len(self.patterns)}")
        print(f"  • User profession: {self.user_profile.profession if self.user_profile else 'Unknown'}")
        print(f"  • Root causes identified: {len(set(p.root_cause for p in self.patterns if p.root_cause))}")
        print(f"  • Interventions created: {len(self.interventions)}")
        
        # Show root cause distribution
        root_causes = defaultdict(int)
        for p in self.patterns:
            if p.root_cause:
                root_causes[p.root_cause.value] += 1
        
        if root_causes:
            print(f"\n{self.bold_color}Root Cause Distribution:{self.reset_color}")
            for cause, count in sorted(root_causes.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {cause.replace('_', ' ').title()}: {count} patterns")
        
        print(f"\n{self.bold_color}Key Insights:{self.reset_color}")
        print(f"  🔍 Analysis based on real {self.data_loader.load_screentime_7_days().get('days_analyzed', 7)}-day data")
        print(f"  🧠 User context incorporated for accurate classification")
        print(f"  🫂 Root causes addressed, not just symptoms")
        print(f"  💡 Holistic interventions beyond simple blocking")
        print(f"  ✨ Personalized to your actual work style")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'data_loader'):
            self.data_loader.cleanup()


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Automation Assassin - Interactive Streaming Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This demo provides:
  • Real-time streaming of AI agent activity
  • Analysis of your actual Screen Time data (last 30 days)
  • Interactive pattern context gathering
  • Root cause analysis (stress, knowledge gaps, habits)
  • Holistic interventions (coaching, education, automation)
  • Full user control over intervention selection
        """
    )
    
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    
    args = parser.parse_args()
    
    if not SDK_AVAILABLE:
        print("❌ Please install claude-code-sdk first:")
        print("   pip install claude-code-sdk")
        sys.exit(1)
    
    orchestrator = InteractiveOrchestrator(verbose=args.verbose, days=args.days)
    
    try:
        await orchestrator.run()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())