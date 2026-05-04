import { loadStartupData, runLevelRequest } from './api.js';
import { createEl, el, refs, setStatus } from './dom.js';
import { renderQuiz } from './quiz.js';
import { renderScorePanel } from './render-score.js';
import { renderMaturityStages, renderBeforeAfter, renderLevelCards, renderUseCases } from './render-static.js';
import { renderTaskboard } from './render-taskboard.js';
import { renderTheatre } from './render-theatre.js';
import { runReplay } from './replay.js';
import { appendMessage, clearOutput, clearRunPanels, updateLevelButtonsVisibility } from './run-ui.js';
import { prefersReducedMotion, sleep, state } from './state.js';

async function runLevel(level) {
  if (!state.confirmedUseCase || state.runInProgress) return;
  state.runInProgress = true;
  setStatus('Running…', 'running');
  clearRunPanels();
  refs.log.textContent = '';
  appendMessage('system', 'Running simulation. No answer needed.');
  try {
    const data = await runLevelRequest({ level, use_case: state.confirmedUseCase, use_case_context: state.selectedUseCaseContext });
    const backend = data?.backend || {};
    setStatus(backend.configured ? 'OpenAI API Connected' : 'OpenAI API Not Connected', backend.configured ? 'ok' : 'err');
    refs.meta.textContent = `request_id=${data?.request_id || 'Available after run'} · provider=${backend.provider || 'Workshop-safe simulation'} · model=${backend.model || 'Workshop-safe simulation'}`;
    renderScorePanel(data.agenticness, data); renderTheatre(data); renderTaskboard(data);
    const lines = Array.isArray(data.lines) && data.lines.length ? data.lines : ['No output lines returned.'];
    refs.log.textContent = '';
    appendMessage('trace', 'Read-only simulation trace. Nothing here requires you to answer.');
    for (const line of lines) { appendMessage('trace', line); await sleep(prefersReducedMotion ? 0 : 120); }
    state.latestArtifact = `Glytch Export\nGenerated: ${new Date().toISOString()}\nLevel: ${level}\nUse case: ${state.confirmedUseCase}\n\n${lines.join('\n')}`;
    refs.downloadArtifactBtn.disabled = false;
  } catch (err) {
    console.error('Level run failed', err);
    const requestId = err?.requestId ? ` Request ID: ${err.requestId}` : '';
    setStatus('Request failed', 'failed');
    refs.log.textContent = '';
    appendMessage('system', `Something went wrong while running the simulation. No action was taken. Please try again.${requestId}`);
    refs.replayBtn.disabled = true;
    refs.downloadArtifactBtn.disabled = true;
  } finally { state.runInProgress = false; }
}

async function init() {
  clearOutput();
  try {
    const [levels, useCases, maturity] = await loadStartupData();
    renderUseCases(useCases.use_cases || {});
    renderMaturityStages(maturity.stages || []);
    renderQuiz();
    renderBeforeAfter(levels.levels || {});
    renderLevelCards(levels.levels || {}, runLevel);
    updateLevelButtonsVisibility();
  } catch (err) {
    console.error('Startup failed', err);
    clearOutput('Glytch could not load the demo data. No action was taken. Please refresh and try again.');
    setStatus('Startup failed', 'failed');
    refs.buttons.querySelectorAll('button').forEach((b) => { b.disabled = true; });
    if (!refs.maturityCards.children.length) refs.maturityCards.appendChild(createEl('p', 'muted', 'Maturity ladder is unavailable until startup data loads.'));
    if (!refs.beforeAfter.children.length) refs.beforeAfter.appendChild(createEl('p', 'muted', 'Level preview is unavailable until startup data loads.'));
  }
}

el('start-btn').onclick = () => { el('entry').classList.add('hidden'); el('app').classList.remove('hidden'); };
refs.confirmBtn.onclick = () => {
  if (!state.selectedUseCase) return clearOutput('Select a use case before confirming direction.');
  state.selectedUseCaseContext = refs.contextInput.value.trim();
  state.confirmedUseCase = state.selectedUseCase;
  refs.selectionLabel.textContent = `Confirmed direction: ${state.selectedUseCase.replaceAll('_', ' ')}${state.selectedUseCaseContext ? ` | context: ${state.selectedUseCaseContext}` : ''}`;
  clearOutput('Direction confirmed. Choose a level to run.');
  updateLevelButtonsVisibility();
};
refs.replayBtn.onclick = runReplay;
refs.downloadArtifactBtn.onclick = () => {
  if (!state.latestArtifact) return;
  const blob = new Blob([state.latestArtifact], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = createEl('a');
  a.href = url; a.download = `glytch-artifact-${new Date().toISOString().slice(0, 10)}.txt`;
  document.body.append(a); a.click(); a.remove(); URL.revokeObjectURL(url);
};
refs.modalCloseBtn.onclick = () => refs.useCaseModal.classList.add('hidden');
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') refs.useCaseModal.classList.add('hidden'); });
if (new URLSearchParams(window.location.search).get('debug') !== '1' && refs.previewTools) refs.previewTools.hidden = true;
init();
