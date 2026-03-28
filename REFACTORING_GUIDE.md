# REFACTORING GUIDE — Aligning SAINIK to the Autonomous Action Framework

## Overview

The SAINIK project has been **refactored from a military-specific agent to a domain-agnostic autonomous action framework** where military operations is just ONE application layer.

This document explains:
1. What changed and why
2. How old SAINIK code maps to the new framework
3. Where to find each piece of functionality
4. How to extend for new domains

---

## 🔄 The Refactoring

### BEFORE (Military-Only SAINIK)
```
OLD STRUCTURE:
src/agent.py (SAINIKAgent)
  ├─ set_active_theatre()
  ├─ schedule_mission()
  ├─ draft_sitrep()
  ├─ retrieve_intelligence()
  ├─ set_tactical_reminder()
  └─ escalate_threat()

Frontend: Military-specific dashboard
Database: Hardcoded military data
API Endpoints: Military-specific (/api/mission, /api/sitrep, etc.)

PROBLEM: This doesn't work for office tasks, smart homes, or any other domain!
```

### AFTER (Domain-Agnostic Framework)
```
NEW STRUCTURE:
core/
  ├─ intent_engine.py      ← Parse any command → Intent
  ├─ decision_engine.py    ← Make ACT/ASK/CONFIRM decisions
  ├─ context_manager.py    ← Track session state
  ├─ task_planner.py       ← Break down complex instructions
  └─ execution_engine.py   ← Orchestrate complete pipeline

tools/
  ├─ tool_registry.py      ← Map intents to tool implementations
  ├─ calendar_tool.py      ← Abstract scheduling tool
  ├─ email_tool.py         ← Abstract communication tool
  ├─ search_tool.py        ← Abstract search tool
  └─ reminder_tool.py      ← Abstract reminder tool

applications/
  ├─ military_layer.py     ← Military operations (translate to generic)
  ├─ office_layer.py       ← Business operations
  └─ smart_home_layer.py   ← Home automation

Frontend: Generic dashboard + domain selector
Database: Supabase (sessions, logs, memory)
API Endpoints: Unified /api/command (works for ALL domains!)

BENEFIT: Same framework works for military, office, smart home, anything!
```

---

## 📍 Code Migration Map

### Old SAINIK Code → New Framework

| OLD (Military-Specific) | NEW (Domain-Agnostic) | Location | Purpose |
|---|---|---|---|
| `SAINIKAgent.schedule_mission()` | `TaskType.SCHEDULE` | `core/task_planner.py` | Abstract scheduling |
| `SAINIKAgent.draft_sitrep()` | `TaskType.SEND` | `core/intent_engine.py` | Abstract messaging |
| `SAINIKAgent.retrieve_intelligence()` | `TaskType.SEARCH` | `core/intent_engine.py` | Abstract search |
| `SAINIKAgent.set_tactical_reminder()` | `TaskType.REMIND` | `core/task_planner.py` | Abstract reminders |
| `SAINIKAgent.escalate_threat()` | `DecisionMode.CONFIRM` | `core/decision_engine.py` | Safety gate logic |
| Theatre selection | `domain` parameter | `context_manager.py` | Context awareness |
| Risk Assessment | `decision.risk_level` | `core/decision_engine.py` | Safety decisions |
| Audit Log | `action_history` | `context_manager.py` | Complete logging |
| SAINIK Endpoints | `/api/command` | `src/main.py` | Unified entry point |

### Database Schema Changes

| OLD | NEW | Storage |
|---|---|---|
| Missions table | `action_logs` table | Supabase |
| SITREPs table | Response results | Supabase |
| Theatre config | `domain` field | Context |
| Threat levels | `risk_level` enum | DecisionResult |

---

## 🚀 Example: How "Schedule Mission" Flows Through New Framework

### OLD SAINIK WAY (Direct to military logic)
```
User: "Schedule patrol Sector 4 tomorrow"
    ↓
FastAPI: POST /api/mission/schedule
    ↓
SAINIKAgent.schedule_mission()
    ↓ [Military-specific logic hardcoded]
    ↓
Returns: {"status": "mission_scheduled", "mission": {...}}
```

