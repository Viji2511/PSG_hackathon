sessions = {}

def get_session(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = {
            "theatre": None,
            "threat_level": "ROUTINE",
            "active_mission": None,
            "units": [],
            "audit_log": [],
            "pending_confirmation": False,
            "messages": []
        }
    return sessions[session_id]

def update_threat(session_id: str, level: str):
    sessions[session_id]["threat_level"] = level

def add_audit(session_id: str, action: str):
    from datetime import datetime
    sessions[session_id]["audit_log"].append({
        "time": datetime.now().strftime("%H%M HRS"),
        "action": action
    })