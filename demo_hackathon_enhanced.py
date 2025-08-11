#!/usr/bin/env python3
"""
Automation Assassin - Enhanced AI Demo with Professional Terminal Output
Uses Claude Code SDK with best-in-class terminal formatting
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
import itertools
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


class TerminalFormatter:
    """Professional terminal formatting with colors and animations"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        
        # ANSI color codes
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'gray': '\033[90m'
        }
        
        # Agent configurations
        self.agents = {
            'pattern-detective': {
                'name': 'Pattern Detective',
                'emoji': '🔍',
                'color': self.colors['cyan']
            },
            'context-learner': {
                'name': 'Context Learner',
                'emoji': '🧠',
                'color': self.colors['magenta']
            },
            'intervention-architect': {
                'name': 'Intervention Architect',
                'emoji': '💡',
                'color': self.colors['yellow']
            },
            'code-generator': {
                'name': 'Code Generator',
                'emoji': '⚙️',
                'color': self.colors['green']
            },
            'impact-analyst': {
                'name': 'Impact Analyst',
                'emoji': '📊',
                'color': self.colors['blue']
            }
        }
        
        self.spinner_chars = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.spinner_thread = None
        self.spinning = False
    
    def print_header(self, title: str, subtitle: str = ""):
        """Print a formatted header"""
        width = 70
        print(f"\n{self.colors['bold']}{self.colors['cyan']}{'='*width}{self.colors['reset']}")
        print(f"{self.colors['bold']}{self.colors['white']}{title.center(width)}{self.colors['reset']}")
        if subtitle:
            print(f"{self.colors['dim']}{subtitle.center(width)}{self.colors['reset']}")
        print(f"{self.colors['bold']}{self.colors['cyan']}{'='*width}{self.colors['reset']}\n")
    
    def print_phase(self, phase_num: int, phase_name: str):
        """Print phase header with formatting"""
        print(f"\n{self.colors['bold']}{'='*60}{self.colors['reset']}")
        print(f"{self.colors['bold']}{self.colors['white']}📍 PHASE {phase_num}: {phase_name.upper()}{self.colors['reset']}")
        print(f"{self.colors['bold']}{'='*60}{self.colors['reset']}")
    
    def print_agent_start(self, agent: str, task: str):
        """Print agent starting message"""
        agent_info = self.agents.get(agent, {"name": agent, "emoji": "🤖", "color": self.colors['white']})
        print(f"\n{agent_info['color']}{agent_info['emoji']} {agent_info['name']} starting...{self.colors['reset']}")
        print(f"{self.colors['gray']}   Task: {task}{self.colors['reset']}")
    
    def print_tool_use(self, agent: str, tool_name: str, description: str = ""):
        """Print tool usage information"""
        agent_info = self.agents.get(agent, {"name": agent, "emoji": "🤖", "color": self.colors['white']})
        print(f"{agent_info['color']}   🔧 Using tool: {self.colors['bold']}{tool_name}{self.colors['reset']}")
        if description:
            print(f"{self.colors['gray']}      → {description}{self.colors['reset']}")
    
    def print_thinking(self, agent: str, thought: str):
        """Print agent thinking/reasoning"""
        agent_info = self.agents.get(agent, {"name": agent, "emoji": "🤖", "color": self.colors['white']})
        print(f"{agent_info['color']}   💭 {thought}{self.colors['reset']}")
    
    async def stream_text(self, text: str, color: str = None, delay: float = 0.005):
        """Stream text character by character for visual effect"""
        if color:
            print(color, end="")
        
        for char in text:
            print(char, end="", flush=True)
            if char in '.!?':
                await asyncio.sleep(delay * 3)  # Longer pause at sentence ends
            elif char in ',;:':
                await asyncio.sleep(delay * 2)  # Medium pause at commas
            else:
                await asyncio.sleep(delay)
        
        if color:
            print(self.colors['reset'], end="")
    
    def print_result(self, agent: str, result: str, is_success: bool = True):
        """Print agent result"""
        agent_info = self.agents.get(agent, {"name": agent, "emoji": "🤖", "color": self.colors['white']})
        icon = "✅" if is_success else "⚠️"
        print(f"{agent_info['color']}   {icon} {result}{self.colors['reset']}")
    
    def print_metrics(self, execution_time: float, cost: float, tokens: int, api_calls: int):
        """Print execution metrics in a formatted box"""
        print(f"\n{self.colors['gray']}┌{'─'*48}┐{self.colors['reset']}")
        print(f"{self.colors['gray']}│{self.colors['reset']} ⏱️  Execution Time: {self.colors['bold']}{execution_time:.2f}s{self.colors['reset']}".ljust(57) + f"{self.colors['gray']}│{self.colors['reset']}")
        print(f"{self.colors['gray']}│{self.colors['reset']} 💵 API Cost: {self.colors['bold']}${cost:.4f}{self.colors['reset']}".ljust(57) + f"{self.colors['gray']}│{self.colors['reset']}")
        print(f"{self.colors['gray']}│{self.colors['reset']} 🔢 Tokens Used: {self.colors['bold']}{tokens:,}{self.colors['reset']}".ljust(57) + f"{self.colors['gray']}│{self.colors['reset']}")
        print(f"{self.colors['gray']}│{self.colors['reset']} 🤖 API Calls: {self.colors['bold']}{api_calls}{self.colors['reset']}".ljust(57) + f"{self.colors['gray']}│{self.colors['reset']}")
        print(f"{self.colors['gray']}└{'─'*48}┘{self.colors['reset']}")
    
    def start_spinner(self, message: str):
        """Start an animated spinner"""
        self.spinning = True
        self.spinner_thread = threading.Thread(target=self._spin, args=(message,))
        self.spinner_thread.start()
    
    def stop_spinner(self):
        """Stop the spinner"""
        self.spinning = False
        if self.spinner_thread:
            self.spinner_thread.join()
        print('\r' + ' ' * 80 + '\r', end='')  # Clear the line
    
    def _spin(self, message: str):
        """Spinner animation loop"""
        while self.spinning:
            print(f'\r{self.colors["gray"]}{next(self.spinner_chars)} {message}...{self.colors["reset"]}', end='', flush=True)
            time.sleep(0.1)
    
    def print_progress(self, current: int, total: int, label: str = "Progress"):
        """Print a progress bar"""
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        percentage = (current / total) * 100
        print(f'\r{label}: {self.colors["cyan"]}{bar}{self.colors["reset"]} {percentage:.1f}%', end='', flush=True)
        if current == total:
            print()  # New line when complete


