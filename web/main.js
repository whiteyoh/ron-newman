const el = (id) => document.getElementById(id);
const buttons = el('buttons'), log = el('log'), apiState = el('api-state'), meta = el('meta');
const useCaseOptions = el('use-case-options'), selectionLabel = el('selection-label'), confirmBtn = el('confirm-btn');
const downloadArtifactBtn = el('download-artifact'), useCaseModal = el('use-case-modal'), modalTitle = el('modal-title');
const modalBody = el('modal-body'), modalCloseBtn = el('modal-close'), contextInput = el('context-input');
const theatreSteps = el('theatre-steps'), replayBtn = el('replay-btn'), replayState = el('replay-state'), taskboardEl = el('taskboard');
const scorePanel = el('score-panel'), beforeAfter = el('before-after');
const mobileViewBtn = el('mobile-view-btn'), desktopViewBtn = el('desktop-view-btn');
let selectedUseCase = null, confirmedUseCase = null, selectedUseCaseContext = '', latestArtifact = null, runInProgress = false, lastReplaySteps = [], theatreCards = [];
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const createEl = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text) n.textContent = text; return n; };
const setStatus = (label, type = '') => { apiState.innerHTML = `<span class="pill ${type}">${label}</span>`; };
function clearRunPanels() { scorePanel.innerHTML=''; theatreSteps.innerHTML=''; taskboardEl.innerHTML=''; replayState.textContent=''; replayBtn.disabled=true; theatreCards=[]; }
function appendMessage(role, text){ const item=createEl('div',`msg ${role}`,text); item.setAttribute('data-role', role); log.appendChild(item); log.scrollTop=log.scrollHeight; }
function normalizeTraceLabel(line){ return line
  .replace(/^Prompt:/, 'Seed prompt used by the demo:')
  .replace(/^Question:/, 'Demo question being processed:')
  .replace(/^Instruction:/, 'Instruction given to the simulated agent:')
  .replace(/^Goal:/, 'Demo goal:')
  .replace(/^Final verifier:/, 'Final verifier check:')
  .replace(/^What the human asked for:?/i, 'Demo request:')
  .replace(/^Can we trust this output\?/i, 'Trust check:')
  .replace(/^Final verifier: is/i, 'Final verifier check: is'); }
