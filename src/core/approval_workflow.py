"""
Approval Workflow - User Control and Intervention Approval System
Gives users full control over pattern interpretation and automation deployment
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
from pathlib import Path

class ApprovalStage(Enum):
    """Stages in the approval workflow"""
    PATTERN_VALIDATION = "pattern_validation"
    INTERVENTION_SELECTION = "intervention_selection"
    PREVIEW_AND_DEPLOY = "preview_and_deploy"
    DEPLOYED = "deployed"
    REJECTED = "rejected"

class InterventionStatus(Enum):
    """Status of an intervention"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    DEPLOYED = "deployed"
    DISABLED = "disabled"

@dataclass
class WorkflowSession:
    """Represents a complete approval workflow session"""
    session_id: str
    start_time: datetime
    current_stage: ApprovalStage
    patterns: List[Dict]  # Patterns being reviewed
    validated_patterns: List[Dict]  # Patterns with user feedback
    selected_interventions: List[Dict]  # Chosen interventions
    deployment_config: Optional[str]  # Final Hammerspoon config
    completion_time: Optional[datetime]
    
@dataclass
class InterventionApproval:
    """Approval details for an intervention"""
    intervention_id: str
    pattern_id: str
    status: InterventionStatus
    user_modifications: Optional[Dict]
    deployment_path: Optional[str]
    enabled: bool
    test_mode: bool
    