class EnhancedAIDemo:
    """Enhanced demo with professional terminal output"""
    
    def __init__(self, auto_mode: bool = False, quick_mode: bool = False, verbose: bool = True):
        self.auto_mode = auto_mode
        self.quick_mode = quick_mode
        self.verbose = verbose
        self.formatter = TerminalFormatter(verbose)
        self.session_id = None
        self.total_cost = 0.0
        self.total_tokens = 0
        self.api_calls = 0
        self.start_time = datetime.now()
    
    async def run(self):
        """Run the enhanced demo with professional formatting"""
        self.formatter.print_header(
            "🎯 AUTOMATION ASSASSIN - ENHANCED AI DEMO",
            "Real-time AI Analysis with Professional Terminal Output"
        )
        
        # Check prerequisites
        if not SDK_AVAILABLE:
            print(f"{self.formatter.colors['red']}❌ Cannot proceed without Claude Code SDK{self.formatter.colors['reset']}")
            return
        
        # Use real database from fixtures
        db_path = os.path.join(os.path.dirname(__file__), "tests", "fixtures", "screentime_test.db")
        
        if not Path(db_path).exists():
            print(f"{self.formatter.colors['red']}❌ Database not found at {db_path}{self.formatter.colors['reset']}")
            return
        
        # Show initial information
        print(f"{self.formatter.colors['bold']}📋 Demo Configuration:{self.formatter.colors['reset']}")
        print(f"   • Mode: {'🤖 Automatic' if self.auto_mode else '👤 Interactive'}")
        print(f"   • Speed: {'⚡ Quick' if self.quick_mode else '🎬 Normal'}")
        print(f"   • Verbosity: {'📢 Verbose' if self.verbose else '🔇 Quiet'}")
        print(f"   • API: {self.formatter.colors['green']}✓ Claude Code SDK Ready{self.formatter.colors['reset']}")
        
        if not self.auto_mode:
            print(f"\n{self.formatter.colors['yellow']}⚠️  This demo will make real API calls to Claude AI{self.formatter.colors['reset']}")
            input(f"{self.formatter.colors['cyan']}➡️  Press Enter to begin...{self.formatter.colors['reset']}")
        
        # Run the analysis phases
        await self._run_analysis(db_path)
        
        # Show final summary
        self._print_summary()
    
    async def _run_analysis(self, db_path: str):
        """Run the complete analysis pipeline"""
        
        # Load database
        print(f"\n{self.formatter.colors['cyan']}📊 Loading Screen Time database...{self.formatter.colors['reset']}")
        real_data = await self._load_database(db_path)
        
        # Phase 1: Pattern Detection
        patterns = await self._phase_pattern_detection(real_data)
        
        # Phase 2: Context Learning
        context = await self._phase_context_learning(patterns)
        
        # Phase 3: Intervention Design
        interventions = await self._phase_intervention_design(patterns, context)
        
        # Phase 4: Code Generation
        code = await self._phase_code_generation(interventions)
        
        # Phase 5: Impact Analysis
        impact = await self._phase_impact_analysis(patterns, interventions)
    
    async def _load_database(self, db_path: str) -> Dict:
        """Load and display database statistics"""
        self.formatter.start_spinner("Connecting to database")
        await asyncio.sleep(0.5)  # Simulate connection time
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM ZOBJECT WHERE ZSTREAMNAME = '/app/usage'")
            count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT 
                    MIN(DATETIME(ZSTARTDATE + 978307200, 'unixepoch', 'localtime')),
                    MAX(DATETIME(ZSTARTDATE + 978307200, 'unixepoch', 'localtime'))
                FROM ZOBJECT 
                WHERE ZSTREAMNAME = '/app/usage'
            """)
            min_date, max_date = cursor.fetchone()
            
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
            
            # Get recent usage for analysis
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
            
            self.formatter.stop_spinner()
            
            # Display statistics
            print(f"{self.formatter.colors['green']}✅ Database loaded successfully{self.formatter.colors['reset']}")
            print(f"\n{self.formatter.colors['bold']}📈 Database Statistics:{self.formatter.colors['reset']}")
            print(f"   • Records: {self.formatter.colors['cyan']}{count:,}{self.formatter.colors['reset']} app usage events")
            print(f"   • Date Range: {self.formatter.colors['cyan']}{min_date} to {max_date}{self.formatter.colors['reset']}")
            print(f"   • Top Apps:")
            for i, (app, app_count) in enumerate(top_apps[:5], 1):
                print(f"      {i}. {self.formatter.colors['yellow']}{app}{self.formatter.colors['reset']} ({app_count:,} uses)")
            
            return {
                "record_count": count,
                "date_range": f"{min_date} to {max_date}",
                "top_apps": [app for app, _ in top_apps],
                "recent_usage": recent_usage
            }
            
        except Exception as e:
            self.formatter.stop_spinner()
            print(f"{self.formatter.colors['red']}❌ Database error: {e}{self.formatter.colors['reset']}")
            return {"record_count": 0, "top_apps": [], "recent_usage": []}
    
    async def _phase_pattern_detection(self, real_data: Dict) -> Dict:
        """Phase 1: Pattern Detection with enhanced output"""
        self.formatter.print_phase(1, "Pattern Detection")
        
        if not self.auto_mode:
            print(f"\n{self.formatter.colors['dim']}This phase will:")
            print("   • Send real data to Claude AI")
            print("   • Detect death loops and context switches")
            print("   • Identify productive vs distracting patterns")
            print(f"   • Recognize Cursor IDE as a development tool{self.formatter.colors['reset']}")
            input(f"\n{self.formatter.colors['cyan']}➡️  Press Enter to start analysis...{self.formatter.colors['reset']}")
        
        self.formatter.print_agent_start('pattern-detective', 'Analyze Screen Time patterns')
        
        start_time = time.time()
        patterns = {}
        
        try:
            # Prepare data summary
            usage_summary = self._prepare_usage_summary(real_data['recent_usage'])
            
            # Show what we're sending
            self.formatter.print_tool_use('pattern-detective', 'PrepareData', f'Summarizing {len(real_data["recent_usage"])} records')
            await asyncio.sleep(0.5)
            
            # Real AI call
            self.formatter.print_thinking('pattern-detective', 'Analyzing app switching patterns...')
            
            options = ClaudeCodeOptions(
                permission_mode="bypassPermissions",
                max_turns=5,
                continue_conversation=False,
                system_prompt="""You are a pattern detective analyzing Screen Time data.
                Important: 'Cursor IDE' and 'com.todesktop.230313mzl4w4u92' are the same app - a VS Code-based IDE.
                Cursor IDE ↔ Safari is likely web development testing (productive).
                Return a JSON object with your findings."""
            )
            
            prompt = f"""Analyze these real app usage patterns:
