"""
Intent Engine Module

Purpose: Convert natural language commands into structured intents.
Uses LLM function calling to parse user input and extract entities.

Architecture: Domain-agnostic - works with any application domain.
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
import json
import logging

logger = logging.getLogger(__name__)

# ═════════════════════ INTENT TYPES ═════════════════════

class IntentType(str, Enum):
    """Base intent types - applicable to any domain"""
    SINGLE_TASK = "single_task"
    MULTI_TASK = "multi_task"
    QUERY = "query"
    CONFIRMATION = "confirmation"
    CLARIFICATION = "clarification"
    UNKNOWN = "unknown"

class TaskType(str, Enum):
    """Generic task types - mapped to domain-specific tools"""
    SCHEDULE = "schedule"
    CREATE = "create"
    SEND = "send"
    SEARCH = "search"
    REMIND = "remind"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    EXECUTE = "execute"

# ═════════════════════ MODELS ═════════════════════

class Entity(BaseModel):
    """Extracted entity from user input"""
    name: str
    type: str  # e.g., "time", "person", "location", "action"
    value: str
    confidence: float = Field(ge=0.0, le=1.0)

class Task(BaseModel):
    """Scheduled/extracted task from intent"""
    task_id: Optional[str] = None
    type: TaskType
    parameters: Dict[str, Any] = {}
    entities: List[Entity] = []
    context: Dict[str, Any] = {}
    priority: str = "normal"  # low, normal, high, critical

class Intent(BaseModel):
    """Structured intent from natural language"""
    intent_id: Optional[str] = None
    intent_type: IntentType
    raw_input: str
    tasks: List[Task] = []
    entities: List[Entity] = []
    missing_fields: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)
    interpretation: str = ""  # Human-readable explanation
    domain_context: Optional[str] = None  # e.g., "military", "office", "smart_home"

# ═════════════════════ INTENT ENGINE ═════════════════════

class IntentEngine:
    """
    Converts natural language commands into structured intents.
    
    Example:
        Input: "Schedule patrol tomorrow and remind team"
        Output: Intent(
            intent_type="multi_task",
            tasks=[
                Task(type="schedule", parameters={"time": "tomorrow"}),
                Task(type="remind", parameters={"target": "team"})
            ]
        )
    """
    
    def __init__(self, llm_provider: Optional[str] = "openai"):
        """
        Initialize Intent Engine.
        
        Args:
            llm_provider: "openai", "anthropic", "local", etc.
        """
        self.llm_provider = llm_provider
        self.intent_counter = 0
        
    def parse_intent(
        self, 
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        domain: str = "generic"
    ) -> Intent:
        """
        Parse user input into structured intent.
        
        Args:
            user_input: Natural language command
            context: Session context for disambiguation
            domain: Domain context ("military", "office", etc.)
        
        Returns:
            Intent object with parsed tasks and entities
        """
        self.intent_counter += 1
        intent_id = f"intent_{self.intent_counter}"
        
        # Step 1: Detect intent type
        intent_type = self._detect_intent_type(user_input)
        logger.info(f"[{intent_id}] Detected intent type: {intent_type.value}")
        
        # Step 2: Extract entities
        entities = self._extract_entities(user_input, context, domain)
        logger.info(f"[{intent_id}] Extracted {len(entities)} entities")
        
        # Step 3: Parse tasks
        tasks = self._parse_tasks(user_input, entities, domain)
        logger.info(f"[{intent_id}] Parsed {len(tasks)} tasks")
        
        # Step 4: Detect missing fields
        missing_fields = self._detect_missing_fields(tasks)
        logger.info(f"[{intent_id}] Missing fields: {missing_fields}")
        
        # Step 5: Calculate confidence
        confidence = self._calculate_confidence(entities, tasks, missing_fields)
        logger.info(f"[{intent_id}] Confidence: {confidence:.2%}")
        
        # Step 6: Generate interpretation
        interpretation = self._generate_interpretation(intent_type, tasks, entities)
        
        return Intent(
            intent_id=intent_id,
            intent_type=intent_type,
            raw_input=user_input,
            tasks=tasks,
            entities=entities,
            missing_fields=missing_fields,
            confidence=confidence,
            interpretation=interpretation,
            domain_context=domain
        )
    
    def _detect_intent_type(self, user_input: str) -> IntentType:
        """Detect if single task, multi-task, query, confirmation, etc."""
        # Simple heuristic (in production, use LLM)
        lowered = user_input.lower()
        
        if "yes" in lowered or "confirm" in lowered or "approve" in lowered:
            return IntentType.CONFIRMATION
        elif "what" in lowered or "how" in lowered or "where" in lowered or "?" in lowered:
            return IntentType.QUERY
        elif " and " in lowered or "," in lowered:
            # Multiple comma-separated or 'and' separated items
            return IntentType.MULTI_TASK
        else:
            return IntentType.SINGLE_TASK
    
    def _extract_entities(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        domain: str
    ) -> List[Entity]:
        """
        Extract named entities from user input.
        
        Examples:
            "Schedule patrol TOMORROW at SECTOR 4"
            → Entity(name="time", value="tomorrow", type="temporal")
            → Entity(name="location", value="sector 4", type="location")
        """
        entities = []
        
        # Simple extraction patterns (in production use NER model or LLM)
        time_keywords = ["tomorrow", "today", "tonight", "monday", "tomorrow night", "0400 hrs"]
        location_keywords = ["sector", "grid", "border", "lac", "control"]
        action_keywords = ["schedule", "alert", "send", "remind", "create"]
        
        for time_kw in time_keywords:
            if time_kw.lower() in user_input.lower():
                entities.append(Entity(
                    name="time",
                    type="temporal",
                    value=time_kw,
                    confidence=0.85
                ))
        
        for loc_kw in location_keywords:
            if loc_kw.lower() in user_input.lower():
                # Extract value after keyword
                idx = user_input.lower().find(loc_kw.lower())
                value = user_input[idx:].split()[0:2]  # Get keyword + next word
                entities.append(Entity(
                    name="location",
                    type="location",
                    value=" ".join(value),
                    confidence=0.80
                ))
        
        return entities
    
    def _parse_tasks(
        self,
        user_input: str,
        entities: List[Entity],
        domain: str
    ) -> List[Task]:
        """
        Parse natural language into task list.
        
        Example:
            Input: "Schedule patrol tomorrow"
            Output: [Task(type="schedule", parameters={"action": "patrol", "time": "tomorrow"})]
        """
        tasks = []
        
        # Map keywords to task types
        keyword_mapping = {
            "schedule": TaskType.SCHEDULE,
            "create": TaskType.CREATE,
            "send": TaskType.SEND,
            "search": TaskType.SEARCH,
            "remind": TaskType.REMIND,
            "alert": TaskType.SEND,
        }
        
        for keyword, task_type in keyword_mapping.items():
            if keyword.lower() in user_input.lower():
                task = Task(
                    type=task_type,
                    parameters={
                        "action": user_input,
                        "domain": domain
                    },
                    entities=entities,
                    priority="normal"
                )
                tasks.append(task)
        
        if not tasks:
            # If no clear task detected, create generic query task
            tasks.append(Task(
                type=TaskType.QUERY,
                parameters={"query": user_input},
                entities=entities
            ))
        
        return tasks
    
    def _detect_missing_fields(self, tasks: List[Task]) -> List[str]:
        """
        Detect missing required fields for task execution.
        
        Example:
            Task: Schedule event
            Missing: ["time", "location"] if not provided
        """
        missing = []
        
        for task in tasks:
            if task.type == TaskType.SCHEDULE:
                if "time" not in task.parameters:
                    missing.append("scheduled_time")
                if "location" not in task.parameters and "target" not in task.parameters:
                    missing.append("target_location" )
            
            elif task.type == TaskType.SEND:
                if "recipient" not in task.parameters:
                    missing.append("recipient")
                if "message" not in task.parameters:
                    missing.append("message_content")
            
            elif task.type == TaskType.REMIND:
                if "time" not in task.parameters:
                    missing.append("reminder_time")
                if "target" not in task.parameters:
                    missing.append("reminder_target")
        
        return missing
    
    def _calculate_confidence(
        self,
        entities: List[Entity],
        tasks: List[Task],
        missing_fields: List[str]
    ) -> float:
        """
        Calculate overall confidence in intent parsing.
        
        Factors:
        - Entity extraction confidence (avg)
        - Number of missing fields (penalty)
        - Task clarity
        """
        if not entities and not tasks:
            return 0.3  # Very low confidence
        
        # Average entity confidence
        entity_conf = sum(e.confidence for e in entities) / len(entities) if entities else 0.5
        
        # Penalty for missing fields
        missing_penalty = len(missing_fields) * 0.15
        
        # Task presence bonus
        task_bonus = min(len(tasks) * 0.05, 0.2)
        
        confidence = entity_conf - missing_penalty + task_bonus
        return max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
    
    def _generate_interpretation(
        self,
        intent_type: IntentType,
        tasks: List[Task],
        entities: List[Entity]
    ) -> str:
        """Generate human-readable explanation of parsed intent."""
        if intent_type == IntentType.MULTI_TASK:
            task_descs = [f"{t.type.value} ({', '.join(f'{k}={v}' for k, v in t.parameters.items())})" for t in tasks[:3]]
            return f"I understood: Multiple tasks - {'; '.join(task_descs)}"
        elif intent_type == IntentType.SINGLE_TASK:
            if tasks:
                t = tasks[0]
                params = ", ".join(f"{k}={v}" for k, v in list(t.parameters.items())[:2])
                return f"I understood: {t.type.value.title()} ({params})"
            return "I understood: Single task"
        elif intent_type == IntentType.QUERY:
            return "I understood: This is a query or question"
        elif intent_type == IntentType.CONFIRMATION:
            return "I understood: This is a confirmation"
        else:
            return "I understood: Action request"