### NEW FRAMEWORK WAY (Generic, then domain-specific)
```
User: "Schedule patrol Sector 4 tomorrow"
    ↓
FastAPI: POST /api/command
    {"user_input": "Schedule patrol Sector 4 tomorrow", "domain": "military"}
    ↓
[INTENT ENGINE] Parse command
    → Intent(type=MULTI_TASK, tasks=[Task(type=SCHEDULE, ...)], confidence=0.85)
    ↓
[CONTEXT MANAGER] Load session
    → SessionContext(user_id=..., domain="military", ...)
    ↓
[DECISION ENGINE] Decide what to do
    → DecisionResult(mode=ACT, confidence=0.85, risk=low)
    ↓
[TASK PLANNER] Break down into steps
    → ExecutionPlan(tasks=[check_units, schedule, notify])
    ↓
[TOOL REGISTRY] Map to tools
    → calendar_tool.schedule_event(...)
    ↓
[MILITARY LAYER] Translate domain terminology
    → "Sector 4 patrol" → standard calendar event
    ↓
[EXECUTION ENGINE] Execute and store
    → Store in context, return response
    ↓
FastAPI: Returns unified ExecutionResponse with all metadata
```

---

## 🔌 How to Use the New Framework

### Option 1: Use the Unified Command Endpoint (Recommended)
```bash
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
    "status": "completed",
    "next_steps": ["Execute patrol", "Check results"]
}
```

### Option 2: Use Domain-Specific Layers (Manual Translation)
```python
# For military operations
from applications.military_layer import translate_military_command

intent = translate_military_command("Schedule patrol Sector 4")
command = Command(intent=intent, domain="military")
```

### Option 3: Use Core Modules Directly
```python
# Advanced: Direct access to core modules
from core.intent_engine import IntentEngine
from core.decision_engine import DecisionEngine

engine = IntentEngine()
intent = engine.parse_intent("Schedule patrol Sector 4", domain="military")
```

---

## 🎯 Extending for New Domains

### To add OFFICE domain support:

**Step 1: Extend Intent Recognition**
```python
# core/intent_engine.py
if "meeting" in user_input or "schedule" in user_input:
    if domain == "office":
        task_type = TaskType.SCHEDULE
        # Extract meeting-specific entities
```

**Step 2: Create Office Application Layer**
```python
# applications/office_layer.py
def translate_office_command(command: str) -> Intent:
    if "reschedule meeting" in command:
        return Intent(
            intent_type=IntentType.MULTI_TASK,
            tasks=[
                Task(type=TaskType.CANCEL, label="Cancel original meeting"),
                Task(type=TaskType.SCHEDULE, label="Create new meeting"),
                Task(type=TaskType.SEND, label="Notify attendees")
            ]
        )
```

**Step 3: Use in Command Endpoint**
```bash
POST /api/command
{
    "user_input": "Reschedule meeting with team from 10am to 2pm",
    "domain": "office"
}
```

---

## 📁 File Structure & Responsibilities

### Core Modules (Domain-Agnostic)

**`core/intent_engine.py`**
- ✅ Parse natural language
- ✅ Extract entities (time, person, action, location)
- ✅ Determine task type
- ✅ Calculate confidence score
- ❌ Does NOT execute or make decisions

**`core/decision_engine.py`**
- ✅ Assess risk level
- ✅ Check confidence thresholds
- ✅ Generate ACT/ASK/CONFIRM decisions
- ✅ Create clarification questions
- ❌ Does NOT execute tasks

**`core/context_manager.py`**
- ✅ Create/load sessions
- ✅ Track conversation history
- ✅ Store pending actions
- ✅ Manage user preferences
- ❌ Does NOT execute or decide

**`core/task_planner.py`**
- ✅ Break multi-step commands into tasks
- ✅ Determine task dependencies
- ✅ Generate execution order
- ✅ Domain-aware decomposition
- ❌ Does NOT execute