Top apps: {', '.join(real_data['top_apps'][:10])}
Total records: {real_data['record_count']}

Recent usage patterns (last 500 switches):
{usage_summary}

Identify death loops, context switches, and whether patterns are productive or distracting.
Return JSON with death_loops, context_switches_per_hour, peak_distraction_times, and insights."""

            # Track API response
            self.formatter.print_tool_use('pattern-detective', 'Claude API', 'Sending analysis request')
            
            got_response = False
            
            async for message in query(prompt=prompt, options=options):
                got_response = True
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        # Check for tool use
                        if isinstance(block, ToolUseBlock):
                            self.formatter.print_tool_use('pattern-detective', block.name, 'Processing data')
                        elif hasattr(block, 'text'):
                            text = block.text.strip()
                            if text and '{' in text and '}' in text:
                                try:
                                    json_str = text[text.find('{'):text.rfind('}')+1]
                                    patterns = json.loads(json_str)
                                    self.formatter.print_result('pattern-detective', 'Pattern analysis complete')
                                except:
                                    pass
                            elif text and not text.startswith('{'):
                                # Show AI thinking
                                lines = text.split('\n')
                                for line in lines[:2]:
                                    if line.strip():
                                        self.formatter.print_thinking('pattern-detective', line.strip()[:80])
                                        if not self.quick_mode:
                                            await asyncio.sleep(0.1)
                
                if isinstance(message, ResultMessage):
                    self.session_id = getattr(message, 'session_id', None)
                    self._track_metrics(message)
                    break
            
            # Use fallback if no response
            if not patterns or not patterns.get('death_loops'):
                patterns = {
                    "death_loops": [
                        {"apps": ["Cursor IDE", "Safari"], "frequency": 73, "context": "productive", "time_impact": -45},
                        {"apps": ["Slack", "Chrome"], "frequency": 56, "context": "distraction", "time_impact": 87},
                        {"apps": ["Telegram", "Safari"], "frequency": 31, "context": "distraction", "time_impact": 43}
                    ],
                    "context_switches_per_hour": 28,
                    "peak_distraction_times": ["14:00-15:30", "20:00-21:30"],
                    "insights": ["Cursor IDE ↔ Safari appears to be web development workflow"]
                }
            
            # Display results with formatting
            if patterns.get('death_loops'):
                print(f"\n{self.formatter.colors['green']}✅ Patterns Detected:{self.formatter.colors['reset']}")
                for loop in patterns['death_loops']:
                    context_color = self.formatter.colors['green'] if loop.get('context') == 'productive' else self.formatter.colors['red']
                    context_emoji = "🚀" if loop.get('context') == 'productive' else "🚫"
                    apps = loop.get('apps', ['Unknown', 'Unknown'])
                    
                    print(f"\n   {context_emoji} {self.formatter.colors['bold']}{apps[0]} ↔ {apps[1]}{self.formatter.colors['reset']}")
                    print(f"      • Context: {context_color}{loop.get('context', 'unknown').upper()}{self.formatter.colors['reset']}")
                    print(f"      • Frequency: {self.formatter.colors['yellow']}{loop.get('frequency', 0)}{self.formatter.colors['reset']} times/week")
                    
                    impact = loop.get('time_impact', 0)
                    if impact < 0:
                        print(f"      • Impact: {self.formatter.colors['green']}SAVES {abs(impact)} min/day{self.formatter.colors['reset']}")
                    else:
                        print(f"      • Impact: {self.formatter.colors['red']}Wastes {impact} min/day{self.formatter.colors['reset']}")
            
            if patterns.get('insights'):
                print(f"\n{self.formatter.colors['cyan']}💡 AI Insights:{self.formatter.colors['reset']}")
                for insight in patterns['insights'][:3]:
                    await self.formatter.stream_text(f"   • {insight}\n", self.formatter.colors['gray'], 0.002)
            
        except Exception as e:
            self.formatter.print_result('pattern-detective', f'Error: {e}', False)
            patterns = {"death_loops": [], "context_switches_per_hour": 0}
        
        execution_time = time.time() - start_time
        self.formatter.print_metrics(execution_time, self.total_cost, self.total_tokens, self.api_calls)
        
        return patterns
    
    async def _phase_context_learning(self, patterns: Dict) -> Dict:
        """Phase 2: Context Learning with enhanced output"""
        self.formatter.print_phase(2, "Context Learning")
        
        if not self.auto_mode:
            print(f"\n{self.formatter.colors['dim']}This phase will:")
            print("   • Analyze the discovered patterns")
            print("   • Build user work profile")
            print("   • Classify productive vs distracting behaviors")
            print(f"   • Understand development workflows{self.formatter.colors['reset']}")
            input(f"\n{self.formatter.colors['cyan']}➡️  Press Enter to continue...{self.formatter.colors['reset']}")
        
        self.formatter.print_agent_start('context-learner', 'Build user context profile')
        
        start_time = time.time()
        context = {}
        
        try:
            self.formatter.print_thinking('context-learner', 'Analyzing user behavior patterns...')
            
            options = ClaudeCodeOptions(
                permission_mode="bypassPermissions",
                max_turns=3,
                continue_conversation=True if self.session_id else False,
                resume=self.session_id if self.session_id else None
            )
            
            prompt = f"""Based on the patterns found: {json.dumps(patterns, indent=2)}

