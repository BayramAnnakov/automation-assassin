"""
Learning Generator - Creates personalized educational interventions
Generates tutorials, cheat sheets, and learning paths based on user needs
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class LearningModule:
    """Represents a learning intervention"""
    title: str
    objective: str
    content_type: str  # 'tutorial', 'cheat_sheet', 'exercise', 'explanation'
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    estimated_time: int  # minutes
    content: str
    practice_exercises: Optional[List[str]]
    spaced_repetition_schedule: Optional[List[int]]  # days

@dataclass
class LearningPath:
    """Complete learning path for a skill or concept"""
    skill_name: str
    total_modules: int
    estimated_completion_days: int
    modules: List[LearningModule]
    success_metrics: List[str]

class LearningGenerator:
    """
    Generates personalized educational content based on user patterns
    Creates tutorials, exercises, and learning paths
    """
    
    def __init__(self):
        self.generated_content = {}
        self.user_progress = {}
        
    def generate_intervention(self, knowledge_gap: str, 
                            search_history: List[str],
                            skill_level: str = "intermediate") -> LearningPath:
        """
        Generate educational intervention for a knowledge gap
        
        Args:
            knowledge_gap: The concept user struggles with
            search_history: User's search history related to this topic
            skill_level: User's current skill level
            
        Returns:
            Complete learning path with modules
        """
        
        # Analyze the knowledge gap
        modules = []
        
        # Module 1: Conceptual Understanding
        concept_module = self._generate_concept_module(knowledge_gap, skill_level)
        modules.append(concept_module)
        
        # Module 2: Practical Cheat Sheet
        cheat_sheet = self._generate_cheat_sheet(knowledge_gap, search_history)
        modules.append(cheat_sheet)
        
        # Module 3: Hands-on Exercises
        exercises = self._generate_exercises(knowledge_gap, skill_level)
        modules.append(exercises)
        
        # Module 4: Real-world Application
        application = self._generate_application_module(knowledge_gap)
        modules.append(application)
        
        # Create learning path
        return LearningPath(
            skill_name=knowledge_gap,
            total_modules=len(modules),
            estimated_completion_days=7,
            modules=modules,
            success_metrics=[
                f"Can explain {knowledge_gap} without references",
                f"Completes tasks without searching for {knowledge_gap}",
                "Confidence level increased to 8/10 or higher",
                "Can teach concept to others"
            ]
        )
    
    def _generate_concept_module(self, topic: str, skill_level: str) -> LearningModule:
        """Generate conceptual understanding module"""
        
        # In production, this would call an LLM to generate content
        # For now, using templates
        
        content = f"""
# Understanding {topic}

## What is {topic}?
{topic} is a fundamental concept that helps you [core purpose]. Think of it like [analogy].

## Why does {topic} matter?
- Solves the problem of [problem it solves]
- Enables you to [what it enables]
- Prevents [what it prevents]

## Core Concepts:
1. **Foundation**: The basic principle is...
2. **Mechanism**: It works by...
3. **Application**: You use it when...

## Mental Model:
Imagine {topic} as a [metaphor]. When you [action], it [reaction].

## Common Misconceptions:
❌ {topic} is not [misconception 1]
❌ It doesn't [misconception 2]
✅ It actually [correct understanding]

## Quick Example:
```
[Simple, clear example]
```

Remember: {topic} is about [core insight], not [common mistake].
"""
        
        return LearningModule(
            title=f"Understanding {topic} - Core Concepts",
            objective=f"Build solid conceptual foundation of {topic}",
            content_type="tutorial",
            difficulty=skill_level,
            estimated_time=10,
            content=content,
            practice_exercises=None,
            spaced_repetition_schedule=[1, 3, 7, 14, 30]
        )
    
    def _generate_cheat_sheet(self, topic: str, search_history: List[str]) -> LearningModule:
        """Generate personalized cheat sheet based on searches"""
        
        # Analyze what user searches for most
        common_questions = self._extract_common_questions(search_history)
        
        content = f"""
# {topic} Personal Cheat Sheet

## Your Most Searched Items:
{self._format_common_searches(common_questions)}

## Quick Reference:

### Syntax:
```
[Most common syntax patterns]
```

### Common Patterns:
1. **Pattern 1**: When you need to [use case]
   ```
   [code example]
   ```

2. **Pattern 2**: When you want to [use case]
   ```
   [code example]
   ```

### Your Gotchas:
Based on your searches, watch out for:
- [Common mistake 1]
- [Common mistake 2]

### Quick Commands:
| What you want | How to do it |
|--------------|--------------|
| [Action 1] | `[command]` |
| [Action 2] | `[command]` |

### Decision Tree:
```
Need to [task]?
├─ If [condition 1] → Use [solution 1]
├─ If [condition 2] → Use [solution 2]
└─ Otherwise → Use [solution 3]
```

💡 Pro tip: [Personalized tip based on patterns]
"""
        
        return LearningModule(
            title=f"{topic} Personal Cheat Sheet",
            objective="Quick reference customized to your needs",
            content_type="cheat_sheet",
            difficulty="all",
            estimated_time=5,
            content=content,
            practice_exercises=None,
            spaced_repetition_schedule=None
        )
    
    def _generate_exercises(self, topic: str, skill_level: str) -> LearningModule:
        """Generate practice exercises"""
        
        exercises = [
            f"Exercise 1: Basic {topic} - Start with fundamentals",
            f"Exercise 2: Common scenario - Apply {topic} to typical use case",
            f"Exercise 3: Debug challenge - Fix broken {topic} implementation",
            f"Exercise 4: Build from scratch - Create {topic} without references",
            f"Exercise 5: Teach back - Explain {topic} in your own words"
        ]
        
        content = f"""
# {topic} Practice Exercises

## Exercise Path:
Work through these in order. Each builds on the previous.

### 🟢 Exercise 1: Warm-up (5 min)
**Task**: [Simple task description]
**Goal**: Get comfortable with basic {topic} syntax

<details>
<summary>Hint</summary>
Start by [hint]
</details>

### 🟡 Exercise 2: Real Scenario (10 min)
**Task**: [Practical task description]
**Goal**: Apply {topic} to actual problem

<details>
<summary>Hint</summary>
Think about [hint]
</details>

### 🔴 Exercise 3: Debug Challenge (15 min)
**Task**: Fix this broken code:
```
[Broken code with {topic} error]
```
**Goal**: Understand common {topic} mistakes

### 🏆 Exercise 4: Create (20 min)
**Task**: Build [something] using {topic}
**Requirements**:
- Must use {topic} correctly
- No looking at references
- Should handle edge cases

### 👨‍🏫 Exercise 5: Teach (10 min)
**Task**: Write explanation of {topic} for a beginner
**Include**:
- What it is
- Why it matters
- Simple example
- Common mistake to avoid

## Self-Assessment:
Rate yourself 1-10 on:
- Understanding: ___/10
- Application: ___/10
- Confidence: ___/10

If any score < 7, review the concept module.
"""
        
        return LearningModule(
            title=f"{topic} Practice Lab",
            objective="Build muscle memory through practice",
            content_type="exercise",
            difficulty=skill_level,
            estimated_time=60,
            content=content,
            practice_exercises=exercises,
            spaced_repetition_schedule=[1, 3, 7]
        )
    
    def _generate_application_module(self, topic: str) -> LearningModule:
        """Generate real-world application module"""
        
        content = f"""
# {topic} in the Real World

