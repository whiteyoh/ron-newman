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
  try {
    const data = await runLevelRequest({ level, use_case: state.confirmedUseCase, use_case_context: state.selectedUseCaseContext });
    const backend = data?.backend || {};
    setStatus(backend.configured ? 'OpenAI API Connected' : 'OpenAI API Not Connected', backend.configured ? 'ok' : 'err');
    refs.meta.textContent = `request_id=${data?.request_id || 'Available after run'} · provider=${backend.provider || 'Workshop-safe simulation'} · model=${backend.model || 'Workshop-safe simulation'}`;
    if (data?.runtime_error) {
      setStatus('Completed with warning', 'failed');
      appendMessage('system', [
        'This level returned structured output with a runtime warning.',
        `Reason: ${data.runtime_error.message || 'Unknown runtime warning'}`,
        `Code: ${data.runtime_error.code || 'unavailable'}`,
        'No external action was taken.',
      ].join('
'));
    }
    renderScorePanel(data.agenticness, data); renderTheatre(data); renderTaskboard(data);
    const lines = Array.isArray(data.lines) && data.lines.length ? data.lines : ['No output lines returned.'];
    refs.log.textContent = '';
    appendMessage('trace', 'Read-only simulation trace. Nothing here requires you to answer.');
    for (const line of lines) { appendMessage('trace', line); await sleep(prefersReducedMotion ? 0 : 120); }
    state.latestArtifact = `Glytch Export\nGenerated: ${new Date().toISOString()}\nLevel: ${level}\nUse case: ${state.confirmedUseCase}\n\n${lines.join('\n')}`;
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
    appendMessage('system', lines.join('\n'));
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
    refs.buttons.querySelectorAll('button').forEach((b) => { b.disabled = true; });
    if (!refs.maturityCards.children.length) refs.maturityCards.appendChild(createEl('p', 'muted', 'Maturity ladder is unavailable until startup data loads.'));
    if (!refs.beforeAfter.children.length) refs.beforeAfter.appendChild(createEl('p', 'muted', 'Level preview is unavailable until startup data loads.'));
  }
}

const onboarding = initOnboarding({ runLevel });

function setSetupMode(mode) {
  state.setupMode = mode;
  if (refs.setupModeExampleBtn) refs.setupModeExampleBtn.classList.toggle('active', mode === 'example');
  if (refs.setupModeCustomBtn) refs.setupModeCustomBtn.classList.toggle('active', mode === 'custom');
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
    if (refs.selectionLabel) refs.selectionLabel.textContent = 'Enter your goal to enable confirmation.';
    if (refs.confirmBtn) refs.confirmBtn.disabled = true;
    return;
  }
  state.selectedUseCase = 'custom';
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
  if (refs.selectionLabel) refs.selectionLabel.textContent = `Selected custom use case: ${state.customUseCaseGoal.slice(0, 72)}`;
  if (refs.confirmBtn) refs.confirmBtn.disabled = false;
  clearOutput('Custom use case updated. Confirm direction to continue.');
  updateLevelButtonsVisibility();
}

el('start-btn').onclick = () => onboarding.openApp();
on(refs.setupModeExampleBtn, 'click', () => setSetupMode('example'));
on(refs.setupModeCustomBtn, 'click', () => setSetupMode('custom'));
on(refs.setupModeSurpriseBtn, 'click', () => setSetupMode('surprise'));
on(refs.customGoalInput, 'input', updateCustomScenario);
on(refs.customAudienceInput, 'input', updateCustomScenario);
on(refs.customConstraintsInput, 'input', updateCustomScenario);
refs.confirmBtn.onclick = () => {
  if (!state.selectedUseCase) return clearOutput('Select a use case before confirming direction.');
  if (state.setupMode === 'example') state.selectedUseCaseContext = refs.contextInput.value.trim();
  if (state.setupMode === 'custom' && !state.selectedUseCaseContext) return clearOutput('Add a clear custom goal before confirming.');
  state.confirmedUseCase = state.selectedUseCase;
  const label = state.setupMode === 'custom' ? 'custom use case' : state.selectedUseCase.replaceAll('_', ' ');
  refs.selectionLabel.textContent = `Confirmed direction: ${label}${state.selectedUseCaseContext ? ` | context: ${state.selectedUseCaseContext}` : ''}`;
  clearOutput('Direction confirmed. Choose a level to run.');
  updateLevelButtonsVisibility();
  onboarding.onConfirmed();
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
setSetupMode('example');
init();