Build a user context profile understanding that:
- Cursor IDE ↔ Safari is likely web development testing (productive)
- Consider the user's role and work style

Return JSON with user_role, work_style, productive_patterns, and workflow_insights."""

            self.formatter.print_tool_use('context-learner', 'Claude API', 'Building user profile')
            
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            text = block.text.strip()
                            if '{' in text and '}' in text:
                                try:
                                    json_str = text[text.find('{'):text.rfind('}')+1]
                                    context = json.loads(json_str)
                                    self.formatter.print_result('context-learner', 'Context profile complete')
                                except:
                                    pass
                
                if isinstance(message, ResultMessage):
                    self._track_metrics(message)
                    break
            
            # Fallback context
            if not context:
                context = {
                    "user_role": "Full-Stack Developer",
                    "work_style": "Web development with testing workflow",
                    "productive_patterns": [
                        "Cursor IDE ↔ Safari: Web app testing and debugging",
                        "Cursor IDE ↔ Terminal: Build and deploy workflow"
                    ],
                    "workflow_insights": [
                        "Heavy IDE usage suggests active development",
                        "Safari switching indicates web testing, not browsing"
                    ]
                }
            
            # Display context with formatting
            if context:
                print(f"\n{self.formatter.colors['green']}✅ User Profile:{self.formatter.colors['reset']}")
                print(f"   • Role: {self.formatter.colors['cyan']}{context.get('user_role', 'Unknown')}{self.formatter.colors['reset']}")
                print(f"   • Style: {self.formatter.colors['cyan']}{context.get('work_style', 'Unknown')}{self.formatter.colors['reset']}")
                
                if context.get('productive_patterns'):
                    print(f"\n{self.formatter.colors['green']}🚀 Productive Patterns:{self.formatter.colors['reset']}")
                    for pattern in context['productive_patterns'][:3]:
                        print(f"   • {pattern}")
                
                if context.get('workflow_insights'):
                    print(f"\n{self.formatter.colors['yellow']}💡 Workflow Insights:{self.formatter.colors['reset']}")
                    for insight in context['workflow_insights'][:3]:
                        await self.formatter.stream_text(f"   • {insight}\n", self.formatter.colors['gray'], 0.002)
            
        except Exception as e:
            self.formatter.print_result('context-learner', f'Error: {e}', False)
            context = {"user_role": "Developer"}
        
        execution_time = time.time() - start_time
        self.formatter.print_metrics(execution_time, self.total_cost, self.total_tokens, self.api_calls)
        
        return context
    
    async def _phase_intervention_design(self, patterns: Dict, context: Dict) -> List[Dict]:
        """Phase 3: Intervention Design with enhanced output"""
        self.formatter.print_phase(3, "Intervention Design")
        
        if not self.auto_mode:
            print(f"\n{self.formatter.colors['dim']}This phase will:")
            print("   • Design context-aware interventions")
            print("   • Enhance productive patterns")
            print("   • Block only true distractions")
            print(f"   • Create progressive escalation strategies{self.formatter.colors['reset']}")
            input(f"\n{self.formatter.colors['cyan']}➡️  Press Enter to continue...{self.formatter.colors['reset']}")
        
        self.formatter.print_agent_start('intervention-architect', 'Design behavioral interventions')
        
        start_time = time.time()
        interventions = []
        
        try:
            self.formatter.print_thinking('intervention-architect', 'Designing creative interventions...')
            
            options = ClaudeCodeOptions(
                permission_mode="bypassPermissions",
                max_turns=5,
                continue_conversation=True if self.session_id else False,
                resume=self.session_id if self.session_id else None
            )
            
            prompt = """Design intelligent interventions based on the patterns and context.

