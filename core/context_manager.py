"""
Context Manager Module

Purpose: Maintain session state and conversation context.
Tracks user intent, previous commands, pending confirmations, and decisions.

Storage: Supabase PostgreSQL (or in-memory for local development)
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json
import logging
import uuid

logger = logging.getLogger(__name__)

# ═════════════════════ MODELS ═════════════════════

class ActionRecord(BaseModel):
    """Record of a single action in context"""
    action_id: str
    timestamp: datetime
    command: str
    decision: str
    confidence: float
    status: str  # "pending", "executed", "failed", "cancelled"
    result: Optional[Dict[str, Any]] = None

class SessionContext(BaseModel):
    """Complete session state"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Current state
    current_intent: Optional[Dict[str, Any]] = None
    current_decision: Optional[str] = None
    pending_confirmation: Optional[Dict[str, Any]] = None
    
    # History
    action_history: List[ActionRecord] = []
    
    # Domain context
    domain: str = "generic"
    
    # Preferences
    user_preferences: Dict[str, Any] = {}
    
    # Metadata
    metadata: Dict[str, Any] = {}

# ═════════════════════ CONTEXT MANAGER ═════════════════════

class ContextManager:
    """
    Manages session context and conversation state.
    
    In-memory storage for local development.
    Supabase integration for production.
    
    Example:
        ctx = ContextManager()
        session = ctx.create_session(user_id="commander_001")
        ctx.update_context(session.session_id, intent=parsed_intent)
        context = ctx.get_context(session.session_id)
    """
    
    def __init__(self, use_supabase: bool = False, supabase_url: Optional[str] = None):
        """
        Initialize Context Manager.
        
        Args:
            use_supabase: Use Supabase backend (requires SUPABASE_URL, SUPABASE_KEY)
            supabase_url: Supabase project URL
        """
        self.use_supabase = use_supabase
        self.supabase_url = supabase_url
        
        # In-memory storage (for local development)
        self._sessions: Dict[str, SessionContext] = {}
        
        # Supabase client (initialized if needed)
        self.supabase_client = None
        if use_supabase and supabase_url:
            self._initialize_supabase()
        
        logger.info(f"ContextManager initialized (Supabase: {use_supabase})")
    
    def create_session(
        self,
        user_id: Optional[str] = None,
        domain: str = "generic"
    ) -> SessionContext:
        """
        Create a new session.
        
        Args:
            user_id: Optional user identifier
            domain: Application domain (e.g., "military", "office", "smart_home")
        
        Returns:
            New SessionContext
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        session = SessionContext(
            session_id=session_id,
            user_id=user_id,
            domain=domain
        )
        
        # Store locally
        self._sessions[session_id] = session
        
        # Store in Supabase if enabled
        if self.use_supabase:
            self._store_session_supabase(session)
        
        logger.info(f"Created session: {session_id} (user: {user_id}, domain: {domain})")
        return session
    
    def get_context(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieve session context.
        
        Args:
            session_id: Session identifier
        
        Returns:
            SessionContext or None if not found
        """
        # Try local memory first
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        # Try Supabase if enabled
        if self.use_supabase:
            return self._retrieve_session_supabase(session_id)
        
        logger.warning(f"Session not found: {session_id}")
        return None
    
    def update_context(
        self,
        session_id: str,
        **kwargs
    ) -> Optional[SessionContext]:
        """
        Update session context with new data.
        
        Args:
            session_id: Session identifier
            **kwargs: Fields to update (intent, decision, pending_confirmation, etc.)
        
        Returns:
            Updated SessionContext
        
        Example:
            ctx.update_context(
                session_id,
                current_intent=parsed_intent,
                current_decision="ask"
            )
        """
        session = self.get_context(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        # Update timestamp
        session.last_updated = datetime.utcnow()
        
        # Store updated session
        if self.use_supabase:
            self._store_session_supabase(session)
        else:
            self._sessions[session_id] = session
        
        logger.info(f"Updated session: {session_id}")
        return session
    
    def store_action(
        self,
        session_id: str,
        command: str,
        decision: str,
        confidence: float,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store action record in session history.
        
        Args:
            session_id: Session identifier
            command: User's original command
            decision: Decision made (ACT/ASK/CONFIRM/HOLD/DENY)
            confidence: Confidence score
            status: Execution status (pending/executed/failed/cancelled)
            result: Execution result
        """
        session = self.get_context(session_id)
        if not session:
            logger.error(f"Cannot store action: session not found ({session_id})")
            return
        
        action = ActionRecord(
            action_id=f"action_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow(),
            command=command,
            decision=decision,
            confidence=confidence,
            status=status,
            result=result
        )
        
        session.action_history.append(action)
        
        # Store updated session
        if self.use_supabase:
            self._store_session_supabase(session)
        else:
            self._sessions[session_id] = session
        
        logger.info(f"Stored action: {action.action_id} in session {session_id}")
    
    def get_history(self, session_id: str, limit: int = 10) -> List[ActionRecord]:
        """
        Get action history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of records to return
        
        Returns:
            List of ActionRecord
        """
        session = self.get_context(session_id)
        if not session:
            return []
        
        return session.action_history[-limit:]
    
    def set_pending_confirmation(
        self,
        session_id: str,
        action_id: str,
        description: str,
        risk_level: str = "medium"
    ) -> None:
        """
        Set an action awaiting confirmation.
        
        Args:
            session_id: Session identifier
            action_id: Action identifier
            description: Readable description of action
            risk_level: Risk level (low/medium/high/critical)
        """
        session = self.update_context(
            session_id,
            pending_confirmation={
                "action_id": action_id,
                "description": description,
                "risk_level": risk_level,
                "awaiting_since": datetime.utcnow().isoformat()
            }
        )
        logger.info(f"Pending confirmation set for action {action_id}")
    
    def clear_pending_confirmation(self, session_id: str) -> None:
        """Clear pending confirmation status"""
        self.update_context(session_id, pending_confirmation=None)
        logger.info(f"Pending confirmation cleared for session {session_id}")
    
    def list_user_sessions(self, user_id: Optional[str] = None) -> List[SessionContext]:
        """
        List all sessions for a user (or all sessions if user_id is None)
        
        Args:
            user_id: Optional user identifier to filter by
        
        Returns:
            List of SessionContext matching the filter
        """
        sessions = list(self._sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)
    
    def set_user_preference(
        self,
        session_id: str,
        preference_key: str,
        preference_value: Any
    ) -> None:
        """
        Store user preference for future decisions.
        
        Example:
            ctx.set_user_preference(
                session_id,
                "auto_confirm_safe_actions",
                True
            )
        """
        session = self.get_context(session_id)
        if not session:
            return
        
        session.user_preferences[preference_key] = preference_value
        self.update_context(session_id)
        logger.info(f"Set user preference: {preference_key} = {preference_value}")
    
    def get_user_preference(
        self,
        session_id: str,
        preference_key: str,
        default: Any = None
    ) -> Any:
        """Retrieve user preference"""
        session = self.get_context(session_id)
        if not session:
            return default
        
        return session.user_preferences.get(preference_key, default)
    
    # ═════════════════════ SUPABASE INTEGRATION ═════════════════════
    
    def _initialize_supabase(self) -> None:
        """Initialize Supabase client (stub for integration)"""
        try:
            from supabase import create_client
            key = "your_supabase_key"  # Load from env
            self.supabase_client = create_client(self.supabase_url, key)
            logger.info("Supabase client initialized")
        except ImportError:
            logger.warning("Supabase client not available. Falling back to in-memory.")
            self.use_supabase = False
    
    def _store_session_supabase(self, session: SessionContext) -> None:
        """Store session in Supabase (stub)"""
        if not self.supabase_client:
            return
        
        try:
            # Convert session to JSON for storage
            session_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "domain": session.domain,
                "context_json": session.model_dump_json(),
                "last_updated": session.last_updated.isoformat()
            }
            
            # Insert or update
            # self.supabase_client.table("sessions").upsert(session_data).execute()
            
            logger.debug(f"Stored session in Supabase: {session.session_id}")
        except Exception as e:
            logger.error(f"Failed to store session in Supabase: {e}")
    
    def _retrieve_session_supabase(self, session_id: str) -> Optional[SessionContext]:
        """Retrieve session from Supabase (stub)"""
        if not self.supabase_client:
            return None
        
        try:
            # response = self.supabase_client.table("sessions").select("*").eq("session_id", session_id).execute()
            # if response.data:
            #    context_json = response.data[0]["context_json"]
            #    return SessionContext.model_validate_json(context_json)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve session from Supabase: {e}")
            return None
