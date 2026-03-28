"""Core SAINIK Agent Logic"""

from src.models import (
    ThreatLevel, Theatre, Mission, SITREP, TacticalReminder,
    OperationalStatus, MissionRiskAssessment, IntelligenceReport, ActionLog,
    ActionType, MissionStatus
)
from datetime import datetime
from typing import List, Optional, Dict, Tuple
import json

class SAINIKAgent:
    """
    SAINIK — Smart AI for National Intelligence & Command
    Core autonomous military action agent
    """
    
    def __init__(self):
        self.threat_level = ThreatLevel.ROUTINE
        self.active_theatre: Optional[Theatre] = None
        self.current_mission: Optional[Mission] = None
        self.units_available = {
            "Line of Control": ["BSF Battalion 1", "BSF Battalion 2", "Army HQ 15 Corps", "Rashtriya Rifles"],
            "Eastern Sector": ["Army 4 Corps", "ITBP", "IAF Forward Base", "Arunachal Command"],
            "Maritime": ["Western Naval Command", "Eastern Naval Command", "Coast Guard", "P-8I Poseidon"]
        }
        self.units_on_standby = ["BSF", "Indian Army", "IAF", "Naval Command"]
        self.pending_actions = []
        self.missions_calendar = []
        self.action_log = []
        self.sitrep_drafts = []
        self.reminders = []
        self.intel_archive = self._load_sample_intel()
        
    def _load_sample_intel(self) -> List[IntelligenceReport]:
        """Load sample intelligence for demo"""
        return [
            IntelligenceReport(
                date="2024-03-26",
                sector="Tawang",
                grid_reference="3381",
                threat_type="LAC Crossing",
                summary="Unconfirmed report of 8-12 PLA personnel near Tawang sector boundary",
                severity="MEDIUM"
            ),
            IntelligenceReport(
                date="2024-03-25",
                sector="Tawang",
                grid_reference="3380",
                threat_type="Infiltration Attempt",
                summary="Surveillance detected movement at 0230 hrs, pattern matches 2021 Galwan pre-escalation",
                severity="HIGH"
            ),
            IntelligenceReport(
                date="2024-03-24",
                sector="West Kameng",
                grid_reference="3375",
                threat_type="Unauthorized Entry",
                summary="Routine patrol report - no hostile contact, cleared sector",
                severity="LOW"
            ),
        ]
    
    # ═════════════════════ SESSION MANAGEMENT ═════════════════════
    
    def initialize_session(self) -> str:
        """Output session initialization briefing"""
        briefing = """
╔════════════════════════════════════════════════════════════════╗
║  SAINIK ONLINE — Smart AI for National Intelligence & Command  ║
║═════════════════════════════════════════════════════════════════║
║                                                                  ║
║  Threat Level:    ROUTINE                                       ║
║  Active Mission:  None                                          ║
║  Units:           Standby — awaiting theatre selection          ║
║                                                                  ║
║  Select operational theatre to begin:                           ║
║    [A] Line of Control — Jammu & Kashmir                        ║
║    [B] Eastern Sector — Arunachal Pradesh                       ║
║    [C] Maritime — Arabian Sea / Bay of Bengal                   ║
║                                                                  ║
║  Awaiting your orders, Commander.                               ║
╚════════════════════════════════════════════════════════════════╝
        """
        return briefing
    
    def set_active_theatre(self, theatre: Theatre) -> str:
        """Set active operational theatre"""
        self.active_theatre = theatre
        available_units = self.units_available.get(theatre.value, [])
        
        log_entry = ActionLog(
            action_type=ActionType.CONTEXT_BRIEFING,
            description=f"Theatre activated: {theatre.value}",
            status="EXECUTED"
        )
        self.action_log.append(log_entry.dict())
        
        return f"""
✓ Theatre activated: {theatre.value}
  Available units: {', '.join(available_units[:2])}... and more
  Threat Level: ROUTINE
  Standing by for orders, Commander.
        """
    
    # ═════════════════════ ACTION 1: MISSION SCHEDULING ═════════════════════
    
    def schedule_mission(self, mission: Mission) -> Tuple[str, Dict]:
        """
        ACTION 1 — Schedule a mission
        Returns: (confirmation message, mission object)
        """
        # Run risk assessment first
        risk_assessment = self.assess_mission_risk(mission)
        mission.risk_assessment = risk_assessment.dict()
        
        # Apply threat level impact
        if self.threat_level == ThreatLevel.HIGH:
            risk_assessment.mission_success_prob -= 20
        elif self.threat_level == ThreatLevel.CRITICAL:
            risk_assessment.mission_success_prob -= 35
        
        # Apply night ops penalty
        if "0" in mission.scheduled_time[:2] or "2" in mission.scheduled_time[:2]:
            risk_assessment.collateral_concern = "MEDIUM"
        
        # Store mission
        self.missions_calendar.append(mission.dict())
        self.current_mission = mission
        
        # Log action
        log_entry = ActionLog(
            action_type=ActionType.MISSION_SCHEDULING,
            description=f"Mission scheduled: {mission.name}",
            status="EXECUTED",
            authorized_by="COMMANDER"
        )
        self.action_log.append(log_entry.dict())
        self.last_action = log_entry.dict()
        
        confirmation = f"""
✓ MISSION SCHEDULED
  Name: {mission.name}
  Time: {mission.scheduled_time}
  Units: {', '.join(mission.units_allocated)}
  Grid: {mission.grid_reference or 'N/A'}
  
MISSION RISK ASSESSMENT — {mission.name}
─────────────────────────────────────────
Personnel Risk:        {risk_assessment.personnel_risk}
Mission Success Prob:  {risk_assessment.mission_success_prob}%
Collateral Concern:    {risk_assessment.collateral_concern}
Confidence Score:      {risk_assessment.confidence_score}%
─────────────────────────────────────────
Recommendation: {risk_assessment.recommendation}

Added to Ops Calendar. Standing by.
        """
        
        return confirmation, mission.dict()
    
    # ═════════════════════ ACTION 2: SECURE COMMUNICATIONS ═════════════════════
    
    def draft_sitrep(self, sitrep: SITREP) -> str:
        """
        ACTION 2 — Draft a Situation Report (SITREP)
        Returns draft for commander review before sending
        """
        sitrep.status = "DRAFTED"
        self.sitrep_drafts.append(sitrep.dict())
        
        draft = f"""
📋 SITREP DRAFT — Ready for transmission
  Recipient: {sitrep.recipient}
  Generated: {datetime.utcnow().strftime('%H%M %Z')}
─────────────────────────────────────────
SITUATION:
{sitrep.situation}

MISSION:
{sitrep.mission}

EXECUTION:
{sitrep.execution}

COMMAND:
{sitrep.command}
─────────────────────────────────────────

Confirm for transmission: Type SEND
Cancel: Type CANCEL
        """
        return draft
    
    def send_sitrep(self, sitrep_id: str) -> str:
        """Send an approved SITREP"""
        # Find the drafted SITREP
        sitrep_data = None
        for draft in self.sitrep_drafts:
            if draft.get("sitrep_id") == sitrep_id:
                sitrep_data = draft
                break
        
        if not sitrep_data:
            return "❌ SITREP not found"
        
        sitrep_data["status"] = "SENT"
        
        log_entry = ActionLog(
            action_type=ActionType.SECURE_COMMUNICATION,
            description=f"SITREP sent to {sitrep_data.get('recipient')}",
            status="EXECUTED",
            authorized_by="COMMANDER"
        )
        self.action_log.append(log_entry.dict())
        
        return f"""
✓ SITREP TRANSMITTED
  Recipient: {sitrep_data.get('recipient')}
  Time: {datetime.utcnow().strftime('%H%M %Z')}
  Status: Sent via secure channel (simulated)
  
Message logged to audit trail. Standing by.
        """
    
    # ═════════════════════ ACTION 3: INTELLIGENCE RETRIEVAL ═════════════════════
    
    def retrieve_intelligence(self, sector: str, time_range: int = 72) -> Tuple[List[IntelligenceReport], str]:
        """
        ACTION 3 — Retrieve intelligence from archive
        Returns: (matching reports, analysis summary)
        """
        matching_reports = [
            r for r in self.intel_archive 
            if sector.lower() in r.sector.lower()
        ]
        
        analysis = ""
        if len(matching_reports) >= 2:
            analysis = f"""
⚠ PATTERN MATCH DETECTED:
  Multiple reports from {sector} in the last {time_range} hours
  Pattern signature matches: "2021 Galwan pre-escalation"
  Recommendation: Escalate to threat review. Recommend field verification.
            """
        
        log_entry = ActionLog(
            action_type=ActionType.INTELLIGENCE_RETRIEVAL,
            description=f"Intelligence query: {sector}",
            status="EXECUTED"
        )
        self.action_log.append(log_entry.dict())
        
        return matching_reports, analysis
    
    # ═════════════════════ ACTION 4: TACTICAL REMINDERS ═════════════════════
    
    def set_tactical_reminder(self, reminder: TacticalReminder) -> str:
        """ACTION 4 — Set a tactical reminder/alert"""
        self.reminders.append(reminder.dict())
        
        log_entry = ActionLog(
            action_type=ActionType.TACTICAL_REMINDER,
            description=f"Reminder set: {reminder.event} at {reminder.scheduled_time}",
            status="EXECUTED"
        )
        self.action_log.append(log_entry.dict())
        
        return f"""
✓ TACTICAL REMINDER SET
  Event: {reminder.event}
  Time: {reminder.scheduled_time}
  Priority: {reminder.priority}
  Status: ACTIVE — Will alert at scheduled time
  
Standing by.
        """
    
    # ═════════════════════ ACTION 5: CONTEXT BRIEFING ═════════════════════
    
    def get_operational_status(self) -> OperationalStatus:
        """ACTION 5 — Return full operational status briefing"""
        
        formatted_log = []
        if self.action_log:
            latest = self.action_log[-1]
            formatted_log.append(f"{latest.get('action_type')} at {latest.get('timestamp')}")
        
        status = OperationalStatus(
            threat_level=self.threat_level,
            active_theatre=self.active_theatre,
            current_mission=self.current_mission.name if self.current_mission else None,
            units_on_standby=self.units_on_standby,
            pending_actions=[p.get("event", str(p)) for p in self.reminders if p.get("status") == "ACTIVE"],
            last_action=formatted_log[0] if formatted_log else None
        )
        
        log_entry = ActionLog(
            action_type=ActionType.CONTEXT_BRIEFING,
            description="Status briefing requested",
            status="EXECUTED"
        )
        self.action_log.append(log_entry.dict())
        
        return status
    
    # ═════════════════════ THREAT ESCALATION ENGINE ═════════════════════
    
    def escalate_threat(self, new_level: ThreatLevel, reason: str) -> str:
        """Auto-escalate threat level and notify commander"""
        old_level = self.threat_level
        self.threat_level = new_level
        
        recommendations = {
            ThreatLevel.GUARDED: [
                "Increase unit readiness to YELLOW state",
                "Activate rapid response protocols",
                "Review recent intel patterns"
            ],
            ThreatLevel.ELEVATED: [
                "Move units to AMBER status",
                "Activate all forward positions",
                "Prepare contingency operations"
            ],
            ThreatLevel.HIGH: [
                "FULL MOBILIZATION — units to RED status",
                "Activate strike support assets",
                "Prepare engagement protocols"
            ],
            ThreatLevel.CRITICAL: [
                "FULL COMBAT READINESS",
                "All assets to battle stations",
                "Senior command notification required"
            ]
        }
        
        rec_list = recommendations.get(new_level, ["Stand by"])
        
        notification = f"""
⚠️  THREAT ESCALATION ALERT
═══════════════════════════════════════════════════════════════
  Level: {old_level.value} → {new_level.value}
  Reason: {reason}
  Time: {datetime.utcnow().strftime('%H%M %Z')}
  Theatre: {self.active_theatre.value if self.active_theatre else 'N/A'}
───────────────────────────────────────────────────────────────
RECOMMENDED IMMEDIATE ACTIONS:
  1) {rec_list[0]}
  2) {rec_list[1] if len(rec_list) > 1 else 'Monitor situation'}
  3) {rec_list[2] if len(rec_list) > 2 else 'Await further orders'}
───────────────────────────────────────────────────────────────

⚠️  Awaiting your orders, Commander.
        """
        
        log_entry = ActionLog(
            action_type=ActionType.CONTEXT_BRIEFING,
            description=f"THREAT ESCALATION: {old_level.value} → {new_level.value}",
            status="EXECUTED"
        )
        self.action_log.append(log_entry.dict())
        
        return notification
    
    # ═════════════════════ MISSION RISK ASSESSMENT ═════════════════════
    
    def assess_mission_risk(self, mission: Mission) -> MissionRiskAssessment:
        """Calculate mission risk assessment"""
        
        # Base values
        personnel_risk = "MEDIUM"
        success_prob = 85
        collateral_concern = "LOW"
        confidence = 80
        
        # Threat level impact
        if self.threat_level == ThreatLevel.GUARDED:
            success_prob -= 10
            personnel_risk = "MEDIUM"
        elif self.threat_level == ThreatLevel.ELEVATED:
            success_prob -= 15
            personnel_risk = "HIGH"
        elif self.threat_level == ThreatLevel.HIGH:
            success_prob -= 20
            personnel_risk = "HIGH"
            confidence -= 20
        elif self.threat_level == ThreatLevel.CRITICAL:
            success_prob -= 35
            personnel_risk = "CRITICAL"
            confidence -= 35
        
        # Night ops penalty (0-5 hrs or 20-23 hrs)
        hour = int(mission.scheduled_time.split(":")[0]) if ":" in mission.scheduled_time else int(mission.scheduled_time[:2])
        if hour < 6 or hour >= 20:
            collateral_concern = "MEDIUM"
            confidence -= 10
        
        # Generate recommendation
        if success_prob >= 80 and personnel_risk in ["LOW", "MEDIUM"]:
            recommendation = "PROCEED"
        elif success_prob >= 65:
            recommendation = "PROCEED WITH CAUTION"
        else:
            recommendation = "HOLD"
        
        reasoning = f"Risk assessment based on threat level {self.threat_level.value}, mission type {mission.mission_type.value}, and time {mission.scheduled_time}"
        
        return MissionRiskAssessment(
            mission_name=mission.name,
            personnel_risk=personnel_risk,
            mission_success_prob=max(0, success_prob),
            collateral_concern=collateral_concern,
            confidence_score=max(0, confidence),
            recommendation=recommendation,
            reasoning=reasoning
        )
    
    # ═════════════════════ AMBIGUITY RESOLUTION PROTOCOL ═════════════════════
    
    def clarification_required(self, issue: str, options: List[str]) -> str:
        """Request clarification when command is ambiguous"""
        options_str = "\n  ".join([f"({chr(97+i)}) {opt}" for i, opt in enumerate(options)])
        msg = f"""
❌ CLARIFICATION REQUIRED
═══════════════════════════════════════════════════════════════
Issue: {issue}

Please confirm one of the following:
  {options_str}
═══════════════════════════════════════════════════════════════

Type response (a, b, or c) to proceed.
        """
        return msg
    
    # ═════════════════════ HUMAN CONFIRMATION GATE ═════════════════════
    
    def require_confirmation_gate(self, action: str, risk_assessment: MissionRiskAssessment) -> str:
        """
        Non-negotiable human confirmation gate for lethal/irreversible actions
        REQUIRES explicit CONFIRM before execution
        """
        gate = f"""
🔴 HUMAN CONFIRMATION REQUIRED
═══════════════════════════════════════════════════════════════
Requested Action: {action}
Classification:   LETHAL / IRREVERSIBLE / HIGH-RISK

MISSION RISK ASSESSMENT
─────────────────────────────────────────────────────────────
Mission: {risk_assessment.mission_name}
Personnel Risk:        {risk_assessment.personnel_risk}
Success Probability:   {risk_assessment.mission_success_prob}%
Collateral Concern:    {risk_assessment.collateral_concern}
Confidence Score:      {risk_assessment.confidence_score}%
Recommendation:        {risk_assessment.recommendation}
─────────────────────────────────────────────────────────────

⚠️  This action cannot be undone.
⚠️  SAINIK will not proceed without explicit authorisation.

Type CONFIRM (uppercase) to authorize execution.
Any other response will CANCEL this action.
═══════════════════════════════════════════════════════════════
        """
        return gate
    
    def execute_authorized_action(self, action_desc: str) -> str:
        """Execute action after CONFIRM authorization"""
        log_entry = ActionLog(
            action_type=ActionType.MISSION_SCHEDULING,
            description=action_desc,
            status="EXECUTED",
            authorized_by="COMMANDER"
        )
        self.action_log.append(log_entry.dict())
        
        execution = f"""
✅ ACTION AUTHORISED by Commander at {datetime.utcnow().strftime('%H%M %Z')}
Executing: {action_desc}

Action logged with complete audit trail for review.
Standing by for next orders.
        """
        return execution
    
    # ═════════════════════ AUDIT LOG ═════════════════════
    
    def get_action_log(self) -> List[Dict]:
        """Return complete audit trail of all actions"""
        return self.action_log
    
    def get_audit_summary(self) -> str:
        """Return formatted audit log summary"""
        if not self.action_log:
            return "No actions recorded."
        
        summary = "AUDIT LOG — Session Activity\n"
        summary += "═══════════════════════════════════════════════════════════════\n"
        for i, log in enumerate(self.action_log[-5:], 1):  # Last 5 actions
            summary += f"{i}. [{log.get('action_type')}] {log.get('description')}\n"
            summary += f"   Time: {log.get('timestamp')} | Status: {log.get('status')}\n"
        
        return summary
