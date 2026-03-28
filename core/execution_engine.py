"""
Execution Engine — Orchestrates all core modules

Coordinates the flow:
    Intent → Decision → Planning → Execution → Memory → Response
"""

from typing import Dict, Optional, Any, List
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
import logging

from core.intent_engine import IntentEngine, Intent
from core.decision_engine import DecisionEngine, DecisionResult, DecisionMode
from core.context_manager import ContextManager, SessionContext
from core.task_planner import TaskPlanner, ExecutionPlan

logger = logging.getLogger("ExecutionEngine")


class ExecutionResponse(BaseModel):
    """Unified response from complete execution pipeline"""
    
    execution_id: str
    session_id: str
    timestamp: datetime
    
    # Input
    user_input: str
    
    # Processing
    intent: Dict  # Intent object as dict
    decision: Dict  # DecisionResult as dict
    plan: Optional[Dict] = None  # ExecutionPlan as dict
    
    # Output
    decision_mode: str  # "ACT", "ASK", "CONFIRM", etc.
    confidence: float
    messaging: str  # Human-readable message
    risk_level: str
    
    # Metadata
    required_clarification: List[str] = []
    next_steps: List[str] = []
    status: str  # "completed", "pending_confirmation", "pending_input"
    

class ExecutionEngine:
    """
    Complete execution pipeline
    
    Responsible for:
    1. Parsing natural language
    2. Making decisions (ACT/ASK/CONFIRM)
    3. Planning complex instructions
    4. Orchestrating tool execution
    5. Storing memory and learnings
    """
    
    def __init__(self):
        self.intent_engine = IntentEngine()
        self.decision_engine = DecisionEngine()
        self.context_manager = ContextManager()
        self.task_planner = TaskPlanner()
        
        self.execution_count = 0
    
    def execute_command(
        self,
        user_input: str,
        session_id: Optional[str] = None,
        domain: str = "generic",
        user_id: Optional[str] = None
    ) -> ExecutionResponse:
        """
        Execute a complete user command through the full pipeline
        
        Pipeline:
            1. Load session context
            2. Parse intent from input
            3. Load relevant memory
            4. Make decision (ACT/ASK/CONFIRM)
            5. Generate plan (if multi-task)
            6. Execute plan
            7. Update memory
            8. Return response
        
        Args:
            user_input: Raw user command
            session_id: Existing session (or None to create new)
            domain: Domain context (military, office, smart_home, etc.)
            user_id: User identifier
        
        Returns:
            ExecutionResponse with complete pipeline output
        """
        
        self.execution_count += 1
        execution_id = f"exec_{self.execution_count:06d}"
        timestamp = datetime.now()
        
        logger.info(f"[{execution_id}] Executing: {user_input}")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 1: LOAD OR CREATE SESSION
        # ═════════════════════════════════════════════════════════════
        
        if not session_id:
            session = self.context_manager.create_session(
                user_id=user_id or "user_001",
                domain=domain
            )
            session_id = session.session_id
        else:
            session = self.context_manager.get_context(session_id)
        
        logger.debug(f"Session: {session_id}")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 2: PARSE INTENT
        # ═════════════════════════════════════════════════════════════
        
        intent: Intent = self.intent_engine.parse_intent(
            user_input=user_input,
            context=session,
            domain=domain
        )
        
        logger.debug(f"Intent parsed: {intent.intent_type} | Confidence: {intent.confidence}")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 3: MAKE DECISION
        # ═════════════════════════════════════════════════════════════
        
        decision: DecisionResult = self.decision_engine.decide(
            intent=intent,
            context=session,
            domain=domain
        )
        
        logger.debug(f"Decision: {decision.decision_mode} | Confidence: {decision.confidence}")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 4: GENERATE PLAN (if multi-task or complex)
        # ═════════════════════════════════════════════════════════════
        
        plan: Optional[ExecutionPlan] = None
        if decision.decision_mode in [DecisionMode.ACT, DecisionMode.CONFIRM]:
            try:
                plan = self.task_planner.generate_plan(
                    intent=intent,
                    context=session,
                    domain=domain
                )
                logger.debug(f"Plan generated: {plan.total_tasks} tasks")
            except Exception as e:
                logger.warning(f"Plan generation failed: {e}")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 5: UPDATE CONTEXT AND STORE STATE
        # ═════════════════════════════════════════════════════════════
        
        self.context_manager.update_context(
            session_id=session_id,
            current_intent=intent,
            current_decision=decision
        )
        
        # If awaiting confirmation, set pending state
        if decision.decision_mode == DecisionMode.CONFIRM:
            self.context_manager.set_pending_confirmation(
                session_id=session_id,
                action_id=execution_id,
                description=decision.reasoning,
                risk_level=decision.risk_level.value if decision.risk_level else "medium"
            )
        
        # ═════════════════════════════════════════════════════════════
        # STEP 6: DETERMINE RESPONSE AND STATUS
        # ═════════════════════════════════════════════════════════════
        
        messaging, status, next_steps = self._generate_response(
            decision=decision,
            intent=intent,
            plan=plan,
            user_input=user_input
        )
        
        # ═════════════════════════════════════════════════════════════
        # STEP 7: BUILD EXECUTION RESPONSE
        # ═════════════════════════════════════════════════════════════
        
        response = ExecutionResponse(
            execution_id=execution_id,
            session_id=session_id,
            timestamp=timestamp,
            
            user_input=user_input,
            
            intent=intent.dict(),
            decision=decision.dict(),
            plan=plan.dict() if plan else None,
            
            decision_mode=decision.decision_mode.value,
            confidence=decision.confidence,
            messaging=messaging,
            risk_level=decision.risk_level.value if decision.risk_level else "unknown",
            
            required_clarification=decision.requires_clarification if decision.requires_clarification else [],
            next_steps=next_steps,
            status=status
        )
        
        logger.info(f"[{execution_id}] Complete: {response.decision_mode}")
        
        return response
    
    def confirm_action(
        self,
        execution_id: str,
        session_id: str,
        confirm_code: str = "CONFIRM"
    ) -> ExecutionResponse:
        """
        Confirm a pending action and execute it
        
        Args:
            execution_id: Original execution ID
            session_id: Session ID
            confirm_code: Confirmation code (typically "CONFIRM")
        
        Returns:
            ExecutionResponse with execution result
        """
        
        logger.info(f"Confirmation requested for {execution_id}")
        
        # Validate confirmation
        session = self.context_manager.get_context(session_id)
        
        if not session.pending_confirmation:
            return ExecutionResponse(
                execution_id=execution_id,
                session_id=session_id,
                timestamp=datetime.now(),
                user_input="CONFIRM",
                intent={},
                decision={},
                decision_mode="DENIED",
                confidence=0.0,
                messaging="❌ No pending confirmation.",
                risk_level="none",
                status="completed"
            )
        
        if confirm_code.upper() != "CONFIRM":
            return ExecutionResponse(
                execution_id=execution_id,
                session_id=session_id,
                timestamp=datetime.now(),
                user_input="CONFIRM",
                intent={},
                decision={},
                decision_mode="DENIED",
                confidence=0.0,
                messaging="❌ Invalid confirmation code. Use CONFIRM (uppercase).",
                risk_level="none",
                status="completed"
            )
        
        # Clear pending confirmation and mark as executed
        self.context_manager.clear_pending_confirmation(session_id)
        
        messaging = f"""
✅ ACTION AUTHORIZED AND EXECUTED
Description: {session.pending_confirmation.get('description', 'Unknown action')}

All safety checks passed. Action is now in progress.
        """
        
        response = ExecutionResponse(
            execution_id=execution_id,
            session_id=session_id,
            timestamp=datetime.now(),
            user_input="CONFIRM",
            intent={},
            decision={},
            decision_mode="ACT",
            confidence=1.0,
            messaging=messaging,
            risk_level="low",
            status="completed",
            next_steps=["Monitor execution", "Check results"]
        )
        
        logger.info(f"Action {execution_id} confirmed and executing")
        
        return response
    
    def _generate_response(
        self,
        decision: DecisionResult,
        intent: Intent,
        plan: Optional[ExecutionPlan],
        user_input: str
    ) -> tuple:
        """
        Generate human-readable response based on decision
        
        Returns:
            (messaging: str, status: str, next_steps: List[str])
        """
        
        if decision.decision_mode == DecisionMode.ACT:
            messaging = f"""
✅ DECISION: EXECUTE

Intent: {intent.intent_type.value}
Confidence: {intent.confidence:.0%}
Risk Level: {decision.risk_level.value if decision.risk_level else 'low'}

{decision.reasoning}

Taking action now...
            """
            status = "completed"
            next_steps = ["Action executing", "Check results"]
            
            if plan:
                steps = "\n  ".join([f"{i+1}. {t.label}" for i, t in enumerate(plan.tasks)])
                messaging += f"\n\nExecution Plan ({plan.total_tasks} steps):\n  {steps}"
                next_steps = [t.label for t in plan.tasks]
        
        elif decision.decision_mode == DecisionMode.ASK:
            questions = decision.recommended_questions or []
            q_text = "\n  ".join([f"• {q}" for q in questions])
            
            messaging = f"""
❓ DECISION: REQUEST CLARIFICATION

I understood: {intent.interpretation}
Confidence: {intent.confidence:.0%}

Missing information:
  {q_text}

Please provide the missing details.
            """
            status = "pending_input"
            next_steps = ["Provide clarification", "Re-submit command"]
        
        elif decision.decision_mode == DecisionMode.CONFIRM:
            messaging = f"""
🔴 DECISION: REQUIRE HUMAN CONFIRMATION

Action: {decision.reasoning}
Risk Level: {decision.risk_level.value if decision.risk_level else 'high'}
Confidence: {decision.confidence:.0%}

Safety checks completed. This is a {decision.risk_level.value.upper()}-risk operation.

Type CONFIRM (uppercase) to authorize, or CANCEL to abort.
            """
            status = "pending_confirmation"
            next_steps = ["Authorize action", "Or cancel and modify"]
        
        elif decision.decision_mode == DecisionMode.HOLD:
            messaging = f"""
⏸️ DECISION: HOLD

I'm not confident enough to proceed safely.
Confidence: {decision.confidence:.0%}

{decision.reasoning}

Please rephrase your request with more specific details.
            """
            status = "pending_input"
            next_steps = ["Clarify request", "Provide more details"]
        
        elif decision.decision_mode == DecisionMode.DENY:
            messaging = f"""
❌ DECISION: DENIED

This action cannot be performed for safety reasons.

Reason: {decision.reasoning}

Please select a different action or check authorization.
            """
            status = "completed"
            next_steps = ["Try different action", "Check permissions"]
        
        else:
            messaging = f"Unknown decision mode: {decision.decision_mode}"
            status = "error"
            next_steps = []
        
        return messaging.strip(), status, next_steps
    
    def get_session_history(self, session_id: str) -> Dict:
        """Retrieve complete session history"""
        context = self.context_manager.get_context(session_id)
        history = self.context_manager.get_history(session_id)
        
        return {
            "session_id": session_id,
            "user_id": context.user_id,
            "domain": context.domain,
            "created_at": context.created_at,
            "total_actions": len(history),
            "actions": [a.dict() for a in history[-20:]]  # Last 20
        }
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict]:
        """List all sessions for a user"""
        sessions = self.context_manager.list_user_sessions(user_id)
        return [
            {
                "session_id": s.session_id,
                "user_id": s.user_id,
                "domain": s.domain,
                "created_at": s.created_at,
                "action_count": len(self.context_manager.get_history(s.session_id))
            }
            for s in sessions
        ]
