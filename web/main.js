const buttons = document.getElementById('buttons');
const log = document.getElementById('log');
const apiState = document.getElementById('api-state');
const meta = document.getElementById('meta');
const useCaseOptions = document.getElementById('use-case-options');
const selectionLabel = document.getElementById('selection-label');
const confirmBtn = document.getElementById('confirm-btn');

const entry = document.getElementById('entry');
const app = document.getElementById('app');
document.getElementById('start-btn').onclick = () => {
  entry.classList.add('hidden');
  app.classList.remove('hidden');
};

let selectedUseCase = null;
let confirmedUseCase = null;

function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

function clearOutput(message = 'Output cleared. Select a level to begin.') {
  log.textContent = message;
  meta.textContent = 'Run a level to verify API path, model, and request id.';
  apiState.innerHTML = '<span class="pill">Waiting</span>';
}

async function streamLines(lines){
  log.textContent = '';
  for (const line of lines){
    log.textContent += line + '\n';
    await sleep(350);
  }
}

async function runLevel(level){
  if (!confirmedUseCase) {
    clearOutput('Please confirm a use case direction first.');
    return;
  }

  apiState.innerHTML = '<span class="pill"><span class="spinner"></span>Running…</span>';
  log.textContent = 'Working...';

  const res = await fetch('/api/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ level, use_case: confirmedUseCase })
  });
  const data = await res.json();

  const backend = data.backend || {};
  const isConfigured = Boolean(backend.configured) && res.ok;
  const stateClass = isConfigured ? 'ok' : 'err';
  const stateLabel = isConfigured ? 'OpenAI API Connected' : 'OpenAI API Not Connected';
  apiState.innerHTML = `<span class="pill ${stateClass}">${stateLabel}</span>`;

  const requestId = data.request_id || 'n/a';
  const model = backend.model || 'n/a';
  const baseUrl = backend.base_url || 'n/a';
  meta.textContent = `request_id=${requestId} · provider=${backend.provider || 'n/a'} · model=${model} · base_url=${baseUrl}`;

  if (!res.ok) {
    const error = data.error || 'unknown error';
    log.textContent = `Request failed (${res.status}): ${error}`;
    return;
  }
  await streamLines(data.lines || ['No output lines returned.']);
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

    if (!levelsResponse.ok || !levels.levels || !useCasesResponse.ok || !useCases.use_cases) {
      log.textContent = 'Could not load configuration.';
      return;
    }

    renderUseCases(useCases.use_cases);

    Object.entries(levels.levels).forEach(([k,v]) => {
      const btn = document.createElement('button');
      btn.textContent = `Level ${k}: ${v.name}`;
      btn.onclick = () => runLevel(k);
      buttons.appendChild(btn);
    });
  } catch (err) {
    log.textContent = `Could not load configuration: ${err.message}`;
  }
}

init();
