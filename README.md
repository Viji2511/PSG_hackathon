# SAMARAN — Smart AI for National Intelligence & Command

## Military Action Agent · India Defense Context · PS3
**AI4Dev '26 · PSG College of Technology**

---

## Overview
SAMARAN is an autonomous military action agent designed to assist Indian Armed Forces commanders by executing real-time operations across three strategic theatres:

- **Line of Control (LoC)** — Jammu & Kashmir
- **Eastern Sector** — Arunachal Pradesh  
- **Maritime** — Arabian Sea / Bay of Bengal

---

## Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI** — High-performance API framework
- **LangChain / Hugging Face Transformers** — LLM orchestration
- **SQLAlchemy** — ORM for database operations
- **Pydantic** — Data validation

### Database & Cache
- **SQLite** (dev) / **PostgreSQL** (production)
- **Redis** — Session state & threat level caching

### Frontend
- **React.js / Vue.js** — Command center dashboard
- **WebSocket (Socket.IO)** — Real-time threat alerts
- **TailwindCSS** — Military-themed UI

### DevOps
- **Docker** — Containerization
- **GitHub Actions** — CI/CD pipeline
- **Environment Variables** — Secure configuration

---

## Core Features

### Five Operational Actions
1. **Mission Scheduling** — Deploy and track operations
2. **Secure Communications** — Send SITREPs to command centers
3. **Intelligence Retrieval** — Query mission archives
4. **Tactical Reminders** — Set critical alerts
5. **Context Briefing** — Real-time operational status

### Threat Level System
- **ROUTINE** → **GUARDED** → **ELEVATED** → **HIGH** → **CRITICAL**
- Auto-escalation based on theatre-specific triggers
- Real-time commander notifications

### Human Confirmation Gate
- Mandatory sign-off for lethal/irreversible actions
- Mission risk assessment matrix
- Audit trail logging

---

## Project Structure
```
psg_hackathon/
├── README.md               # This file
├── .gitignore              # Git configuration
├── requirements.txt        # Python dependencies (to be added)
├── config/                 # Configuration module
├── src/                    # Core agent logic
├── tests/                  # Unit tests
├── data/                   # Datasets & mission data
├── frontend/               # React/Vue frontend
└── logs/                   # Operation logs
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Git
- GitHub account (for version control)

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd psg_hackathon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (to be created)
pip install -r requirements.txt
```

### Run SAINIK
```bash
# Start FastAPI server
uvicorn src.main:app --reload
```

The agent will initialize with theatre selection and await your orders.

---

## Operational Context

### Threat Escalation Rules
- **LoC**: 2+ infiltration reports in 6 hours → **HIGH**
- **Eastern Sector**: LAC crossing confirmed → **ELEVATED**
- **Maritime**: Unidentified submarine contact → **HIGH**; No response in 30 min → **CRITICAL**

### Units Available
- **BSF** — Border Security Force
- **Indian Army** — Ground operations
- **IAF** — Air Force assets
- **Naval Command** — Maritime operations

---

## Security & Compliance
- All actions logged to audit trail
- Classified SITREP handling
- Encrypted communications (simulated)
- Human-in-the-loop for critical decisions

---

## Contributing
Team members: PSG Hackathon Participants

---

## License
Internal Use Only — Indian Armed Forces

---

**SAINIK READY FOR DEPLOYMENT**
