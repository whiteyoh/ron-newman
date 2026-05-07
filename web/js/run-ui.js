import { createEl, refs, setStatus } from './dom.js';
import { state } from './state.js';

export function clearRunPanels() {
  if (refs.scorePanel) refs.scorePanel.textContent = '';
  if (refs.theatreSteps) refs.theatreSteps.textContent = '';
  if (refs.taskboardEl) refs.taskboardEl.textContent = '';
  if (refs.replayState) refs.replayState.textContent = '';
  if (refs.replayBtn) refs.replayBtn.disabled = true;
  state.theatreCards = [];
  if (refs.runSummaryPanel) refs.runSummaryPanel.classList.add('hidden');
  if (refs.runSummaryPanel) refs.runSummaryPanel.classList.remove('warning');
  if (refs.runSummaryStatus) refs.runSummaryStatus.textContent = 'Waiting';
  if (refs.runSummaryCopy) refs.runSummaryCopy.textContent = '';
  if (refs.runSummaryList) refs.runSummaryList.textContent = '';
  if (refs.runInsightPanel) refs.runInsightPanel.classList.add('hidden');
  if (refs.runInsightLevel) refs.runInsightLevel.textContent = 'Level insight';
  if (refs.runInsightCopy) refs.runInsightCopy.textContent = '';
  if (refs.finalOutputPanel) refs.finalOutputPanel.classList.add('hidden');
  if (refs.finalOutputBody) refs.finalOutputBody.textContent = '';
  if (refs.finalOutputStatus) refs.finalOutputStatus.textContent = 'Candidate';
  if (refs.learningTakeawayPanel) refs.learningTakeawayPanel.classList.add('hidden');
  if (refs.learningTakeawayCopy) refs.learningTakeawayCopy.textContent = '';
  if (refs.nextStepPanel) refs.nextStepPanel.classList.add('hidden');
  if (refs.nextStepCopy) refs.nextStepCopy.textContent = '';
  if (refs.quickCompareActions) refs.quickCompareActions.textContent = '';
  if (refs.copyOutputBtn) {
    refs.copyOutputBtn.disabled = true;
    refs.copyOutputBtn.textContent = 'Copy output';
  }
  if (refs.advancedResultsDetails) {
    refs.advancedResultsDetails.open = false;
    refs.advancedResultsDetails.classList.add('hidden');
  }
  if (refs.rawTraceDetails) refs.rawTraceDetails.open = false;
}

export function appendMessage(role, text) {
  if (!refs.log) return;
  const item = createEl('div', `msg ${role}`, text);
  item.setAttribute('data-role', role);
  refs.log.appendChild(item);
  refs.log.scrollTop = refs.log.scrollHeight;
}

export function clearOutput(msg = 'Choose a level to watch a simulated agent workflow. The output is a read-only trace; you only need to choose the scenario and level.') {
  if (refs.log) refs.log.textContent = '';
  appendMessage('system', msg);
  if (refs.meta) refs.meta.textContent = 'Run a level to verify API path, model and request id.';
  setStatus('Waiting');
  state.latestArtifact = null;
  if (refs.downloadArtifactBtn) refs.downloadArtifactBtn.disabled = true;
  clearRunPanels();
}

export const updateLevelButtonsVisibility = () => {
  if (refs.buttons) refs.buttons.classList.toggle('hidden', !state.confirmedUseCase);
};
