"""Pydantic models for SAINIK"""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

# ═══════════════════════ ENUMS ═══════════════════════

class ThreatLevel(str, Enum):
    ROUTINE = "ROUTINE"
    GUARDED = "GUARDED"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Theatre(str, Enum):
    LOC = "Line of Control"
    EASTERN = "Eastern Sector"
    MARITIME = "Maritime"

class MissionType(str, Enum):
    PATROL = "PATROL"
    SURVEILLANCE = "SURVEILLANCE"
    DRILL = "DRILL"
    STRIKE_SUPPORT = "STRIKE_SUPPORT"
    RECONNAISSANCE = "RECONNAISSANCE"
    ENGAGEMENT = "ENGAGEMENT"

class ActionType(str, Enum):
    MISSION_SCHEDULING = "MISSION_SCHEDULING"
    SECURE_COMMUNICATION = "SECURE_COMMUNICATION"
    INTELLIGENCE_RETRIEVAL = "INTELLIGENCE_RETRIEVAL"
    TACTICAL_REMINDER = "TACTICAL_REMINDER"
    CONTEXT_BRIEFING = "CONTEXT_BRIEFING"

class MissionStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"

# ═══════════════════════ REQUEST/RESPONSE MODELS ═══════════════════════

class MissionRequest(BaseModel):
    """Mission scheduling request"""
    name: str
    mission_type: MissionType
    theatre: Theatre
    scheduled_time: str  # Military time: "0330 hrs"
    units_to_allocate: List[str]
    grid_reference: Optional[str] = None
    description: Optional[str] = None

class IntelligenceQuery(BaseModel):
    """Intelligence retrieval request"""
    sector: str
    threat_type: Optional[str] = None
    time_range_hours: int = 72  # Default 72 hours
    search_keywords: Optional[List[str]] = None

class SITREPRequest(BaseModel):
    """SITREP (Situation Report) request"""
    recipient: str  # E.g., "Eastern Command", "Battalion HQ"
    situation: str
    mission: str
    execution: str
    command: str

class TargetDesignation(BaseModel):
    """Target designation for engagement"""
    grid_reference: str
    target_type: str
    priority_level: str  # LOW, MEDIUM, HIGH, CRITICAL

class EngagementAuthorization(BaseModel):
    """Engagement authorization (requires CONFIRM)"""
    target_grid: str
    engagement_type: str  # PRECISION_STRIKE, SUPPORT_FIRE, etc.
    authorization_code: str = "CONFIRM"

class TacticalReminderRequest(BaseModel):
    """Tactical reminder request"""
    event: str
    scheduled_time: str  # Military time
    priority: str  # CRITICAL, HIGH, ROUTINE

class TheatreSelection(BaseModel):
    """Theatre selection at session start"""
    theatre: Theatre

# ═══════════════════════ DATA MODELS ═══════════════════════

class Mission(BaseModel):
    """Mission object"""
    mission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    mission_type: MissionType
    theatre: Theatre
    scheduled_time: str
    units_allocated: List[str]
    grid_reference: Optional[str] = None
    status: MissionStatus = MissionStatus.SCHEDULED
    risk_assessment: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "COMMANDER"

class IntelligenceReport(BaseModel):
    """Intelligence entry"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str
    sector: str
    grid_reference: str
    threat_type: str
    summary: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL

class SITREP(BaseModel):
    """Situation Report"""
    sitrep_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient: str
    situation: str
    mission: str
    execution: str
    command: str
    status: str = "DRAFTED"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TacticalReminder(BaseModel):
    """Tactical reminder"""
    reminder_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event: str
    scheduled_time: str
    priority: str
    status: str = "ACTIVE"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OperationalStatus(BaseModel):
    """Current operational status"""
    threat_level: ThreatLevel
    active_theatre: Optional[Theatre] = None
    current_mission: Optional[str] = None
    units_on_standby: List[str]
    pending_actions: List[dict]
    last_action: Optional[str] = None
    last_update: datetime = Field(default_factory=datetime.utcnow)

class MissionRiskAssessment(BaseModel):
    """Mission risk assessment"""
    mission_name: str
    personnel_risk: str  # LOW, MEDIUM, HIGH, CRITICAL
    mission_success_prob: int = Field(ge=0, le=100)  # 0-100%
    collateral_concern: str  # LOW, MEDIUM, HIGH
    confidence_score: int = Field(ge=0, le=100)  # 0-100%
    recommendation: str  # PROCEED, PROCEED WITH CAUTION, HOLD
    reasoning: Optional[str] = None

class ActionLog(BaseModel):
    """Action audit log entry"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action_type: ActionType
    description: str
    actor: str = "SAINIK"
    authorized_by: Optional[str] = None
    status: str  # PENDING, EXECUTED, REJECTED