function inferRole(line){ const t=(line||'').toLowerCase().trim(); if(/^(tool|search|execute|call|api|command|retriev)/.test(t)) return 'tool'; if(/^(verifier|trust check|final verifier check|verification)/.test(t)) return 'verifier'; if(/^(agent|assistant|planner|worker)/.test(t)) return 'agent'; if(/^(system|status|demo|seed prompt used by the demo|instruction given to the simulated agent|demo question being processed|demo goal)/.test(t)) return 'trace'; return 'trace'; }
function clearOutput(msg='Choose a level to watch a simulated agent workflow. The output is a read-only trace; you only need to choose the scenario and level.'){ log.innerHTML=''; appendMessage('system', msg); meta.textContent='Run a level to verify API path, model and request id.'; setStatus('Waiting'); latestArtifact=null; downloadArtifactBtn.disabled=true; clearRunPanels(); }
function updateLevelButtonsVisibility(){ buttons.classList.toggle('hidden', !confirmedUseCase); }
function renderUseCases(data){ useCaseOptions.textContent=''; Object.entries(data).forEach(([key,text], i)=>{ const b=createEl('button','option'); b.innerHTML=`<strong>${i+1}. ${key.replaceAll('_',' ')}</strong><div class="muted">${text.split('.')[0]}.</div><span class="pill">Select scenario</span>`; b.onclick=()=>{ selectedUseCase=key; confirmedUseCase=null; confirmBtn.disabled=false; selectionLabel.textContent=`Selected (not confirmed): ${key.replaceAll('_',' ')}`; document.querySelectorAll('.option').forEach((o)=>o.classList.remove('active')); b.classList.add('active'); clearOutput('Use case changed. Confirm direction to continue.'); updateLevelButtonsVisibility(); }; b.ondblclick=()=>{ modalTitle.textContent=`Use case context: ${key.replaceAll('_',' ')}`; modalBody.textContent=text; useCaseModal.classList.remove('hidden');}; useCaseOptions.appendChild(b); });}
function renderScorePanel(agenticness, data){ if(!agenticness){scorePanel.innerHTML=''; return;} const sim=data?.yegge_simulation||{}; const fields=[['Capability being taught',sim.capability_being_taught||'n/a'],['Yegge workflow simulation',sim.workflow_name||'n/a'],['Closest Yegge stage',agenticness.closest_yegge_stage||sim.closest_yegge_stage||'n/a'],['Yegge alignment score',`${agenticness.yegge_alignment_score||'n/a'}/10`],['Why this maps to Yegge',sim.why_this_maps_to_yegge||agenticness.yegge_alignment_explanation||'n/a'],['Why this is not production',sim.why_not_production||'Workshop-safe simulation'],['What human controls',sim.human_role||'n/a'],['What agent controls',sim.agent_role||'n/a'],['What is simulated',sim.simulated_environment||'n/a']]; scorePanel.innerHTML=''; fields.forEach(([k,v])=>{ const c=createEl('article','score-card'); c.innerHTML=`<strong>${k}</strong><div>${v}</div>`; scorePanel.appendChild(c); }); }
function renderTheatre(data){ theatreSteps.innerHTML=''; theatreCards=[]; const steps=data.theatre_steps||[]; const labelMap={
  'What the human asked for':'Demo request',
  'What the human asked for:':'Demo request',
  'What the agent checked':'Verification performed',
  'Where the human stays in control':'Human approval gate'
}; steps.forEach((s)=>{ const card=createEl('article','theatre-step'); const actor=(s.actor||'Agent').toLowerCase(); card.innerHTML=`<div class="section-header"><span class="actor">${actor}</span><span class="pill ${s.status||'complete'}">${s.status||'complete'}</span></div><strong>${labelMap[s.label]||s.label||'Step'}</strong><div>${s.summary||''}</div><div class="muted">${s.detail||''}</div>`; theatreCards.push(card); theatreSteps.appendChild(card); }); lastReplaySteps=data.replay_steps||steps.map((s)=>s.summary||s.label); replayBtn.disabled=!lastReplaySteps.length; }
function renderTaskboard(data){ taskboardEl.innerHTML=''; if(!data?.taskboard) return; const statuses=['pending','running','completed','needs human review','merged']; const wrap=createEl('div','taskboard-grid'); statuses.forEach((status)=>{ const col=createEl('section','taskboard-column'); col.innerHTML=`<h4>${status.replace(/\b\w/g,(m)=>m.toUpperCase())}</h4>`; (data.taskboard.workers||[]).filter((w)=>(w.status||'').toLowerCase()===status).forEach((w)=>{ const wc=createEl('article',`worker-card ${(w.status||'').includes('review')?'review':w.status}`); wc.innerHTML=`<strong>${w.worker||'Worker'}</strong><div>Task: ${w.task||'n/a'}</div><div>Status: ${w.status||'n/a'} · Attempt: ${w.attempt||1}</div><div>Output: ${w.output_summary||w.summary||'n/a'}</div><div>Verified: ${w.verified?'Yes':'No'}</div>`; col.appendChild(wc); }); wrap.appendChild(col); });
 const gate=createEl('article','card'); const g=data.taskboard.approval_gate||{}; gate.innerHTML=`<h4>Approval gate</h4><div>Verifier result: ${g.verifier_result||'n/a'}</div><div>Approved for merge: ${g.approved_for_merge??'n/a'}</div><div>Merge decision: ${g.merge_decision||'n/a'}</div>`;
 taskboardEl.append(wrap, gate); }
