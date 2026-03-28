"""
FastAPI Application — Refactored for Generic Autonomous Action Agent

This is the unified FastAPI application that:
1. Provides unified /api/command endpoint for the generic framework
2. Maintains backward-compatible SAINIK endpoints (for military ops)
3. Supports multiple domains (military, office, smart_home, etc.)
4. Works with the core execution engine

The old SAINIK-specific code is abstracted into the military application layer.
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os
from enum import Enum
from pydantic import BaseModel
from typing import Optional

from config.settings import settings
from core.execution_engine import ExecutionEngine, ExecutionResponse

# ═════════════════════ LOGGING ═════════════════════

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SAINIK_FRAMEWORK")

# ═════════════════════ GLOBAL ENGINE ═════════════════════

engine = ExecutionEngine()

# ═════════════════════ REQUEST/RESPONSE MODELS ═════════════════════

class CommandRequest(BaseModel):
    """User command input"""
    user_input: str
    session_id: Optional[str] = None
    domain: str = "military"  # Default to military for SAINIK
    user_id: Optional[str] = None

class ConfirmationRequest(BaseModel):
    """Confirmation input"""
    execution_id: str
    session_id: str
    confirm_code: str = "CONFIRM"

class DomainEnum(str, Enum):
    """Supported domains"""
    MILITARY = "military"
    OFFICE = "office"
    SMART_HOME = "smart_home"
    GENERIC = "generic"

# ═════════════════════ LIFESPAN ═════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("╔══════════════════════════════════════════════════════════════╗")
    logger.info("║  SAINIK FRAMEWORK — Context-Aware Autonomous Action Agent    ║")
    logger.info("║  Domain-Agnostic Core with Military Operations Support       ║")
    logger.info("╚══════════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info("✓ Execution Engine initialized")
    logger.info("✓ Intent Engine ready")
    logger.info("✓ Decision Engine ready")
    logger.info("✓ Context Manager ready")
    logger.info("")
    yield
    logger.info("SAINIK FRAMEWORK OFFLINE")

# ═════════════════════ FASTAPI APP ═════════════════════

app = FastAPI(
    title="SAINIK Framework",
    description="Context-Aware Autonomous Action Agent - Unified Command Interface",
    version="0.2.0",
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

# ═════════════════════ ROOT ROUTE ═════════════════════

@app.get("/")
async def root():
    """Serve dashboard"""
    dashboard_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {
        "status": "online",
        "message": "SAINIK Framework Online",
        "api": "/docs",
        "domains": ["military", "office", "smart_home", "generic"]
    }

# ═════════════════════🔥 UNIFIED COMMAND ENDPOINT 🔥═════════════════════
# THIS IS THE MAIN ENTRY POINT FOR THE FRAMEWORK
# All natural language commands go here

@app.post("/api/command")
async def execute_command(request: CommandRequest) -> ExecutionResponse:
    """
    🔥 UNIFIED COMMAND ENDPOINT 🔥
    
    Execute any command through the autonomous action agent framework.
    
    This endpoint implements the complete pipeline:
    1. Intent Parsing (natural language → structured intent)
    2. Context Loading (session state + preferences)
    3. Decision Making (ACT / ASK / CONFIRM / HOLD / DENY)
    4. Task Planning (multi-step instruction decomposition)
    5. Execution (will call tools/execute_tool)
    6. Memory Update (store for learning)
    
    Args:
        request: CommandRequest with user_input and optional session_id, domain
    
    Returns:
        ExecutionResponse with decision, confidence, messaging, next_steps
    
    Example:
        POST /api/command
        {
            "user_input": "Schedule patrol Sector 4 tomorrow",
            "domain": "military"
        }
        
        Response:
        {
            "decision_mode": "act",
            "confidence": 0.85,
            "messaging": "✓ Patrol scheduled for Sector 4 tomorrow",
            "status": "completed"
        }
    """
    
    try:
        # Execute through full pipeline
        response = engine.execute_command(
            user_input=request.user_input,
            session_id=request.session_id,
            domain=request.domain,
            user_id=request.user_id
        )
        
        logger.info(f"Command executed: {response.decision_mode}")
        return response
    
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

# ═════════════════════ CONFIRMATION ENDPOINT ═════════════════════

@app.post("/api/confirm")
async def confirm_action(request: ConfirmationRequest) -> ExecutionResponse:
    """
    Confirm a pending action.
    
    Use this endpoint to authorize pending actions that required human confirmation.
    
    Args:
        request: ConfirmationRequest with execution_id, session_id, confirm_code
    
    Returns:
        ExecutionResponse with execution result
    
    Example:
        POST /api/confirm
        {
            "execution_id": "exec_000001",
            "session_id": "session_abc123",
            "confirm_code": "CONFIRM"
        }
    """
    
    try:
        response = engine.confirm_action(
            execution_id=request.execution_id,
            session_id=request.session_id,
            confirm_code=request.confirm_code
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Confirmation error: {e}")
        raise HTTPException(status_code=500, detail=f"Confirmation error: {str(e)}")

# ═════════════════════ SESSION MANAGEMENT ENDPOINTS ═════════════════════

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session history and context"""
    try:
        history = engine.get_session_history(session_id)
        return {
            "status": "success",
            "data": history
        }
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/sessions")
async def list_sessions(user_id: Optional[str] = None):
    """List all sessions for a user"""
    try:
        sessions = engine.list_sessions(user_id)
        return {
            "status": "success",
            "count": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail="Error listing sessions")

