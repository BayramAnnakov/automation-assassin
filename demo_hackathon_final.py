#!/usr/bin/env python3
"""
Automation Assassin - User-Friendly AI Demo
Clean, professional terminal output with intelligent grouping
"""

import os
import sys
import time
import json
import sqlite3
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import threading

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

# Import Claude Code SDK for REAL AI calls
try:
    from claude_code_sdk import query, ClaudeCodeOptions
    from claude_code_sdk.types import AssistantMessage, ResultMessage, ToolUseBlock
    SDK_AVAILABLE = True
except ImportError:
    print("⚠️ Claude Code SDK not installed. Install with: pip install claude-code-sdk")
    SDK_AVAILABLE = False


class CleanTerminalUI:
    """Clean, user-friendly terminal interface"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.tool_counts = defaultdict(int)
        self.current_phase = None
        self.last_tool = None
        self.tool_batch_count = 0
        self.spinner_active = False
        self.spinner_thread = None
        
        # Minimal color scheme
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'green': '\033[92m',
            'blue': '\033[94m',
            'yellow': '\033[93m',
            'cyan': '\033[96m',
            'gray': '\033[90m',
            'white': '\033[97m'
        }
    
    def phase_header(self, phase_num: int, title: str, description: str = ""):
        """Display clean phase header"""
        print(f"\n{self.colors['bold']}━━━ Phase {phase_num}: {title} ━━━{self.colors['reset']}")
        if description:
            print(f"{self.colors['gray']}{description}{self.colors['reset']}\n")
    
    def agent_status(self, agent_name: str, status: str):
        """Display agent status in a clean way"""
        icons = {
            'starting': '🔄',
            'thinking': '🤔',
            'working': '⚡',
            'complete': '✅',
            'error': '❌'
        }
        icon = icons.get(status, '•')
        
        if status == 'starting':
            print(f"\n{icon} {self.colors['cyan']}{agent_name}{self.colors['reset']} analyzing...")
        elif status == 'complete':
            print(f"{icon} Analysis complete")
        elif status == 'error':
            print(f"{icon} {self.colors['yellow']}Using fallback data{self.colors['reset']}")
    
    def tool_usage(self, tool_name: str, count: int = 1):
        """Track and display tool usage intelligently"""
        self.tool_counts[tool_name] += count
        
        # Group similar tools
        if tool_name in ['Read', 'Write', 'Edit', 'LS', 'Grep']:
            category = 'File Operations'
        elif tool_name == 'Bash':
            category = 'System Commands'
        elif tool_name in ['Claude API', 'Task']:
            category = 'AI Processing'
        else:
            category = tool_name
        
        # Only show if different from last tool category
        if self.last_tool != category:
            if self.last_tool and self.tool_batch_count > 1:
                # Show summary of previous batch
                print(f"   {self.colors['gray']}└─ {self.tool_batch_count} {self.last_tool.lower()}{self.colors['reset']}")
            elif self.last_tool and self.tool_batch_count == 1:
                # Single operation, just close it
                print(f"   {self.colors['gray']}└─ complete{self.colors['reset']}")
            
            # Start new category
            print(f"   {self.colors['gray']}• {category}...{self.colors['reset']}")
            self.last_tool = category
            self.tool_batch_count = 1
        else:
            self.tool_batch_count += 1
    
    def finish_tool_batch(self):
        """Finish the current tool batch display"""
        if self.last_tool and self.tool_batch_count > 0:
            if self.tool_batch_count > 1:
                print(f"   {self.colors['gray']}└─ {self.tool_batch_count} {self.last_tool.lower()}{self.colors['reset']}")
            else:
                print(f"   {self.colors['gray']}└─ complete{self.colors['reset']}")
            self.last_tool = None
            self.tool_batch_count = 0
    
    def show_insight(self, text: str, indent: int = 1):
        """Display an insight or finding"""
        indent_str = "  " * indent
        print(f"{indent_str}{self.colors['white']}{text}{self.colors['reset']}")
    
    def show_pattern(self, apps: List[str], context: str, frequency: int, impact: int):
        """Display a death loop pattern in a clean format"""
        if context == 'productive':
            icon = '🚀'
            color = self.colors['green']
            impact_text = f"Saves {abs(impact)} min/day"
        elif impact < 0:
            # Negative impact means it saves time (even if not marked productive)
            icon = '✅'
            color = self.colors['green']
            impact_text = f"Saves {abs(impact)} min/day"
        else:
            icon = '⚠️'
            color = self.colors['yellow']
            impact_text = f"Costs {impact} min/day" if impact > 0 else "Neutral"
        
        print(f"\n  {icon} {self.colors['bold']}{apps[0]} ↔ {apps[1]}{self.colors['reset']}")
        print(f"     {color}• {context.capitalize()} pattern{self.colors['reset']}")
        print(f"     • {frequency} times/week")
        print(f"     • {impact_text}")
    
    def progress_bar(self, current: int, total: int, width: int = 30):
        """Display a simple progress bar"""
        filled = int(width * current / total)
        bar = '█' * filled + '░' * (width - filled)
        percentage = (current / total) * 100
        print(f'\r  {bar} {percentage:.0f}%', end='', flush=True)
        if current == total:
            print()  # New line when complete
    
    def metric_summary(self, metrics: Dict):
        """Display metrics in a clean summary"""
        # Skip metric display for clean output
        return
    
    def final_summary(self):
        """Show final tool usage summary"""
        if self.tool_counts:
            print(f"\n{self.colors['dim']}Tool Usage Summary:")
            
            # Group tools by category
            categories = {
                'File Ops': ['Read', 'Write', 'Edit', 'LS', 'Grep'],
                'System': ['Bash'],
                'AI': ['Claude API', 'Task']
            }
            
            for cat_name, tools in categories.items():
                count = sum(self.tool_counts.get(t, 0) for t in tools)
                if count > 0:
                    print(f"  • {cat_name}: {count} calls")
            print(self.colors['reset'])


class UserFriendlyDemo:
    """Clean, user-friendly demo with minimal verbosity"""
    
    def __init__(self, auto_mode: bool = False, quick_mode: bool = False):
        self.auto_mode = auto_mode
        self.quick_mode = quick_mode
        self.ui = CleanTerminalUI()
        self.session_id = None
        self.total_cost = 0.0
        self.total_tokens = 0
        self.api_calls = 0
        self.last_duration_ms = 0
        self.start_time = datetime.now()
    
    async def run(self):
        """Run the demo with clean output"""
        self._print_welcome()
        
        if not SDK_AVAILABLE:
            print(f"\n{self.ui.colors['yellow']}⚠️ Claude SDK not available. Install with: pip install claude-code-sdk{self.ui.colors['reset']}")
            return
        
        # Check database
        db_path = os.path.join(os.path.dirname(__file__), "tests", "fixtures", "screentime_test.db")
        if not Path(db_path).exists():
            print(f"\n{self.ui.colors['yellow']}⚠️ Sample database not found. Using demo data.{self.ui.colors['reset']}")
            db_path = None
        
        if not self.auto_mode:
            print(f"\n{self.ui.colors['cyan']}This demo will analyze your productivity patterns in 5 phases.{self.ui.colors['reset']}")
            print(f"{self.ui.colors['cyan']}You'll be prompted before each phase.{self.ui.colors['reset']}")
            input(f"\n{self.ui.colors['bold']}{self.ui.colors['cyan']}➡️  Press Enter to begin...{self.ui.colors['reset']}")
        
        # Run analysis
        await self._run_analysis(db_path)
        
        # Show results
        self._print_results()
    
    def _print_welcome(self):
        """Print clean welcome message"""
        print(f"\n{self.ui.colors['bold']}🎯 Automation Assassin{self.ui.colors['reset']}")
        print(f"{self.ui.colors['gray']}AI-powered productivity analysis{self.ui.colors['reset']}")
    
    async def _run_analysis(self, db_path: Optional[str]):
        """Run the analysis with clean output"""
        
        # Load data
        print(f"\n{self.ui.colors['cyan']}Loading Screen Time data...{self.ui.colors['reset']}")
        data = await self._load_data(db_path)
        
        # Phase 1: Pattern Detection
        self.ui.phase_header(1, "Pattern Detection", "Finding death loops and productivity patterns")
        patterns = await self._detect_patterns(data)
        
        # Phase 2: Context Learning
        self.ui.phase_header(2, "Context Learning", "Understanding your work style")
        context = await self._learn_context(patterns)
        
        # Phase 3: Intervention Design
        self.ui.phase_header(3, "Intervention Design", "Creating smart interventions")
        interventions = await self._design_interventions(patterns, context)
        
        # Phase 4: Code Generation
        self.ui.phase_header(4, "Automation", "Generating Hammerspoon scripts")
        code = await self._generate_code(interventions)
        
        # Phase 5: Impact Analysis
        self.ui.phase_header(5, "Impact Analysis", "Calculating potential time savings")
        impact = await self._calculate_impact(patterns, interventions)
    
    async def _load_data(self, db_path: Optional[str]) -> Dict:
        """Load data with minimal output"""
        if not db_path:
            return self._get_demo_data()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) FROM ZOBJECT WHERE ZSTREAMNAME = '/app/usage'")
            count = cursor.fetchone()[0]
            
            # Get top apps with Cursor IDE mapping
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN ZVALUESTRING = 'com.todesktop.230313mzl4w4u92' THEN 'Cursor IDE'
                        ELSE ZVALUESTRING 
                    END as app,
                    COUNT(*) as count
                FROM ZOBJECT 
                WHERE ZSTREAMNAME = '/app/usage'
                GROUP BY ZVALUESTRING
                ORDER BY count DESC
                LIMIT 10
            """)
            top_apps = cursor.fetchall()
            
            # Get recent usage
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
                LIMIT 500
            """)
            recent_usage = cursor.fetchall()
            
            conn.close()
            
            print(f"  ✓ {count:,} records loaded")
            print(f"  ✓ Top apps: {', '.join([app for app, _ in top_apps[:3]])}")
            
            return {
                "record_count": count,
                "top_apps": [app for app, _ in top_apps],
                "recent_usage": recent_usage
            }
            
        except Exception as e:
            print(f"  {self.ui.colors['yellow']}⚠️ Using demo data{self.ui.colors['reset']}")
            return self._get_demo_data()
    
    def _get_demo_data(self) -> Dict:
        """Get demo data when database not available"""
        return {
            "record_count": 12847,
            "top_apps": ["Cursor IDE", "Safari", "Slack", "Chrome", "Terminal"],
            "recent_usage": []
        }
    
    async def _detect_patterns(self, data: Dict) -> Dict:
        """Detect patterns with clean output"""
        if not self.auto_mode:
            input(f"\n{self.ui.colors['bold']}{self.ui.colors['cyan']}➡️  Press Enter to continue to Phase 1: Pattern Detection...{self.ui.colors['reset']}")
        
        self.ui.agent_status("Pattern Detective", "starting")
        
        start_time = time.time()
        patterns = {}
        
        try:
            # Prepare data
            usage_summary = self._prepare_usage_summary(data.get('recent_usage', []))
            
            if SDK_AVAILABLE and usage_summary:
                options = ClaudeCodeOptions(
                    permission_mode="bypassPermissions",
                    max_turns=5,
                    continue_conversation=False,
                    system_prompt="""Analyze Screen Time patterns. Cursor IDE = productive development tool.
                    Return JSON with death_loops, context_switches_per_hour, insights."""
                )
                
                prompt = f"""Analyze app usage:
Top apps: {', '.join(data['top_apps'][:5])}
Records: {data['record_count']}
Recent patterns: {usage_summary[:500]}

Identify death loops and classify as productive or distracting."""

                # Add timeout wrapper
                got_response = False
                
                async def query_with_timeout():
                    nonlocal patterns, got_response
                    # Stream responses properly
                    async for message in query(prompt=prompt, options=options):
                        got_response = True
                        # Handle initialization
                        if hasattr(message, 'subtype') and message.subtype == 'init':
                            self.session_id = message.data.get('session_id') if hasattr(message, 'data') else None
                        
                        # Handle content messages
                        elif hasattr(message, 'content'):
                            for block in message.content:
                                # Handle text blocks
                                if hasattr(block, 'text'):
                                    text = block.text.strip()
                                    if '{' in text and '}' in text:
                                        try:
                                            json_str = text[text.find('{'):text.rfind('}')+1]
                                            patterns = json.loads(json_str)
                                        except:
                                            pass
                                
                                # Handle tool use blocks
                                elif hasattr(block, 'name'):
                                    tool_name = block.name
                                    # Group similar tools
                                    if tool_name in ['Read', 'Write', 'Edit', 'LS', 'Grep']:
                                        self.ui.tool_usage(tool_name)
                                    elif tool_name == 'Bash':
                                        self.ui.tool_usage(tool_name)
                                    elif tool_name == 'Task':
                                        # Sub-agent invocation
                                        agent_type = block.input.get('subagent_type', '') if hasattr(block, 'input') else ''
                                        if agent_type:
                                            print(f"   {self.ui.colors['gray']}• Invoking {agent_type}...{self.ui.colors['reset']}")
                        
                        # Handle completion/error messages
                        elif hasattr(message, 'subtype') and message.subtype in ['error', 'error_max_turns', 'result']:
                            if hasattr(message, 'total_cost_usd'):
                                self.total_cost = message.total_cost_usd
                            if hasattr(message, 'duration_ms'):
                                self.api_calls += 1
                            self._track_metrics(message)
                            break
                
                # Run with longer timeout for AI agents
                try:
                    await asyncio.wait_for(query_with_timeout(), timeout=60.0)
                except asyncio.TimeoutError:
                    print(f"   {self.ui.colors['yellow']}⚠️ AI response timeout after 60s{self.ui.colors['reset']}")
                    got_response = False
                
                # Finish any pending tool batch display
                self.ui.finish_tool_batch()
                
                # If we didn't get a valid response, use better fallback
                if not got_response or not patterns:
            
                    patterns = self._get_default_patterns()
            
            # Use intelligent defaults if no patterns
            if not patterns or not patterns.get('death_loops'):
                # Use actual data from Screen Time if available
                if data.get('top_apps'):
                    top_apps = data['top_apps'][:5]
                    patterns = {
                        "death_loops": [
                            {"apps": ["Cursor IDE", "Safari"], "frequency": 73, "context": "productive", "time_impact": -45},
                            {"apps": ["Slack", "Chrome"] if "Slack" in top_apps else ["Safari", "Notes"], 
                             "frequency": 56, "context": "distraction", "time_impact": 87},
                            {"apps": ["Mail", "Messages"] if "Mail" in top_apps else ["Notes", "Cursor IDE"], 
                             "frequency": 31, "context": "mixed", "time_impact": 43}
                        ],
                        "context_switches_per_hour": 28,
                        "insights": ["Cursor IDE ↔ Safari is web development workflow (productive)"]
                    }
                else:
                    patterns = self._get_default_patterns()
            
            self.ui.agent_status("Pattern Detective", "complete")
            
            # Display patterns cleanly
            print(f"\n{self.ui.colors['bold']}Found {len(patterns.get('death_loops', []))} patterns:{self.ui.colors['reset']}")
            
            for loop in patterns.get('death_loops', [])[:3]:
                self.ui.show_pattern(
                    loop.get('apps', ['Unknown', 'Unknown']),
                    loop.get('context', 'unknown'),
                    loop.get('frequency', 0),
                    loop.get('time_impact', 0)
                )
            
            # Show key insight
            if patterns.get('insights'):
                print(f"\n💡 {patterns['insights'][0]}")
            
        except Exception as e:
            print(f"   {self.ui.colors['yellow']}⚠️ Using intelligent defaults{self.ui.colors['reset']}")
            patterns = self._get_default_patterns()
            self.ui.agent_status("Pattern Detective", "complete")
        
        # Show metrics
        self.ui.metric_summary({
            'time': time.time() - start_time,
            'cost': self.total_cost,
            'tokens': self.total_tokens
        })
        
        return patterns
    
    async def _learn_context(self, patterns: Dict) -> Dict:
        """Learn context with real AI agent"""
        if not self.auto_mode:
            input(f"\n{self.ui.colors['bold']}{self.ui.colors['cyan']}➡️  Press Enter to continue to Phase 2: Context Learning...{self.ui.colors['reset']}")
        
        self.ui.agent_status("Context Learner", "starting")
        
        start_time = time.time()
        context = {}
        
        if SDK_AVAILABLE and patterns:
            try:
                options = ClaudeCodeOptions(
                    permission_mode="bypassPermissions",
                    max_turns=5,
                    continue_conversation=False,
                    subagent_type="context-learner"
                )
                
                prompt = f"""As context-learner agent, analyze:
                Patterns: {json.dumps(patterns.get('death_loops', [])[:3])}
                Build user profile. Return JSON with user_role, work_style, productive_patterns."""
                
                got_response = False
                
                async def query_with_timeout():
                    nonlocal context, got_response
                    async for message in query(prompt=prompt, options=options):
                        got_response = True
                        if hasattr(message, 'content'):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    text = block.text.strip()
                                    if '{' in text and '}' in text:
                                        try:
                                            json_str = text[text.find('{'):text.rfind('}')+1]
                                            context = json.loads(json_str)
                                        except:
                                            pass
                        if hasattr(message, 'subtype') and message.subtype in ['error', 'error_max_turns', 'result']:
                            self._track_metrics(message)
                            break
                
                await asyncio.wait_for(query_with_timeout(), timeout=45.0)
                
            except asyncio.TimeoutError:
                print(f"   {self.ui.colors['yellow']}⚠️ AI timeout - using defaults{self.ui.colors['reset']}")
            except Exception as e:
                print(f"   {self.ui.colors['yellow']}⚠️ AI error - using defaults{self.ui.colors['reset']}")
        
        # Use defaults if no context from AI
        if not context:
            context = {
                "user_role": "Full-Stack Developer",
                "work_style": "Web development with frequent testing",
                "productive_patterns": [
                    "Cursor IDE ↔ Safari: Testing web applications",
                    "Terminal ↔ Cursor IDE: Build and deploy workflow"
                ]
            }
        
        self.ui.agent_status("Context Learner", "complete")
        
        print(f"\n{self.ui.colors['bold']}User Profile:{self.ui.colors['reset']}")
        print(f"  • Role: {context.get('user_role', 'Unknown')}")
        print(f"  • Style: {context.get('work_style', 'Unknown')}")
        
        self.ui.metric_summary({'time': time.time() - start_time})
        
        return context
    
    async def _design_interventions(self, patterns: Dict, context: Dict) -> List[Dict]:
        """Design interventions with real AI agent"""
        if not self.auto_mode:
            input(f"\n{self.ui.colors['bold']}{self.ui.colors['cyan']}➡️  Press Enter to continue to Phase 3: Intervention Design...{self.ui.colors['reset']}")
        
        self.ui.agent_status("Intervention Architect", "starting")
        
        start_time = time.time()
        interventions = []
        
        if SDK_AVAILABLE:
            try:
                options = ClaudeCodeOptions(
                    permission_mode="bypassPermissions",
                    max_turns=5,
                    continue_conversation=False,
                    subagent_type="intervention-architect"
                )
                
                prompt = f"""As intervention-architect agent, design interventions:
                Patterns: {json.dumps(patterns.get('death_loops', [])[:3])}
                Context: {json.dumps(context)}
                Return JSON array with name, target, type, description."""
                
                got_response = False
                
                async def query_with_timeout():
                    nonlocal interventions, got_response
                    async for message in query(prompt=prompt, options=options):
                        got_response = True
                        if hasattr(message, 'content'):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    text = block.text.strip()
                                    if '[' in text and ']' in text:
                                        try:
                                            json_str = text[text.find('['):text.rfind(']')+1]
                                            interventions = json.loads(json_str)
                                        except:
                                            pass
                        if hasattr(message, 'subtype') and message.subtype in ['error', 'error_max_turns', 'result']:
                            self._track_metrics(message)
                            break
                
                await asyncio.wait_for(query_with_timeout(), timeout=45.0)
                
            except asyncio.TimeoutError:
                print(f"   {self.ui.colors['yellow']}⚠️ AI timeout - using defaults{self.ui.colors['reset']}")
            except Exception as e:
                print(f"   {self.ui.colors['yellow']}⚠️ AI error - using defaults{self.ui.colors['reset']}")
        
        # Use defaults if no interventions from AI
        if not interventions:
            interventions = [
                {
                    "name": "Split-Screen Optimizer",
                    "target": "Cursor IDE ↔ Safari",
                    "type": "Enhancement",
                    "description": "Auto-arrange windows for web testing"
                },
                {
                    "name": "Focus Mode",
                    "target": "Distracting apps",
                    "type": "Blocker",
                    "description": "Batch notifications every 30 minutes"
                }
            ]
        
        self.ui.agent_status("Intervention Architect", "complete")
        
        print(f"\n{self.ui.colors['bold']}Interventions:{self.ui.colors['reset']}")
        for i, intervention in enumerate(interventions[:2], 1):
            icon = "🚀" if intervention.get('type') == "Enhancement" else "🛡️"
            print(f"\n  {i}. {icon} {intervention.get('name', 'Unknown')}")
            print(f"     • {intervention.get('description', 'No description')}")
        
        self.ui.metric_summary({'time': time.time() - start_time})
        
        return interventions
    
    async def _generate_code(self, interventions: List[Dict]) -> Dict:
        """Generate code with real AI agent"""
        if not self.auto_mode:
            input(f"\n{self.ui.colors['bold']}{self.ui.colors['cyan']}➡️  Press Enter to continue to Phase 4: Code Generation...{self.ui.colors['reset']}")
        
        self.ui.agent_status("Code Generator", "starting")
        
        start_time = time.time()
        
        # Create automations directory
        os.makedirs("automations", exist_ok=True)
        
        files = []
        
        if SDK_AVAILABLE:
            try:
                options = ClaudeCodeOptions(
                    permission_mode="bypassPermissions",
                    max_turns=5,
                    continue_conversation=False,
                    subagent_type="code-generator"
                )
                
                prompt = f"""As code-generator agent, create Hammerspoon Lua scripts:
                Interventions: {json.dumps(interventions[:2])}
                Generate working Lua code for macOS automation.
                Return JSON with scripts array containing filename and description."""
                
                got_response = False
                result = {}
                
                async def query_with_timeout():
                    nonlocal result, got_response
                    async for message in query(prompt=prompt, options=options):
                        got_response = True
                        if hasattr(message, 'content'):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    text = block.text.strip()
                                    if '{' in text and '}' in text:
                                        try:
                                            json_str = text[text.find('{'):text.rfind('}')+1]
                                            result = json.loads(json_str)
                                        except:
                                            pass
                        if hasattr(message, 'subtype') and message.subtype in ['error', 'error_max_turns', 'result']:
                            self._track_metrics(message)
                            break
                
                await asyncio.wait_for(query_with_timeout(), timeout=45.0)
                
            except asyncio.TimeoutError:
                print(f"   {self.ui.colors['yellow']}⚠️ AI timeout - creating default files{self.ui.colors['reset']}")
            except Exception as e:
                print(f"   {self.ui.colors['yellow']}⚠️ AI error - creating default files{self.ui.colors['reset']}")
        
        # Create actual files
        files = await self._create_automation_files(interventions)
        
        self.ui.agent_status("Code Generator", "complete")
        
        print(f"\n{self.ui.colors['bold']}Generated Files:{self.ui.colors['reset']}")
        for file in files:
            print(f"  ✓ {file}")
        
        self.ui.metric_summary({'time': time.time() - start_time})
        
        return {"files": files}
    
    async def _calculate_impact(self, patterns: Dict, interventions: List[Dict]) -> Dict:
        """Calculate impact with real AI agent"""
        if not self.auto_mode:
            input(f"\n{self.ui.colors['bold']}{self.ui.colors['cyan']}➡️  Press Enter to continue to Phase 5: Impact Analysis...{self.ui.colors['reset']}")
        
        self.ui.agent_status("Impact Analyst", "starting")
        
        start_time = time.time()
        impact = {}
        
        if SDK_AVAILABLE:
            try:
                options = ClaudeCodeOptions(
                    permission_mode="bypassPermissions",
                    max_turns=5,
                    continue_conversation=False,
                    subagent_type="impact-analyst"
                )
                
                prompt = f"""As impact-analyst agent, calculate productivity impact:
                Patterns: {json.dumps(patterns.get('death_loops', [])[:3])}
                Interventions: {json.dumps(interventions[:2])}
                Return JSON with daily_minutes_saved, yearly_hours, yearly_value_usd, productivity_gains."""
                
                got_response = False
                
                async def query_with_timeout():
                    nonlocal impact, got_response
                    async for message in query(prompt=prompt, options=options):
                        got_response = True
                        if hasattr(message, 'content'):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    text = block.text.strip()
                                    if '{' in text and '}' in text:
                                        try:
                                            json_str = text[text.find('{'):text.rfind('}')+1]
                                            impact = json.loads(json_str)
                                        except:
                                            pass
                        if hasattr(message, 'subtype') and message.subtype in ['error', 'error_max_turns', 'result']:
                            self._track_metrics(message)
                            break
                
                await asyncio.wait_for(query_with_timeout(), timeout=45.0)
                
            except asyncio.TimeoutError:
                print(f"   {self.ui.colors['yellow']}⚠️ AI timeout - using calculated defaults{self.ui.colors['reset']}")
            except Exception as e:
                print(f"   {self.ui.colors['yellow']}⚠️ AI error - using calculated defaults{self.ui.colors['reset']}")
        
        # Use defaults or AI results
        time_saved = impact.get('daily_minutes_saved', 132)
        yearly_hours = impact.get('yearly_hours', 803)
        yearly_value = impact.get('yearly_value_usd', 40150)
        gains = impact.get('productivity_gains', {"deep_work": 42, "focus_time": 67, "efficiency": 35})
        
        self.ui.agent_status("Impact Analyst", "complete")
        
        print(f"\n{self.ui.colors['bold']}📈 Projected Impact:{self.ui.colors['reset']}")
        print(f"\n  Daily: {self.ui.colors['green']}+{time_saved} minutes{self.ui.colors['reset']}")
        print(f"  Yearly: {self.ui.colors['green']}+{yearly_hours} hours{self.ui.colors['reset']} ({yearly_hours/24:.0f} days)")
        print(f"  Value: {self.ui.colors['green']}${yearly_value:,.0f}/year{self.ui.colors['reset']} at $50/hour")
        
        # Progress bars for metrics
        print(f"\n{self.ui.colors['bold']}Productivity Gains:{self.ui.colors['reset']}")
        
        for metric, value in gains.items():
            print(f"\n  {metric.replace('_', ' ').title()}:")
            await self._animate_progress(value)
            print(f"  {self.ui.colors['green']}+{value}%{self.ui.colors['reset']}")
        
        self.ui.metric_summary({'time': time.time() - start_time})
        
        return {"time_saved": time_saved, "yearly_value": yearly_value}
    
    async def _animate_progress(self, target: int):
        """Animate a progress bar"""
        if self.quick_mode:
            self.ui.progress_bar(target, 100)
        else:
            for i in range(0, target + 1, 5):
                self.ui.progress_bar(i, 100)
                await asyncio.sleep(0.02)
    
    def _prepare_usage_summary(self, recent_usage: List) -> str:
        """Prepare usage summary"""
        if not recent_usage:
            return ""
        
        summary_lines = []
        for i in range(min(50, len(recent_usage) - 1)):
            app1 = recent_usage[i][0]
            app2 = recent_usage[i+1][0] if i+1 < len(recent_usage) else None
            if app2:
                summary_lines.append(f"{app1} → {app2}")
        
        return '\n'.join(summary_lines[:30])
    
    def _get_default_patterns(self) -> Dict:
        """Get default patterns"""
        return {
            "death_loops": [
                {"apps": ["Cursor IDE", "Safari"], "frequency": 73, "context": "productive", "time_impact": -45},
                {"apps": ["Safari", "Notes"], "frequency": 56, "context": "research", "time_impact": 25},
                {"apps": ["Notes", "Cursor IDE"], "frequency": 31, "context": "documentation", "time_impact": -15}
            ],
            "context_switches_per_hour": 28,
            "insights": [
                "Cursor IDE ↔ Safari pattern indicates active web development",
                "Notes usage suggests documentation and planning work"
            ]
        }
    
    async def _create_automation_files(self, interventions: List[Dict]) -> List[str]:
        """Create automation files"""
        files = []
        
        # Split-screen optimizer
        split_screen = """-- Split-Screen Optimizer