async function replayRun(){ if(!lastReplaySteps.length||runInProgress) return; replayBtn.disabled=true; replayState.textContent='Replay running…'; for(let i=0;i<lastReplaySteps.length;i++){ theatreCards.forEach((c)=>c.classList.remove('active-replay')); theatreCards[i]?.classList.add('active-replay'); appendMessage('system',`Replay: ${lastReplaySteps[i]}`); await sleep(prefersReducedMotion?0:320); } replayState.textContent='Replay finished'; replayBtn.disabled=false; }
async function runLevel(level){ if(!confirmedUseCase || runInProgress) return; runInProgress=true; setStatus('Running…'); clearRunPanels(); log.innerHTML=''; appendMessage('system','Running simulation. No answer needed.');
 try{ const res=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({level,use_case:confirmedUseCase,use_case_context:selectedUseCaseContext})}); const data=await res.json(); const backend=data.backend||{}; setStatus(backend.configured&&res.ok?'OpenAI API Connected':'OpenAI API Not Connected', backend.configured&&res.ok?'ok':'err'); meta.textContent=`request_id=${data.request_id||'n/a'} · provider=${backend.provider||'n/a'} · model=${backend.model||'n/a'}`; if(!res.ok){ log.innerHTML=''; appendMessage('system',`Request failed (${res.status}): ${data.error||'unknown error'}`); return; }
 renderScorePanel(data.agenticness, data); renderTheatre(data); renderTaskboard(data);
 const lines=data.lines||['No output lines returned.']; log.innerHTML=''; appendMessage('trace','This is the agent workflow trace. You do not need to type a response.'); for(const line of lines){ const normalized=normalizeTraceLabel(line); appendMessage(inferRole(normalized),normalized); await sleep(prefersReducedMotion?0:170);} latestArtifact=`Glytch Export\nGenerated: ${new Date().toISOString()}\nLevel: ${level}\nUse case: ${confirmedUseCase}\n\n${lines.join('\n')}`; downloadArtifactBtn.disabled=false;
 } catch(err){ setStatus('OpenAI API Not Connected','err'); log.innerHTML=''; appendMessage('system',`Request failed: ${err.message}`); } finally { runInProgress=false; }}