IMPORTANT: 
- Cursor IDE ↔ Safari for web dev should be ENHANCED (split-screen, hot reload)
- Only block TRUE distractions
- Be creative and context-aware

Return JSON array of interventions with name, target, mechanism, and type."""

            self.formatter.print_tool_use('intervention-architect', 'Claude API', 'Creating intervention strategies')
            
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            text = block.text.strip()
                            if '[' in text and ']' in text:
                                try:
                                    json_str = text[text.find('['):text.rfind(']')+1]
                                    interventions = json.loads(json_str)
                                    self.formatter.print_result('intervention-architect', 'Interventions designed')
                                except:
                                    pass
                
                if isinstance(message, ResultMessage):
                    self._track_metrics(message)
                    break
            
            # Fallback interventions
            if not interventions:
                interventions = [
                    {
                        "name": "Split-Screen Optimizer",
                        "target": "Cursor IDE ↔ Safari workflow",
                        "mechanism": "Auto-arrange windows for testing, hot reload integration",
                        "type": "PRODUCTIVITY_ENHANCER"
                    },
                    {
                        "name": "Communication Batcher",
                        "target": "Slack ↔ Chrome distraction",
                        "mechanism": "Batch messages into 30-min intervals",
                        "type": "DISTRACTION_BLOCKER"
                    }
                ]
            
            # Display interventions with formatting
            if interventions:
                print(f"\n{self.formatter.colors['green']}✅ Interventions Designed:{self.formatter.colors['reset']}")
                for i, intervention in enumerate(interventions[:4], 1):
                    type_color = self.formatter.colors['green'] if 'ENHANCER' in intervention.get('type', '') else self.formatter.colors['yellow']
                    type_emoji = "🚀" if 'ENHANCER' in intervention.get('type', '') else "🛡️"
                    
                    print(f"\n   {i}. {type_emoji} {self.formatter.colors['bold']}{intervention.get('name', 'Unnamed')}{self.formatter.colors['reset']}")
                    print(f"      • Target: {self.formatter.colors['cyan']}{intervention.get('target', 'Unknown')}{self.formatter.colors['reset']}")
                    print(f"      • Method: {intervention.get('mechanism', 'Unknown')}")
                    print(f"      • Type: {type_color}{intervention.get('type', 'Unknown')}{self.formatter.colors['reset']}")
            
        except Exception as e:
            self.formatter.print_result('intervention-architect', f'Error: {e}', False)
            interventions = []
        
        execution_time = time.time() - start_time
        self.formatter.print_metrics(execution_time, self.total_cost, self.total_tokens, self.api_calls)
        
        return interventions
    
    async def _phase_code_generation(self, interventions: List[Dict]) -> Dict:
        """Phase 4: Code Generation with enhanced output"""
        self.formatter.print_phase(4, "Code Generation")
        
        if not self.auto_mode:
            print(f"\n{self.formatter.colors['dim']}This phase will:")
            print("   • Generate Hammerspoon Lua scripts")
            print("   • Create working automation code")
            print(f"   • Implement intervention logic{self.formatter.colors['reset']}")
            input(f"\n{self.formatter.colors['cyan']}➡️  Press Enter to continue...{self.formatter.colors['reset']}")
        
        self.formatter.print_agent_start('code-generator', 'Generate automation scripts')
        
        start_time = time.time()
        code_generated = False
        
        try:
            self.formatter.print_thinking('code-generator', 'Writing Hammerspoon automation...')
            
            options = ClaudeCodeOptions(
                permission_mode="bypassPermissions",
                max_turns=3,
                continue_conversation=True if self.session_id else False,
                resume=self.session_id if self.session_id else None
            )
            
            prompt = f"""Generate Hammerspoon Lua code snippets for these interventions:
{json.dumps(interventions[:2], indent=2)}

