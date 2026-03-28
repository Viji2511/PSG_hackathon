const API = "http://localhost:8000";
const SESSION = "sainik-" + Date.now();

const DEMO_STEPS = [
  { label: "Ops status briefing",      cmd: "Give me current ops status" },
  { label: "Intel retrieval",          cmd: "Find infiltration reports from Tawang sector in last 72 hours" },
  { label: "Report LAC crossing",      cmd: "We have a confirmed LAC crossing at Grid 4482" },
  { label: "Schedule surveillance",    cmd: "Schedule aerial surveillance over Grid 4482 at 0330 hrs" },
  { label: "Ambiguous strike command", cmd: "Strike the position" },
  { label: "Authorise engagement",     cmd: "Authorise precision engagement at Grid 4482" },
  { label: "Send SITREP",              cmd: "Send SITREP to Eastern Command about the Grid 4482 engagement" },
  { label: "Set reminder",             cmd: "Remind me to check drone surveillance feed at 0500 hrs" }
];

let currentStep = 0;
let isWaiting = false;

window.onload = () => {
  startClock();
  buildDemoSteps();
};

// ── CLOCK ──
function startClock() {
  const el = document.getElementById('clock');
  function tick() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2,'0');
    const m = String(now.getMinutes()).padStart(2,'0');
    el.textContent = `${h}${m} HRS`;
  }
  tick();
  setInterval(tick, 1000);
}

// ── DEMO STEPS ──
function buildDemoSteps() {
  const container = document.getElementById('demoSteps');
  DEMO_STEPS.forEach((step, i) => {
    const btn = document.createElement('button');
    btn.className = 'step-btn';
    btn.id = `step-${i}`;
    btn.innerHTML = `
      <span class="step-num">STEP ${i + 1}</span>
      <span class="step-title">${step.label}</span>
    `;
    btn.onclick = () => injectDemo(i);
    container.appendChild(btn);
  });
}

function injectDemo(index) {
  if (isWaiting) return;
  const input = document.getElementById('msgInput');
  input.value = DEMO_STEPS[index].cmd;
  document.querySelectorAll('.step-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`step-${index}`)?.classList.add('active');
  sendMessage();
}

// ── THEATRE ──
async function setTheatre(theatre) {
  document.getElementById('theatreSelect').style.display = 'none';

  try {
    const res = await fetch(`${API}/set-theatre`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: SESSION, theatre })
    });
    const data = await res.json();
    updateState(data.state);

    const labels = {
      LOC: 'Line of Control — J&K',
      EASTERN: 'Eastern Sector — Arunachal Pradesh',
      MARITIME: 'Maritime — Arabian Sea / Bay of Bengal'
    };
    document.getElementById('statTheatre').textContent = theatre;

    appendMessage('sainik',
      `SAINIK ONLINE — Smart AI for National Intelligence & Command\n` +
      `─────────────────────────────────────────\n` +
      `Theatre:      ${labels[theatre]}\n` +
      `Threat Level: ROUTINE\n` +
      `Units:        Allocated and on standby\n` +
      `─────────────────────────────────────────\n` +
      `Awaiting your orders, Commander.`
    );
  } catch(e) {
    appendMessage('sainik', 'COMMS ERROR — Cannot reach backend. Ensure server is running on port 8000.');
  }
}

// ── SEND MESSAGE ──
async function sendMessage() {
  if (isWaiting) return;
  const input = document.getElementById('msgInput');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  isWaiting = true;
  appendMessage('user', msg);
  showTyping();

  try {
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: SESSION, message: msg })
    });
    const data = await res.json();
    hideTyping();
    appendMessage('sainik', data.reply);
    updateState(data.state);

    // mark step done
    if (currentStep < DEMO_STEPS.length) {
      document.getElementById(`step-${currentStep}`)?.classList.add('done');
      currentStep++;
    }
  } catch(e) {
    hideTyping();
    appendMessage('sainik', 'COMMS ERROR — Backend unreachable. Check server on port 8000.');
  } finally {
    isWaiting = false;
  }
}

