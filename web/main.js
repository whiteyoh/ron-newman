const buttons = document.getElementById('buttons');
const log = document.getElementById('log');
const apiState = document.getElementById('api-state');
const meta = document.getElementById('meta');
const useCaseOptions = document.getElementById('use-case-options');
const selectionLabel = document.getElementById('selection-label');
const confirmBtn = document.getElementById('confirm-btn');
const downloadArtifactBtn = document.getElementById('download-artifact');
const useCaseModal = document.getElementById('use-case-modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');
const modalCloseBtn = document.getElementById('modal-close');
const contextInput = document.getElementById('context-input');
const theatreSteps = document.getElementById('theatre-steps');
const replayBtn = document.getElementById('replay-btn');
const taskboardEl = document.getElementById('taskboard');
let lastReplaySteps = [];


const entry = document.getElementById('entry');
const app = document.getElementById('app');
const startBtn = document.getElementById('start-btn');

function updateLevelButtonsVisibility() {
  buttons.classList.toggle('hidden', !confirmedUseCase);
}

let latestArtifact = null;
let runInProgress = false;

function enterDemo() {
  entry.classList.add('hidden');
  app.classList.remove('hidden');
}

startBtn.addEventListener('click', enterDemo);

let selectedUseCase = null;
let confirmedUseCase = null;
let selectedUseCaseContext = '';

function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

function clearArtifact() {
  latestArtifact = null;
  downloadArtifactBtn.disabled = true;
}

function clearOutput(message = 'Output cleared. Select a level to begin.') {
  log.innerHTML = '';
  appendMessage('system', message);
  meta.textContent = 'Run a level to verify API path, model, and request id.';
  apiState.innerHTML = '<span class="pill">Waiting</span>';
  clearArtifact();
}

function appendMessage(role, text) {
  const item = document.createElement('div');
  item.className = `msg ${role}`;
  item.textContent = text;
  log.appendChild(item);
  log.scrollTop = log.scrollHeight;
}

function renderThinkingMessage(message = 'Glytch is thinking...') {
  const item = document.createElement('div');
  item.className = 'msg ai';
  item.innerHTML = `<span class="thinking"><img src="assets/robotic-person.svg" alt="Thinking" class="robot-spinner" />${message}</span>`;
  log.appendChild(item);
  log.scrollTop = log.scrollHeight;
}

function inferRole(line) {
  const l = line.toLowerCase();
  if (l.includes('prompt:') || l.includes('instruction:') || l.includes('question:') || l.includes('goal:') || l.includes('task expression:')) return 'user';
  if (l.includes('model') || l.includes('answer') || l.includes('draft') || l.includes('coordinator output') || l.includes('plan:') || l.includes('agenda')) return 'ai';
  return 'system';
}

async function streamLines(lines){
  log.innerHTML = '';
  for (const line of lines){
    appendMessage(inferRole(line), line);
    await sleep(350);
  }
}

function createArtifact(level, lines) {
  const stamp = new Date().toISOString();
  latestArtifact = `Glytch Export\nGenerated: ${stamp}\nLevel: ${level}\nUse case: ${confirmedUseCase || 'n/a'}\n\n${lines.join('\n')}`;
  downloadArtifactBtn.disabled = false;
}

