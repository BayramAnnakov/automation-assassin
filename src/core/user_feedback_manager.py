"""
User Feedback Manager - Interactive Pattern Validation System
Collects user feedback on patterns and learns preferences
"""

import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
from enum import Enum

class FeedbackType(Enum):
    """Types of user feedback"""
    CONFIRM = "confirm"  # Yes, this is a problem
    REJECT = "reject"    # No, this is productive
    RECLASSIFY = "reclassify"  # Different interpretation
    CUSTOM = "custom"    # User-provided explanation

@dataclass
class PatternFeedback:
    """User feedback on a pattern"""
    pattern_id: str  # app_a|app_b
    feedback_type: FeedbackType
    user_classification: Optional[str]
    user_explanation: Optional[str]
    suggested_intervention: Optional[str]
    timestamp: datetime
    confidence_adjustment: float  # How much to adjust future confidence

@dataclass 
class UserPreference:
    """Learned user preferences"""
    pattern: str
    is_productive: bool
    custom_classification: Optional[str]
    preferred_interventions: List[str]
    never_block: bool
    always_allow_together: bool
    notes: Optional[str]

class UserFeedbackManager:
    """
    Manages user feedback on patterns and learns preferences
    Provides interactive validation and stores feedback for learning
    """
    
    def __init__(self, db_path: str = "data/user_feedback.db"):
        self.db_path = db_path
        self._init_database()
        self.feedback_cache = {}
        self.preferences = self._load_preferences()
        
    def _init_database(self):
        """Initialize feedback database"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                user_classification TEXT,
                user_explanation TEXT,
                suggested_intervention TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                confidence_adjustment REAL DEFAULT 0.0
            )
        ''')
        
        # Create preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                pattern TEXT PRIMARY KEY,
                is_productive BOOLEAN,
                custom_classification TEXT,
                preferred_interventions TEXT,  -- JSON array
                never_block BOOLEAN DEFAULT FALSE,
                always_allow_together BOOLEAN DEFAULT FALSE,
                notes TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create learning history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT,
                old_classification TEXT,
                new_classification TEXT,
                confidence_before REAL,
                confidence_after REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_preferences(self) -> Dict[str, UserPreference]:
        """Load user preferences from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern, is_productive, custom_classification,
                   preferred_interventions, never_block, always_allow_together, notes
            FROM user_preferences
        ''')
        
        preferences = {}
        for row in cursor.fetchall():
            pattern = row[0]
            preferences[pattern] = UserPreference(
                pattern=pattern,
                is_productive=bool(row[1]),
                custom_classification=row[2],
                preferred_interventions=json.loads(row[3]) if row[3] else [],
                never_block=bool(row[4]),
                always_allow_together=bool(row[5]),
                notes=row[6]
            )
        
        conn.close()
        return preferences
    
    def get_pattern_feedback_prompt(self, pattern_data: Dict) -> Dict:
        """
        Generate an interactive feedback prompt for a pattern
        
        Args:
            pattern_data: Dictionary with pattern details
            
        Returns:
            Feedback prompt structure
        """
        app_a = pattern_data.get('app_a', '')
        app_b = pattern_data.get('app_b', '')
        occurrences = pattern_data.get('occurrences', 0)
        pattern_type = pattern_data.get('pattern_type', 'unknown')
        confidence = pattern_data.get('confidence', 50)
        
        pattern_id = f"{app_a}|{app_b}"
        
        # Check for existing preferences
        existing_pref = self.preferences.get(pattern_id)
        
        prompt = {
            'pattern_id': pattern_id,
            'display_name': f"{app_a} ↔ {app_b}",
            'occurrences': occurrences,
            'our_interpretation': {
                'type': pattern_type,
                'confidence': confidence,
                'description': self._get_pattern_description(pattern_type)
            },
            'has_previous_feedback': existing_pref is not None,
            'previous_feedback': existing_pref.__dict__ if existing_pref else None,
            'options': [
                {
                    'id': 'confirm',
                    'emoji': '✅',
                    'label': 'Yes, this is problematic',
                    'description': 'This pattern wastes my time and needs intervention'
                },
                {
                    'id': 'reject',
                    'emoji': '❌',
                    'label': 'No, this is productive',
                    'description': 'This is part of my normal workflow'
                },
                {
                    'id': 'reclassify',
                    'emoji': '🔄',
                    'label': 'Different interpretation',
                    'description': 'I\'ll explain what this pattern actually is'
                },
                {
                    'id': 'custom',
                    'emoji': '💡',
                    'label': 'Custom intervention',
                    'description': 'I have a specific idea for handling this'
                }
            ],
            'follow_up_questions': self._get_follow_up_questions(pattern_type)
        }
        
        return prompt
    
    def _get_pattern_description(self, pattern_type: str) -> str:
        """Get human-readable description of pattern type"""
        descriptions = {
            'testing_workflow': 'Testing web application (productive)',
            'research_workflow': 'Researching and documenting (productive)',
            'distraction_loop': 'Distraction interrupting work (problematic)',
            'communication_burst': 'Frequent message checking (possibly problematic)',
            'creative_workflow': 'Creative process (productive)',
            'unknown': 'Pattern needs more context'
        }
        return descriptions.get(pattern_type, 'Unknown pattern')
    
    def _get_follow_up_questions(self, pattern_type: str) -> List[Dict]:
        """Get follow-up questions based on pattern type"""
        if pattern_type == 'testing_workflow':
            return [
                {
                    'id': 'testing_type',
                    'question': 'What kind of testing are you doing?',
                    'options': ['Manual QA', 'Frontend development', 'API testing', 'Other']
                },
                {
                    'id': 'automation_interest',
                    'question': 'Would browser automation help?',
                    'options': ['Yes, definitely', 'Maybe', 'No, manual is fine']
                }
            ]
        elif pattern_type == 'distraction_loop':
            return [
                {
                    'id': 'distraction_severity',
                    'question': 'How disruptive is this to your work?',
                    'options': ['Very disruptive', 'Somewhat', 'Minor annoyance']
                },
                {
                    'id': 'intervention_strength',
                    'question': 'How aggressive should interventions be?',
                    'options': ['Block completely', 'Progressive delays', 'Gentle reminders']
                }
            ]
        else:
            return []
    
    def record_feedback(self, pattern_id: str, feedback: Dict) -> bool:
        """
        Record user feedback on a pattern
        
        Args:
            pattern_id: Identifier for the pattern (app_a|app_b)
            feedback: User's feedback dictionary
            
        Returns:
            Success boolean
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Record feedback
            cursor.execute('''
                INSERT INTO pattern_feedback 
                (pattern_id, feedback_type, user_classification, 
                 user_explanation, suggested_intervention, confidence_adjustment)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                pattern_id,
                feedback.get('type', 'unknown'),
                feedback.get('classification'),
                feedback.get('explanation'),
                feedback.get('suggested_intervention'),
                feedback.get('confidence_adjustment', 0.0)
            ))
            
            # Update preferences
            self._update_preferences(pattern_id, feedback, cursor)
            
            conn.commit()
            conn.close()
            
            # Update cache
            self.preferences = self._load_preferences()
            
            return True
            
        except Exception as e:
            print(f"Error recording feedback: {e}")
            return False
    
    def _update_preferences(self, pattern_id: str, feedback: Dict, cursor):
        """Update user preferences based on feedback"""
        
        is_productive = feedback.get('type') == 'reject' or \
                       feedback.get('classification') in ['testing', 'research', 'creative']
        
        never_block = feedback.get('type') == 'reject' or \
                     feedback.get('never_block', False)
        
        preferred_interventions = json.dumps(
            feedback.get('preferred_interventions', [])
        )
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences
            (pattern, is_productive, custom_classification, 
             preferred_interventions, never_block, always_allow_together, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            is_productive,
            feedback.get('classification'),
            preferred_interventions,
            never_block,
            feedback.get('always_allow', False),
            feedback.get('notes')
        ))
    
    def get_pattern_preference(self, app_a: str, app_b: str) -> Optional[UserPreference]:
        """
        Get user's preference for a specific pattern
        
        Args:
            app_a: First app
            app_b: Second app
            
        Returns:
            UserPreference if exists, None otherwise
        """
        # Try both orders
        pattern_ids = [f"{app_a}|{app_b}", f"{app_b}|{app_a}"]
        
        for pattern_id in pattern_ids:
            if pattern_id in self.preferences:
                return self.preferences[pattern_id]
        
        return None
    
    def adjust_confidence(self, pattern_type: str, app_a: str, app_b: str) -> float:
        """
        Adjust confidence based on user feedback history
        
        Args:
            pattern_type: Initial classification
            app_a: First app
            app_b: Second app
            
        Returns:
            Confidence adjustment (-100 to +100)
        """
        pattern_id = f"{app_a}|{app_b}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get feedback history
        cursor.execute('''
            SELECT feedback_type, confidence_adjustment
            FROM pattern_feedback
            WHERE pattern_id = ? OR pattern_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (pattern_id, f"{app_b}|{app_a}"))
        
        total_adjustment = 0.0
        feedback_count = 0
        
        for row in cursor.fetchall():
            feedback_type = row[0]
            adjustment = row[1]
            
            # Weight recent feedback more heavily
            weight = 1.0 / (feedback_count + 1)
            
            if feedback_type == 'confirm':
                total_adjustment += 20 * weight
            elif feedback_type == 'reject':
                total_adjustment -= 30 * weight
            elif feedback_type == 'reclassify':
                total_adjustment -= 20 * weight
            
            total_adjustment += adjustment * weight
            feedback_count += 1
        
        conn.close()
        
        return max(-50, min(50, total_adjustment))
    
    def generate_feedback_report(self) -> Dict:
        """Generate a report of user feedback patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get feedback statistics
        cursor.execute('''
            SELECT feedback_type, COUNT(*) as count
            FROM pattern_feedback
            GROUP BY feedback_type
        ''')
        
        feedback_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get most productive patterns
        cursor.execute('''
            SELECT pattern, custom_classification
            FROM user_preferences
            WHERE is_productive = 1
            LIMIT 10
        ''')
        
        productive_patterns = [
            {'pattern': row[0], 'classification': row[1]}
            for row in cursor.fetchall()
        ]
        
        # Get patterns to block
        cursor.execute('''
            SELECT pattern, preferred_interventions
            FROM user_preferences
            WHERE is_productive = 0 AND never_block = 0
            LIMIT 10
        ''')
        
        patterns_to_block = [
            {
                'pattern': row[0],
                'interventions': json.loads(row[1]) if row[1] else []
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'total_feedback': sum(feedback_stats.values()),
            'feedback_breakdown': feedback_stats,
            'productive_patterns': productive_patterns,
            'patterns_to_block': patterns_to_block,
            'learning_progress': {
                'patterns_learned': len(self.preferences),
                'productive_identified': len(productive_patterns),
                'distractions_identified': len(patterns_to_block)
            }
        }
    
    def export_preferences(self, filepath: str):
        """Export user preferences to JSON file"""
        preferences_dict = {
            pattern: {
                'is_productive': pref.is_productive,
                'classification': pref.custom_classification,
                'interventions': pref.preferred_interventions,
                'never_block': pref.never_block,
                'notes': pref.notes
            }
            for pattern, pref in self.preferences.items()
        }
        
        with open(filepath, 'w') as f:
            json.dump(preferences_dict, f, indent=2)
    
    def import_preferences(self, filepath: str):
        """Import user preferences from JSON file"""
        with open(filepath, 'r') as f:
            preferences_dict = json.load(f)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern, pref_data in preferences_dict.items():
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences
                (pattern, is_productive, custom_classification,
                 preferred_interventions, never_block, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                pattern,
                pref_data.get('is_productive', False),
                pref_data.get('classification'),
                json.dumps(pref_data.get('interventions', [])),
                pref_data.get('never_block', False),
                pref_data.get('notes')
            ))
        
        conn.commit()
        conn.close()
        
        # Reload preferences
        self.preferences = self._load_preferences()