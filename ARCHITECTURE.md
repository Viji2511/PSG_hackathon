# ARCHITECTURE — Context-Aware Autonomous Action Agent Framework

## 🎯 Problem Statement

Most AI assistants only **describe** actions instead of **executing** them. This framework builds a **true autonomous action agent** that:

- ✅ Interprets ambiguous instructions
- ✅ Asks clarification only when necessary
- ✅ Maintains context across conversations
- ✅ Handles multi-step instructions
- ✅ Decides when to **ACT, ASK, or CONFIRM**
- ✅ Executes real actions via integrations
- ✅ Behaves like a reliable assistant, not a chatbot

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│           CONTEXT-AWARE AUTONOMOUS ACTION AGENT                 │
└─────────────────────────────────────────────────────────────────┘

USER INPUT (Voice or Text)
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: INTENT UNDERSTANDING                                   │
│ Purpose: Parse natural language → structured intents            │
│ Module: core/intent_engine.py                                    │
│ Output: Intent(tasks, entities, missing_fields, confidence)     │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: CONTEXT MANAGEMENT                                     │
│ Purpose: Load session context, track state                      │
│ Module: core/context_manager.py                                  │
│ Storage: Supabase PostgreSQL (or in-memory)                     │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: DECISION ENGINE ⭐ CORE INNOVATION                     │
│ Purpose: Decide ACT / ASK / CONFIRM / HOLD / DENY              │
│ Module: core/decision_engine.py                                  │
│ Logic: Risk assessment + confidence analysis + safety checks   │
│ Output: DecisionResult(mode, confidence, reasoning)             │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: TASK PLANNING                                          │
│ Purpose: Break down complex instructions into steps             │
│ Module: core/task_planner.py                                     │
│ Output: ExecutionPlan(tasks, execution_order)                   │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 5: TOOL SELECTION                                         │
│ Purpose: Map tasks to tools                                     │
│ Module: tools/tool_registry.py                                   │
│ Tools: Calendar, Email, Search, Reminder, ...                  │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 6: SAFETY VALIDATION                                      │
│ Purpose: Final safety checks before execution                   │
│ Module: safety/safety_engine.py                                  │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 7: EXECUTION                                              │
│ Purpose: Execute tool calls                                     │
│ Module: tools/execution_engine.py                                │
│ Action: Call external APIs, update local systems                │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 8: MEMORY UPDATE                                          │
│ Purpose: Store action results and learnings                     │
│ Module: memory/memory_engine.py                                  │
│ Storage: Supabase vector embeddings for similarity search       │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 9: RESPONSE GENERATION                                    │
│ Purpose: Format result for user                                 │
│ Module: response/response_engine.py                              │
│ Output: Structured response with decision, confidence, result   │
└─────────────────────────────────────────────────────────────────┘
    ↓
RESPONSE TO USER
```

---

## 📁 Project Structure

```
psg_hackathon/
├── core/                          # ⭐ Core decision-making modules (PRIORITY 1)
│   ├── __init__.py
│   ├── intent_engine.py           # Parse natural language → Intent
│   ├── decision_engine.py         # ACT/ASK/CONFIRM logic
│   ├── context_manager.py         # Session + state management
│   └── task_planner.py            # Multi-step task planning
│
├── tools/                         # Tool integrations (PRIORITY 2)
│   ├── __init__.py
│   ├── base_tool.py              # Abstract tool interface
│   ├── tool_registry.py          # Maps intent → tool
│   ├── calendar_tool.py          # Schedule events
│   ├── email_tool.py             # Send emails/messages
│   ├── search_tool.py            # Search documents
│   ├── reminder_tool.py          # Create reminders
│   └── execution_engine.py       # Execute tool calls
│
├── safety/                        # Safety & risk assessment
│   ├── __init__.py
│   └── safety_engine.py          # Confidence, risk, validation
│
├── memory/                        # Persistence & learning
│   ├── __init__.py
│   └── memory_engine.py          # Store, retrieve, similarity search
│
├── response/                      # Response formatting
│   ├── __init__.py
│   └── response_engine.py        # Structured outputs
│
├── applications/                  # Domain-specific layers
│   ├── __init__.py
│   ├── military_layer.py         # Military operations use case
│   ├── office_layer.py           # Office/business use case
│   └── smart_home_layer.py       # Smart home use case
│
├── src/                           # FastAPI application (refactored)
│   ├── main.py                   # FastAPI endpoints
│   └── models.py                 # Pydantic schemas
│
├── config/
│   └── settings.py               # Configuration
│
├── frontend/
│   └── index.html                # Dashboard (updated)
│
├── requirements.txt              # Dependencies
├── README.md                      # Project overview
├── ARCHITECTURE.md               # This file
└── WORKFLOW_LOGIC.md             # Detailed workflow
```

---

## 🔧 Core Modules Explained

### MODULE 1: INTENT ENGINE
**Purpose:** Convert natural language → structured intents

```python
# Input
"Schedule surveillance tomorrow and remind team"