function downloadArtifact() {
  if (!latestArtifact) return;
  const blob = new Blob([latestArtifact], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `glytch-artifact-${new Date().toISOString().slice(0,10)}.txt`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

downloadArtifactBtn.addEventListener('click', downloadArtifact);

function setLevelButtonsDisabled(disabled) {
  document.querySelectorAll('#buttons button').forEach((btn) => { btn.disabled = disabled; });
}

async function runLevel(level){
  if (!confirmedUseCase) {
    clearOutput('Please confirm a use case direction first.');
    return;
  }

  if (runInProgress) return;
  runInProgress = true;
  setLevelButtonsDisabled(true);
  apiState.innerHTML = '<span class="pill">Running…</span>';
  log.innerHTML = '';
  renderThinkingMessage('Glytch is thinking...');

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 60000);
    const res = await fetch('/api/run', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ level, use_case: confirmedUseCase, use_case_context: selectedUseCaseContext }), signal: controller.signal
    });
    clearTimeout(timeout);
    const contentType = res.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
      ? await res.json()
      : { error: await res.text() };

  const backend = data.backend || {};
  const isConfigured = Boolean(backend.configured) && res.ok;
  apiState.innerHTML = `<span class="pill ${isConfigured ? 'ok' : 'err'}">${isConfigured ? 'OpenAI API Connected' : 'OpenAI API Not Connected'}</span>`;

  meta.textContent = `request_id=${data.request_id || 'n/a'} · provider=${backend.provider || 'n/a'} · model=${backend.model || 'n/a'} · base_url=${backend.base_url || 'n/a'}`;

  if (!res.ok) {
    log.innerHTML = '';
    appendMessage('system', `Request failed (${res.status}): ${data.error || 'unknown error'}`);
    clearArtifact();
    return;
  }

  const lines = data.lines || ['No output lines returned.'];
  renderTheatre(data);
  if (data.agenticness) {
    lines.unshift(`Why this score is justified: ${data.agenticness.explanation}`);
    lines.unshift(`Yegge alignment score: ${data.agenticness.yegge_alignment_score}/10`);
    lines.unshift(`Closest Yegge stage: ${data.agenticness.closest_yegge_stage}`);
    lines.unshift(`Agenticness score: ${data.agenticness.score}/10`);
  }
  createArtifact(level, lines);
  await streamLines(lines);
  } catch (err) {
    log.innerHTML = "";
    const timedOut = err.name === "AbortError";
    apiState.innerHTML = `<span class="pill err">${timedOut ? "Request timed out" : "OpenAI API Not Connected"}</span>`;
    appendMessage('system', timedOut
      ? "Request timed out after 60 seconds. Please try again or use a lighter prompt/context."
      : `Request failed: ${err.message}`);
    clearArtifact();
  } finally {
    runInProgress = false;
    setLevelButtonsDisabled(false);
  }
}

function renderUseCases(data) {
  useCaseOptions.textContent = '';
  Object.entries(data).forEach(([key, text], index) => {
    const [summary] = text.split('.');
    const shortSummary = `${summary}.`;
    const option = document.createElement('button');
    option.className = 'option';
    option.innerHTML = `
      <strong>${index + 1}. ${key.replaceAll('_', ' ')}</strong>
      <div class="muted">${shortSummary}</div>
      <div style="margin-top:0.5rem; display:flex; gap:0.5rem;">
        <span class="pill">Select</span>
        <span class="pill ghost modal-trigger">More context</span>
      </div>
    `;
    option.querySelector('.modal-trigger').addEventListener('click', (event) => {
      event.stopPropagation();
      modalTitle.textContent = `Use case context: ${key.replaceAll('_', ' ')}`;
      modalBody.textContent = text;
      useCaseModal.classList.remove('hidden');
    });
    option.onclick = () => {
      selectedUseCase = key;
      selectedUseCaseContext = contextInput.value.trim();
      confirmedUseCase = null;
      confirmBtn.disabled = false;
      selectionLabel.textContent = `Selected (not confirmed): ${key.replaceAll('_', ' ')}${selectedUseCaseContext ? ` | context: ${selectedUseCaseContext}` : ''}`;
      document.querySelectorAll('.option').forEach((el) => el.classList.remove('active'));
      option.classList.add('active');
      clearOutput('Use case changed. Previous output cleared. Confirm direction to continue.');
      updateLevelButtonsVisibility();
    };
    useCaseOptions.appendChild(option);
  });
}

confirmBtn.onclick = () => {
  if (!selectedUseCase) {
    clearOutput("Select a use case before confirming direction.");
    return;
  }
  selectedUseCaseContext = contextInput.value.trim();
  confirmedUseCase = selectedUseCase;
  const friendlyName = selectedUseCase.replaceAll("_", " ");
  selectionLabel.textContent = `Confirmed direction: ${friendlyName}${selectedUseCaseContext ? ` | context: ${selectedUseCaseContext}` : ""}`;
  clearOutput("Direction confirmed. Choose a level to run.");
  updateLevelButtonsVisibility();
};
modalCloseBtn.onclick = () => useCaseModal.classList.add('hidden');

async function init(){
  try {
    const [levelsResponse, useCasesResponse, maturityResponse] = await Promise.all([fetch('/api/levels'), fetch('/api/use-cases'), fetch('/api/agentic-maturity')]);
    const levels = await levelsResponse.json();
    const useCases = await useCasesResponse.json();
    const maturity = await maturityResponse.json();
    if (!levelsResponse.ok || !levels.levels || !useCasesResponse.ok || !useCases.use_cases) return clearOutput('Could not load configuration.');
    renderUseCases(useCases.use_cases);
    renderMaturityCards(maturity.stages || []);
    renderQuiz();

    Object.entries(levels.levels).forEach(([k,v]) => {
      const btn = document.createElement('button');
      btn.textContent = `Level ${k}: ${v.name}`;
      btn.onclick = () => runLevel(Number(k));
      buttons.appendChild(btn);
    });
    updateLevelButtonsVisibility();
  } catch (err) {
    clearOutput(`Could not load configuration: ${err.message}`);
  }
}

