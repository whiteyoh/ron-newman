import { loadStartupData, runLevelRequest } from './api.js';
import { createEl, el, refs, setStatus } from './dom.js';
import { renderQuiz } from './quiz.js';
import { renderScorePanel } from './render-score.js';
import { renderMaturityStages, renderBeforeAfter, renderLevelCards, renderSurpriseUseCases, renderUseCases } from './render-static.js';
import { renderTaskboard } from './render-taskboard.js';
import { renderTheatre } from './render-theatre.js';
import { runReplay } from './replay.js';
import { appendMessage, clearOutput, clearRunPanels, updateLevelButtonsVisibility } from './run-ui.js';
import { initOnboarding } from './onboarding.js';
import { prefersReducedMotion, sleep, state } from './state.js';

function on(node, event, handler) {
  if (!node) return;
  node.addEventListener(event, handler);
}

async function runLevel(level) {
  state.lastRunLevel = level;
  if (!state.confirmedUseCase || state.runInProgress) return;
  state.runInProgress = true;
  setStatus('Running…', 'running');
  clearRunPanels();
  refs.log.textContent = '';
  appendMessage('system', 'Running simulation. No answer needed.');
  appendMessage('trace', 'Read-only simulation trace. Nothing here requires you to answer.');
  try {
    const data = await runLevelRequest({ level, use_case: state.confirmedUseCase, use_case_context: state.selectedUseCaseContext });
    const backend = data?.backend || {};
    setStatus(backend.configured ? 'OpenAI API Connected' : 'OpenAI API Not Connected', backend.configured ? 'ok' : 'err');
    refs.meta.textContent = `request_id=${data?.request_id || 'Available after run'} · provider=${backend.provider || 'Workshop-safe simulation'} · model=${backend.model || 'Workshop-safe simulation'}`;
    renderScorePanel(data.agenticness, data); renderTheatre(data); renderTaskboard(data);
    if (refs.runSummaryPanel) refs.runSummaryPanel.classList.remove('hidden');
    if (refs.runSummaryList) refs.runSummaryList.textContent = '';
    const lines = Array.isArray(data.lines) && data.lines.length ? data.lines : ['No output lines returned.'];
    refs.log.textContent = '';
    appendMessage('trace', 'Read-only simulation trace. Nothing here requires you to answer.');
    const finalAnswer = data?.approval_summary?.final_answer || data?.final_answer || lines[lines.length - 1] || '';
    if (refs.finalOutputPanel && finalAnswer) {
      refs.finalOutputPanel.classList.remove('hidden');
      if (refs.finalOutputBody) refs.finalOutputBody.textContent = finalAnswer;
      if (refs.finalOutputStatus) refs.finalOutputStatus.textContent = data?.approval_summary?.final_status || 'Candidate';
    } else if (refs.finalOutputPanel) refs.finalOutputPanel.classList.add('hidden');
    if (refs.rawTraceDetails) refs.rawTraceDetails.open = Boolean(data?.runtime_error);
        if (data?.runtime_error) {
      setStatus('Completed with warning', 'failed');
      if (refs.runSummaryPanel) refs.runSummaryPanel.classList.add('warning');
      if (refs.runSummaryStatus) refs.runSummaryStatus.textContent = 'Rendered with warning';
      if (refs.runSummaryCopy) refs.runSummaryCopy.textContent = 'This level returned structured output, but one or more AI calls failed safely. No external action was taken.';
      [
        `Warning: ${data.runtime_error.message || 'Unknown runtime warning'}`,
        `Code: ${data.runtime_error.code || 'unavailable'}`,
        'Action: Check OPENAI_MODEL, model access, quota or billing',
        'Next step: Review the trace, retry, or try a lower level',
      ].forEach((line) => {
        const item = createEl('li', '', line);
        refs.runSummaryList?.appendChild(item);
      });
      appendMessage('system', [
        'This level rendered with a runtime warning.',
        `Reason: ${data.runtime_error.message || 'Unknown runtime warning'}`,
        `Code: ${data.runtime_error.code || 'unavailable'}`,
        'No external action was taken.',
      ].join('\n'));
    } else {
      if (refs.runSummaryStatus) refs.runSummaryStatus.textContent = 'Completed';
      if (refs.runSummaryCopy) refs.runSummaryCopy.textContent = 'Glytch rendered this level as a workshop-safe simulation. Review the score, theatre steps and transcript before using the output.';
      const backendLabel = backend.configured ? 'OpenAI API Connected' : 'Workshop-safe simulation';
      [
        `Level: Level ${level}`,
        `Use case: ${state.confirmedUseCaseLabel || state.confirmedUseCase || 'Available after run'}`,
        `Backend: ${backendLabel}`,
        'Next step: Review the trace or compare with another level',
      ].forEach((line) => {
        const item = createEl('li', '', line);
        refs.runSummaryList?.appendChild(item);
      });
    }
    for (const line of lines) { appendMessage('trace', line); await sleep(prefersReducedMotion ? 0 : 120); }
    state.latestArtifact = `Glytch Export\nGenerated: ${new Date().toISOString()}\nLevel: ${level}\nUse case: ${state.confirmedUseCaseLabel || state.confirmedUseCase}\nBackend key: ${state.confirmedUseCase}\n\n${lines.join('\n')}`;
    refs.downloadArtifactBtn.disabled = false;
  } catch (err) {
    console.error('Level run failed', err);
    setStatus('Request failed', 'failed');
    refs.log.textContent = '';
    const lines = [
      'Simulation could not complete. No action was taken.',
      `Reason: ${err?.message || 'Unknown error'}`,
    ];
    if (err?.code) lines.push(`Code: ${err.code}`);
    if (err?.status) lines.push(`HTTP status: ${err.status}`);
    if (err?.requestId) lines.push(`Request ID: ${err.requestId}`);
    if (err?.code === 'upstream_http') {
      lines.push(
        'Hint: Check OPENAI_MODEL in your hosting environment. If you recently tried gpt-5.2, set OPENAI_MODEL back to gpt-4.1-mini or confirm your OpenAI project has access to the configured model.'
      );
    }
    appendMessage('system', lines.join(String.fromCharCode(10)));
    refs.replayBtn.disabled = true;
    refs.downloadArtifactBtn.disabled = true;
  } finally { state.runInProgress = false; }
  onboarding?.onRunComplete(level);
}