## Your Use Cases:
Based on your work patterns, you'll use {topic} for:
1. [Specific use case 1 from user's context]
2. [Specific use case 2]
3. [Specific use case 3]

## Integration with Your Workflow:

### With Your Tools:
- **In [Tool 1]**: Use {topic} by...
- **In [Tool 2]**: Apply {topic} when...

### Your Projects:
Looking at your codebase, {topic} would improve:
- [Specific file/function]
- [Another specific area]

## Advanced Patterns:
Once comfortable, explore:
- [Advanced technique 1]
- [Advanced technique 2]

## Debugging Guide:
When {topic} doesn't work:
1. Check [common issue 1]
2. Verify [common issue 2]
3. Ensure [common issue 3]

## Performance Tips:
- [Optimization 1]
- [Optimization 2]

## Next Steps:
✅ You've mastered {topic}!
→ Consider learning [related topic 1]
→ Explore [related topic 2]
"""
        
        return LearningModule(
            title=f"Applying {topic} to Your Work",
            objective="Connect learning to actual projects",
            content_type="application",
            difficulty="intermediate",
            estimated_time=15,
            content=content,
            practice_exercises=None,
            spaced_repetition_schedule=[7, 14, 30]
        )
    
    def _extract_common_questions(self, search_history: List[str]) -> List[str]:
        """Extract common questions from search history"""
        
        # In production, would use NLP to extract patterns
        # For now, return sample questions
        return search_history[:5] if search_history else [
            "How to use this feature?",
            "Why doesn't this work?",
            "What's the syntax for this?"
        ]
    
    def _format_common_searches(self, questions: List[str]) -> str:
        """Format common searches into readable list"""
        
        formatted = ""
        for i, q in enumerate(questions, 1):
            formatted += f"{i}. {q}\n"
        return formatted
    
    def generate_coaching_message(self, pattern: str, root_cause: str) -> str:
        """Generate coaching message for behavioral patterns"""
        
        messages = {
            "stress_response": """
🧠 **Understanding Your Pattern**

You're not broken - your brain is trying to protect you. When you face challenging code, 
your stress response triggers task-switching as a relief valve.

**What's happening:**
- Difficult task → Cortisol spike
- Brain seeks relief → Switch apps
- Temporary comfort → Return to task
- Cycle repeats

**Better alternatives:**
1. **Box Breathing**: 4 seconds in, 4 hold, 4 out, 4 hold
2. **Micro-walk**: 30 seconds away from screen
3. **Progress celebration**: Acknowledge small wins

Try this: Next time you feel the switch urge, pause and take 3 deep breaths first.
""",
            
            "procrastination": """
😊 **You're Not Lazy - You're Overwhelmed**

That Twitter check before big tasks? It's your brain avoiding perceived threat.
Large tasks trigger your amygdala's threat response.

**The science:**
Task looks big → Brain says "danger" → Seek safety in familiar apps

**The solution - 2-Minute Rule:**
1. Commit to just 2 minutes
2. Only open the file/document
3. No pressure to continue
4. Usually, momentum takes over

Remember: Starting is the hardest part. Make it tiny.
""",
            
            "knowledge_gap": """
📚 **From Searching to Knowing**

You've searched this {pattern} times. Let's move it from Google to your brain permanently.

**Why repetition isn't working:**
- You're memorizing syntax, not understanding concepts
- Each search is isolated, not connected
- No active recall practice

**The fix - Active Learning:**
1. Understand the WHY, not just HOW
2. Create your personal examples
3. Teach it back (even to rubber duck)
4. Spaced repetition: Review in 1, 3, 7 days

Let's start with a 5-minute visual explanation...
"""
        }
        
        return messages.get(root_cause, self._generate_generic_coaching(pattern))
    
    def _generate_generic_coaching(self, pattern: str) -> str:
        """Generate generic coaching message"""
        
        return f"""
💡 **Insight About Your {pattern} Pattern**

Every behavior serves a purpose. Your pattern might be:
- Managing cognitive load
- Seeking mental breaks
- Processing information
- Regulating emotions

**Questions to explore:**
1. What triggers this pattern?
2. How do you feel before/after?
3. What need is it meeting?

Understanding 'why' is the first step to 'how to change.'
"""
    
    def track_progress(self, user_id: str, module_id: str, completed: bool):
        """Track user progress through learning modules"""
        
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
            
        self.user_progress[user_id][module_id] = {
            'completed': completed,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_next_module(self, user_id: str, learning_path: LearningPath) -> Optional[LearningModule]:
        """Get next module in learning path for user"""
        
        if user_id not in self.user_progress:
            return learning_path.modules[0]
            
        completed = self.user_progress[user_id]
        
        for module in learning_path.modules:
            module_id = f"{learning_path.skill_name}_{module.title}"
            if module_id not in completed or not completed[module_id].get('completed'):
                return module
                
        return None  # All completed