**`core/execution_engine.py`** (NEW)
- ✅ Orchestrate complete pipeline
- ✅ Call all core modules in order
- ✅ Generate response
- ✅ Handle confirmation flow
- ❌ Does NOT execute tools (that's next layer)

### Tool Layer (Domain-Agnostic Tools)

**`tools/tool_registry.py`** (TO-DO)
- Map `TaskType.SCHEDULE` → `calendar_tool`
- Map `TaskType.SEND` → `email_tool`
- Map `TaskType.SEARCH` → `search_tool`
- Map `TaskType.REMIND` → `reminder_tool`
- Support custom tool registration

**`tools/calendar_tool.py`** (TO-DO)
- `schedule_event(start, end, title, location)`
- `cancel_event(event_id)`
- `reschedule_event(event_id, new_start, new_end)`
- Works for: military missions, office meetings, smart home automations

**`tools/email_tool.py`** (TO-DO)
- `send_message(recipient, subject, body)`
- Works for: military SITREPs, office emails, smart home notifications

### Application Layers (Domain-Specific)

**`applications/military_layer.py`** (TO-DO)
- Translate military terminology to generic intents
- Map "SITREP" → `TaskType.SEND`
- Map "patrol" → `TaskType.SCHEDULE`
- Map "intelligence" → `TaskType.SEARCH`
- Defense-specific validation

**`applications/office_layer.py`** (TO-DO)
- Translate business terminology
- Map "meeting" → `TaskType.SCHEDULE`
- Map "email" → `TaskType.SEND`
- Business-specific validation

### API Layer

**`src/main.py`** (REFACTORED)
- `/api/command` ← Main endpoint
- `/api/confirm` ← Confirmation endpoint
- `/api/session/{id}` ← Session history
- `/legacy/*` ← Backward compatibility

---

## 💻 Implementation Priorities

### PHASE 1: CORE (✅ DONE)
- ✅ Intent Engine
- ✅ Decision Engine
- ✅ Context Manager
- ✅ Task Planner
- ✅ Execution Engine
- ✅ FastAPI integration (main.py)

### PHASE 2: TOOLS (🚀 NEXT)
- ⏳ Tool Registry
- ⏳ Base Tool Interface
- ⏳ Calendar Tool
- ⏳ Email Tool
- ⏳ Search Tool
- ⏳ Reminder Tool

### PHASE 3: SAFETY & MEMORY
- ⏳ Safety Engine
- ⏳ Memory Engine (Supabase + vectors)
- ⏳ Response Generator

### PHASE 4: APPLICATIONS
- ⏳ Military Layer (translate.py)
- ⏳ Office Layer
- ⏳ Smart Home Layer

### PHASE 5: TESTING & DEPLOYMENT
- ⏳ Unit tests
- ⏳ Integration tests
- ⏳ E2E tests
- ⏳ Docker containerization

---

## 🗣️ Terminology Guide

| Term | OLD Context | NEW Context | Example |
|------|---|---|---|
| **Intent** | Military command | Any domain command | "Schedule patrol", "Schedule meeting" |
| **Task** | Operation | Atomic action | SCHEDULE, SEND, SEARCH, REMIND |
| **Domain** | Theatre location | Application domain | military, office, smart_home |
| **Context** | Briefing state | Session state | All conversation history |
| **Decision** | Threat assessment | ACT/ASK/CONFIRM | Applies to any domain |
| **Plan** | Mission plan | Execution plan | Order of sub-tasks |
| **Tool** | Military system | Generic integration | Calendar, email, search |

---

## 🧪 Testing the New Framework

### Test 1: Simple Command (Military)
```bash
POST /api/command
{"user_input": "Schedule patrol tomorrow", "domain": "military"}

Expected: ❓ ASK (missing location)
Response: "Which sector?"
```

### Test 2: Complete Command (Military)
```bash
POST /api/command
{"user_input": "Schedule patrol Sector 4 tomorrow at 0800", "domain": "military"}

Expected: ✓ ACT
Response: "Patrol scheduled for Sector 4 tomorrow at 0800"
```

### Test 3: Office Command (NEW Domain)
```bash
POST /api/command
{"user_input": "Reschedule meeting with team from 10am to 2pm", "domain": "office"}

Expected: ✓ ACT or 🔴 CONFIRM
Response: Plan with steps [cancel, create, notify]
```

### Test 4: Sensitive Command (Confirmation)
```bash
POST /api/command
{"user_input": "Send emergency alert to all units", "domain": "military"}

Expected: 🔴 CONFIRM (high-risk)
Response: "Requires human authorization"

Then:
POST /api/confirm
{"execution_id": "exec_001", "session_id": "...", "confirm_code": "CONFIRM"}

Expected: ✓ Authorized
Response: "Alert sent"
```

---

## ⚙️ Configuration & Settings

**Domain-Specific Settings:**

```python
# config/settings.py
DOMAINS = {
    "military": {
        "default_risk_threshold": 0.75,
        "sensitive_keywords": ["strike", "engage", "alert"],
        "auto_escalate_threshold": 0.8
    },
    "office": {
        "default_risk_threshold": 0.60,
        "sensitive_keywords": ["delete", "urgent"],
        "auto_escalate_threshold": 0.5
    }
}
```

---

## 🔑 Key Concepts

### 1. Domain-Agnostic vs Domain-Specific

**Domain-Agnostic (Core):**
- Intent parsing works for ANY domain
- Decision logic applies universally
- Task planning is generic
- No hardcoded military terminology

**Domain-Specific (Application Layer):**
- Military layer translates "patrol" → "schedule"
- Office layer translates "meeting" → "schedule"
- Each layer registers domain-specific tools

### 2. Intent Confidence vs Risk Level

**Confidence** = "How well did I understand the command?"
- 90% = "Clear, unambiguous command"
- 70% = "Understood, but missing some details"
- 40% = "Very ambiguous, need clarification"

**Risk** = "How dangerous is this action?"
- LOW = "Routine, reversible"
- MEDIUM = "Moderate impact"
- HIGH = "Irreversible, sensitive keywords"
- CRITICAL = "Dangerous, requires override"

Decision depends on BOTH:
- HIGH confidence + LOW risk = **ACT**
- LOW confidence + ANY risk = **ASK/CONFIRM**
- HIGH risk + sensitive = **CONFIRM** (always)

### 3. The Five Decision Modes

| Mode | Trigger | Response |
|------|---------|----------|
| **ACT** | Confidence ≥75%, low risk | Execute immediately |
| **ASK** | Missing required fields | Ask clarifying questions |
| **CONFIRM** | High risk OR low confidence | Require human approval |
| **HOLD** | Very low confidence <50% | Wait for clarification |
| **DENY** | Safety policy violation | Reject and explain why |

---

## 🎯 Next Steps

### Immediate (Week 1)
1. ✅ Create ARCHITECTURE.md
2. ✅ Refactor main.py to use execution_engine
3. ✅ Create execution_engine.py
4. ⏳ Create tool_registry.py
5. ⏳ Create base_tool.py

### Short-term (Week 2-3)
1. Implement concrete tools (calendar, email, search)
2. Create military application layer
3. Add unit tests for core modules
4. Test with real commands

### Medium-term (Week 4+)
1. Implement office and smart_home layers
2. Add Supabase integration
3. Implement memory engine
4. Build safety engine
5. Create admin dashboard

---

## 🤝 Contributing New Domains

To add a new domain (e.g., "retail"):

1. **Extend Intent Recognition** (intent_engine.py)
   ```python
   if domain == "retail":
       # Add retail-specific entity extraction
   ```

2. **Create Application Layer** (applications/retail_layer.py)
   ```python
   def translate_retail_command(command: str) -> Intent:
       # Translate retail terminology
   ```

3. **Register Custom Tools** (tools/tool_registry.py)
   ```python
   if domain == "retail":
       tools = [
           ("ORDER", inventory_tool),
           ("SEARCH", catalog_tool),
           ("NOTIFY", customer_tool)
       ]
   ```

4. **Test** 
   ```bash
   POST /api/command
   {"user_input": "Order 50 units of product X", "domain": "retail"}
   ```

---

## 📚 Reference Documents

- [ARCHITECTURE.md](ARCHITECTURE.md) — Complete system design
- [WORKFLOW_LOGIC.md](WORKFLOW_LOGIC.md) — Old SAINIK workflow (legacy)
- [README.md](README.md) — Project overview

---

**This refactoring transforms SAINIK from a military-specific agent into a universal autonomous action framework that can power any domain.**