async function init() {
  clearOutput();
  try {
    const [levels, useCases, maturity] = await loadStartupData();
    state.surpriseUseCases = [
      {
        title: 'Small business launch',
        description: 'Create a simple launch plan for a new product.',
        goal: 'create a simple launch plan for a new sustainable coffee brand',
        audience: 'busy small business owner',
        constraints: 'plain English, practical next steps, no jargon',
      },
      {
        title: 'Student revision plan',
        description: 'Build a revision plan for an upcoming exam.',
        goal: 'build a revision plan for a GCSE student preparing for exams',
        audience: 'student and parent',
        constraints: 'short daily actions, confidence-building, easy to follow',
      },
    ].map((item) => ({
      ...item,
      context: `Goal: ${item.goal}\nAudience: ${item.audience}\nConstraints: ${item.constraints}`,
    }));
    renderUseCases(useCases.use_cases || {});
    renderSurpriseUseCases(state.surpriseUseCases);
    renderMaturityStages(maturity.stages || []);
    renderQuiz();
    renderBeforeAfter(levels.levels || {});
    renderLevelCards(levels.levels || {}, runLevel);
    updateLevelButtonsVisibility();
  } catch (err) {
    console.error('Startup failed', err);
    clearOutput('Glytch could not load the demo data. No action was taken. Please refresh and try again.');
    setStatus('Startup failed', 'failed');
    if (refs.buttons) {
      refs.buttons.querySelectorAll('button').forEach((b) => { b.disabled = true; });
    }
    if (refs.maturityCards && !refs.maturityCards.children.length) {
      refs.maturityCards.appendChild(createEl('p', 'muted', 'Maturity ladder is unavailable until startup data loads.'));
    }
    if (refs.beforeAfter && !refs.beforeAfter.children.length) {
      refs.beforeAfter.appendChild(createEl('p', 'muted', 'Level preview is unavailable until startup data loads.'));
    }
  }
}

const onboarding = initOnboarding({ runLevel });

function setSetupMode(mode) {
  state.setupMode = mode;
  if (refs.setupModeExampleBtn) refs.setupModeExampleBtn.classList.toggle('active', mode === 'example');
  if (refs.setupModeCustomBtn) refs.setupModeCustomBtn.classList.toggle('active', mode === 'custom');
  if ((mode === 'custom' || mode === 'surprise') && onboarding?.dismissGuideForManualChoice) onboarding.dismissGuideForManualChoice();
  if (refs.setupModeSurpriseBtn) refs.setupModeSurpriseBtn.classList.toggle('active', mode === 'surprise');
  if (refs.useCaseOptions) refs.useCaseOptions.classList.toggle('hidden', mode !== 'example');
  if (refs.customUseCaseForm) refs.customUseCaseForm.classList.toggle('hidden', mode !== 'custom');
  if (refs.surpriseUseCaseOptions) refs.surpriseUseCaseOptions.classList.toggle('hidden', mode !== 'surprise');
  const helpText = {
    example: 'Start with a ready-made scenario.',
    custom: 'Describe what you want to use AI for.',
    surprise: 'Pick from two quick examples.',
  };
  if (refs.setupModeHelp) refs.setupModeHelp.textContent = helpText[mode];
}


