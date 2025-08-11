#!/usr/bin/env python3
"""
Automation Assassin - Browser-Aware Pattern Detection
Integrates browser history for deeper context understanding
"""

import os
import sys
import time
import json
import sqlite3
import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from urllib.parse import urlparse

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    from claude_code_sdk.types import AssistantMessage, ResultMessage
    SDK_AVAILABLE = True
except ImportError:
    print("⚠️ Claude Code SDK not installed. Install with: pip install claude-code-sdk")
    SDK_AVAILABLE = False


class BrowserHistoryAnalyzer:
    """Analyzes browser history to provide context for app switches"""
    
    def __init__(self, safari_db: Optional[str] = None, chrome_db: Optional[str] = None):
        self.safari_db = safari_db
        self.chrome_db = chrome_db
        self.history_cache = {}
    
    def get_safari_history(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get Safari browsing history for a time range"""
        if not self.safari_db or not Path(self.safari_db).exists():
            return []
        
        try:
            conn = sqlite3.connect(self.safari_db)
            cursor = conn.cursor()
            
            # Convert to macOS reference time
            start_ref = (start_time.timestamp() - 978307200)
            end_ref = (end_time.timestamp() - 978307200)
            
            cursor.execute("""
                SELECT 
                    url,
                    title,
                    datetime(visit_time + 978307200, 'unixepoch', 'localtime') as visit_time,
                    visit_count
                FROM history_items 
                JOIN history_visits ON history_items.id = history_visits.history_item
                WHERE visit_time >= ? AND visit_time <= ?
                ORDER BY visit_time DESC
                LIMIT 100
            """, (start_ref, end_ref))
            
            results = []
            for row in cursor.fetchall():
                url, title, visit_time, count = row
                domain = urlparse(url).netloc
                
                # Categorize the URL
                category = self._categorize_url(url, title)
                
                results.append({
                    'url': url,
                    'title': title or '',
                    'domain': domain,
                    'category': category,
                    'timestamp': visit_time,
                    'visit_count': count
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error reading Safari history: {e}")
            return []
    
    def get_chrome_history(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get Chrome browsing history for a time range"""
        if not self.chrome_db or not Path(self.chrome_db).exists():
            return []
        
        try:
            conn = sqlite3.connect(self.chrome_db)
            cursor = conn.cursor()
            
            # Chrome uses microseconds since 1601-01-01
            chrome_epoch = datetime(1601, 1, 1)
            start_chrome = int((start_time - chrome_epoch).total_seconds() * 1000000)
            end_chrome = int((end_time - chrome_epoch).total_seconds() * 1000000)
            
            cursor.execute("""
                SELECT 
                    urls.url,
                    urls.title,
                    datetime(visits.visit_time/1000000 - 11644473600, 'unixepoch', 'localtime') as visit_time,
                    urls.visit_count
                FROM urls
                JOIN visits ON urls.id = visits.url
                WHERE visits.visit_time >= ? AND visits.visit_time <= ?
                ORDER BY visits.visit_time DESC
                LIMIT 100
            """, (start_chrome, end_chrome))
            
            results = []
            for row in cursor.fetchall():
                url, title, visit_time, count = row
                domain = urlparse(url).netloc
                category = self._categorize_url(url, title)
                
                results.append({
                    'url': url,
                    'title': title or '',
                    'domain': domain,
                    'category': category,
                    'timestamp': visit_time,
                    'visit_count': count
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error reading Chrome history: {e}")
            return []
    
    def _categorize_url(self, url: str, title: str = "") -> str:
        """Intelligently categorize a URL based on domain and title"""
        url_lower = url.lower()
        title_lower = title.lower() if title else ""
        domain = urlparse(url).netloc.lower()
        
        # Development related
        if any(x in domain for x in ['github.com', 'gitlab.com', 'bitbucket.org', 'stackoverflow.com']):
            return 'development'
        if any(x in url_lower for x in ['localhost:', '127.0.0.1:', '0.0.0.0:']):
            return 'local_testing'
        if 'npm' in domain or 'pypi.org' in domain or 'docs.' in domain:
            return 'documentation'
        
        # Communication
        if any(x in domain for x in ['slack.com', 'discord.com', 'teams.microsoft', 'zoom.us']):
            return 'communication'
        if 'mail' in domain or 'gmail' in domain or 'outlook' in domain:
            return 'email'
        
        # Social media
        if any(x in domain for x in ['twitter.com', 'x.com', 'facebook.com', 'instagram.com', 'linkedin.com', 'reddit.com']):
            return 'social_media'
        
        # News/Entertainment
        if any(x in domain for x in ['youtube.com', 'netflix.com', 'twitch.tv']):
            return 'entertainment'
        if any(x in domain for x in ['news', 'cnn.', 'bbc.', 'nytimes.']):
            return 'news'
        
        # Productivity
        if any(x in domain for x in ['notion.', 'trello.', 'asana.', 'jira.', 'confluence.']):
            return 'productivity'
        if 'docs.google' in domain or 'sheets.google' in domain:
            return 'productivity'
        
        # AI/ML
        if any(x in domain for x in ['claude.ai', 'chatgpt', 'openai', 'anthropic', 'huggingface']):
            return 'ai_tools'
        
        # Search
        if any(x in domain for x in ['google.com/search', 'bing.com', 'duckduckgo']):
            return 'search'
        
        return 'other'
    
    def get_context_for_app_switch(self, app1: str, app2: str, timestamp: datetime) -> Dict:
        """Get browser context around an app switch"""
        # Look 5 minutes before and after the switch
        start_time = timestamp - timedelta(minutes=5)
        end_time = timestamp + timedelta(minutes=5)
        
        safari_history = self.get_safari_history(start_time, end_time)
        chrome_history = self.get_chrome_history(start_time, end_time)
        
        # Combine and analyze
        all_history = safari_history + chrome_history
        
        if not all_history:
            return {'context': 'unknown', 'confidence': 0}
        
        # Count categories
        categories = defaultdict(int)
        for item in all_history:
            categories[item['category']] += 1
        
        # Determine primary activity
        if categories['local_testing'] > 0 or categories['development'] > 2:
            return {
                'context': 'web_development',
                'confidence': 0.9,
                'evidence': 'Local testing or dev sites visited',
                'urls': [h['domain'] for h in all_history[:3]]
            }
        elif categories['documentation'] > 2:
            return {
                'context': 'learning',
                'confidence': 0.8,
                'evidence': 'Documentation sites visited',
                'urls': [h['domain'] for h in all_history[:3]]
            }
        elif categories['social_media'] > 3:
            return {
                'context': 'distraction',
                'confidence': 0.9,
                'evidence': 'Social media browsing',
                'urls': [h['domain'] for h in all_history[:3]]
            }
        elif categories['communication'] > 2:
            return {
                'context': 'communication',
                'confidence': 0.7,
                'evidence': 'Work communication',
                'urls': [h['domain'] for h in all_history[:3]]
            }
        else:
            return {
                'context': 'mixed',
                'confidence': 0.5,
                'evidence': 'Various activities',
                'urls': [h['domain'] for h in all_history[:3]]
            }


class BrowserAwareDemo:
    """Demo with browser history integration"""
    
    def __init__(self, auto_mode: bool = False):
        self.auto_mode = auto_mode
        self.session_id = None
        self.total_cost = 0.0
        self.total_tokens = 0
        
        # Initialize browser analyzer
        fixtures_path = Path(__file__).parent / "tests" / "fixtures"
        self.browser_analyzer = BrowserHistoryAnalyzer(
            safari_db=str(fixtures_path / "safari_history.db"),
            chrome_db=str(fixtures_path / "chrome_history.db")
        )
    
    async def run(self):
        """Run the browser-aware demo"""
        self._print_header()
        
        # Load Screen Time data
        db_path = Path(__file__).parent / "tests" / "fixtures" / "screentime_test.db"
        if not db_path.exists():
            print("❌ Screen Time database not found")
            return
        
        print("\n📊 Loading Screen Time and Browser History...")
        
        # Get Screen Time patterns
        patterns = self._get_screentime_patterns(str(db_path))
        
        # Enrich with browser context
        enriched_patterns = await self._enrich_with_browser_context(patterns)
        
        # Analyze with AI
        insights = await self._analyze_with_ai(enriched_patterns)
        
        # Display results
        self._display_results(insights)
    
    def _print_header(self):
        """Print header"""
        print("\n" + "="*60)
        print("🌐 BROWSER-AWARE PATTERN DETECTION")
        print("Understanding what you're actually doing")
        print("="*60)
    
    def _get_screentime_patterns(self, db_path: str) -> Dict:
        """Get basic Screen Time patterns"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get app switches with timestamps
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN ZVALUESTRING = 'com.todesktop.230313mzl4w4u92' THEN 'Cursor IDE'
                        ELSE ZVALUESTRING 
                    END as app,
                    DATETIME(ZSTARTDATE + 978307200, 'unixepoch', 'localtime') as timestamp
                FROM ZOBJECT 
                WHERE ZSTREAMNAME = '/app/usage'
                ORDER BY ZSTARTDATE DESC
                LIMIT 200
            """)
            
            switches = cursor.fetchall()
            conn.close()
            
            # Find patterns
            patterns = []
            for i in range(len(switches) - 1):
                app1, time1 = switches[i]
                app2, time2 = switches[i+1]
                
                # Convert timestamp string to datetime
                timestamp = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
                
                patterns.append({
                    'from_app': app1,
                    'to_app': app2,
                    'timestamp': timestamp,
                    'time_str': time1
                })
            
            print(f"✓ Found {len(patterns)} app switches")
            return {'switches': patterns}
            
        except Exception as e:
            print(f"Error loading Screen Time: {e}")
            return {'switches': []}
    
    async def _enrich_with_browser_context(self, patterns: Dict) -> Dict:
        """Enrich patterns with browser history context"""
        print("\n🔍 Analyzing browser context for app switches...")
        
        enriched_switches = []
        context_summary = defaultdict(int)
        
        for switch in patterns['switches'][:50]:  # Analyze first 50 switches
            # Get browser context
            if 'Safari' in switch['from_app'] or 'Safari' in switch['to_app']:
                context = self.browser_analyzer.get_context_for_app_switch(
                    switch['from_app'],
                    switch['to_app'],
                    switch['timestamp']
                )
                
                switch['browser_context'] = context
                context_summary[context['context']] += 1
                
                # Show some examples
                if len(enriched_switches) < 3 and context['confidence'] > 0.7:
                    enriched_switches.append(switch)
        
        # Display context summary
        print("\n📈 Browser Context Summary:")
        for context_type, count in context_summary.items():
            emoji = {
                'web_development': '💻',
                'learning': '📚',
                'distraction': '🚫',
                'communication': '💬',
                'mixed': '🔄'
            }.get(context_type, '•')
            print(f"  {emoji} {context_type}: {count} switches")
        
        # Show enriched examples
        if enriched_switches:
            print("\n💡 Example Context-Aware Patterns:")
            for switch in enriched_switches:
                ctx = switch['browser_context']
                print(f"\n  {switch['from_app']} → {switch['to_app']}")
                print(f"    Context: {ctx['context']} (confidence: {ctx['confidence']:.0%})")
                print(f"    Evidence: {ctx['evidence']}")
                if ctx.get('urls'):
                    print(f"    Sites: {', '.join(ctx['urls'][:3])}")
        
        patterns['enriched_switches'] = enriched_switches
        patterns['context_summary'] = dict(context_summary)
        
        return patterns
    
    async def _analyze_with_ai(self, patterns: Dict) -> Dict:
        """Analyze enriched patterns with AI"""
        if not SDK_AVAILABLE:
            return self._get_fallback_insights(patterns)
        
        print("\n🤖 AI Analysis with Browser Context...")
        
        try:
            options = ClaudeCodeOptions(
                permission_mode="bypassPermissions",
                max_turns=3,
                continue_conversation=False
            )
            
            # Prepare context-aware prompt
            context_data = json.dumps(patterns['context_summary'], indent=2)
            examples = []
            for switch in patterns.get('enriched_switches', [])[:3]:
                ctx = switch.get('browser_context', {})
                examples.append(f"{switch['from_app']} → {switch['to_app']}: {ctx.get('context', 'unknown')}")
            
            prompt = f"""Analyze these app switching patterns WITH browser context:

Context Summary:
{context_data}

Example Patterns with Browser Context:
{chr(10).join(examples)}

Key insights:
1. When Cursor IDE ↔ Safari with local testing URLs = productive web development
2. When Slack ↔ Chrome with social media = distraction pattern
3. When Safari shows documentation sites = learning/research

Provide insights about:
- Which patterns are truly productive vs distracting
- What the user is actually working on
- Specific recommendations based on browser activity"""

            insights = {}
            
            # Make API call with timeout
            async def query_with_timeout():
                async for message in query(prompt=prompt, options=options):
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                text = block.text.strip()
                                if text:
                                    insights['ai_analysis'] = text
                                    return
                    
                    if hasattr(message, 'subtype') and message.subtype in ['error', 'result']:
                        break
            
            try:
                await asyncio.wait_for(query_with_timeout(), timeout=10.0)
            except asyncio.TimeoutError:
                print("  ⚠️ AI timeout - using fallback")
            
            if not insights:
                insights = self._get_fallback_insights(patterns)
            
            return insights
            
        except Exception as e:
            print(f"  ❌ AI error: {e}")
            return self._get_fallback_insights(patterns)
    
    def _get_fallback_insights(self, patterns: Dict) -> Dict:
        """Fallback insights when AI not available"""
        context_summary = patterns.get('context_summary', {})
        
        insights = {
            'ai_analysis': f"""Based on browser context analysis:

• Web Development Activity: {context_summary.get('web_development', 0)} sessions detected
  - Cursor IDE ↔ Safari switches are productive when visiting localhost
  - Indicates active testing and development workflow

• Learning Sessions: {context_summary.get('learning', 0)} documentation visits
  - Research and skill development detected
  - Consider batching research time for better focus

• Distraction Patterns: {context_summary.get('distraction', 0)} social media sessions
  - Social media visits interrupt workflow
  - Recommend blocking during focus hours

Key Recommendation: Your Cursor ↔ Safari pattern is PRODUCTIVE when combined with 
local testing URLs. This is web development, not procrastination."""
        }
        
        return insights
    
    def _display_results(self, insights: Dict):
        """Display final results"""
        print("\n" + "="*60)
        print("✅ BROWSER-AWARE INSIGHTS")
        print("="*60)
        
        if insights.get('ai_analysis'):
            print(f"\n{insights['ai_analysis']}")
        
        print("\n🎯 Key Takeaways:")
        print("  • Browser history reveals true intent behind app switches")
        print("  • Local testing URLs = productive development")
        print("  • Social media URLs = distraction patterns")
        print("  • Documentation URLs = learning/research")
        
        print("\n📊 Next Steps:")
        print("  1. Enhance productive patterns (split-screen for testing)")
        print("  2. Block distracting patterns (social media batching)")
        print("  3. Optimize learning sessions (dedicated research time)")
        
        print("\n✨ Your patterns are now understood with full context!\n")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Browser-Aware Pattern Detection Demo"
    )
    parser.add_argument("--auto", action="store_true", help="Skip prompts")
    
    args = parser.parse_args()
    
    demo = BrowserAwareDemo(auto_mode=args.auto)
    
    try:
        await demo.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())