"""
Decision Engine Module

Purpose: CORE INNOVATION - Decide when to ACT, ASK, CONFIRM, or HOLD.
This is the intelligence layer that makes the agent autonomous.

Architecture: Domain-agnostic decision framework.
"""

from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# ═════════════════════ DECISION MODES ═════════════════════

class DecisionMode(str, Enum):
    """
    Core decision modes for autonomous agents.
    
    ACT:     Clear, safe, executable action - proceed immediately
    ASK:     Missing critical parameters - clarify before proceeding
    CONFIRM: High-risk/sensitive action - require human approval
    HOLD:    Low confidence or conflicting data - wait for verification
    DENY:    Unsafe action detected - refuse execution
    """
    ACT = "act"           # Execute immediately
    ASK = "ask"           # Ask for clarification
    CONFIRM = "confirm"   # Require human confirmation
    HOLD = "hold"         # Wait for verification
    DENY = "deny"         # Refuse to execute

class RiskLevel(str, Enum):
    """Risk assessment levels"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ═════════════════════ MODELS ═════════════════════

class SafetyCheck(BaseModel):
    """Safety validation result"""
    is_safe: bool
    risk_level: RiskLevel
    warnings: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)

class DecisionResult(BaseModel):
    """Decision engine output"""
    decision_mode: DecisionMode
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    requires_clarification: List[str] = []
    risk_assessment: Optional[SafetyCheck] = None
    recommended_questions: List[str] = []
    next_steps: List[str] = []

# ═════════════════════ DECISION ENGINE ═════════════════════

class DecisionEngine:
    """
    Makes autonomous decisions: ACT, ASK, CONFIRM, HOLD, or DENY.
    
    Rules:
    1. Missing critical fields → ASK
    2. High risk + sensitive action → CONFIRM
    3. Confidence < 70% → CONFIRM or HOLD
    4. Unsafe patterns detected → DENY
    5. All good + confidence > 75% → ACT
    
    Example:
        Command: "Schedule patrol tomorrow"
        Missing: location/sector
        Decision: ASK "Which sector?"
        
        Command: "Schedule patrol Sector 4 tomorrow"
        Missing: none
        Confidence: 85%
        Decision: ACT
    """
    
    # Configuration thresholds
    CONFIDENCE_ACT_THRESHOLD = 0.75      # Need 75%+ to ACT
    CONFIDENCE_CONFIRM_THRESHOLD = 0.70  # 70-75% requires CONFIRM
    CONFIDENCE_HOLD_THRESHOLD = 0.50     # Below 50% → HOLD
    
    # Risk keywords that trigger CONFIRM
    SENSITIVE_KEYWORDS = {
        "delete", "critical", "emergency", "immediate",
        "send alert", "engagement", "strike", "breach",
        "irreversible", "fire", "launch", "authorize"
    }
    
    # Safety rule violations
    UNSAFE_PATTERNS = {
        "no_human_review",
        "irreversible_without_confirm",
        "critical_risk_no_check"
    }
    
    def __init__(self):
        """Initialize Decision Engine"""
        self.decision_counter = 0
    
    def decide(
        self,
        intent: Any,  # Intent object from intent_engine
        context: Optional[Dict[str, Any]] = None,
        safety_check: Optional[SafetyCheck] = None,
        risk_level: str = "low",
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> DecisionResult:
        """
        Make autonomous decision: ACT, ASK, CONFIRM, HOLD, or DENY.
        
        Args:
            intent: Parsed intent from IntentEngine
            context: Session context
            safety_check: Pre-computed safety check
            risk_level: Task risk level
            user_preferences: User's preferred thresholds
        
        Returns:
            DecisionResult with decision mode and reasoning
        """
        self.decision_counter += 1
        decision_id = f"decision_{self.decision_counter}"
        
        logger.info(f"[{decision_id}] Making decision for intent: {intent.intent_type}")
        
        # Step 1: Check for missing fields
        has_missing_fields = bool(intent.missing_fields)
        
        # Step 2: Assess risk
        risk_assessment = safety_check or self._assess_risk(intent, risk_level)
        
        # Step 3: Check confidence
        confidence = intent.confidence if hasattr(intent, 'confidence') else 0.5
        
        # Step 4: Detect sensitive keywords
        is_sensitive = self._is_sensitive_action(intent)
        
        # Step 5: Apply decision rules
        decision_mode, reasoning, next_steps = self._apply_decision_rules(
            has_missing_fields=has_missing_fields,
            confidence=confidence,
            risk_level=risk_assessment.risk_level,
            is_sensitive=is_sensitive,
            intent=intent
        )
        
        logger.info(f"[{decision_id}] Decision: {decision_mode.value} (confidence: {confidence:.0%})")
        
        # Step 6: Generate recommended questions if ASK
        recommended_questions = []
        if decision_mode == DecisionMode.ASK:
            recommended_questions = self._generate_clarification_questions(intent)
        
        return DecisionResult(
            decision_mode=decision_mode,
            confidence=confidence,
            reasoning=reasoning,
            requires_clarification=intent.missing_fields,
            risk_assessment=risk_assessment,
            recommended_questions=recommended_questions,
            next_steps=next_steps
        )
    
    def _assess_risk(self, intent: Any, risk_level: str) -> SafetyCheck:
        """
        Assess risk of executing the intent.
        
        Checks:
        - Irreversible actions
        - Sensitive operations
        - Dangerous keywords
        - System impact
        """
        warnings = []
        risk_enum = RiskLevel(risk_level)
        is_safe = risk_enum not in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # Check for dangerous patterns
        raw_input = intent.raw_input.lower() if hasattr(intent, 'raw_input') else ""
        
        if any(kw in raw_input for kw in ["delete", "remove", "clear"]):
            warnings.append("⚠️  Irreversible action detected (delete/remove)")
            is_safe = False
        
        if any(kw in raw_input for kw in ["all", "everyone", "system-wide"]):
            warnings.append("⚠️  Broad scope action - affects multiple targets")
            is_safe = False
        
        confidence = 0.9 if is_safe else 0.6
        
        return SafetyCheck(
            is_safe=is_safe,
            risk_level=risk_enum,
            warnings=warnings,
            confidence=confidence
        )
    
    def _is_sensitive_action(self, intent: Any) -> bool:
        """Check if action involves sensitive operations"""
        raw_input = intent.raw_input.lower() if hasattr(intent, 'raw_input') else ""
        return any(kw in raw_input for kw in self.SENSITIVE_KEYWORDS)
    
    def _apply_decision_rules(
        self,
        has_missing_fields: bool,
        confidence: float,
        risk_level: RiskLevel,
        is_sensitive: bool,
        intent: Any
    ) -> Tuple[DecisionMode, str, List[str]]:
        """
        Apply decision rules to determine action.
        
        Decision Tree:
        1. If missing fields → ASK
        2. If unsafe → DENY
        3. If high risk + sensitive → CONFIRM
        4. If confidence < 70% → CONFIRM or HOLD
        5. If confidence >= 75% → ACT
        """
        
        # Rule 1: Missing fields → ASK
        if has_missing_fields:
            reasoning = f"Missing required information: {', '.join(intent.missing_fields)}"
            return DecisionMode.ASK, reasoning, ["Request user to provide missing fields"]
        
        # Rule 2: Unsafe detected → DENY
        if risk_level == RiskLevel.CRITICAL:
            reasoning = "Critical risk detected - action is unsafe"
            return DecisionMode.DENY, reasoning, ["Refuse execution", "Log security event"]
        
        # Rule 3: High risk + sensitive → CONFIRM
        if risk_level == RiskLevel.HIGH and is_sensitive:
            reasoning = f"Sensitive high-risk action detected. Confidence: {confidence:.0%}"
            return DecisionMode.CONFIRM, reasoning, ["Show confirmation gate", "Require CONFIRM code"]
        
        # Rule 4: Medium confidence → CONFIRM or HOLD
        if confidence < self.CONFIDENCE_ACT_THRESHOLD:
            if confidence < self.CONFIDENCE_HOLD_THRESHOLD:
                reasoning = f"Low confidence in interpretation ({confidence:.0%}). Awaiting verification."
                return DecisionMode.HOLD, reasoning, ["Wait for user confirmation", "Provide context"]
            else:
                reasoning = f"Moderate confidence ({confidence:.0%}). Require explicit approval."
                return DecisionMode.CONFIRM, reasoning, ["Show confirmation gate"]
        
        # Rule 5: High confidence + safe → ACT
        reasoning = f"All conditions met. Confidence: {confidence:.0%}. Ready to execute."
        return DecisionMode.ACT, reasoning, ["Execute task", "Log action", "Return result"]
    
    def _generate_clarification_questions(self, intent: Any) -> List[str]:
        """
        Generate specific clarification questions.
        
        Rule: Ask ONE specific question at a time, not vague open questions.
        
        Example:
            Missing: ["location", "time"]
            Question: "Which location? (Sector 1, Sector 2, ...)" ← GOOD
            NOT: "What location?" ← BAD
        """
        questions = []
        
        for missing_field in intent.missing_fields:
            if missing_field == "scheduled_time":
                questions.append(
                    "When should this happen? "
                    "(e.g., 'tomorrow', '0400 hrs', 'next week')"
                )
            elif missing_field == "target_location":
                questions.append(
                    "Where? "
                    "(e.g., 'Sector 4', 'Grid 3381', 'Eastern Sector')"
                )
            elif missing_field == "recipient":
                questions.append(
                    "Who should receive this? "
                    "(e.g., 'Eastern Command', 'Battalion HQ', 'Team A')"
                )
            elif missing_field == "message_content":
                questions.append(
                    "What should the message contain? "
                    "(e.g., 'Situation report', 'Alert message')"
                )
            elif missing_field == "reminder_target":
                questions.append(
                    "Who or what should be reminded? "
                    "(e.g., 'Commander', 'Team', 'System')"
                )
            elif missing_field == "action":
                questions.append(
                    "What action specifically? "
                    "(e.g., 'patrol', 'surveillance', 'alert')"
                )
        
        return questions[:3]  # Ask max 3 questions at once
    
    def override_decision(
        self,
        original_decision: DecisionResult,
        override_mode: DecisionMode,
        reason: str
    ) -> DecisionResult:
        """
        Allow human override of automated decision.
        
        Example:
            Original decision: ASK (missing location)
            Human: "Never ask for location, always default to Sector 1"
            New decision: ACT (with location="Sector 1")
        """
        logger.warning(f"Decision override: {original_decision.decision_mode.value} → {override_mode.value}")
        
        original_decision.decision_mode = override_mode
        original_decision.reasoning = f"[OVERRIDE] {reason}"
        
        return original_decision