function clearGuidedContextIfPresent() {
  const guidedContext = 'Year 10 revision lesson on nutrition and healthy eating';
  const currentContext = refs.contextInput?.value.trim() || '';
  if (currentContext === guidedContext && refs.contextInput) refs.contextInput.value = '';
  if (state.selectedUseCaseContext === guidedContext) state.selectedUseCaseContext = '';
}

function buildCustomContext() {
  const lines = [];
  if (state.customUseCaseGoal) lines.push(`Goal: ${state.customUseCaseGoal}`);
  if (state.customUseCaseAudience) lines.push(`Audience: ${state.customUseCaseAudience}`);
  if (state.customUseCaseConstraints) lines.push(`Constraints: ${state.customUseCaseConstraints}`);
  return lines.join('\n');
}

function updateCustomScenario() {
  const goal = refs.customGoalInput?.value.trim() || '';
  const audience = refs.customAudienceInput?.value.trim() || '';
  const constraints = refs.customConstraintsInput?.value.trim() || '';
  state.customUseCaseGoal = goal;
  state.customUseCaseAudience = audience;
  state.customUseCaseConstraints = constraints;
  if (state.customUseCaseGoal.length < 8) {
    state.selectedUseCaseLabel = null;
    if (refs.selectionLabel) refs.selectionLabel.textContent = 'Enter your goal to enable confirmation.';
    if (refs.confirmBtn) refs.confirmBtn.disabled = true;
    return;
  }
  state.selectedUseCase = 'custom';
  state.selectedUseCaseLabel = state.customUseCaseGoal.slice(0, 72);
  state.selectedCustomScenario = {
    key: 'custom',
    title: 'Custom use case',
    description: 'User-created scenario',
    goal: state.customUseCaseGoal,
    audience: state.customUseCaseAudience,
    constraints: state.customUseCaseConstraints,
  };
  state.selectedUseCaseContext = buildCustomContext();
  state.confirmedUseCase = null;
  state.confirmedUseCaseLabel = null;
  if (refs.selectionLabel) refs.selectionLabel.textContent = `Selected custom use case: ${state.customUseCaseGoal.slice(0, 72)}`;
  if (refs.confirmBtn) refs.confirmBtn.disabled = false;
  clearOutput('Custom use case updated. Confirm direction to continue.');
  updateLevelButtonsVisibility();
}

on(el('start-btn'), 'click', () => {
  onboarding.openApp();
  state.selectedUseCaseContext = '';
  if (refs.contextInput) refs.contextInput.value = '';
});
on(refs.setupModeExampleBtn, 'click', () => {
  setSetupMode('example');
  clearGuidedContextIfPresent();
});
on(refs.setupModeCustomBtn, 'click', () => {
  setSetupMode('custom');
  clearGuidedContextIfPresent();
});
on(refs.setupModeSurpriseBtn, 'click', () => {
  setSetupMode('surprise');
  clearGuidedContextIfPresent();
});
on(refs.customGoalInput, 'input', updateCustomScenario);
on(refs.customAudienceInput, 'input', updateCustomScenario);
on(refs.customConstraintsInput, 'input', updateCustomScenario);
on(refs.confirmBtn, 'click', () => {
  if (!state.selectedUseCase) return clearOutput('Select a use case before confirming direction.');
  if (state.setupMode === 'example') state.selectedUseCaseContext = refs.contextInput?.value.trim() || '';
  if (state.setupMode === 'custom' && !state.selectedUseCaseContext) return clearOutput('Add a clear custom goal before confirming.');
  state.confirmedUseCase = state.selectedUseCase;
  state.confirmedUseCaseLabel = state.selectedUseCaseLabel || state.selectedUseCase;
  const label = state.confirmedUseCaseLabel;
  if (refs.selectionLabel) refs.selectionLabel.textContent = `Confirmed direction: ${label}${state.selectedUseCaseContext ? ` | context: ${state.selectedUseCaseContext}` : ''}`;
  clearOutput('Direction confirmed. Choose a level to run.');
  updateLevelButtonsVisibility();
  onboarding.onConfirmed();
});
on(refs.replayBtn, 'click', runReplay);
on(refs.downloadArtifactBtn, 'click', () => {
  if (!state.latestArtifact) return;
  const blob = new Blob([state.latestArtifact], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = createEl('a');
  a.href = url; a.download = `glytch-artifact-${new Date().toISOString().slice(0, 10)}.txt`;
  document.body.append(a); a.click(); a.remove(); URL.revokeObjectURL(url);
});
on(refs.modalCloseBtn, 'click', () => refs.useCaseModal?.classList.add('hidden'));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') refs.useCaseModal?.classList.add('hidden'); });
if (new URLSearchParams(window.location.search).get('debug') !== '1' && refs.previewTools) refs.previewTools.hidden = true;
setSetupMode('example');
init();
