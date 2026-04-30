const buttons = document.getElementById('buttons');
const log = document.getElementById('log');
const apiState = document.getElementById('api-state');
const meta = document.getElementById('meta');

function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

async function streamLines(lines){
  log.textContent = '';
  for (const line of lines){
    log.textContent += line + '\n';
    await sleep(450);
  }
}

async function runLevel(level){
  apiState.innerHTML = '<span class="pill">Running…</span>';
  const res = await fetch(`/api/run/${level}`);
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

async function init(){
  const levels = await (await fetch('/api/levels')).json();
  Object.entries(levels.levels).forEach(([k,v]) => {
    const btn = document.createElement('button');
    btn.textContent = `Level ${k}: ${v.name}`;
    btn.onclick = () => runLevel(k);
    buttons.appendChild(btn);
  });
}

init();
