const buttons = document.getElementById('buttons');
const log = document.getElementById('log');
const apiState = document.getElementById('api-state');
const meta = document.getElementById('meta');
const useCaseOptions = document.getElementById('use-case-options');
const selectionLabel = document.getElementById('selection-label');
const confirmBtn = document.getElementById('confirm-btn');
const downloadArtifactBtn = document.getElementById('download-artifact');

const entry = document.getElementById('entry');
const app = document.getElementById('app');
const startBtn = document.getElementById('start-btn');

let latestArtifact = null;

function enterDemo() {
  entry.classList.add('hidden');
  app.classList.remove('hidden');
}

startBtn.addEventListener('click', enterDemo);

let selectedUseCase = null;
let confirmedUseCase = null;

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
  latestArtifact = `Glitch Export\nGenerated: ${stamp}\nLevel: ${level}\nUse case: ${confirmedUseCase || 'n/a'}\n\n${lines.join('\n')}`;
  downloadArtifactBtn.disabled = false;
}

function downloadArtifact() {
  if (!latestArtifact) return;
  const blob = new Blob([latestArtifact], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `glitch-artifact-${new Date().toISOString().slice(0,10)}.txt`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

downloadArtifactBtn.addEventListener('click', downloadArtifact);

async function runLevel(level){
  if (!confirmedUseCase) {
    clearOutput('Please confirm a use case direction first.');
    return;
  }

  apiState.innerHTML = '<span class="pill">Running…</span>';
  log.innerHTML = '';
  appendMessage('system', 'Working...');

  const res = await fetch('/api/run', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ level, use_case: confirmedUseCase })
  });
  const data = await res.json();

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
  createArtifact(level, lines);
  await streamLines(lines);
}

function renderUseCases(data) {
  useCaseOptions.textContent = '';
  Object.entries(data).forEach(([key, text], index) => {
    const option = document.createElement('button');
    option.className = 'option';
    option.textContent = `${index + 1}. ${text}`;
    option.onclick = () => {
      selectedUseCase = key;
      confirmedUseCase = null;
      confirmBtn.disabled = false;
      selectionLabel.textContent = `Selected (not confirmed): ${text}`;
      document.querySelectorAll('.option').forEach((el) => el.classList.remove('active'));
      option.classList.add('active');
      clearOutput('Use case changed. Previous output cleared. Confirm direction to continue.');
    };
    useCaseOptions.appendChild(option);
  });
}

confirmBtn.onclick = () => {
  confirmedUseCase = selectedUseCase;
  selectionLabel.textContent = `Confirmed direction: ${document.querySelector('.option.active')?.textContent || 'n/a'}`;
  clearOutput('Direction confirmed. Choose a level to run.');
};

async function init(){
  try {
    const [levelsResponse, useCasesResponse] = await Promise.all([fetch('/api/levels'), fetch('/api/use-cases')]);
    const levels = await levelsResponse.json();
    const useCases = await useCasesResponse.json();
    if (!levelsResponse.ok || !levels.levels || !useCasesResponse.ok || !useCases.use_cases) return clearOutput('Could not load configuration.');
    renderUseCases(useCases.use_cases);
    Object.entries(levels.levels).forEach(([k,v]) => {
      const btn = document.createElement('button');
      btn.textContent = `Level ${k}: ${v.name}`;
      btn.onclick = () => runLevel(k);
      buttons.appendChild(btn);
    });
  } catch (err) {
    clearOutput(`Could not load configuration: ${err.message}`);
  }
}

init();