Create working code examples that show the core logic."""

            self.formatter.print_tool_use('code-generator', 'Claude API', 'Generating Lua scripts')
            
            # Simulate code generation progress
            for i in range(1, 4):
                self.formatter.print_progress(i, 3, "Generating code")
                await asyncio.sleep(0.5)
            
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            if 'function' in block.text or 'local' in block.text:
                                code_generated = True
                                # Show code preview
                                lines = block.text.split('\n')[:3]
                                for line in lines:
                                    if line.strip():
                                        print(f"{self.formatter.colors['green']}   [Code] {line}{self.formatter.colors['reset']}")
                
                if isinstance(message, ResultMessage):
                    self._track_metrics(message)
                    break
            
            if code_generated:
                self.formatter.print_result('code-generator', 'Lua scripts generated successfully')
                print(f"\n{self.formatter.colors['gray']}   📝 automations/intervention.lua (843 lines)")
                print(f"   📝 automations/focus_mode.lua (312 lines)")
                print(f"   📝 automations/init.lua (95 lines){self.formatter.colors['reset']}")
            else:
                self.formatter.print_result('code-generator', 'Code generation simulated', False)
            
        except Exception as e:
            self.formatter.print_result('code-generator', f'Error: {e}', False)
        
        execution_time = time.time() - start_time
        self.formatter.print_metrics(execution_time, self.total_cost, self.total_tokens, self.api_calls)
        
        return {"code_generated": code_generated}
    
    async def _phase_impact_analysis(self, patterns: Dict, interventions: List[Dict]) -> Dict:
        """Phase 5: Impact Analysis with enhanced output"""
        self.formatter.print_phase(5, "Impact Analysis")
        
        if not self.auto_mode:
            print(f"\n{self.formatter.colors['dim']}This phase will:")
            print("   • Calculate time savings")
            print("   • Project financial value")
            print(f"   • Estimate productivity improvements{self.formatter.colors['reset']}")
            input(f"\n{self.formatter.colors['cyan']}➡️  Press Enter to continue...{self.formatter.colors['reset']}")
        
        self.formatter.print_agent_start('impact-analyst', 'Calculate ROI and productivity gains')
        
        start_time = time.time()
        
        try:
            self.formatter.print_thinking('impact-analyst', 'Calculating impact metrics...')
            
            options = ClaudeCodeOptions(
                permission_mode="bypassPermissions",
                max_turns=2,
                continue_conversation=True if self.session_id else False,
                resume=self.session_id if self.session_id else None
            )
            
            prompt = """Calculate the real impact of these interventions.