function renderQuiz(){ const q=el('quiz-questions'); const qs=['Only prompt AI','AI edits files','You approve every action','AI runs tools','Terminal agents','Multiple agents','Taskboard review','Own orchestration system']; q.innerHTML=''; qs.forEach((t,i)=>{ const c=createEl('label','quiz-card'); c.innerHTML=`<strong>${i+1}. ${t}</strong><select data-q="${i}"><option value="0">No</option><option value="1">Yes</option></select>`; q.appendChild(c);}); q.onchange=renderAssessmentResult; renderAssessmentResult(); }
function renderAssessmentResult(){ const v=[...document.querySelectorAll('#quiz-questions select')].map((s)=>Number(s.value||0)); let stage=1; if(v[7]) stage=8; else if(v[5]||v[6]) stage=6+(v[6]?1:0); else if(v[3]||v[4]) stage=4+(v[4]?1:0); else if(v[1]&&v[2]) stage=3; else if(v[0]) stage=2; const conf = stage>=6?'medium-high':stage>=4?'medium':'early-signal'; const risk = stage>=6?'Risk warning: automation drift without strong verifier gates.':'Risk warning: confidence may exceed safeguards.'; const next = stage<4?'Next safe step: supervised edits with explicit approval.' : stage<7?'Next safe step: bounded tool runs with verification logs.' : 'Next safe step: tighten merge policy and rollback checks.'; el('assessment-result').textContent=`You are probably around Stage ${stage}. Confidence: ${conf}. ${risk} ${next} Try Glytch Level ${Math.min(8,stage+1)} next.`; }
function renderBeforeAfter(levels){ beforeAfter.innerHTML=''; Object.entries(levels).forEach(([id,l])=>{ const c=createEl('article','card'); c.innerHTML=`<h3>Level ${id}: ${l.name}</h3><p><strong>Before:</strong> ${l.before||'Raw model capability.'}</p><p><strong>Agentic:</strong> ${l.agentic||'Adds checks, approval, and traceable decisions.'}</p>`; beforeAfter.appendChild(c); }); }
function setForcedView(mode){
  const nextMode = mode === 'mobile' ? 'mobile' : 'desktop';
  document.body.classList.remove('force-mobile','force-desktop');
  document.body.classList.add(nextMode === 'mobile' ? 'force-mobile' : 'force-desktop');
  mobileViewBtn.classList.toggle('active', nextMode==='mobile');
  desktopViewBtn.classList.toggle('active', nextMode==='desktop');
  mobileViewBtn.setAttribute('aria-pressed', String(nextMode==='mobile'));
  desktopViewBtn.setAttribute('aria-pressed', String(nextMode==='desktop'));
  try { window.localStorage.setItem('glytch:view-mode', nextMode); } catch (_) {}
}
async function init(){ clearOutput(); const [l,u,m]=await Promise.all([fetch('/api/levels'),fetch('/api/use-cases'),fetch('/api/agentic-maturity')]); const levels=await l.json(), useCases=await u.json(), maturity=await m.json(); renderUseCases(useCases.use_cases||{}); (maturity.stages||[]).forEach((s)=>{ const c=createEl('article','card'); c.innerHTML=`<strong>Stage ${s.id}: ${s.name}</strong><div class="muted">${s.plain_english_summary||''}</div>`; el('maturity-cards').appendChild(c);}); renderQuiz(); renderBeforeAfter(levels.levels||{});
 Object.entries(levels.levels||{}).forEach(([k,v])=>{ const b=createEl('button','level-card'); b.innerHTML=`<strong>Level ${k}: ${v.name}</strong><span>${v.description||''}</span><span class="muted">Agenticness: ${v.agenticness_score||'pending simulation'} · Yegge stage: ${v.closest_yegge_stage||'mapped after run'}</span>`; b.onclick=()=>runLevel(Number(k)); buttons.appendChild(b);}); updateLevelButtonsVisibility(); }
el('start-btn').onclick=()=>{ el('entry').classList.add('hidden'); el('app').classList.remove('hidden'); };
confirmBtn.onclick=()=>{ if(!selectedUseCase) return clearOutput('Select a use case before confirming direction.'); selectedUseCaseContext=contextInput.value.trim(); confirmedUseCase=selectedUseCase; selectionLabel.textContent=`Confirmed direction: ${selectedUseCase.replaceAll('_',' ')}${selectedUseCaseContext?` | context: ${selectedUseCaseContext}`:''}`; clearOutput('Direction confirmed. Choose a level to run.'); updateLevelButtonsVisibility(); };
replayBtn.onclick=replayRun; downloadArtifactBtn.onclick=()=>{ if(!latestArtifact) return; const blob=new Blob([latestArtifact],{type:'text/plain;charset=utf-8'}); const url=URL.createObjectURL(blob); const a=createEl('a'); a.href=url; a.download=`glytch-artifact-${new Date().toISOString().slice(0,10)}.txt`; document.body.append(a); a.click(); a.remove(); URL.revokeObjectURL(url); };
modalCloseBtn.onclick=()=>useCaseModal.classList.add('hidden'); document.addEventListener('keydown',(e)=>{ if(e.key==='Escape') useCaseModal.classList.add('hidden'); });
const systemDefaultMode = window.matchMedia('(max-width: 759px)').matches ? 'mobile' : 'desktop';
let savedMode = null;
try { savedMode = window.localStorage.getItem('glytch:view-mode'); } catch (_) {}
setForcedView(savedMode || systemDefaultMode);
mobileViewBtn.onclick=()=>setForcedView('mobile');
desktopViewBtn.onclick=()=>setForcedView('desktop');
window.matchMedia('(max-width: 759px)').addEventListener('change', (event) => {
  let persisted = null;
  try { persisted = window.localStorage.getItem('glytch:view-mode'); } catch (_) {}
  if (!persisted) setForcedView(event.matches ? 'mobile' : 'desktop');
});
init();