init();


document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') useCaseModal.classList.add('hidden');
});


function renderAssessmentResult() {
  const selected = document.querySelector('input[name="selfcheck"]:checked')?.value;
  const out = document.getElementById('assessment-result');
  if (selected === 'prompt_only') out.textContent = 'You are around Level 1 to Level 2 depending on whether AI touches your files. Prompt-only use is not yet very agentic. Next step: supervised file edits with strict review.';
  else if (selected === 'ai_edits') out.textContent = 'You are around Level 2 to Level 4. Next step: move to bounded CLI agent runs with clear logs and stop conditions.';
  else if (selected === 'cli_agents') out.textContent = 'You are around Level 5 to Level 6. Next step: coordinate multiple specialist agents with explicit verification.';
  else out.textContent = 'You are around Level 7 to Level 8 maturity. Keep improving governance, policy checks, and rollback safety.';
}

function renderMaturityCards(stages) {
  const container = document.getElementById('maturity-cards');
  if (!container) return;
  container.innerHTML = '';
  stages.forEach((stage) => {
    const card = document.createElement('div');
    card.className = 'option';
    card.innerHTML = `<strong>Level ${stage.id}: ${stage.name}</strong><div class="muted">${stage.plain_english_summary}</div><div class="muted">Risk: ${stage.risk}</div><div class="muted">Level up: ${stage.next_step_to_level_up}</div>`;
    container.appendChild(card);
  });
}

function renderTheatre(data){
  theatreSteps.innerHTML='';
  (data.theatre_steps||[]).forEach((s)=>{const c=document.createElement('div'); c.className='option'; c.innerHTML=`<strong>${s.label}</strong><div class="muted">${s.summary}</div><div class="muted">${s.detail}</div>`; theatreSteps.appendChild(c);});
  lastReplaySteps = data.replay_steps || [];
  replayBtn.disabled = lastReplaySteps.length===0;
  taskboardEl.innerHTML='';
  if(data.taskboard){ const h=document.createElement('h3'); h.textContent='Level 8 Orchestrator Dashboard'; taskboardEl.appendChild(h); (data.taskboard.workers||[]).forEach(w=>{const c=document.createElement('div'); c.className='option'; c.innerHTML=`<strong>${w.worker}</strong><div class="muted">task: ${w.task}</div><div class="muted">status: ${w.status} · attempts: ${w.attempt}</div><div class="muted">verified: ${w.verified ? 'yes':'no'}</div>`; taskboardEl.appendChild(c);}); }
}
replayBtn?.addEventListener('click', async ()=>{ if(!lastReplaySteps.length) return; log.innerHTML=''; for(const step of lastReplaySteps){ appendMessage('system', `Replay: ${step}`); await sleep(300);} });
function renderQuiz(){ const q=document.getElementById('quiz-questions'); if(!q) return; const questions=[
'Do you only ask AI questions?', 'Do you let AI edit files?', 'Do you approve every action?', 'Do you let AI run tools?', 'Do you run agents in the terminal?', 'Do you run multiple agents at once?', 'Do you review outputs through a taskboard?', 'Do you have your own orchestration system?'
]; q.innerHTML=''; questions.forEach((text,i)=>{ const row=document.createElement('div'); row.innerHTML=`<label>${text} <select data-q="${i}"><option value="0">No</option><option value="1">Yes</option></select></label>`; q.appendChild(row);}); q.addEventListener('change', renderAssessmentResult); renderAssessmentResult(); }
function renderAssessmentResult(){ const vals=[...document.querySelectorAll('#quiz-questions select')].map(s=>Number(s.value||0)); const score=vals.reduce((a,b)=>a+b,0); const stage=Math.min(8, Math.max(1, score)); const out=document.getElementById('assessment-result'); const conf=score>=6?'high':score>=3?'medium':'early-signal'; const next=stage<3?'supervised edits with approval gates':stage<6?'bounded tool use + verification':'taskboard orchestration with merge gates'; const tryLevel=Math.min(8, stage+1); out.textContent=`You are probably around Stage ${stage}. Confidence: ${conf}. Your next safe step is ${next}. Try Glytch Level ${tryLevel} next.`; }