# Output
Intent(
    intent_id="intent_001",
    intent_type=IntentType.MULTI_TASK,
    tasks=[
        Task(type=TaskType.SCHEDULE, parameters={"action": "surveillance", "time": "tomorrow"}),
        Task(type=TaskType.REMIND, parameters={"target": "team"})
    ],
    entities=[
        Entity(name="time", type="temporal", value="tomorrow", confidence=0.95),
        Entity(name="action", type="action", value="surveillance", confidence=0.90)
    ],
    missing_fields=["location"],
    confidence=0.82
)
```

**Key Methods:**
- `parse_intent()` — Main entry point
- `_extract_entities()` — Named entity recognition
- `_detect_missing_fields()` — Identify required but missing parameters
- `_calculate_confidence()` — Score interpretation quality

---

### MODULE 2: DECISION ENGINE ⭐
**Purpose:** Core innovation - decide when to ACT, ASK, CONFIRM, HOLD, or DENY

```python
# Decision Rules (Priority Order)
if missing_fields:
    DECISION = ASK  # Ask for clarification
elif risk_level == CRITICAL:
    DECISION = DENY  # Refuse unsafe action
elif risk_level == HIGH and is_sensitive:
    DECISION = CONFIRM  # Require human approval
elif confidence < 0.70:
    DECISION = CONFIRM  # Require explicit approval
else:
    DECISION = ACT  # Execute immediately
```

**Decision Modes:**

| Mode | Meaning | Example |
|------|---------|---------|
| **ACT** | Clear, safe, executable | "Schedule patrol tomorrow at Sector 4" (all info provided) |
| **ASK** | Missing critical info | "Schedule patrol" (missing location/sector) |
| **CONFIRM** | High-risk/sensitive | "Send emergency alert" (requires human sign-off) |
| **HOLD** | Low confidence | Ambiguous input needing verification |
| **DENY** | Unsafe pattern | Dangerous operation detected |

**Confidence Thresholds:**
- `confidence >= 0.75` → ACT (75% confident)
- `0.70 - 0.75` → CONFIRM (moderate, need approval)
- `confidence < 0.70` → CONFIRM or HOLD (too uncertain)

---

### MODULE 3: CONTEXT MANAGER
**Purpose:** Track session state, conversation history, pending actions

**Session State:**
```python
SessionContext(
    session_id="session_abc123",
    user_id="commander_001",
    domain="military",
    
    # Current state
    current_intent=parsed_intent,
    current_decision="confirm",
    pending_confirmation={
        "action_id": "action_001",
        "description": "Send high-priority alert",
        "risk_level": "high"
    },
    
    # History
    action_history=[
        ActionRecord(action_id="act_001", command="...", decision="act", status="executed"),
        ...
    ]
)
```

**Storage Options:**
- **Local (dev):** In-memory dictionary
- **Production:** Supabase PostgreSQL

**Key Methods:**
- `create_session()` — Start new session
- `get_context()` — Load session state
- `update_context()` — Update state
- `store_action()` — Log action to history
- `set_pending_confirmation()` — Mark action awaiting approval

---

### MODULE 4: TASK PLANNER
**Purpose:** Break down complex instructions into executable steps

**Example:**
```
Input: "Prepare surveillance operation"

Output:
Step 1: Check available units
Step 2: Schedule mission  
Step 3: Send notification to command
Step 4: Set tactical reminder

Estimated duration: ~15 seconds
```

**Domain-Aware Decomposition:**

**Military:**
- "Prepare surveillance" → [check units] → [schedule] → [notify] → [set reminder]
- "Schedule patrol" → [schedule] → [notify]

**Office:**
- "Reschedule meeting" → [cancel] → [create new] → [notify]
- "Prepare meeting" → [create] → [invite] → [set reminder]

**Smart Home:**
- "Automate morning" → [lights on] → [coffee] → [notification]

---

## 🎛️ Decision Engine: Deep Dive

### The ACT/ASK/CONFIRM Logic

**Scenario 1: Complete Information → ACT**
```
Command: "Schedule patrol Sector 4 tomorrow"
Analysis:
  ✓ All required fields: location (Sector 4), time (tomorrow), action (patrol)
  ✓ Confidence: 90%
  ✓ Risk: Low
  ✓ Safe pattern
Decision: ACT
Response: "✓ Patrol scheduled for Sector 4 tomorrow"
```

**Scenario 2: Missing Parameter → ASK**
```
Command: "Schedule patrol tomorrow"
Analysis:
  ✗ Missing: location/sector
  ? Confidence: 60%
