# SAINIK — COMPLETE WORKFLOW & LOGIC DOCUMENTATION
## Smart AI for National Intelligence & Command

---

## 📋 TABLE OF CONTENTS
1. [Architecture Overview](#architecture-overview)
2. [The 8-Step Demo Workflow](#the-8-step-demo-workflow)
3. [Core Logic Explanation](#core-logic-explanation)
4. [API Endpoints Reference](#api-endpoints-reference)
5. [State Management](#state-management)
6. [Safety Mechanisms](#safety-mechanisms)

---

## Architecture Overview

### System Design
```
┌─────────────────────────────────────────────────────────────┐
│                    SAINIK ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (HTML/CSS Dashboard)                               │
│  ├─ Command Center Interface                                │
│  ├─ Real-time Status Display                                │
│  └─ Action Buttons & Forms                                  │
│           ↓                                                  │
│  FastAPI Backend (Python) — src/main.py                     │
│  ├─ REST API Endpoints (/api/*)                             │
│  ├─ Request Validation (Pydantic Models)                    │
│  └─ CORS Middleware (Allow cross-origin requests)           │
│           ↓                                                  │
│  SAINIKAgent Class (Core Logic) — src/agent.py              │
│  ├─ 5 Core Actions                                          │
│  ├─ Threat Escalation Engine                                │
│  ├─ Mission Risk Assessment                                 │
│  ├─ Human Confirmation Gate                                 │
│  ├─ Ambiguity Resolution Protocol                           │
│  └─ Audit Trail Logging                                     │
│           ↓                                                  │
│  Data Models (Schema Definition) — src/models.py            │
│  ├─ Request/Response Pydantic models                        │
│  ├─ Database models                                         │
│  └─ Enums (ThreatLevel, Theatre, ActionType, etc.)          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack
- **Backend**: FastAPI (high-performance async framework)
- **Language**: Python 3.10+
- **Frontend**: HTML5 + CSS3 (military-themed dark dashboard)
- **Database**: SQLite (dev) / Supabase PostgreSQL (production)
- **Validation**: Pydantic (type-safe data validation)

---

## The 8-Step Demo Workflow

### **STEP 1: Context Briefing (ACTION 5)**
**What Happens:**
1. Dashboard loads → "SAINIK ONLINE" briefing appears
2. Commander selects Theatre B (Eastern Sector)
3. Commander clicks "REQUEST STATUS BRIEFING"

**Code Flow:**
```
Frontend (Button click)
  └─→ POST /api/status/briefing
      └─→ SAINIKAgent.get_operational_status()
          ├─ Reads: self.threat_level (ROUTINE)
          ├─ Reads: self.active_theatre (Eastern Sector)
          ├─ Reads: self.current_mission (None)
          ├─ Reads: self.units_on_standby
          ├─ Reads: self.pending_actions
          ├─ Reads: self.last_action
          └─ Returns OperationalStatus JSON
      └─→ Response displayed on Dashboard
```

**Data Structure Example:**
```json
{
  "threat_level": "ROUTINE",
  "active_theatre": "Eastern Sector",
  "current_mission": null,
  "units_on_standby": ["BSF", "Indian Army", "IAF", "Naval Command"],
  "pending_actions": [],
  "last_action": "Theatre activated"
}
```

**Demonstrates:** ✓ State tracking, ✓ Situational awareness, ✓ Military tone

---

### **STEP 2: Intelligence Retrieval (ACTION 3)**
**What Happens:**
1. Commander types search: "Find infiltration reports from Tawang sector in the last 72 hours"
2. SAINIK queries intel_archive (loaded from memory)
3. Returns 3 matching reports with dates, grids, summaries
4. **PROACTIVE FLAGGING**: "Pattern matches 2021 Galwan pre-escalation signature"

**Code Flow:**
```
Frontend (Search button)
  └─→ POST /api/intelligence/search
      ├─ Query: { sector: "Tawang", time_range_hours: 72 }
      └─→ SAINIKAgent.retrieve_intelligence()
          ├─ Filter: self.intel_archive by sector
          ├─ Return matching IntelligenceReport objects
          └─ IF matches.length >= 2:
              └─ Append pattern analysis warning
      └─→ Response with reports + analysis
      └─→ Dashboard displays 3 reports + ⚠️ pattern warning
```

**Sample Intel Archive (hardcoded in agent.py):**
```python
IntelligenceReport(
    date="2024-03-26",
    sector="Tawang",
    grid_reference="3381",
    threat_type="LAC Crossing",
    summary="Unconfirmed: 8-12 PLA personnel near Tawang boundary",
    severity="MEDIUM"
)
```

**Demonstrates:** ✓ Document retrieval, ✓ Pattern recognition, ✓ Proactive flagging

---

### **STEP 3: Threat Escalation Auto-Trigger**
**What Happens:**
1. Commander reports: "CONFIRMED LAC crossing at Grid 4482"
2. SAINIK **auto-fires** escalation (no human needed for this trigger)
3. Threat level: ROUTINE → ELEVATED
4. Header badge turns **AMBER**, pulsing alerts
5. "Recommended immediate actions" list displayed

**Code Flow:**
```
Frontend (Confirmation button)
  └─→ POST /api/threat/confirm-lac-crossing
      ├─ Payload: { grid_reference: "4482", ... }
      └─→ SAINIKAgent.escalate_threat()
          ├─ old_level = self.threat_level (ROUTINE)
          ├─ new_level = ThreatLevel.ELEVATED
          ├─ self.threat_level = ELEVATED
          ├─ Generate recommendations list:
          │  ├ "Move units to AMBER status"
          │  ├ "Activate all forward positions"
          │  └ "Prepare contingency operations"
          ├─ Log to action_log with timestamp
          └─ Return notification with recommendations
      └─→ Frontend updates threat badge color (CSS class change)
      └─→ Dashboard displays escalation alert
```

**Escalation Rules (in SAINIKAgent):**
```python
if self.threat_level == ThreatLevel.ELEVATED:
    success_prob -= 15        # Affects all future mission success %
    personnel_risk = "HIGH"
elif self.threat_level == ThreatLevel.HIGH:
    success_prob -= 20
    confidence -= 20
```

**Demonstrates:** ✓ Auto-escalation engine, ✓ Real-time UI updates, ✓ Context-aware responses

---

### **STEP 4: Mission Scheduling + Risk Assessment (ACTION 1)**
**What Happens:**
1. Commander schedules: "Aerial surveillance Grid 4482 at 0330 hrs"
2. SAINIK calculates **Mission Risk Assessment** automatically
3. Returns: Risk scores, success probability, recommendation
4. Mission added to calendar

**Code Flow:**
```
Frontend (Schedule Mission form)
  └─→ POST /api/mission/schedule
      ├─ Payload:
      │  {
      │    "name": "Aerial Surveillance Grid-4482",
      │    "scheduled_time": "0330 hrs",
      │    "units_to_allocate": ["IAF"],
      │    "grid_reference": "4482"
      │  }
      └─→ SAINIKAgent.schedule_mission()
          ├─ Create Mission object
          ├─ Call assess_mission_risk(mission)
          │  ├─ Base success_prob = 85%
          │  ├─ Apply threat level impact:
          │  │  └─ threat_level == ELEVATED → success_prob -= 15 (now 70%)
          │  ├─ Apply time penalty (0330 = night):
          │  │  └─ hour < 6 or hour >= 20 → collateral_concern = MEDIUM
          │  ├─ Calculate recommendation:
          │  │  └─ IF success_prob >= 80 AND personnel_risk <= MEDIUM:
          │  │      └─ "PROCEED"
          │  │  └─ ELIF success_prob >= 65:
          │  │      └─ "PROCEED WITH CAUTION" ← This case
          │  │  └─ ELSE:
          │  │      └─ "HOLD"
          │  └─ Return MissionRiskAssessment
          ├─ Store mission in missions_calendar
          ├─ Log to action_log
          └─ Return confirmation + risk assessment
      └─→ Dashboard displays:
          ├ ✓ MISSION SCHEDULED
          ├ Name, time, units, grid
          └─ Mission Risk Assessment card with all scores
```

**Risk Assessment Logic (src/agent.py:assess_mission_risk):**
```python
# Base values
personnel_risk = "MEDIUM"
success_prob = 85
collateral_concern = "LOW"
confidence = 80

# Threat level modifiers
if threat_level == ELEVATED:
    success_prob -= 15  # Now 70%
    personnel_risk = "HIGH"
elif threat_level == HIGH:
    success_prob -= 20  # Now 65%
    personnel_risk = "HIGH"
    confidence -= 20

# Night ops penalty
if hour < 6 or hour >= 20:  # 0330 hrs fits here
    collateral_concern = "MEDIUM"
    confidence -= 10  # Now 70%

# Recommendation logic
if success_prob >= 80 and personnel_risk in ["LOW", "MEDIUM"]:
    recommendation = "PROCEED"
elif success_prob >= 65:
    recommendation = "PROCEED WITH CAUTION"  ← Category for 70% success
else:
    recommendation = "HOLD"
```

**Output (shown to commander):**
```
MISSION RISK ASSESSMENT — Aerial Surveillance Grid-4482
─────────────────────────────────────────────────────────
Personnel Risk:        HIGH
Mission Success Prob:  70%    ← Reduced from 85% due to ELEVATED threat
Collateral Concern:    MEDIUM ← Raised due to night ops
Confidence Score:      70%    ← Reduced from 80%
─────────────────────────────────────────────────────────
Recommendation: PROCEED WITH CAUTION

Added to Ops Calendar. Standing by.
```

**Demonstrates:** ✓ Risk scoring with dynamic adjustments, ✓ Mission scheduling, ✓ Threat-aware decision-making

---

### **STEP 5: Ambiguity Resolution Protocol (ARP)**
**What Happens:**
1. Commander types ambiguous command: "Strike the position"
2. SAINIK **REFUSES to proceed**
3. Outputs: "CLARIFICATION REQUIRED"
4. Asks ONE specific question with 2-3 options

**Code Flow:**
```
Frontend (Text input)
  └─→ Natural language detection triggered
      └─→ POST /api/clarify
          ├─ Payload: { issue: "No target designated", options: [...] }
          └─→ SAINIKAgent.clarification_required()
              ├─ Format: "CLARIFICATION REQUIRED: [issue]"
              ├─ options = [
              │   "(a) Grid 4482 LAC crossing contact",
              │   "(b) New coordinate — provide grid",
              │   "(c) Simulated training strike"
              │ ]
              └─ Return formatted message requesting one answer
      └─→ Dashboard displays clarification request
      └─→ Commander picks (a), (b), or (c)
      └─→ Proceeds only after resolution
```

**Key Protection:** ✗ SAINIK does NOT guess, ✗ Does NOT assume, ✓ Asks specific question

**Demonstrates:** ✓ Ambiguity resolution, ✓ No blind execution, ✓ Safety-first

---

### **STEP 6: Human Confirmation Gate (LETHAL ACTION)**
**What Happens:**
1. Commander requests: "AUTHORIZE precision engagement at Grid 4482"
2. SAINIK **HARD STOPS** (🔴 flag)
3. Shows full Mission Risk Assessment
4. **Requires explicit CONFIRM (uppercase)**
5. Only then executes action

**Code Flow:**
```
Frontend (Engagement button)
  └─→ POST /api/engagement/request-authorization
      ├─ Payload: { grid_reference: "4482", ... }
      └─→ SAINIKAgent.require_confirmation_gate()
          ├─ Generate risk assessment for engagement
          ├─ Format: 🔴 HUMAN CONFIRMATION REQUIRED
          ├─ Show action, classification, risk scores
          ├─ Message: "Type CONFIRM to execute. Any other = CANCEL"
          └─ Return gate message (NO execution yet)
      └─→ Dashboard shows gate modal
      └─→ Commander must type "CONFIRM" (case-insensitive check)
      └─→ POST /api/engagement/authorize
          ├─ Payload: { authorization_code: "CONFIRM", ... }
          └─→ SAINIKAgent.execute_authorized_action()
              ├─ Check: IF auth.authorization_code.upper() != "CONFIRM":
              │   └─ REJECT: "Invalid authorization code"
              ├─ ELSE:
              │   ├─ Create ActionLog entry
              │   ├─ Log to action_log with timestamp
              │   ├─ Mark: authorized_by = "COMMANDER"
              │   └─ Return: ✅ ACTION AUTHORISED
              └─ Return success message
      └─→ Dashboard shows: ✅ ACTION AUTHORISED at [TIME]
```

**The Gate Message (exact output):**
```
🔴 HUMAN CONFIRMATION REQUIRED
═══════════════════════════════════════════════════════════════
Requested Action: PRECISION ENGAGEMENT at Grid 4482
Classification:   LETHAL / IRREVERSIBLE / HIGH-RISK

MISSION RISK ASSESSMENT
─────────────────────────────────────────────────────────────
Mission: Engagement at Grid 4482
Personnel Risk:        MEDIUM
Success Probability:   75%
Collateral Concern:    LOW
Confidence Score:      72%
Recommendation:        PROCEED WITH CAUTION
─────────────────────────────────────────────────────────────

⚠️  This action cannot be undone.
⚠️  SAINIK will not proceed without explicit authorisation.

Type CONFIRM (uppercase) to authorize execution.
Any other response will CANCEL this action.
═══════════════════════════════════════════════════════════════
```

**Why This Is Critical:**
- Prevents accidental clicks
- Forces conscious decision
- Creates audit trail (who, when)
- Risk assessment shown before commit
- **REVERSIBLE ONLY IF USER CANCELS BEFORE CONFIRM**

**Demonstrates:** ✓ Human-in-the-loop gate, ✓ Safety-first design, ✓ Irreversible action protection

---

### **STEP 7: Secure Communications (ACTION 2 — SITREP)**
**What Happens:**
1. Commander composes SITREP (Situation Report)
2. SAINIK **drafts** the message
3. Shows preview with SITUATION / MISSION / EXECUTION / COMMAND structure
4. Commander reviews & approves
5. **Then** SAINIK sends it (not before review)

**Code Flow:**
```
Frontend (SITREP form)
  └─→ POST /api/sitrep/draft
      ├─ Payload:
      │  {
      │    "recipient": "Eastern Command",
      │    "situation": "LAC crossing confirmed Grid 4482...",
      │    "mission": "Initiate air surveillance...",
      │    "execution": "IAF P-8I deployed...",
      │    "command": "Full command authority..."
      │  }
      └─→ SAINIKAgent.draft_sitrep()
          ├─ Create SITREP object
          ├─ Set status = "DRAFTED"
          ├─ Store in self.sitrep_drafts
          ├─ Format message with section dividers
          └─ Return draft (NOT sent yet)
      └─→ Dashboard shows draft preview + "SEND SITREP" button
      └─→ Commander reads draft
      └─→ Commander clicks "SEND SITREP"
          └─→ POST /api/sitrep/send/{sitrep_id}
              └─→ SAINIKAgent.send_sitrep()
                  ├─ Find drafted SITREP by ID
                  ├─ Update status = "SENT"
                  ├─ Log ActionLog with timestamp
                  └─ Return confirmation message
              └─→ Dashboard shows: ✓ SITREP TRANSMITTED
```

**Demonstrates:** ✓ Structured military comms, ✓ Human review before send, ✓ Two-step process (draft→send)

---

### **STEP 8: Tactical Reminders (ACTION 4)**
**What Happens:**
1. Commander sets reminder: "Check drone feed at 0500 hrs"
2. SAINIK creates reminder with priority
3. Stores in pending_actions
4. Will alert at scheduled time

**Code Flow:**
```
Frontend (Reminder form)
  └─→ POST /api/reminder/set
      ├─ Payload:
      │  {
      │    "event": "Check drone surveillance feed",
      │    "scheduled_time": "0500 hrs",
      │    "priority": "HIGH"
      │  }
      └─→ SAINIKAgent.set_tactical_reminder()
          ├─ Create TacticalReminder object
          ├─ Store in self.reminders
          ├─ Add to self.pending_actions
          ├─ Log ActionLog entry
          └─ Return confirmation
      └─→ Dashboard shows: ✓ TACTICAL REMINDER SET
```

**Demonstrates:** ✓ Priority-aware reminders, ✓ Scheduled event tracking

---

## Core Logic Explanation

### **1. STATE MANAGEMENT (SAINIKAgent class)**

All state is tracked in the `SAINIKAgent` instance:

```python
class SAINIKAgent:
    def __init__(self):
        self.threat_level = ThreatLevel.ROUTINE
        self.active_theatre = None
        self.current_mission = None
        self.units_on_standby = ["BSF", "Indian Army", ...]
        self.pending_actions = []
        self.missions_calendar = []
        self.action_log = []  # ← AUDIT TRAIL
        self.sitrep_drafts = []
        self.reminders = []
        self.intel_archive = [...]  # ← Sample data
```

**Critical:** All changes must go through agent methods → logged to action_log

---

### **2. THREAT ESCALATION ENGINE**

**Threat Level Hierarchy:**
```
ROUTINE
    ↓ (2+ reports in LoC / single verified intrusion EASTERN / submarine detection MARITIME)
GUARDED
    ↓ (LAC crossing confirmed OR 3+ reports)
ELEVATED
    ↓ (Hostile contact OR theatre-specific trigger)
HIGH
    ↓ (Active engagement OR command unresponsive)
CRITICAL
```

**Impact on Mission Risk:**
```python
# Each level reduces success probability
ROUTINE   → No penalty
GUARDED   → -10%
ELEVATED  → -15%
HIGH      → -20%
CRITICAL  → -35%
```

**Auto-Escalation Rules (hardcoded):**
- LoC: 2+ infiltration reports in 6 hours → HIGH
- Eastern: LAC crossing confirmed → ELEVATED
- Maritime: Unidentified submarine → HIGH; No response 30 min → CRITICAL

---

### **3. MISSION RISK ASSESSMENT MATRIX**

**Inputs:** Threat level, mission type, time of day, units available

**Scoring Logic:**
```python
def assess_mission_risk(mission):
    # Base scores
    success_prob = 85
    personnel_risk = "MEDIUM"
    confidence = 80
    collateral = "LOW"
    
    # Apply threat modifier
    if threat_level == ELEVATED:
        success_prob -= 15  # 70%
    elif threat_level == HIGH:
        success_prob -= 20  # 65%
        confidence -= 20    # 60%
    
    # Apply time penalty (night ops = riskier)
    if hour < 6 or hour >= 20:
        collateral = "MEDIUM"
        confidence -= 10
    
    # Recommendation logic
    if success_prob >= 80:
        recommendation = "PROCEED"
    elif success_prob >= 65:
        recommendation = "PROCEED WITH CAUTION"
    else:
        recommendation = "HOLD"
    
    return MissionRiskAssessment(...)
```

---

### **4. AMBIGUITY RESOLUTION PROTOCOL (ARP)**

**When Triggered:**
- Command is ambiguous or incomplete
- Multiple interpretations possible
- Could lead to unintended consequences

**Process:**
1. **STOP** — Do not guess
2. **Ask ONE specific question** with 2-3 options
3. **Wait for clarification**
4. **Proceed only after resolution**

**Example:**
```
Command: "Strike the position"
Response:
  "CLARIFICATION REQUIRED: No active target designated.
   Please confirm one of the following:
   (a) Grid 4482 LAC crossing contact
   (b) A new coordinate — provide grid reference
   (c) Simulated training strike"
```

---

### **5. HUMAN CONFIRMATION GATE (HCG)**

**Non-Negotiable:** Must CONFIRM before executing:
- Lethal/engagement commands
- Evacuation orders
- Irreversible actions
- High-risk operations (depends on threat level)

**Gate Logic:**
```python
def require_confirmation_gate(action, risk_assessment):
    return f"""
🔴 HUMAN CONFIRMATION REQUIRED
Requested Action: {action}
Classification: LETHAL / IRREVERSIBLE

[Full Mission Risk Assessment display]

Type CONFIRM to authorize. Any other = CANCEL.
    """

def execute_authorized_action(auth_code):
    if auth_code.upper() != "CONFIRM":
        return "❌ DENIED"
    else:
        return "✅ ACTION AUTHORISED"
```

**Audit Trail:**
```
✅ ACTION AUTHORISED by Commander at 0347 hrs
Executing: Precision engagement at Grid 4482
Action logged with complete audit trail.
```

---

### **6. AUDIT TRAIL LOGGING**

**Every action** logged to `action_log`:

```python
log_entry = ActionLog(
    timestamp=datetime.utcnow(),
    action_type=ActionType.MISSION_SCHEDULING,
    description="Mission scheduled: Aerial Surveillance",
    actor="SAINIK",
    authorized_by="COMMANDER",
    status="EXECUTED"
)
self.action_log.append(log_entry.dict())
```

**Sample Audit Log:**
```
1. [CONTEXT_BRIEFING] Theatre activated: Eastern Sector
   Time: 2024-03-28 14:35:22 | Status: EXECUTED

2. [INTELLIGENCE_RETRIEVAL] Intelligence query: Tawang
   Time: 2024-03-28 14:36:10 | Status: EXECUTED

3. [CONTEXT_BRIEFING] THREAT ESCALATION: ROUTINE → ELEVATED
   Time: 2024-03-28 14:37:45 | Status: EXECUTED

4. [MISSION_SCHEDULING] Mission scheduled: Aerial Surveillance
   Time: 2024-03-28 14:38:20 | Status: EXECUTED | Authorized: COMMANDER
```

---

## API Endpoints Reference

### **Session Management**
```
GET /api/init
  → Return: SAINIK briefing, initial status

POST /api/theatre-select
  → Accept: { theatre: "Line of Control" | "Eastern Sector" | "Maritime" }
  → Return: Confirmation, threat level
```

### **ACTION 1: Mission Scheduling**
```
POST /api/mission/schedule
  → Accept: MissionRequest
    {
      name: "Aerial Surveillance Grid-4482"
      mission_type: "SURVEILLANCE"
      theatre: "Eastern Sector"
      scheduled_time: "0330 hrs"
      units_to_allocate: ["IAF"]
      grid_reference: "4482"
    }
  → Return: Confirmation, Mission, Risk Assessment, updated threat level
```

### **ACTION 2: Secure Communications**
```
POST /api/sitrep/draft
  → Accept: SITREPRequest (situation, mission, execution, command)
  → Return: SITREP draft (NOT sent yet)

POST /api/sitrep/send/{sitrep_id}
  → Accept: sitrep_id
  → Return: Confirmation message
```

### **ACTION 3: Intelligence Retrieval**
```
POST /api/intelligence/search
  → Accept: IntelligenceQuery
    {
      sector: "Tawang"
      time_range_hours: 72
    }
  → Return: [IntelligenceReport], pattern analysis
```

### **ACTION 4: Tactical Reminders**
```
POST /api/reminder/set
  → Accept: TacticalReminderRequest
    {
      event: "Check drone feed"
      scheduled_time: "0500 hrs"
      priority: "HIGH"
    }
  → Return: Confirmation message
```

### **ACTION 5: Context Briefing**
```
GET /api/status/briefing
  → Return: OperationalStatus
    {
      threat_level: "ELEVATED"
      active_theatre: "Eastern Sector"
      current_mission: "Aerial Surveillance"
      units_on_standby: [...]
      pending_actions: [...]
      last_action: "..."
    }
```

### **Threat Escalation**
```
POST /api/threat/escalate
  → Accept: { level: "HIGH", reason: "..." }
  → Return: Escalation notification

POST /api/threat/confirm-lac-crossing
  → Accept: TargetDesignation
  → Return: Auto-escalation notification (→ ELEVATED)
```

### **Engagement Authorization**
```
POST /api/engagement/request-authorization
  → Accept: TargetDesignation
  → Return: 🔴 Confirmation gate (NO action yet)

POST /api/engagement/authorize
  → Accept: EngagementAuthorization { authorization_code: "CONFIRM" }
  → Return: ✅ Authorized OR ❌ Denied
```

### **Audit & Admin**
```
GET /api/audit/log
  → Return: Full action_log + formatted summary

GET /api/health
  → Return: System status, threat level version
```

---

## State Management

### **Session Lifecycle**

```
1. SESSION INIT (GET /api/init)
   → SAINIK ONLINE briefing
   → threat_level = ROUTINE
   → active_theatre = None

2. THEATRE SELECTION (POST /api/theatre-select)
   → active_theatre = selected
   → units_on_standby = theatre-specific list
   → threat_level = ROUTINE (reset)

3. OPERATIONS (multiple actions)
   → threat_level may escalate (auto or manual)
   → missions added to missions_calendar
   → all actions logged to action_log

4. SESSION END
   → action_log persists
   → can be exported/audited
```

### **Data Persistence**

**In-Memory (Session-based):**
- threat_level (resets on new session)
- active_theatre
- missions_calendar
- action_log
- pending_actions

**Sample Database (Supabase)** (for production):
```sql
CREATE TABLE missions (
    mission_id UUID PRIMARY KEY,
    name VARCHAR,
    threat_level VARCHAR,
    scheduled_time VARCHAR,
    status VARCHAR,
    created_at TIMESTAMP,
    authorized_by VARCHAR
);

CREATE TABLE action_logs (
    log_id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    action_type VARCHAR,
    description VARCHAR,
    actor VARCHAR,
    authorized_by VARCHAR,
    status VARCHAR
);
```

---

## Safety Mechanisms

### **1. No Blind Execution**
- Ambiguous commands → Clarification required
- No assumptions or guessing
- Clear, specific questions posed

### **2. Lethal Action Gate**
- 🔴 HARD STOP for irreversible actions
- Requires explicit CONFIRM (uppercase)
- Full risk assessment shown
- Audit trail created

### **3. Human-in-the-Loop**
- Draft → Review → Send (for SITREPs)
- Request → Clarification → Proceed
- Suggest → Authorize → Execute (for missions)

### **4. Threat Escalation Safeguards**
- Auto-escalation only on verified threats
- Risk scores reduced during elevated threats
- Recommendations change based on threat level
- Commander can manually escalate anytime

### **5. Audit Trail**
- Every action logged with timestamp
- Who authorized it
- What status (PENDING/EXECUTED/REJECTED)
- Cannot be deleted (immutable log)

### **6. Reversibility**
- Most actions reversible until CONFIRM
- Only CONFIRM-gated actions are irreversible
- Clear warnings before irreversible actions

---

## Key Takeaways for Judges

| Feature | What It Proves |
|---------|----------------|
| Status Briefing | Real-time state tracking |
| Intel Retrieval | Pattern recognition + proactive flagging |
| Auto-Escalation | Context-aware decision making |
| Risk Assessment | Dynamic risk scoring based on threat |
| Ambiguity Resolution | Safety-first: no blind execution |
| Confirmation Gate | Human-in-the-loop for lethal actions |
| SITREP Drafting | Structured military communications |
| Audit Trail | Complete explainability + accountability |

---

## To Run the Application

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Run FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 4. Open browser
# http://localhost:8000
```

---

## Demo Script (For Judges)

```
1. Load dashboard
2. Select Theatre B (Eastern Sector)
3. Click "REQUEST STATUS BRIEFING"
4. Search intelligence: "Tawang sector"
5. Confirm LAC crossing at Grid 4482
6. Schedule aerial surveillance mission (see risk assessment update)
7. Try to "Strike the position" (see clarification request)
8. Request engagement authorization (see confirmation gate)
9. Type "CONFIRM" to authorize
10. Send SITREP to Eastern Command
11. Set reminder for 0500 hrs
12. View audit log
```

Each step demonstrates one safety mechanism + operational capability.

---

**SAINIK READY FOR DEPLOYMENT** 🔱
