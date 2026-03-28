"""FastAPI Application for SAINIK"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os

from config.settings import settings
from src.agent import SAINIKAgent
from src.models import (
    Theatre, MissionRequest, IntelligenceQuery, SITREPRequest,
    TacticalReminderRequest, TheatreSelection, ThreatLevel, Mission,
    SITREP, TacticalReminder, TargetDesignation, EngagementAuthorization
)

# ═════════════════════ LOGGING ═════════════════════

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SAINIK")

# ═════════════════════ GLOBAL AGENT ═════════════════════

sainik = SAINIKAgent()

# ═════════════════════ LIFESPAN ═════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("═══════════════════════════════════════════════════════════════")
    logger.info("SAINIK ONLINE — Smart AI for National Intelligence & Command")
    logger.info("═══════════════════════════════════════════════════════════════")
    yield
    logger.info("SAINIK OFFLINE")

# ═════════════════════ FASTAPI APP ═════════════════════

app = FastAPI(
    title="SAINIK",
    description="Smart AI for National Intelligence & Command",
    version="0.1.0",
    lifespan=lifespan
)

# ═════════════════════ CORS ═════════════════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═════════════════════ STATIC FILES ═════════════════════

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="frontend")

# ═════════════════════ ROUTES ═════════════════════

@app.get("/")
async def root():
    """Serve dashboard"""
    dashboard_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "SAINIK Online - Open /docs for API"}

@app.get("/api/init")
async def initialize():
    """Initialize session"""
    briefing = sainik.initialize_session()
    return {
        "status": "online",
        "briefing": briefing,
        "threat_level": sainik.threat_level.value,
        "theatre": None
    }

@app.post("/api/theatre-select")
async def select_theatre(selection: TheatreSelection):
    """Select operational theatre"""
    response = sainik.set_active_theatre(selection.theatre)
    return {
        "theatre": selection.theatre.value,
        "response": response,
        "threat_level": sainik.threat_level.value
    }

# ═════════════════════ ACTION 1: MISSION SCHEDULING ═════════════════════

@app.post("/api/mission/schedule")
async def schedule_mission(request: MissionRequest):
    """ACTION 1 — Schedule a mission"""
    mission = Mission(
        name=request.name,
        mission_type=request.mission_type,
        theatre=request.theatre,
        scheduled_time=request.scheduled_time,
        units_allocated=request.units_to_allocate,
        grid_reference=request.grid_reference
    )
    
    confirmation, mission_data = sainik.schedule_mission(mission)
    
    return {
        "status": "mission_scheduled",
        "confirmation": confirmation,
        "mission": mission_data,
        "threat_level": sainik.threat_level.value
    }

# ═════════════════════ ACTION 2: SECURE COMMUNICATIONS ═════════════════════

@app.post("/api/sitrep/draft")
async def draft_sitrep(request: SITREPRequest):
    """ACTION 2 — Draft a SITREP"""
    sitrep = SITREP(
        recipient=request.recipient,
        situation=request.situation,
        mission=request.mission,
        execution=request.execution,
        command=request.command
    )
    
    draft = sainik.draft_sitrep(sitrep)
    
    return {
        "status": "sitrep_drafted",
        "sitrep_id": sitrep.sitrep_id,
        "draft": draft
    }

@app.post("/api/sitrep/send/{sitrep_id}")
async def send_sitrep(sitrep_id: str):
    """Send approved SITREP"""
    message = sainik.send_sitrep(sitrep_id)
    return {
        "status": "sitrep_sent",
        "message": message
    }

# ═════════════════════ ACTION 3: INTELLIGENCE RETRIEVAL ═════════════════════

@app.post("/api/intelligence/search")
async def search_intelligence(query: IntelligenceQuery):
    """ACTION 3 — Retrieve intelligence"""
    reports, analysis = sainik.retrieve_intelligence(
        sector=query.sector,
        time_range=query.time_range_hours
    )
    
    formatted_reports = []
    for r in reports:
        formatted_reports.append({
            "date": r.date,
            "sector": r.sector,
            "grid": r.grid_reference,
            "threat_type": r.threat_type,
            "summary": r.summary,
            "severity": r.severity
        })
    
    return {
        "status": "intelligence_retrieved",
        "sector": query.sector,
        "count": len(formatted_reports),
        "reports": formatted_reports,
        "analysis": analysis
    }

# ═════════════════════ ACTION 4: TACTICAL REMINDERS ═════════════════════

@app.post("/api/reminder/set")
async def set_reminder(request: TacticalReminderRequest):
    """ACTION 4 — Set tactical reminder"""
    reminder = TacticalReminder(
        event=request.event,
        scheduled_time=request.scheduled_time,
        priority=request.priority
    )
    
    message = sainik.set_tactical_reminder(reminder)
    
    return {
        "status": "reminder_set",
        "reminder_id": reminder.reminder_id,
        "message": message
    }

# ═════════════════════ ACTION 5: CONTEXT BRIEFING ═════════════════════

@app.get("/api/status/briefing")
async def get_status():
    """ACTION 5 — Get operational status"""
    status = sainik.get_operational_status()
    
    return {
        "status": "briefing_provided",
        "threat_level": status.threat_level.value,
        "theatre": status.active_theatre.value if status.active_theatre else None,
        "current_mission": status.current_mission,
        "units_on_standby": status.units_on_standby,
        "pending_actions": status.pending_actions,
        "last_action": status.last_action
    }

# ═════════════════════ THREAT ESCALATION ═════════════════════

@app.post("/api/threat/escalate")
async def escalate_threat_manual(data: dict):
    """Manually escalate threat level (for demo)"""
    threat_level = ThreatLevel[data.get("level")]
    reason = data.get("reason", "Commander-initiated escalation")
    
    notification = sainik.escalate_threat(threat_level, reason)
    
    return {
        "status": "threat_escalated",
        "new_level": threat_level.value,
        "notification": notification
    }

@app.post("/api/threat/confirm-lac-crossing")
async def confirm_lac_crossing(target: TargetDesignation):
    """Confirm LAC crossing (demo scenario 3)"""
    notification = sainik.escalate_threat(
        ThreatLevel.ELEVATED,
        f"CONFIRMED LAC crossing at Grid {target.grid_reference}"
    )
    
    return {
        "status": "lac_crossing_confirmed",
        "threat_level": sainik.threat_level.value,
        "notification": notification
    }

# ═════════════════════ AMBIGUITY RESOLUTION ═════════════════════

@app.post("/api/clarify")
async def request_clarification(data: dict):
    """Request clarification for ambiguous commands"""
    issue = data.get("issue", "Ambiguous command detected")
    options = data.get("options", ["Proceed", "Cancel", "Clarify"])
    
    message = sainik.clarification_required(issue, options)
    
    return {
        "status": "clarification_required",
        "message": message
    }

# ═════════════════════ HUMAN CONFIRMATION GATE ═════════════════════

@app.post("/api/engagement/request-authorization")
async def request_engagement_authorization(target: TargetDesignation):
    """Request authorization for engagement (requires CONFIRM)"""
    # Create dummy risk assessment for the response
    from src.models import MissionRiskAssessment
    risk = MissionRiskAssessment(
        mission_name=f"Engagement at Grid {target.grid_reference}",
        personnel_risk="MEDIUM",
        mission_success_prob=75,
        collateral_concern="LOW",
        confidence_score=72,
        recommendation="PROCEED WITH CAUTION"
    )
    
    gate = sainik.require_confirmation_gate(
        f"PRECISION ENGAGEMENT at Grid {target.grid_reference}",
        risk
    )
    
    return {
        "status": "confirmation_required",
        "gate": gate,
        "requires_confirm": True
    }

@app.post("/api/engagement/authorize")
async def authorize_engagement(auth: EngagementAuthorization):
    """Authorize engagement (requires CONFIRM code)"""
    if auth.authorization_code.upper() != "CONFIRM":
        return {
            "status": "denied",
            "message": "❌ Invalid authorization code. Type CONFIRM (uppercase) to proceed."
        }
    
    message = sainik.execute_authorized_action(
        f"Precision engagement at Grid {auth.target_grid}"
    )
    
    return {
        "status": "authorized",
        "message": message,
        "threat_level": sainik.threat_level.value
    }

# ═════════════════════ AUDIT LOG ═════════════════════

@app.get("/api/audit/log")
async def get_audit_log():
    """Get complete audit trail"""
    log = sainik.get_action_log()
    summary = sainik.get_audit_summary()
    
    return {
        "status": "audit_log",
        "total_actions": len(log),
        "actions": log,
        "summary": summary
    }

# ═════════════════════ HEALTH ═════════════════════

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "online",
        "agent": "SAINIK",
        "version": settings.app_version,
        "threat_level": sainik.threat_level.value
    }

# ═════════════════════ RUN ═════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info"
    )
