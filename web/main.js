const buttons = document.getElementById('buttons');
const log = document.getElementById('log');

function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

async function streamLines(lines){
  log.textContent = '';
  for (const line of lines){
    log.textContent += line + '\n';
    await sleep(450);
  }
}

async function runLevel(level){
  const res = await fetch(`/api/run/${level}`);
  const data = await res.json();
  await streamLines(data.lines);
}

async function init(){
  const levels = await (await fetch('/api/levels')).json();
  Object.entries(levels).forEach(([k,v]) => {
    const btn = document.createElement('button');
    btn.textContent = `Level ${k}: ${v.name}`;
    btn.onclick = () => runLevel(k);
    buttons.appendChild(btn);
  });
}

init();
