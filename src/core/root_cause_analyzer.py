"""
Root Cause Analyzer - Identifies deeper reasons behind productivity patterns
Goes beyond surface behaviors to understand underlying needs and gaps
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

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

@dataclass
class RootCause:
    """Represents a root cause analysis result"""
    cause_type: RootCauseType
    confidence: float  # 0-100
    description: str
    evidence: List[str]
    psychological_explanation: str
    recommended_intervention: str
    learning_opportunity: Optional[str]

@dataclass
class PatternAnalysis:
    """Complete analysis of a pattern including root causes"""
    pattern_description: str
    surface_behavior: str
    root_causes: List[RootCause]
    primary_cause: RootCause
    intervention_type: str  # 'educational', 'coaching', 'behavioral', 'environmental'
    
class RootCauseAnalyzer:
    """
    Analyzes productivity patterns to identify root causes
    Recommends educational and coaching interventions
    """
    
    def __init__(self):
        self.pattern_history = {}
        self.learning_profile = {}
        
    def analyze_pattern(self, pattern_data: Dict, browser_context: Optional[Dict] = None) -> PatternAnalysis:
        """
        Analyze a pattern to identify root causes
        
        Args:
            pattern_data: Pattern information including apps, frequency, timing
            browser_context: Optional browser history for deeper analysis
            
        Returns:
            PatternAnalysis with root causes and recommendations
        """
        # Extract pattern characteristics
        app_a = pattern_data.get('app_a', '')
        app_b = pattern_data.get('app_b', '')
        occurrences = pattern_data.get('occurrences', 0)
        avg_gap = pattern_data.get('avg_gap_seconds', 0)
        time_of_day = pattern_data.get('peak_hours', [])
        
        # Analyze for different root cause types
        root_causes = []
        
        # Check for knowledge gaps
        knowledge_cause = self._analyze_knowledge_gap(pattern_data, browser_context)
        if knowledge_cause:
            root_causes.append(knowledge_cause)
            
        # Check for stress responses
        stress_cause = self._analyze_stress_response(pattern_data)
        if stress_cause:
            root_causes.append(stress_cause)
            
        # Check for skill deficits
        skill_cause = self._analyze_skill_deficit(pattern_data, browser_context)
        if skill_cause:
            root_causes.append(skill_cause)
            
        # Check for emotional regulation
        emotional_cause = self._analyze_emotional_pattern(pattern_data)
        if emotional_cause:
            root_causes.append(emotional_cause)
            
        # Check for biological rhythms
        biological_cause = self._analyze_biological_rhythm(pattern_data)
        if biological_cause:
            root_causes.append(biological_cause)
        
        # Determine primary cause
        primary_cause = self._determine_primary_cause(root_causes)
        
        # Create analysis
        surface_behavior = f"Switching between {app_a} and {app_b} {occurrences} times"
        
        return PatternAnalysis(
            pattern_description=f"{app_a} ↔ {app_b} pattern",
            surface_behavior=surface_behavior,
            root_causes=root_causes,
            primary_cause=primary_cause,
            intervention_type=self._recommend_intervention_type(primary_cause)
        )
    
    def _analyze_knowledge_gap(self, pattern_data: Dict, 
                              browser_context: Optional[Dict]) -> Optional[RootCause]:
        """Identify knowledge gaps from repeated searches"""
        
        if not browser_context:
            return None
            
        # Look for repeated searches
        search_patterns = self._extract_search_patterns(browser_context)
        
        if search_patterns:
            repeated_topic = search_patterns[0] if search_patterns else "technical concept"
            
            return RootCause(
                cause_type=RootCauseType.KNOWLEDGE_GAP,
                confidence=85,
                description=f"Repeated searches for '{repeated_topic}' indicate knowledge gap",
                evidence=[
                    f"Searched similar terms {len(search_patterns)} times",
                    "Pattern occurs during active work hours",
                    "Searches are technical/educational in nature"
                ],
                psychological_explanation=(
                    "When we repeatedly search for the same information, it indicates "
                    "the concept hasn't moved from working memory to long-term memory. "
                    "This is often due to lack of conceptual understanding rather than "
                    "poor memory."
                ),
                recommended_intervention="Structured learning with spaced repetition",
                learning_opportunity=f"Master {repeated_topic} permanently through focused education"
            )
        
        return None
    
    def _analyze_stress_response(self, pattern_data: Dict) -> Optional[RootCause]:
        """Identify stress-induced behavior patterns"""
        
        avg_gap = pattern_data.get('avg_gap_seconds', 0)
        occurrences = pattern_data.get('occurrences', 0)
        
        # Rapid switching often indicates stress
        if avg_gap < 10 and occurrences > 100:
            return RootCause(
                cause_type=RootCauseType.STRESS_RESPONSE,
                confidence=75,
                description="Rapid task switching as stress management mechanism",
                evidence=[
                    f"Very short gaps ({avg_gap}s) between switches",
                    f"High frequency ({occurrences} occurrences)",
                    "Pattern intensifies during complex tasks"
                ],
                psychological_explanation=(
                    "Your brain uses task-switching as a pressure release valve. "
                    "When cognitive load becomes overwhelming, rapid switching provides "
                    "micro-breaks that temporarily reduce mental strain. This is an "
                    "unconscious coping mechanism."
                ),
                recommended_intervention="Stress management and cognitive load techniques",
                learning_opportunity="Learn healthier stress response strategies"
            )
        
        return None
    
    def _analyze_skill_deficit(self, pattern_data: Dict, 
                              browser_context: Optional[Dict]) -> Optional[RootCause]:
        """Identify skill deficits from inefficient workflows"""
        
        # Look for inefficient patterns
        app_a = pattern_data.get('app_a', '').lower()
        app_b = pattern_data.get('app_b', '').lower()
        
        # Check for manual processes that could be automated
        if 'terminal' in app_a and 'finder' in app_b:
            return RootCause(
                cause_type=RootCauseType.SKILL_DEFICIT,
                confidence=70,
                description="Manual file navigation instead of terminal commands",
                evidence=[
                    "Switching between Terminal and Finder frequently",
                    "Could use command-line navigation",
                    "Indicates unfamiliarity with terminal commands"
                ],
                psychological_explanation=(
                    "We default to familiar tools even when better options exist. "
                    "This 'path of least resistance' saves cognitive effort short-term "
                    "but creates inefficiency long-term."
                ),
                recommended_intervention="Command-line navigation tutorial",
                learning_opportunity="Master terminal file operations"
            )
        
        return None
    
    def _analyze_emotional_pattern(self, pattern_data: Dict) -> Optional[RootCause]:
        """Identify emotional regulation patterns"""
        
        app_b = pattern_data.get('app_b', '').lower()
        
        # Social media or entertainment as emotional regulation
        emotional_apps = ['twitter', 'facebook', 'reddit', 'youtube', 'instagram']
        
        if any(app in app_b for app in emotional_apps):
            peak_hours = pattern_data.get('peak_hours', [])
            
            # Check if it happens before big tasks (procrastination)
            if peak_hours and min(peak_hours) in [9, 10, 14, 15]:  # Common task-start times
                return RootCause(
                    cause_type=RootCauseType.EMOTIONAL_REGULATION,
                    confidence=80,
                    description="Using social media to manage task anxiety",
                    evidence=[
                        "Pattern occurs at task initiation times",
                        "Involves mood-regulating apps",
                        "Delays start of challenging work"
                    ],
                    psychological_explanation=(
                        "Procrastination is rarely about laziness - it's emotional regulation. "
                        "When faced with tasks that trigger anxiety or overwhelm, your brain "
                        "seeks predictable, low-effort rewards to restore emotional balance."
                    ),
                    recommended_intervention="Task decomposition and anxiety management",
                    learning_opportunity="Understand and manage task-related anxiety"
                )
        
        return None
    
    def _analyze_biological_rhythm(self, pattern_data: Dict) -> Optional[RootCause]:
        """Identify patterns related to circadian rhythms"""
        
        peak_hours = pattern_data.get('peak_hours', [])
        
        # Check for post-lunch dip (2-4 PM)
        if peak_hours and any(h in [14, 15, 16] for h in peak_hours):
            return RootCause(
                cause_type=RootCauseType.BIOLOGICAL_RHYTHM,
                confidence=65,
                description="Pattern aligns with natural circadian rhythm dip",
                evidence=[
                    "Occurs during 2-4 PM circadian low",
                    "Universal biological pattern",
                    "Not a personal weakness"
                ],
                psychological_explanation=(
                    "Your circadian rhythm naturally dips between 2-4 PM due to "
                    "biological factors. This isn't laziness - it's biology. Your "
                    "body temperature drops and melatonin slightly increases."
                ),
                recommended_intervention="Schedule adjustment and energy management",
                learning_opportunity="Work with your biology, not against it"
            )
        
        return None
    
    def _extract_search_patterns(self, browser_context: Dict) -> List[str]:
        """Extract repeated search topics from browser history"""
        
        if not browser_context or not browser_context.get('history'):
            return []
            
        # Analyze page titles for repeated topics
        titles = [h.get('title', '') for h in browser_context.get('history', [])]
        
        # Simple repetition detection (in production, would use NLP)
        common_terms = {}
        tech_terms = ['react', 'python', 'git', 'css', 'javascript', 'api', 'debug']
        
        for title in titles:
            title_lower = title.lower()
            for term in tech_terms:
                if term in title_lower:
                    common_terms[term] = common_terms.get(term, 0) + 1
        
        # Return terms searched more than 3 times
        repeated = [term for term, count in common_terms.items() if count > 3]
        return repeated
    
    def _determine_primary_cause(self, causes: List[RootCause]) -> RootCause:
        """Determine the most likely root cause"""
        
        if not causes:
            return RootCause(
                cause_type=RootCauseType.UNCLEAR,
                confidence=0,
                description="Root cause unclear - needs more analysis",
                evidence=[],
                psychological_explanation="More data needed to understand this pattern",
                recommended_intervention="Continue monitoring",
                learning_opportunity=None
            )
        
        # Sort by confidence and return highest
        causes.sort(key=lambda x: x.confidence, reverse=True)
        return causes[0]
    
    def _recommend_intervention_type(self, root_cause: RootCause) -> str:
        """Recommend intervention type based on root cause"""
        
        intervention_map = {
            RootCauseType.KNOWLEDGE_GAP: "educational",
            RootCauseType.STRESS_RESPONSE: "coaching",
            RootCauseType.SKILL_DEFICIT: "educational",
            RootCauseType.EMOTIONAL_REGULATION: "coaching",
            RootCauseType.COGNITIVE_OVERLOAD: "behavioral",
            RootCauseType.HABIT_FORMATION: "behavioral",
            RootCauseType.ENVIRONMENTAL_TRIGGER: "environmental",
            RootCauseType.BIOLOGICAL_RHYTHM: "environmental",
            RootCauseType.SOCIAL_NEED: "coaching",
            RootCauseType.UNCLEAR: "monitoring"
        }
        
        return intervention_map.get(root_cause.cause_type, "monitoring")
    
    def generate_insight(self, analysis: PatternAnalysis) -> str:
        """Generate human-friendly insight from analysis"""
        
        primary = analysis.primary_cause
        
        insight = f"🔍 **Pattern Analysis: {analysis.pattern_description}**\n\n"
        insight += f"**What you're doing:** {analysis.surface_behavior}\n\n"
        insight += f"**Why you're really doing it:** {primary.description}\n\n"
        insight += f"**The psychology:** {primary.psychological_explanation}\n\n"
        
        if primary.learning_opportunity:
            insight += f"**Opportunity:** {primary.learning_opportunity}\n\n"
            
        insight += f"**Recommended approach:** {primary.recommended_intervention}\n"
        
        return insight