class ApprovalWorkflow:
    """
    Three-stage approval workflow for pattern validation and intervention deployment
    Ensures user maintains full control over automations
    """
    
    def __init__(self, feedback_manager, intervention_generator):
        self.feedback_manager = feedback_manager
        self.intervention_generator = intervention_generator
        self.current_session = None
        self.approval_history = []
        self.deployed_interventions = {}
        
    def start_workflow(self, patterns: List[Dict]) -> WorkflowSession:
        """
        Start a new approval workflow session
        
        Args:
            patterns: List of detected patterns to review
            
        Returns:
            WorkflowSession object
        """
        from uuid import uuid4
        
        session = WorkflowSession(
            session_id=str(uuid4()),
            start_time=datetime.now(),
            current_stage=ApprovalStage.PATTERN_VALIDATION,
            patterns=patterns,
            validated_patterns=[],
            selected_interventions=[],
            deployment_config=None,
            completion_time=None
        )
        
        self.current_session = session
        return session
    
    def stage1_pattern_validation(self, patterns: List[Dict]) -> Dict:
        """
        Stage 1: Validate patterns with user
        
        Args:
            patterns: List of patterns with context
            
        Returns:
            Validation interface data
        """
        validation_interface = {
            'stage': 'pattern_validation',
            'title': 'Pattern Review',
            'description': 'Help us understand your workflows better',
            'patterns': []
        }
        
        for pattern in patterns:
            # Get feedback prompt for each pattern
            prompt = self.feedback_manager.get_pattern_feedback_prompt(pattern)
            
            # Add visual representation
            pattern_card = {
                'id': prompt['pattern_id'],
                'visual': self._generate_pattern_visual(pattern),
                'stats': {
                    'occurrences': pattern['occurrences'],
                    'daily_average': pattern['occurrences'] / 30,
                    'time_lost': pattern.get('total_time_lost', 0) / 60,
                    'peak_hours': pattern.get('peak_hours', [])
                },
                'our_guess': prompt['our_interpretation'],
                'validation_options': prompt['options'],
                'quick_actions': [
                    {'id': 'productive', 'label': '✅ Productive', 'color': 'green'},
                    {'id': 'distraction', 'label': '🚨 Distraction', 'color': 'red'},
                    {'id': 'context', 'label': '🤔 Needs Context', 'color': 'yellow'}
                ]
            }
            
            validation_interface['patterns'].append(pattern_card)
        
        validation_interface['bulk_actions'] = [
            {'id': 'mark_all_productive', 'label': 'Mark All as Productive'},
            {'id': 'mark_all_distraction', 'label': 'Mark All as Distractions'},
            {'id': 'auto_classify', 'label': 'Use AI Classification'}
        ]
        
        return validation_interface
    
    def _generate_pattern_visual(self, pattern: Dict) -> str:
        """Generate ASCII visual of pattern"""
        app_a = pattern.get('app_a', 'App A')[:10]
        app_b = pattern.get('app_b', 'App B')[:10]
        count = pattern.get('occurrences', 0)
        
        # Create visual representation
        visual = f"""
        ┌────────────┐     {count}x     ┌────────────┐
        │ {app_a:^10} │ ←────────→ │ {app_b:^10} │
        └────────────┘              └────────────┘
        """
        
        return visual.strip()
    
    def process_pattern_feedback(self, pattern_id: str, feedback: Dict) -> bool:
        """
        Process user feedback for a pattern
        
        Args:
            pattern_id: Pattern identifier
            feedback: User's feedback
            
        Returns:
            Success boolean
        """
        # Record feedback
        success = self.feedback_manager.record_feedback(pattern_id, feedback)
        
        if success and self.current_session:
            # Update validated patterns
            validated_pattern = {
                'pattern_id': pattern_id,
                'user_classification': feedback.get('classification'),
                'is_productive': feedback.get('type') == 'reject',
                'needs_intervention': feedback.get('type') == 'confirm',
                'custom_explanation': feedback.get('explanation')
            }
            
            self.current_session.validated_patterns.append(validated_pattern)
        
        return success
    
    def stage2_intervention_selection(self) -> Dict:
        """
        Stage 2: Select and customize interventions
        
        Returns:
            Intervention selection interface
        """
        if not self.current_session:
            return {'error': 'No active workflow session'}
        
        selection_interface = {
            'stage': 'intervention_selection',
            'title': 'Choose Your Interventions',
            'description': 'Select how you want to handle each pattern',
            'pattern_interventions': []
        }
        
        # Generate interventions for patterns needing them
        for validated in self.current_session.validated_patterns:
            if not validated.get('needs_intervention'):
                continue
            
            # Find original pattern data
            pattern = next(
                (p for p in self.current_session.patterns 
                 if f"{p['app_a']}|{p['app_b']}" == validated['pattern_id']),
                None
            )
            
            if not pattern:
                continue
            
            # Generate interventions
            interventions = self.intervention_generator.generate_interventions(
                pattern_type=validated.get('user_classification', 'unknown'),
                app_a=pattern['app_a'],
                app_b=pattern['app_b'],
                context=pattern
            )
            
            # Rank by effectiveness
            ranked = self.intervention_generator.rank_interventions(interventions)
            
            pattern_card = {
                'pattern_id': validated['pattern_id'],
                'pattern_display': f"{pattern['app_a']} ↔ {pattern['app_b']}",
                'recommended_interventions': [
                    {
                        'id': f"{validated['pattern_id']}_{i}",
                        'name': intervention.name,
                        'type': intervention.type.value,
                        'description': intervention.description,
                        'difficulty': intervention.difficulty,
                        'effectiveness': intervention.effectiveness,
                        'preview_available': intervention.type.value.startswith('hammerspoon'),
                        'selected': i == 0  # Pre-select top recommendation
                    }
                    for i, intervention in enumerate(ranked[:5])
                ],
                'custom_option': {
                    'enabled': True,
                    'placeholder': 'Describe your custom intervention...'
                }
            }
            
            selection_interface['pattern_interventions'].append(pattern_card)
        
        selection_interface['global_settings'] = {
            'test_mode': {
                'enabled': True,
                'duration': 3600,  # 1 hour test
                'description': 'Try interventions for 1 hour before permanent deployment'
            },
            'intensity': {
                'options': ['gentle', 'moderate', 'aggressive'],
                'default': 'moderate',
                'description': 'How strict should interventions be?'
            },
            'schedule': {
                'enabled': True,
                'work_hours': '9:00-18:00',
                'description': 'Only activate during work hours'
            }
        }
        
        return selection_interface
    
    def stage3_preview_and_deploy(self) -> Dict:
        """
        Stage 3: Preview and deploy selected interventions
        
        Returns:
            Preview and deployment interface
        """
        if not self.current_session or not self.current_session.selected_interventions:
            return {'error': 'No interventions selected'}
        
        # Generate combined Hammerspoon config
        selected = []
        for intervention_data in self.current_session.selected_interventions:
            # Reconstruct intervention object (simplified here)
            selected.append(intervention_data)
        
        config = self.intervention_generator.generate_combined_config(selected)
        
        preview_interface = {
            'stage': 'preview_and_deploy',
            'title': 'Review and Deploy',
            'description': 'Final review before activation',
            'preview': {
                'hammerspoon_config': config,
                'line_count': len(config.split('\n')),
                'interventions_count': len(selected),
                'estimated_time_savings': self._estimate_time_savings(selected)
            },
            'deployment_options': [
                {
                    'id': 'test_1hour',
                    'label': 'Test for 1 Hour',
                    'description': 'Try it out with easy rollback',
                    'icon': '🧪'
                },
                {
                    'id': 'test_1day',
                    'label': 'Test for 1 Day',
                    'description': 'Full day trial',
                    'icon': '📅'
                },
                {
                    'id': 'deploy_permanent',
                    'label': 'Deploy Permanently',
                    'description': 'Activate all interventions',
                    'icon': '🚀'
                },
                {
                    'id': 'save_only',
                    'label': 'Save Configuration',
                    'description': 'Save for manual deployment',
                    'icon': '💾'
                }
            ],
            'safety_features': [
                {
                    'name': 'Kill Switch',
                    'description': 'Cmd+Shift+Escape disables all interventions',
                    'enabled': True
                },
                {
                    'name': 'Auto-Rollback',
                    'description': 'Revert if productivity drops',
                    'enabled': True
                },
                {
                    'name': 'Gradual Activation',
                    'description': 'Phase in interventions over time',
                    'enabled': False
                }
            ],
            'code_preview': self._generate_code_preview(config),
            'mcp_setup': self._extract_mcp_instructions(config)
        }
        
        self.current_session.deployment_config = config
        
        return preview_interface
    
    def _estimate_time_savings(self, interventions: List) -> Dict:
        """Estimate time savings from interventions"""
        # Simplified estimation
        base_savings = len(interventions) * 15  # 15 min per intervention
        
        return {
            'daily_minutes': base_savings,
            'weekly_hours': base_savings * 5 / 60,
            'yearly_days': base_savings * 250 / (60 * 24),
            'confidence': 'moderate'
        }
    
    def _generate_code_preview(self, config: str) -> Dict:
        """Generate a preview of the Hammerspoon code"""
        lines = config.split('\n')
        
        # Extract key sections
        sections = {
            'hotkeys': [],
            'watchers': [],
            'functions': []
        }
        
        for i, line in enumerate(lines):
            if 'hs.hotkey.bind' in line:
                sections['hotkeys'].append({
                    'line': i + 1,
                    'code': line.strip(),
                    'description': self._extract_hotkey_desc(line)
                })
            elif 'watcher.new' in line:
                sections['watchers'].append({
                    'line': i + 1,
                    'code': line.strip(),
                    'description': 'App activity monitor'
                })
            elif line.strip().startswith('function'):
                sections['functions'].append({
                    'line': i + 1,
                    'code': line.strip(),
                    'description': self._extract_function_desc(lines, i)
                })
        
        return sections
    
    def _extract_hotkey_desc(self, line: str) -> str:
        """Extract hotkey description from code"""
        import re
        match = re.search(r'\{([^}]+)\},\s*"([^"]+)"', line)
        if match:
            keys = match.group(1).replace('"', '').replace(',', '+')
            key = match.group(2)
            return f"{keys}+{key}"
        return "Hotkey"
    
    def _extract_function_desc(self, lines: List[str], index: int) -> str:
        """Extract function description from comments"""
        if index > 0 and '--' in lines[index - 1]:
            return lines[index - 1].replace('--', '').strip()
        return "Helper function"
    
    def _extract_mcp_instructions(self, config: str) -> List[Dict]:
        """Extract MCP setup instructions from config"""
        mcp_instructions = []
        
        if 'MCP Server Setup' in config:
            lines = config.split('\n')
            in_mcp_section = False
            current_mcp = {}
            
            for line in lines:
                if 'MCP Server Setup' in line:
                    in_mcp_section = True
                elif in_mcp_section:
                    if line.startswith('-- ') and ':' in line:
                        if current_mcp:
                            mcp_instructions.append(current_mcp)
                        current_mcp = {'name': line.replace('--', '').replace(':', '').strip()}
                    elif 'npm install' in line or 'pip install' in line:
                        current_mcp['install'] = line.replace('--', '').strip()
            
            if current_mcp:
                mcp_instructions.append(current_mcp)
        
        return mcp_instructions
    
    def deploy_interventions(self, deployment_type: str) -> Dict:
        """
        Deploy the selected interventions
        
        Args:
            deployment_type: Type of deployment (test_1hour, test_1day, permanent, save_only)
            
        Returns:
            Deployment result
        """
        if not self.current_session or not self.current_session.deployment_config:
            return {'success': False, 'error': 'No configuration ready'}
        
        config = self.current_session.deployment_config
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if deployment_type == 'save_only':
            # Just save the configuration
            save_path = f"automations/config_{timestamp}.lua"
            Path(save_path).parent.mkdir(exist_ok=True)
            
            with open(save_path, 'w') as f:
                f.write(config)
            
            return {
                'success': True,
                'message': f'Configuration saved to {save_path}',
                'path': save_path
            }
        
        # Add safety features based on deployment type
        if deployment_type.startswith('test'):
            duration = 3600 if deployment_type == 'test_1hour' else 86400
            config = self._add_test_wrapper(config, duration)
        
        # Add kill switch
        config = self._add_kill_switch(config)
        
        # Save to Hammerspoon config location
        hammerspoon_path = Path.home() / '.hammerspoon' / 'automation_assassin.lua'
        
        # Backup existing config
        if hammerspoon_path.exists():
            backup_path = hammerspoon_path.with_suffix(f'.backup_{timestamp}.lua')
            hammerspoon_path.rename(backup_path)
        
        # Write new config
        with open(hammerspoon_path, 'w') as f:
            f.write(config)
        
        # Update init.lua to load our config
        init_path = Path.home() / '.hammerspoon' / 'init.lua'
        init_content = init_path.read_text() if init_path.exists() else ''
        
        if 'automation_assassin' not in init_content:
            with open(init_path, 'a') as f:
                f.write('\n-- Automation Assassin\n')
                f.write('require("automation_assassin")\n')
        
        # Record deployment
        self.deployed_interventions[timestamp] = {
            'type': deployment_type,
            'config_path': str(hammerspoon_path),
            'backup_path': str(backup_path) if deployment_type != 'test_1hour' else None,
            'patterns': len(self.current_session.validated_patterns),
            'interventions': len(self.current_session.selected_interventions)
        }
        
        # Complete workflow
        self.current_session.completion_time = datetime.now()
        self.current_session.current_stage = ApprovalStage.DEPLOYED
        self.approval_history.append(self.current_session)
        
        return {
            'success': True,
            'message': f'Interventions deployed ({deployment_type})',
            'config_path': str(hammerspoon_path),
            'rollback_available': True,
            'deployment_id': timestamp
        }
    
    def _add_test_wrapper(self, config: str, duration: int) -> str:
        """Add test mode wrapper to config"""
        wrapper = f'''
-- TEST MODE: Auto-disable after {duration} seconds
local testEndTime = os.time() + {duration}
local testTimer = hs.timer.doEvery(60, function()
    if os.time() >= testEndTime then
        hs.notify.new({{
            title = "Test Mode Ended",
            informativeText = "Automation Assassin interventions disabled",
            soundName = hs.notify.defaultNotificationSound
        }}):send()
        
        -- Disable all watchers and hotkeys
        if appWatcher then appWatcher:stop() end
        if blockWatcher then blockWatcher:stop() end
        if focusTimer then focusTimer:stop() end
        
        -- Stop the test timer
        testTimer:stop()
    end
end)

hs.notify.new({{
    title = "Test Mode Active",
    informativeText = "Testing for {duration // 3600} hour(s)",
    soundName = hs.notify.defaultNotificationSound
}}):send()

'''
        return wrapper + config
    
    def _add_kill_switch(self, config: str) -> str:
        """Add emergency kill switch to config"""
        kill_switch = '''
-- EMERGENCY KILL SWITCH: Cmd+Shift+Escape
hs.hotkey.bind({"cmd", "shift"}, "escape", function()
    hs.alert.show("🛑 AUTOMATION ASSASSIN DISABLED", 3)
    
    -- Stop all watchers
    if appWatcher then appWatcher:stop() end
    if blockWatcher then blockWatcher:stop() end
    if testingWatcher then testingWatcher:stop() end
    if focusTimer then focusTimer:stop() end
    if batchTimer then batchTimer:stop() end
    
    -- Clear all hotkeys except kill switch
    for _, hotkey in pairs(hs.hotkey.getHotkeys()) do
        if not hotkey:idx():find("escape") then
            hotkey:delete()
        end
    end
    
    hs.notify.new({
        title = "Automation Assassin Disabled",
        informativeText = "All interventions stopped. Restart Hammerspoon to re-enable.",
        soundName = hs.notify.defaultNotificationSound
    }):send()
end)

'''
        return kill_switch + config
    
    def rollback_deployment(self, deployment_id: str) -> Dict:
        """
        Rollback a deployment
        
        Args:
            deployment_id: Timestamp ID of deployment
            
        Returns:
            Rollback result
        """
        if deployment_id not in self.deployed_interventions:
            return {'success': False, 'error': 'Deployment not found'}
        
        deployment = self.deployed_interventions[deployment_id]
        
        if deployment['backup_path'] and Path(deployment['backup_path']).exists():
            # Restore backup
            Path(deployment['config_path']).unlink(missing_ok=True)
            Path(deployment['backup_path']).rename(deployment['config_path'])
            
            return {
                'success': True,
                'message': 'Successfully rolled back to previous configuration'
            }
        else:
            # Just remove the config
            Path(deployment['config_path']).unlink(missing_ok=True)
            
            return {
                'success': True,
                'message': 'Interventions removed'
            }
    
    def get_workflow_status(self) -> Dict:
        """Get current workflow status"""
        if not self.current_session:
            return {'status': 'no_active_session'}
        
        return {
            'session_id': self.current_session.session_id,
            'current_stage': self.current_session.current_stage.value,
            'patterns_reviewed': len(self.current_session.validated_patterns),
            'patterns_total': len(self.current_session.patterns),
            'interventions_selected': len(self.current_session.selected_interventions),
            'ready_to_deploy': self.current_session.deployment_config is not None
        }