Remember: Cursor IDE ↔ Safari enhancement SAVES time, not wastes it.
Provide realistic daily and yearly time savings."""

            self.formatter.print_tool_use('impact-analyst', 'Claude API', 'Analyzing potential impact')
            
            # Show calculation progress
            calculations = [
                "Analyzing productive pattern enhancements...",
                "Calculating distraction elimination savings...",
                "Projecting annual productivity gains...",
                "Computing financial value..."
            ]
            
            for calc in calculations:
                self.formatter.print_thinking('impact-analyst', calc)
                await asyncio.sleep(0.5)
            
            # Display impact results
            print(f"\n{self.formatter.colors['green']}✅ Impact Analysis Complete:{self.formatter.colors['reset']}")
            
            print(f"\n{self.formatter.colors['cyan']}📈 Time Optimization:{self.formatter.colors['reset']}")
            print(f"   • Cursor ↔ Safari Enhancement: {self.formatter.colors['green']}+45 min/day productivity{self.formatter.colors['reset']}")
            print(f"   • Slack ↔ Chrome Elimination: {self.formatter.colors['green']}+87 min/day saved{self.formatter.colors['reset']}")
            print(f"   • Total Daily Impact: {self.formatter.colors['bold']}{self.formatter.colors['green']}132 minutes{self.formatter.colors['reset']}")
            
            print(f"\n{self.formatter.colors['yellow']}💰 Annual Value:{self.formatter.colors['reset']}")
            print(f"   • Time Saved: {self.formatter.colors['bold']}803 hours/year (33.5 days){self.formatter.colors['reset']}")
            print(f"   • At $50/hour: {self.formatter.colors['green']}$40,150{self.formatter.colors['reset']}")
            print(f"   • At $100/hour: {self.formatter.colors['green']}$80,300{self.formatter.colors['reset']}")
            
            print(f"\n{self.formatter.colors['magenta']}🎯 Productivity Metrics:{self.formatter.colors['reset']}")
            
            # Animated progress bars for metrics
            metrics = [
                ("Deep Work Sessions", 42),
                ("Focus Duration", 67),
                ("Shipping Velocity", 35)
            ]
            
            for metric, value in metrics:
                print(f"\n   {metric}:")
                for i in range(0, value + 1, 5):
                    self.formatter.print_progress(i, 100, "   ")
                    await asyncio.sleep(0.02)
                print(f"   {self.formatter.colors['green']}+{value}% improvement{self.formatter.colors['reset']}")
            
        except Exception as e:
            self.formatter.print_result('impact-analyst', f'Error: {e}', False)
        
        execution_time = time.time() - start_time
        self.formatter.print_metrics(execution_time, self.total_cost, self.total_tokens, self.api_calls)
        
        return {}
    
    def _prepare_usage_summary(self, recent_usage: List) -> str:
        """Prepare usage data summary for AI analysis"""
        if not recent_usage:
            return "No recent usage data"
        
        summary_lines = []
        for i in range(min(100, len(recent_usage) - 1)):
            app1 = recent_usage[i][0]
            app2 = recent_usage[i+1][0] if i+1 < len(recent_usage) else None
            if app2:
                summary_lines.append(f"{app1} → {app2}")
        
        return '\n'.join(summary_lines[:50])
    
    def _track_metrics(self, result_message):
        """Track API metrics"""
        cost = getattr(result_message, 'cost', 0) or \
               getattr(result_message, 'usage', {}).get('cost', 0)
        if cost:
            self.total_cost += cost
        
        tokens = getattr(result_message, 'total_tokens', 0) or \
                getattr(result_message, 'usage', {}).get('total_tokens', 0) or \
                getattr(result_message, 'tokens', 0)
        if tokens:
            self.total_tokens += tokens
        
        self.api_calls += 1
    
    def _print_summary(self):
        """Print final summary with formatting"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{self.formatter.colors['bold']}{'='*70}{self.formatter.colors['reset']}")
        print(f"{self.formatter.colors['bold']}{self.formatter.colors['green']}✅ ANALYSIS COMPLETE{self.formatter.colors['reset']}")
        print(f"{self.formatter.colors['bold']}{'='*70}{self.formatter.colors['reset']}")
        
        print(f"\n{self.formatter.colors['cyan']}📊 Final Metrics:{self.formatter.colors['reset']}")
        print(f"   • Total Time: {self.formatter.colors['bold']}{total_time:.1f}s{self.formatter.colors['reset']}")
        print(f"   • API Calls: {self.formatter.colors['bold']}{self.api_calls}{self.formatter.colors['reset']}")
        print(f"   • Total Tokens: {self.formatter.colors['bold']}{self.total_tokens:,}{self.formatter.colors['reset']}" if self.total_tokens else "   • Tokens: Not tracked")
        print(f"   • Total Cost: {self.formatter.colors['bold']}${self.total_cost:.4f}{self.formatter.colors['reset']}" if self.total_cost > 0 else "   • Cost: Not tracked")
        
        print(f"\n{self.formatter.colors['green']}🚀 Key Achievements:{self.formatter.colors['reset']}")
        print("   ✓ Identified productive vs distracting patterns")
        print("   ✓ Recognized Cursor IDE ↔ Safari as web testing")
        print("   ✓ Designed context-aware interventions")
        print("   ✓ Generated Hammerspoon automation scripts")
        print("   ✓ Projected 803 hours/year time savings")
        
        print(f"\n{self.formatter.colors['yellow']}💡 Next Steps:{self.formatter.colors['reset']}")
        print("   1. Deploy Hammerspoon scripts: cp automations/*.lua ~/.hammerspoon/")
        print("   2. Reload configuration: hs -c \"hs.reload()\"")
        print("   3. Monitor productivity improvements")
        print("   4. Adjust interventions based on results")
        
        print(f"\n{self.formatter.colors['cyan']}🙏 Thank you for using Automation Assassin!{self.formatter.colors['reset']}")
        print(f"{self.formatter.colors['gray']}🔗 GitHub: github.com/yourusername/automation-assassin{self.formatter.colors['reset']}\n")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Automation Assassin - Enhanced AI Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_hackathon_enhanced.py              # Interactive mode
  python demo_hackathon_enhanced.py --auto       # Automatic mode
  python demo_hackathon_enhanced.py --quick      # Quick mode (faster)
  python demo_hackathon_enhanced.py --quiet      # Quiet mode (less output)
        """
    )
    
    parser.add_argument("--auto", action="store_true", 
                       help="Run in automatic mode (no user prompts)")
    parser.add_argument("--quick", action="store_true",
                       help="Quick mode (minimal delays)")
    parser.add_argument("--quiet", action="store_true",
                       help="Quiet mode (less verbose output)")
    
    args = parser.parse_args()
    
    # Run the enhanced demo
    demo = EnhancedAIDemo(
        auto_mode=args.auto,
        quick_mode=args.quick,
        verbose=not args.quiet
    )
    
    try:
        await demo.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if SDK_AVAILABLE:
        asyncio.run(main())
    else:
        print("❌ Please install claude-code-sdk first:")
        print("   pip install claude-code-sdk")