import { createEl, refs, setStatus } from './dom.js';
import { state } from './state.js';

export function clearRunPanels() {
  refs.scorePanel.textContent = '';
  refs.theatreSteps.textContent = '';
  refs.taskboardEl.textContent = '';
  refs.replayState.textContent = '';
  refs.replayBtn.disabled = true;
  state.theatreCards = [];
  if (refs.runSummaryPanel) refs.runSummaryPanel.classList.add('hidden');
  if (refs.runSummaryPanel) refs.runSummaryPanel.classList.remove('warning');
  if (refs.runSummaryStatus) refs.runSummaryStatus.textContent = 'Waiting';
  if (refs.runSummaryCopy) refs.runSummaryCopy.textContent = '';
  if (refs.runSummaryList) refs.runSummaryList.textContent = '';
}

export function appendMessage(role, text) {
  const item = createEl('div', `msg ${role}`, text);
  item.setAttribute('data-role', role);
  refs.log.appendChild(item);
  refs.log.scrollTop = refs.log.scrollHeight;
}

export function clearOutput(msg = 'Choose a level to watch a simulated agent workflow. The output is a read-only trace; you only need to choose the scenario and level.') {
  refs.log.textContent = '';
  appendMessage('system', msg);
  refs.meta.textContent = 'Run a level to verify API path, model and request id.';
  setStatus('Waiting');
  state.latestArtifact = null;
  refs.downloadArtifactBtn.disabled = true;
  clearRunPanels();
}

export const updateLevelButtonsVisibility = () => refs.buttons.classList.toggle('hidden', !state.confirmedUseCase);
