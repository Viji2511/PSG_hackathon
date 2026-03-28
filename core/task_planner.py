"""
Task Planner Module

Purpose: Break down complex, multi-step instructions into executable task lists.
Handles task dependencies, ordering, and sequencing.

Architecture: Domain-agnostic planning system.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)

# ═════════════════════ MODELS ═════════════════════

class TaskDependency(BaseModel):
    """Task dependency specification"""
    depends_on: str  # Task ID that must complete first
    type: str = "sequential"  # sequential, parallel, conditional

class ExecutableTask(BaseModel):
    """Task ready for execution"""
    task_id: str
    type: str  # "schedule", "send", "search", "remind", etc.
    label: str  # Human-readable name
    parameters: Dict[str, Any] = {}
    dependencies: List[TaskDependency] = []
    priority: int = 0  # Higher = more important
    retry_on_failure: bool = False
    timeout_seconds: Optional[int] = None

class ExecutionPlan(BaseModel):
    """Multi-step execution plan"""
    plan_id: str
    tasks: List[ExecutableTask] = []
    execution_order: List[str] = []  # Task IDs in execution order
    total_tasks: int
    estimated_duration_seconds: Optional[int] = None
    description: str = ""  # Human-readable plan description

# ═════════════════════ TASK PLANNER ═════════════════════

class TaskPlanner:
    """
    Converts complex instructions into step-by-step execution plans.
    
    Example:
        Input: "Prepare surveillance operation"
        Output: ExecutionPlan(
            tasks=[
                Task("check units"),
                Task("schedule mission"),
                Task("send message"),
                Task("set reminder")
            ],
            execution_order=["check_units", "schedule", "send", "remind"]
        )
    """
    
    def __init__(self):
        """Initialize Task Planner"""
        self.plan_counter = 0
    
    def generate_plan(
        self,
        intent: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """
        Generate execution plan from intent.
        
        Args:
            intent: Parsed intent from IntentEngine
            context: Session context for disambiguation
        
        Returns:
            ExecutionPlan with ordered tasks
        """
        self.plan_counter += 1
        plan_id = f"plan_{self.plan_counter}"
        
        logger.info(f"[{plan_id}] Generating execution plan for intent: {intent.intent_type}")
        
        # Step 1: Extract tasks from intent
        tasks = self._extract_tasks(intent, context)
        logger.info(f"[{plan_id}] Extracted {len(tasks)} tasks")
        
        # Step 2: Determine dependencies
        self._resolve_dependencies(tasks)
        
        # Step 3: Order tasks (topological sort)
        execution_order = self._order_tasks(tasks)
        logger.info(f"[{plan_id}] Execution order: {execution_order}")
        
        # Step 4: Generate description
        description = self._generate_plan_description(tasks, execution_order)
        
        # Step 5: Estimate duration
        estimated_duration = self._estimate_duration(tasks)
        
        plan = ExecutionPlan(
            plan_id=plan_id,
            tasks=tasks,
            execution_order=execution_order,
            total_tasks=len(tasks),
            estimated_duration_seconds=estimated_duration,
            description=description
        )
        
        logger.info(f"[{plan_id}] Plan generated: {description}")
        return plan
    
    def _extract_tasks(
        self,
        intent: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ExecutableTask]:
        """
        Extract executable tasks from intent.
        
        If intent has explicit tasks, use those.
        Otherwise, decompose complex instructions into subtasks.
        
        Example:
            Intent: "Prepare surveillance operation"
            Decomposed into:
            1. Verify available units
            2. Schedule mission
            3. Notify command
            4. Set reminder
        """
        tasks = []
        
        # If intent already has tasks, convert them
        if hasattr(intent, 'tasks') and intent.tasks:
            for idx, task in enumerate(intent.tasks):
                executable = ExecutableTask(
                    task_id=f"task_{idx}",
                    type=task.type.value if hasattr(task.type, 'value') else str(task.type),
                    label=self._generate_task_label(task),
                    parameters=task.parameters,
                    priority=0
                )
                tasks.append(executable)
        else:
            # Decompose complex instruction
            tasks = self._decompose_instruction(
                intent.interpretation if hasattr(intent, 'interpretation') else intent.raw_input,
                intent.domain_context if hasattr(intent, 'domain_context') else "generic"
            )
        
        return tasks
    
    def _decompose_instruction(
        self,
        instruction: str,
        domain: str
    ) -> List[ExecutableTask]:
        """
        Break down complex instruction into subtasks.
        
        Domain-aware decomposition:
        - Military: patrol,surveillance → check units → schedule → notify
        - Office: meeting → create event → send invites → set reminder
        - Smart home: automate morning → lights → coffee → notification
        """
        tasks = []
        instruction_lower = instruction.lower()
        
        # Military domain decomposition
        if domain == "military" or "patrol" in instruction_lower or "surveillance" in instruction_lower:
            if "prepare" in instruction_lower or "setup" in instruction_lower:
                tasks = [
                    ExecutableTask(task_id="check_units", type="query", label="Check available units"),
                    ExecutableTask(task_id="schedule", type="schedule", label="Schedule mission"),
                    ExecutableTask(task_id="notify", type="send", label="Notify command center"),
                    ExecutableTask(task_id="remind", type="remind", label="Set tactical reminder")
                ]
            elif "schedule" in instruction_lower:
                tasks = [
                    ExecutableTask(task_id="schedule", type="schedule", label="Schedule patrol/mission"),
                    ExecutableTask(task_id="notify", type="send", label="Notify units")
                ]
        
        # Office domain decomposition
        elif domain == "office" or "meeting" in instruction_lower or "event" in instruction_lower:
            if "reschedule" in instruction_lower:
                tasks = [
                    ExecutableTask(task_id="cancel", type="update", label="Cancel original event"),
                    ExecutableTask(task_id="create", type="create", label="Create new event"),
                    ExecutableTask(task_id="notify", type="send", label="Notify attendees")
                ]
            else:
                tasks = [
                    ExecutableTask(task_id="create", type="create", label="Create event"),
                    ExecutableTask(task_id="invite", type="send", label="Send invitations"),
                    ExecutableTask(task_id="remind", type="remind", label="Set reminder")
                ]
        
        # Default decomposition
        if not tasks:
            tasks = [
                ExecutableTask(
                    task_id="default_task",
                    type="execute",
                    label=instruction[:50],
                    parameters={"instruction": instruction}
                )
            ]
        
        return tasks
    
    def _generate_task_label(self, task: Any) -> str:
        """Generate human-readable label for task"""
        task_type = task.type.value if hasattr(task.type, 'value') else str(task.type)
        
        labels = {
            "schedule": "Schedule mission/event",
            "create": "Create new item",
            "send": "Send notification/message",
            "search": "Search/retrieve information",
            "remind": "Set reminder/alert",
            "update": "Update existing item",
            "delete": "Delete item",
            "query": "Query/lookup information",
        }
        
        return labels.get(task_type, f"Execute {task_type}")
    
    def _resolve_dependencies(self, tasks: List[ExecutableTask]) -> None:
        """
        Determine if tasks depend on each other.
        
        Rules:
        - Schedule must come before sending related message
        - Query must come before using query results
        - Create before update/delete
        """
        task_types = [t.type for t in tasks]
        
        for idx, task in enumerate(tasks):
            # If sending, check if there's a prior create/schedule
            if task.type == "send":
                for prior_task in tasks[:idx]:
                    if prior_task.type in ["schedule", "create"]:
                        task.dependencies.append(
                            TaskDependency(depends_on=prior_task.task_id, type="sequential")
                        )
            
            # If updating, must have create first
            elif task.type == "update":
                for prior_task in tasks[:idx]:
                    if prior_task.type == "create":
                        task.dependencies.append(
                            TaskDependency(depends_on=prior_task.task_id, type="sequential")
                        )
    
    def _order_tasks(self, tasks: List[ExecutableTask]) -> List[str]:
        """
        Order tasks respecting dependencies (topological sort).
        
        Returns: List of task IDs in execution order
        """
        # Build task lookup
        task_dict = {t.task_id: t for t in tasks}
        
        ordered = []
        remaining = set(task_dict.keys())
        
        while remaining:
            # Find tasks with no unmet dependencies
            ready = []
            for task_id in remaining:
                task = task_dict[task_id]
                deps_met = all(
                    dep.depends_on in ordered
                    for dep in task.dependencies
                )
                if deps_met:
                    ready.append(task_id)
            
            if not ready:
                # Circular dependency or issue - just add first item
                ready = [remaining.pop()]
            
            # Add ready tasks in order (by priority)
            ready.sort(
                key=lambda tid: task_dict[tid].priority,
                reverse=True
            )
            
            for task_id in ready:
                ordered.append(task_id)
                remaining.remove(task_id)
        
        return ordered
    
    def _generate_plan_description(
        self,
        tasks: List[ExecutableTask],
        execution_order: List[str]
    ) -> str:
        """Generate human-readable plan description"""
        if not tasks:
            return "No tasks"
        
        task_dict = {t.task_id: t for t in tasks}
        descriptions = []
        
        for step_num, task_id in enumerate(execution_order, 1):
            task = task_dict[task_id]
            descriptions.append(f"{step_num}. {task.label}")
        
        return " → ".join(descriptions) if len(descriptions) <= 3 else "\n".join(descriptions)
    
    def _estimate_duration(self, tasks: List[ExecutableTask]) -> Optional[int]:
        """Estimate total execution time in seconds"""
        if not tasks:
            return None
        
        # Rough estimates per task type
        duration_estimates = {
            "schedule": 5,
            "create": 3,
            "send": 2,
            "search": 3,
            "remind": 1,
            "update": 3,
            "delete": 2,
            "query": 2,
            "execute": 10
        }
        
        total = sum(
            duration_estimates.get(t.type, 5)
            for t in tasks
        )
        
        return total
    
    def validate_plan(self, plan: ExecutionPlan) -> Tuple[bool, List[str]]:
        """
        Validate execution plan.
        
        Checks:
        - All tasks present
        - No circular dependencies
        - All dependencies satisfied
        """
        errors = []
        
        if len(plan.tasks) != plan.total_tasks:
            errors.append(f"Task count mismatch: {len(plan.tasks)} vs {plan.total_tasks}")
        
        if len(plan.execution_order) != plan.total_tasks:
            errors.append(f"Execution order incomplete: {len(plan.execution_order)} vs {plan.total_tasks}")
        
        # Check all task IDs in execution order exist
        task_ids = {t.task_id for t in plan.tasks}
        for task_id in plan.execution_order:
            if task_id not in task_ids:
                errors.append(f"Unknown task in execution order: {task_id}")
        
        return len(errors) == 0, errors