Decision: ASK
Clarification: "Which sector? (Sector 1, 2, 3, 4, ...)"
```

**Scenario 3: Sensitive Operation → CONFIRM**
```
Command: "Send high-priority alert to all units"
Analysis:
  ✓ Fields present
  ✓ Confidence: 85%
  ⚠ Sensitive keywords: "alert", "all units"
  ⚠ Risk: HIGH
Decision: CONFIRM
Gate: 🔴 "HUMAN CONFIRMATION REQUIRED
  Action: Send alert to all units
  Risk: HIGH
  Type CONFIRM to authorize"
```

**Scenario 4: Low Confidence → HOLD/CONFIRM**
```
Command: "Alert thing about stuff"
Analysis:
  ? Ambiguous terminology
  ? Confidence: 35%
  ? Cannot interpret safely
Decision: HOLD or CONFIRM
Response: "I'm not confident in this interpretation. Can you clarify?"
```

---

## 🛠️ Tool Registry Pattern

Tools are unified under a common interface:

```python
class BaseTool:
    def execute(self, parameters: Dict) -> Dict:
        """Execute tool with parameters, return result"""
        pass

# Implementations
calendar_tool.schedule_event(start_time=..., location=...)
email_tool.send_message(recipient=..., content=...)
search_tool.search(query=..., scope=...)
reminder_tool.create_reminder(event=..., time=...)
```

**Tool Registry Maps:**
```
TaskType.SCHEDULE → calendar_tool
TaskType.SEND    → email_tool
TaskType.SEARCH  → search_tool
TaskType.REMIND  → reminder_tool
```

---

## 🔐 Safety & Validation

**Safety Engine Checks:**

1. **Confidence Threshold**
   - Allow ACT if `confidence >= 75%`
   - Require CONFIRM if `confidence < 75%`
   - Require HOLD if `confidence < 50%`

2. **Risk Assessment**
   - Low: Routine operations
   - Medium: Moderate impact
   - High: Irreversible/sensitive
   - Critical: Dangerous patterns

3. **Sensitive Keywords**
   - "delete", "emergency", "immediate", "critical"
   - "engagement", "strike", "fire", "launch"
   - These trigger CONFIRM

4. **Unsafe Patterns**
   - No human review for critical actions
   - Irreversible actions without CONFIRM
   - Broad scope without verification

---

## 💾 Memory & Learning

**Memory Engine stores:**

1. **Action History** — Every command executed
2. **Similar Requests** — Vector embeddings for pattern matching
3. **Failure Cases** — Learn from errors
4. **User Preferences** — How user likes decisions made

**Example:**
```
User previously said: "For patrol, always use Sector 3"
New command: "Schedule patrol tomorrow"
Memory retrieves: Similar request from 2 days ago

Agent: "Should I use Sector 3 again? (Based on previous preference)"
```

---

## 🌐 Supabase Integration

**Tables:**

```sql
-- Sessions
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id VARCHAR,
    context_json JSONB,
    domain VARCHAR,
    created_at TIMESTAMP,
    last_updated TIMESTAMP
);

-- Actions/Logs
CREATE TABLE action_logs (
    log_id UUID PRIMARY KEY,
    session_id UUID,
    command VARCHAR,
    decision VARCHAR,
    confidence FLOAT,
    status VARCHAR,
    result JSONB,
    timestamp TIMESTAMP
);

-- Memory/Embeddings
CREATE TABLE memory (
    id UUID PRIMARY KEY,
    embedding vector(1536),  -- OpenAI embeddings
    text VARCHAR,
    metadata JSONB,
    created_at TIMESTAMP
);
```

---

## 🎯 Domain-Agnostic Design

**The framework is generic and applies to ANY domain:**

### Military Operations
- Tool: `calendar_tool` → Task: Schedule mission
- Tool: `email_tool` → Task: Send SITREP
- Tool: `search_tool` → Task: Retrieve intelligence
- Tool: `reminder_tool` → Task: Tactical alert

### Office / Business
- Tool: `calendar_tool` → Task: Schedule meeting
- Tool: `email_tool` → Task: Send email
- Tool: `search_tool` → Task: Find documents
- Tool: `reminder_tool` → Task: Set deadline

### Smart Home
- Tool: `calendar_tool` → Task: Schedule automation
- Tool: `email_tool` → Task: Send notifications
- Tool: `search_tool` → Task: Find settings
- Tool: `reminder_tool` → Task: Alert user

**Domain Layer Example:**
```python
# applications/military_layer.py
def translate_military_command(command: str) -> Intent:
    """Translate military jargon → generic intent"""
    
    if "patrol" in command:
        task_type = TaskType.SCHEDULE  # Patrol = schedule
    elif "sitrep" in command:
        task_type = TaskType.SEND      # SITREP = send
    elif "intelligence" in command:
        task_type = TaskType.SEARCH    # Intel = search
    
    return translate_to_generic_intent(...)
