from __future__ import annotations

from datetime import datetime
import re
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from intel_archive import search_intel
from state_manager import add_audit, get_session, update_threat

load_dotenv()

app = FastAPI(title="SAINIK Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIV = "â”€" * 42

THEATRE_UNITS = {
    "LOC": ["BSF battalions", "Indian Army (15 Corps)", "Rashtriya Rifles"],
    "EASTERN": ["Indian Army (4 Corps)", "ITBP", "IAF forward bases"],
    "MARITIME": ["Western Naval Command", "Eastern Naval Command", "Coast Guard", "P-8I Poseidon"],
}

THEATRE_LABELS = {
    "LOC": "Line of Control â€” J&K",
    "EASTERN": "Eastern Sector â€” Arunachal Pradesh",
    "MARITIME": "Maritime â€” Arabian Sea / Bay of Bengal",
}


class TheatreRequest(BaseModel):
    session_id: str
    theatre: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


def now_hhmm() -> str:
    return datetime.now().strftime("%H%M HRS")


def normalize_theatre(value: str) -> str:
    val = value.strip().upper()
    if val in ("LOC", "LINE", "LINE OF CONTROL"):
        return "LOC"
    if val in ("EAST", "EASTERN", "EASTERN SECTOR"):
        return "EASTERN"
    if val in ("SEA", "MARITIME", "NAVAL"):
        return "MARITIME"
    return val


def extract_time(text: str) -> Optional[str]:
    match = re.search(r"\b(\d{3,4})\s*(?:hrs?|h)\b", text, re.IGNORECASE)
    if not match:
        match = re.search(r"\b(\d{3,4})\b", text)
    if not match:
        return None
    raw = match.group(1)
    if len(raw) == 3:
        raw = "0" + raw
    return raw


def is_night_operation(hhmm: Optional[str]) -> bool:
    if not hhmm or len(hhmm) != 4:
        return False
    hour = int(hhmm[:2])
    return hour >= 20 or hour < 6


def bump_risk(level: str) -> str:
    tiers = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    if level not in tiers:
        return "MEDIUM"
    idx = min(tiers.index(level) + 1, len(tiers) - 1)
    return tiers[idx]


def build_risk_assessment(mission_name: str, state: dict, op_time: Optional[str], has_intel: bool) -> str:
    personnel_risk = "LOW"
    success_prob = 85
    collateral = "LOW"
    confidence = 80

    if state.get("threat_level") in ("HIGH", "CRITICAL"):
        success_prob -= 20

    theatre = state.get("theatre")
    total_units = len(THEATRE_UNITS.get(theatre, []))
    if total_units and len(state.get("units", [])) < max(1, total_units // 2):
        personnel_risk = bump_risk(personnel_risk)

    if not has_intel:
        confidence -= 30

    if is_night_operation(op_time):
        collateral = bump_risk(collateral)

    recommendation = "PROCEED"
    if personnel_risk in ("HIGH", "CRITICAL") or confidence < 50:
        recommendation = "PROCEED WITH CAUTION"

    return (
        f"MISSION RISK ASSESSMENT â€” {mission_name}\n"
        f"{DIV}\n"
        f"Personnel Risk:        {personnel_risk}\n"
        f"Mission Success Prob:  {max(0, success_prob)}%\n"
        f"Collateral Concern:    {collateral}\n"
        f"Confidence Score:      {max(0, confidence)}%\n"
        f"{DIV}\n"
        f"Recommendation: {recommendation}"
    )


def build_status_brief(state: dict) -> str:
    return (
        "OPERATIONAL STATUS BRIEF\n"
        f"{DIV}\n"
        f"THREAT LEVEL:     {state.get('threat_level')}\n"
        f"ACTIVE THEATRE:   {state.get('theatre') or 'Not selected'}\n"
        f"ACTIVE MISSION:   {state.get('active_mission') or 'None'}\n"
        f"UNITS ON STANDBY: {', '.join(state.get('units') or []) or 'None'}\n"
        f"PENDING ACTIONS:  {'Awaiting confirmation' if state.get('pending_confirmation') else 'None'}\n"
        f"LAST ACTION:      {state.get('audit_log', [])[-1]['action'] if state.get('audit_log') else 'None'}\n"
        f"{DIV}\n"
        "Awaiting your orders, Commander."
    )


def build_intel_retrieval(query: str) -> str:
    results = search_intel(query)
    blocks = []
    for item in results:
        blocks.append(
            f"{item['id']} | {item['date']} | {item['sector']}\n"
            f"Type: {item['type']}\n"
            f"Summary: {item['summary']}\n"
            f"Threat Contribution: {item['threat_contribution']}\n"
            f"Source: {item['source']}\n"
        )
    pattern_line = ""
    if any(item["threat_contribution"] in ("HIGH", "CRITICAL") for item in results):
        pattern_line = "Pattern alert: Recent incidents indicate elevated risk. Monitor escalation triggers."
    return (
        f"INTEL RETRIEVAL â€” {query}\n"
        f"{DIV}\n"
        + f"{DIV}\n".join(blocks)
        + f"{DIV}\n"
        + (pattern_line + "\n" if pattern_line else "")
        + "Standing by."
    )


def build_threat_escalation(old: str, new: str, reason: str) -> str:
    return (
        f"âš  THREAT ESCALATION: Level updated from {old} to {new}.\n"
        f"Reason: {reason}\n"
        "Recommended Actions:\n"
        "1. Increase ISR coverage in sector.\n"
        "2. Notify theatre command and stand up QRF.\n"
        "3. Verify intel from forward units within 30 minutes.\n"
        "Awaiting your orders, Commander."
    )


def build_sitrep(recipient: str, message: str) -> str:
    return (
        f"SITREP â€” {recipient} | {now_hhmm()}\n"
        f"{DIV}\n"
        f"SITUATION:  {message}\n"
        "MISSION:    Execute per theatre SOP and report deviations.\n"
        "EXECUTION:  Forward teams remain on standby; ISR assets tasked.\n"
        "COMMAND:    Theatre Commander\n"
        f"{DIV}\n"
        "SITREP transmitted via secure channel (simulated). Logged.\n"
        "Standing by."
    )


def build_reminder(event: str, hhmm: Optional[str]) -> str:
    time_label = f"{hhmm} HRS" if hhmm else "TBD"
    return (
        "REMINDER SET\n"
        f"{DIV}\n"
        f"Event:     {event}\n"
        f"Time:      {time_label}\n"
        "Priority:  ROUTINE\n"
        "Status:    ACTIVE\n"
        f"{DIV}\n"
        "Standing by."
    )


def build_mission_schedule(message: str, state: dict) -> str:
    mission_name = "Recon Patrol"
    if "surveillance" in message:
        mission_name = "Aerial Surveillance"
    if "drone" in message:
        mission_name = "Drone Recon"

    hhmm = extract_time(message)
    grid_match = re.search(r"grid\s*([A-Za-z0-9-]+)", message, re.IGNORECASE)
    sector = f"Grid {grid_match.group(1)}" if grid_match else state.get("theatre") or "Unspecified"

    has_intel = bool(search_intel(sector))
    risk_block = build_risk_assessment(mission_name, state, hhmm, has_intel)

    unit = (state.get("units") or ["Unassigned Unit"])[0]
    time_label = f"{hhmm} HRS" if hhmm else "TBD"
    state["active_mission"] = mission_name
    add_audit(state["session_id"], f"Mission scheduled: {mission_name} @ {time_label}")

    return (
        f"{risk_block}\n"
        "MISSION SCHEDULED\n"
        f"{DIV}\n"
        f"Mission Name:    {mission_name}\n"
        f"Time:            {time_label}\n"
        f"Unit Allocated:  {unit}\n"
        f"Sector:          {sector}\n"
        "Status:          CONFIRMED\n"
        f"{DIV}\n"
        "Added to Ops Calendar. Standing by."
    )


def build_clarification() -> str:
    return (
        "CLARIFICATION REQUIRED: intent unclear. Please confirm: "
        "Request status brief, retrieve intel, or schedule a mission?"
    )


def build_confirmation_required(action: str, state: dict) -> str:
    risk_block = build_risk_assessment("High-Risk Engagement", state, None, has_intel=True)
    return (
        "ðŸ”´ HUMAN CONFIRMATION REQUIRED\n"
        f"{DIV}\n"
        f"Requested Action: {action}\n"
        "Classification:   LETHAL\n"
        f"{risk_block}\n"
        "This action cannot be undone. Type CONFIRM to execute. Any other response cancels.\n"
        f"{DIV}\n"
        "Awaiting your orders, Commander."
    )


@app.post("/set-theatre")
def set_theatre(payload: TheatreRequest):
    state = get_session(payload.session_id)
    state["session_id"] = payload.session_id
    theatre = normalize_theatre(payload.theatre)
    state["theatre"] = theatre
    state["threat_level"] = "ROUTINE"
    state["units"] = THEATRE_UNITS.get(theatre, [])
    add_audit(payload.session_id, f"Theatre set to {THEATRE_LABELS.get(theatre, theatre)}")
    return {"state": state}


@app.post("/chat")
def chat(payload: ChatRequest):
    state = get_session(payload.session_id)
    state["session_id"] = payload.session_id

    message = payload.message.strip()
    lower = message.lower()

    if state.get("pending_confirmation") and message == "CONFIRM":
        state["pending_confirmation"] = False
        action = state.pop("pending_action", "Requested action")
        add_audit(payload.session_id, f"Action authorised: {action}")
        reply = (
            f"âœ… ACTION AUTHORISED by Commander at {now_hhmm()}.\n"
            f"Executing: {action}. Logged with Mission Risk Score for audit.\n"
            "Action complete. Standing by."
        )
        return {"reply": reply, "state": state}

    if "status" in lower or "brief" in lower or "situation" in lower or "ops" in lower:
        reply = build_status_brief(state)
        add_audit(payload.session_id, "Status brief delivered")
        return {"reply": reply, "state": state}

    if any(token in lower for token in ("find", "search", "retrieve", "look up", "show me", "what do we know")):
        reply = build_intel_retrieval(message)
        add_audit(payload.session_id, "Intel retrieval executed")
        return {"reply": reply, "state": state}

    if "lac crossing" in lower and "confirmed" in lower:
        old = state.get("threat_level", "ROUTINE")
        new = "ELEVATED" if state.get("theatre") == "EASTERN" else "GUARDED"
        update_threat(payload.session_id, new)
        add_audit(payload.session_id, f"Threat escalated to {new}")
        reply = build_threat_escalation(old, new, "Confirmed LAC crossing reported.")
        return {"reply": reply, "state": state}

    if any(token in lower for token in ("schedule", "plan", "set up", "organise", "deploy")):
        reply = build_mission_schedule(lower, state)
        return {"reply": reply, "state": state}

    if any(token in lower for token in ("send", "alert", "notify", "message", "report", "sitrep")):
        recipient_match = re.search(r"\bto\s+([A-Za-z ]+)", message, re.IGNORECASE)
        recipient = recipient_match.group(1).strip() if recipient_match else "COMMAND"
        reply = build_sitrep(recipient.upper(), message)
        add_audit(payload.session_id, f"SITREP sent to {recipient.upper()}")
        return {"reply": reply, "state": state}

    if any(token in lower for token in ("remind", "alert at", "set alarm", "flag")):
        hhmm = extract_time(message)
        reply = build_reminder(message, hhmm)
        add_audit(payload.session_id, "Reminder set")
        return {"reply": reply, "state": state}

    if any(token in lower for token in ("strike", "engage", "engagement", "authorise", "authorize", "precision")):
        if "strike" in lower and "authorise" not in lower and "authorize" not in lower:
            reply = (
                "CLARIFICATION REQUIRED: target and intent unclear. Please confirm: "
                "Surveillance, warning shot, or precision engagement?"
            )
            return {"reply": reply, "state": state}
        state["pending_confirmation"] = True
        state["pending_action"] = message
        add_audit(payload.session_id, "Human confirmation requested")
        reply = build_confirmation_required(message, state)
        return {"reply": reply, "state": state}

    reply = build_clarification()
    return {"reply": reply, "state": state}