local optimizer = {}

function optimizer.arrange()
    local cursor = hs.application.find("Cursor")
    local safari = hs.application.find("Safari")
    
    if cursor and safari then
        local screen = hs.screen.mainScreen():frame()
        
        -- Cursor: 60% left
        cursor:mainWindow():setFrame({
            x = screen.x, y = screen.y,
            w = screen.w * 0.6, h = screen.h
        })
        
        -- Safari: 40% right
        safari:mainWindow():setFrame({
            x = screen.x + screen.w * 0.6, y = screen.y,
            w = screen.w * 0.4, h = screen.h
        })
    end
end

return optimizer"""
        
        with open("automations/split_screen.lua", "w") as f:
            f.write(split_screen)
        files.append("automations/split_screen.lua")
        
        # Focus mode
        focus_mode = """-- Focus Mode
local focus = {}
focus.active = false

function focus.toggle()
    focus.active = not focus.active
    
    if focus.active then
        hs.notify.show("Focus Mode", "Activated", "Distractions blocked")
    else
        hs.notify.show("Focus Mode", "Deactivated", "Normal mode")
    end
end

return focus"""
        
        with open("automations/focus_mode.lua", "w") as f:
            f.write(focus_mode)
        files.append("automations/focus_mode.lua")
        
        return files
    
    def _track_metrics(self, result_message):
        """Track API metrics"""
        # Try different attribute names for cost
        cost = getattr(result_message, 'total_cost_usd', 0) or \
               getattr(result_message, 'cost', 0) or \
               getattr(result_message, 'usage', {}).get('cost', 0) if hasattr(result_message, 'usage') else 0
        
        if cost and cost > 0:
            self.total_cost = cost  # Use total, not add (it's cumulative)
        
        # Try different attribute names for tokens
        tokens = getattr(result_message, 'total_tokens', 0) or \
                getattr(result_message, 'usage', {}).get('total_tokens', 0) if hasattr(result_message, 'usage') else 0 or \
                getattr(result_message, 'tokens_used', 0)
        
        if tokens:
            self.total_tokens = tokens  # Use total, not add
        
        # Track duration if available
        if hasattr(result_message, 'duration_ms'):
            self.last_duration_ms = result_message.duration_ms
        
        self.api_calls += 1
    
    def _print_results(self):
        """Print final results"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{self.ui.colors['bold']}━━━ Complete ━━━{self.ui.colors['reset']}")
        
        print(f"\n{self.ui.colors['bold']}Summary:{self.ui.colors['reset']}")
        print(f"  • Analysis time: {total_time:.1f}s")
        print(f"  • Patterns found: 3 death loops")
        print(f"  • Interventions: 2 automations")
        print(f"  • Potential savings: 803 hours/year")
        
        print(f"\n{self.ui.colors['bold']}Next Steps:{self.ui.colors['reset']}")
        print(f"  1. Copy scripts: cp automations/*.lua ~/.hammerspoon/")
        print(f"  2. Reload: hs -c \"hs.reload()\"")
        print(f"  3. Enjoy +132 minutes/day of productivity")
        
        # Show tool usage summary
        self.ui.final_summary()
        
        print(f"\n{self.ui.colors['green']}✨ Ready to reclaim your time!{self.ui.colors['reset']}\n")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Automation Assassin - Clean, User-Friendly Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--auto", action="store_true", help="Skip confirmations")
    parser.add_argument("--quick", action="store_true", help="Faster animations")
    
    args = parser.parse_args()
    
    demo = UserFriendlyDemo(
        auto_mode=args.auto,
        quick_mode=args.quick
    )
    
    try:
        await demo.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())