```

---

## 📊 Response Format

All responses follow same structure:

```json
{
  "decision_mode": "act",
  "confidence": 0.85,
  "reasoning": "All required fields provided. Confidence 85%.",
  "action_taken": "Mission scheduled for Sector 4 tomorrow at 0800 hrs",
  "next_steps": ["Execute mission", "Log to audit trail"],
  "requires_clarification": [],
  "risk_level": "low"
}
```

---

## 🚀 Example Workflows

### Workflow 1: Simple Command (ACT)
```
User: "Schedule patrol Sector 4 tomorrow"
↓
Intent Engine: "Schedule" action, time="tomorrow", location="Sector 4"
↓
Decision Engine: All fields present, confidence=90%, decision=ACT
↓
Task Planner: 1 task - schedule mission
↓
Tool Registry: calendar_tool.schedule()
↓
Response: "✓ Patrol scheduled for Sector 4 tomorrow"
```

### Workflow 2: Ambiguous Command (ASK)
```
User: "Schedule patrol tomorrow"
↓
Intent Engine: time="tomorrow", location=MISSING, confidence=60%
↓
Decision Engine: Missing field, decision=ASK
↓
Response: "Which sector? (Sector 1, 2, 3, 4)"
↓
User: "Sector 4"
↓
[Back to Workflow 1]
```

### Workflow 3: Multi-Step (Plan)
```
User: "Prepare surveillance operation"
↓
Intent Engine: "Prepare" = multi-task
↓
Task Planner: [check units] → [schedule] → [notify] → [remind]
↓
For each task: Decision → Tool → Execute
↓
Response: 
  ✓ Step 1: Units checked
  ✓ Step 2: Mission scheduled
  ✓ Step 3: Command notified
  ✓ Step 4: Reminder set
```

### Workflow 4: Sensitive Action (CONFIRM)
```
User: "Send emergency alert to all units"
↓
Intent Engine: "Send" action, recipient="all units", priority="emergency"
↓
Decision Engine: Sensitive keywords, HIGH risk, decision=CONFIRM
↓
Response: 🔴 "HUMAN CONFIRMATION REQUIRED
  Type CONFIRM to authorize alert to all units"
↓
User: "CONFIRM"
↓
Execution: Send alert
↓
Response: "✅ Alert sent to all units"
```

---

## 🏃 Implementation Roadmap

**Phase 1: Core Modules (DONE)**
- ✅ Intent Engine
- ✅ Decision Engine
- ✅ Context Manager
- ✅ Task Planner

**Phase 2: Tool System (NEXT)**
- Tool Registry
- Calendar Tool
- Email Tool
- Search Tool
- Reminder Tool
- Execution Engine

**Phase 3: Safety & Memory (LATER)**
- Safety Engine
- Memory Engine
- Response Engine

**Phase 4: Applications (FINAL)**
- Military Layer
- Office Layer
- Smart Home Layer
- FastAPI Integration

---

## 💻 Tech Stack

- **Backend:** Python 3.10+, FastAPI
- **Data:** Pydantic (type-safe), SQLAlchemy (ORM)
- **Database:** Supabase PostgreSQL + pgvector
- **LLM:** OpenAI (function calling) or local LLM
- **Frontend:** HTML, CSS, minimal JavaScript
- **DevOps:** Docker, GitHub Actions

---

## 🎓 Key Concepts

| Concept | Meaning |
|---------|---------|
| **Intent** | Parsed user command with tasks, entities, confidence |
| **Task** | Atomic action to execute (schedule, send, search, etc.) |
| **Decision** | Autonomous choice (ACT/ASK/CONFIRM/HOLD/DENY) |
| **Context** | Session state, history, preferences |
| **Plan** | Step-by-step execution sequence |
| **Tool** | External API or system integration |
| **Risk** | Safety assessment (low/medium/high/critical) |
| **Memory** | Stored learnings for future decisions |

---

## ✅ Quality Assurance

**Validation:**
- Confidence scoring for all intents
- Risk assessment for all actions
- Type hints on all code
- Docstrings on all functions
- Clean separation of concerns

**Testing (to-do):**
- Unit tests for each module
- Integration tests for workflows
- Safety validation tests
- Domain-specific test cases

---

**This architecture enables TRUE autonomous action – not just description.**

🔱 **SAINIK + Autonomous Action Framework = Production-Ready Agent**