# ═════════════════════ HEALTH CHECK ═════════════════════

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "online",
        "agent": "SAINIK_FRAMEWORK",
        "version": "0.2.0",
        "domains": ["military", "office", "smart_home", "generic"],
        "execution_count": engine.execution_count
    }

# ═════════════════════ INFORMATION ENDPOINTS ═════════════════════

@app.get("/api/info")
async def framework_info():
    """Get framework information"""
    return {
        "name": "SAINIK Framework",
        "version": "0.2.0",
        "description": "Context-Aware Autonomous Action Agent",
        "domains": [
            {
                "name": "Military",
                "domain": "military",
                "description": "Military operations, surveillance, intelligence"
            },
            {
                "name": "Office",
                "domain": "office",
                "description": "Business tasks, meetings, schedules"
            },
            {
                "name": "Smart Home",
                "domain": "smart_home",
                "description": "Home automation, IoT devices"
            }
        ],
        "endpoints": {
            "command": "/api/command (POST) - Execute command",
            "confirm": "/api/confirm (POST) - Confirm pending action",
            "session": "/api/session/{id} (GET) - Get session history",
            "sessions": "/api/sessions (GET) - List user sessions"
        }
    }

# ═════════════════════ BACKWARD COMPATIBILITY: OLD SAINIK ENDPOINTS ═════════════════════
# These endpoints exist for backward compatibility with old SAINIK code
# They translate old-style requests to the new unified /api/command endpoint

@app.post("/api/legacy/mission/schedule")
async def legacy_schedule_mission(request: dict):
    """
    Legacy SAINIK endpoint - Schedule mission
    Translates to new framework
    """
    command = f"Schedule mission {request.get('name')} at {request.get('scheduled_time')} in {request.get('theatre')}"
    
    cmd_req = CommandRequest(
        user_input=command,
        domain="military",
        user_id=request.get('user_id')
    )
    
    return await execute_command(cmd_req)

@app.post("/api/legacy/intelligence/search")
async def legacy_search_intelligence(query: str = None, sector: str = None):
    """Legacy SAINIK endpoint - Search intelligence"""
    command = f"Search intelligence in {sector}" if sector else "Search intelligence"
    
    cmd_req = CommandRequest(
        user_input=command,
        domain="military"
    )
    
    return await execute_command(cmd_req)

@app.post("/api/legacy/sitrep/draft")
async def legacy_draft_sitrep(request: dict):
    """Legacy SAINIK endpoint - Draft SITREP"""
    command = f"Draft SITREP for {request.get('recipient')}"
    
    cmd_req = CommandRequest(
        user_input=command,
        domain="military"
    )
    
    return await execute_command(cmd_req)

# ═════════════════════ DEBUG ENDPOINTS (Development Only) ═════════════════════

@app.get("/api/debug/test")
async def debug_test():
    """Test the framework with a sample command"""
    test_input = "Schedule patrol Sector 4 tomorrow at 0800"
    
    response = engine.execute_command(
        user_input=test_input,
        domain="military"
    )
    
    return {
        "status": "debug_test",
        "input": test_input,
        "response": response.dict()
    }

# ═════════════════════ RUN APPLICATION ═════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info"
    )