// ── CONFIRM / CANCEL ──
async function sendConfirm() {
  document.getElementById('confirmGate').style.display = 'none';
  document.getElementById('inputRow').style.display = 'flex';
  document.getElementById('msgInput').value = 'CONFIRM';
  await sendMessage();
}

function sendCancel() {
  document.getElementById('confirmGate').style.display = 'none';
  document.getElementById('inputRow').style.display = 'flex';
  appendMessage('sainik', 'Action cancelled. No changes made. Standing by for next orders, Commander.');
}

// ── STATE UPDATE ──
function updateState(state) {
  if (!state) return;

  // threat badge + color
  const level = (state.threat_level || 'ROUTINE').toUpperCase();
  const badge = document.getElementById('threatBadge');
  badge.textContent = level;
  badge.className = 'threat-badge threat-' + level.toLowerCase();

  const statThreat = document.getElementById('statThreat');
  statThreat.textContent = level;
  const colorMap = { ROUTINE:'green', GUARDED:'', ELEVATED:'amber', HIGH:'red', CRITICAL:'red' };
  statThreat.className = 'status-val ' + (colorMap[level] || '');

  // mission
  if (state.active_mission) {
    document.getElementById('statMission').textContent = state.active_mission;
  }

  // units
  if (state.units && state.units.length > 0) {
    document.getElementById('unitsList').innerHTML = state.units.map(u =>
      `<div class="unit-item"><div class="unit-dot"></div>${u}</div>`
    ).join('');
  }

  // confirmation gate
  if (state.pending_confirmation) {
    document.getElementById('confirmGate').style.display = 'flex';
    document.getElementById('inputRow').style.display = 'none';
  } else {
    document.getElementById('confirmGate').style.display = 'none';
    document.getElementById('inputRow').style.display = 'flex';
  }

  // audit log
  if (state.audit_log && state.audit_log.length > 0) {
    document.getElementById('auditLog').innerHTML = [...state.audit_log].reverse().map(entry =>
      `<div class="audit-entry">
        <span class="audit-time">${entry.time}</span>
        <span class="audit-action">${entry.action}</span>
      </div>`
    ).join('');
  }
}

// ── CHAT RENDERING ──
function appendMessage(from, text) {
  const area = document.getElementById('chatArea');
  const div = document.createElement('div');
  div.className = `msg msg-${from}`;

  const isAlert = text.includes('HUMAN CONFIRMATION REQUIRED');
  const isWarn  = text.includes('THREAT ESCALATION');
  const isGood  = text.includes('ACTION AUTHORISED');

  div.innerHTML = `
    <div class="msg-from">${from === 'user' ? 'COMMANDER' : 'SAINIK'}</div>
    <div class="msg-bubble ${isAlert ? 'bubble-alert' : isWarn ? 'bubble-warn' : ''}">
      ${formatText(text)}
    </div>
  `;

  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
}

function formatText(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
    .replace(/─{3,}/g, '<hr class="divider">')
    .replace(/(⚠[^\n<]*)/g, '<span class="highlight-amber">$1</span>')
    .replace(/(🔴[^\n<]*)/g, '<span class="highlight-red">$1</span>')
    .replace(/(✅[^\n<]*)/g, '<span class="highlight-green">$1</span>')
    .replace(/(THREAT ESCALATION[^\n<]*)/g, '<span class="highlight-amber">$1</span>')
    .replace(/(HUMAN CONFIRMATION REQUIRED)/g, '<span class="highlight-red">$1</span>')
    .replace(/(ACTION AUTHORISED[^\n<]*)/g, '<span class="highlight-green">$1</span>');
}

function showTyping() {
  const area = document.getElementById('chatArea');
  const div = document.createElement('div');
  div.id = 'typing';
  div.className = 'msg msg-sainik';
  div.innerHTML = `
    <div class="msg-from">SAINIK</div>
    <div class="msg-bubble typing-dots"><span></span><span></span><span></span></div>
  `;
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
}

function hideTyping() {
  document.getElementById('typing')?.remove();
}