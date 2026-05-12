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
import { showConfirmedContext, hideConfirmedContext } from './confirmed-context.js';
import { prefersReducedMotion, sleep, state } from './state.js';

function on(node, event, handler) {
  if (!node) return;
  node.addEventListener(event, handler);
}


function setText(node, value) {
  if (node) node.textContent = value;
}

function setDisabled(node, value) {
  if (node) node.disabled = value;
}

function getCandidateStatusLabel(status) {
  const value = String(status || '').toLowerCase();
  if (['merged', 'completed', 'approved'].includes(value)) return 'Ready for review';
  if (value === 'needs_human_review') return 'Needs human review';
  if (value === 'blocked') return 'Blocked by check';
  if (value === 'failed') return 'Could not complete safely';
  if (value === 'running') return 'Running';
  if (value === 'pending') return 'Pending';
  return 'Review needed';
}

function renderFinalOutput(bodyNode, text) {
  if (!bodyNode) return;
  bodyNode.textContent = '';
  const headingSet = new Set([
    'draft', 'draft update', 'draft customer update', 'confirmed facts', 'assumptions',
    'current assumption', 'checks before use', 'check before use', 'human review',
    'human review needed', 'next steps',
  ]);
  const lines = String(text || '').split('\n');
  let current = createEl('section', 'final-output-section');
  lines.forEach((line) => {
    const normalized = line.trim().replace(/:$/, '').toLowerCase();
    if (headingSet.has(normalized)) {
      if (current.childNodes.length) bodyNode.appendChild(current);
      const block = createEl('section', 'final-output-section');
      block.appendChild(createEl('h4', 'final-output-heading', line.trim().replace(/:$/, '')));
      bodyNode.appendChild(block);
      current = createEl('section', 'final-output-section');
      return;
    }
    current.appendChild(document.createTextNode(`${line}\n`));
  });
  if (current.childNodes.length) bodyNode.appendChild(current);
}

function getRunInsight(level) {
  const copyByLevel = {
    1: 'This is basic prompting. The AI answers directly, but the human still has to judge quality, accuracy, and next steps.',
    2: 'This adds more structure to the prompt. The AI has clearer instructions, but the workflow is still mostly human-led.',
    3: 'This introduces a bounded tool-style path. The AI is no longer just answering; it is following a more controlled process.',
    4: 'This shows a more structured workflow with clearer checks. The task is still safe and simulated, but the path is more visible.',
    5: 'This adds stronger workflow control. The AI output is shaped by steps, constraints, and review points.',
    6: 'This shows a more mature controlled workflow. The value is not just the answer, but the visible process around it.',
    7: 'This starts to look like coordinated agentic work. The system separates responsibilities and makes decisions easier to inspect.',
    8: 'This is orchestration. Multiple simulated workers plan, draft, check, and prepare a candidate output for review.',
  };
  return copyByLevel[level] || 'This run shows how structure, checks, and visibility change the AI experience.';
}

function getLearningTakeaway(level, hasRuntimeError) {
  let takeaway = 'Mature AI use means adding boundaries, checks, and clear process around the model.';
  if (level <= 2) takeaway = 'Higher AI maturity is not about longer prompts. It is about adding the right amount of structure for the task.';
  if (level >= 7) takeaway = 'Orchestration is useful when work needs multiple roles, but it still needs review before real-world action.';
  if (hasRuntimeError) takeaway += ' This run rendered with a safe warning, so treat the output as a demonstration only.';
  return takeaway;
}

function getRecommendedNextStep(level) {
  if (level === 1) return 'Next, try Level 3 to see how a controlled tool-style path changes the workflow.';
  if (level === 3) return 'Next, try Level 8 to see orchestration with multiple simulated workers.';
  if (level === 8) return 'Now compare this with Level 1 to see how much structure was added.';
  return 'Try Level 1, Level 3, or Level 8 to compare the maturity jump.';
}


function getRuntimeWarningLines(runtimeError) {
  const code = runtimeError?.code || 'unavailable';
  const message = runtimeError?.message || 'Unknown runtime warning';

  if (code === 'upstream_timeout') {
    return [
      `Warning: ${message}`,
      `Code: ${code}`,
      'Action: The AI provider took too long to respond. Retry, try a lower level, or reduce scenario detail.',
      'Next step: The demo stayed safe and no external action was taken.',
    ];
  }

  if (code === 'insufficient_quota') {
    return [
      `Warning: ${message}`,
      `Code: ${code}`,
      'Action: Check OpenAI quota or billing.',
      'Next step: Retry after quota or billing is resolved.',
    ];
  }

  if (code === 'model_not_found' || code === 'invalid_model') {
    return [
      `Warning: ${message}`,
      `Code: ${code}`,
      'Action: Check OPENAI_MODEL and model access.',
      'Next step: Use a model your OpenAI project can access.',
    ];
  }

  return [
    `Warning: ${message}`,
    `Code: ${code}`,
    'Action: Review the trace, retry, or try a lower level.',
    'Next step: The demo stayed safe and no external action was taken.',
  ];
}

async function runLevel(level) {
  state.lastRunLevel = level;
  if (!state.confirmedUseCase || state.runInProgress) return;
  state.runInProgress = true;
  setStatus('Running…', 'running');
  clearRunPanels();
  el('dashboard-title')?.scrollIntoView({
    behavior: prefersReducedMotion ? 'auto' : 'smooth',
    block: 'start',
  });
  setText(refs.log, '');
  appendMessage('system', 'Running simulation. No answer needed.');
  try {
    const data = await runLevelRequest({ level, use_case: state.confirmedUseCase, use_case_context: state.selectedUseCaseContext });
    const backend = data?.backend || {};
    setStatus(backend.configured ? 'OpenAI API Connected' : 'Workshop-safe simulation mode', backend.configured ? 'ok' : 'review');
    setText(refs.meta, `request_id=${data?.request_id || 'Available after run'} · provider=${backend.provider || 'Workshop-safe simulation'} · model=${backend.model || 'Workshop-safe simulation'}`);
    renderScorePanel(data.agenticness, data); renderTheatre(data); renderTaskboard(data);
    if (refs.advancedResultsDetails) {
      refs.advancedResultsDetails.classList.remove('hidden');
      refs.advancedResultsDetails.open = false;
    }
    if (refs.runSummaryPanel) refs.runSummaryPanel.classList.remove('hidden');
    if (refs.runInsightPanel) refs.runInsightPanel.classList.remove('hidden');
    if (refs.runInsightLevel) refs.runInsightLevel.textContent = `Level ${level}`;
    if (refs.runInsightCopy) refs.runInsightCopy.textContent = getRunInsight(level);
    if (refs.runSummaryList) refs.runSummaryList.textContent = '';
    const lines = Array.isArray(data.lines) && data.lines.length ? data.lines : ['No output lines returned.'];
    setText(refs.log, '');
    appendMessage('trace', 'Read-only simulation trace. Nothing here requires you to answer.');
    const finalAnswer = data?.final_answer || data?.approval_summary?.final_answer || lines[lines.length - 1] || '';
    const hiddenPrefixes = ['honest limitation note', 'workshop-safe', 'simulation note', 'audit trail', 'approval gate', 'policy', 'taskboard'];
    const normalizedFinalAnswer = String(finalAnswer || '').trim();
    const isUsefulFinalAnswer = normalizedFinalAnswer && !hiddenPrefixes.some((prefix) => normalizedFinalAnswer.toLowerCase().startsWith(prefix));
    if (refs.finalOutputPanel && isUsefulFinalAnswer) {
      refs.finalOutputPanel.classList.remove('hidden');
      if (refs.finalOutputBody) renderFinalOutput(refs.finalOutputBody, normalizedFinalAnswer);
      if (refs.finalOutputStatus) refs.finalOutputStatus.textContent = getCandidateStatusLabel(data?.approval_summary?.final_status);
      if (refs.copyOutputBtn) refs.copyOutputBtn.disabled = false;
    } else if (refs.finalOutputPanel) refs.finalOutputPanel.classList.add('hidden');
    if (!isUsefulFinalAnswer) {
      if (refs.copyOutputBtn) refs.copyOutputBtn.disabled = true;
    }
    if (refs.learningTakeawayPanel) refs.learningTakeawayPanel.classList.remove('hidden');
    if (refs.learningTakeawayCopy) refs.learningTakeawayCopy.textContent = getLearningTakeaway(level, Boolean(data?.runtime_error));
    if (refs.nextStepPanel) refs.nextStepPanel.classList.remove('hidden');
    if (refs.nextStepCopy) refs.nextStepCopy.textContent = getRecommendedNextStep(level);
    renderQuickCompareActions(level);
    if (refs.rawTraceDetails) refs.rawTraceDetails.open = Boolean(data?.runtime_error);
    if (data?.runtime_error) {
      setStatus('Rendered with warning', 'failed');
      if (refs.runSummaryPanel) refs.runSummaryPanel.classList.add('warning');
      if (refs.runSummaryStatus) refs.runSummaryStatus.textContent = 'Rendered with warning';
      if (refs.runSummaryCopy) refs.runSummaryCopy.textContent = 'This level returned structured output, but one or more AI calls failed safely. No external action was taken.';
      getRuntimeWarningLines(data.runtime_error).forEach((line) => {
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
      if (refs.runSummaryCopy) refs.runSummaryCopy.textContent = 'Glytch rendered this level as a workshop-safe simulation. Review the scores, workflow steps and transcript before using the output.';
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
    setDisabled(refs.downloadArtifactBtn, false);
  } catch (err) {
    console.error('Level run failed', err);
    setStatus('Request failed', 'failed');
    setText(refs.log, '');
    const lines = [
      'Simulation could not complete. No action was taken.',
      `Reason: ${err?.message || 'Unknown error'}`,
    ];
    if (err?.code) lines.push(`Code: ${err.code}`);
    if (err?.status) lines.push(`HTTP status: ${err.status}`);
    if (err?.requestId) lines.push(`Request ID: ${err.requestId}`);
    if (err?.code === 'upstream_timeout') {
      lines.push(
        'Hint: The AI provider took too long to respond. Retry, try a lower level, or reduce scenario detail.'
      );
    }
    if (err?.code === 'upstream_http') {
      lines.push(
        'Hint: Check OPENAI_MODEL in your hosting environment. If you recently tried gpt-5.2, set OPENAI_MODEL back to gpt-4.1-mini or confirm your OpenAI project has access to the configured model.'
      );
    }
    if (refs.runSummaryPanel) {
      refs.runSummaryPanel.classList.remove('hidden');
      refs.runSummaryPanel.classList.add('warning');
    }
    if (refs.runSummaryStatus) refs.runSummaryStatus.textContent = 'Request failed';
    if (refs.runSummaryCopy) {
      refs.runSummaryCopy.textContent = 'The run could not complete. No external action was taken.';
    }
    if (refs.runSummaryList) {
      refs.runSummaryList.textContent = '';
      lines.forEach((line) => {
        refs.runSummaryList.appendChild(createEl('li', '', line));
      });
    }
    if (refs.advancedResultsDetails) {
      refs.advancedResultsDetails.classList.remove('hidden');
      refs.advancedResultsDetails.open = true;
    }
    if (refs.rawTraceDetails) refs.rawTraceDetails.open = true;
    appendMessage('system', lines.join(String.fromCharCode(10)));
    setDisabled(refs.replayBtn, true);
    setDisabled(refs.downloadArtifactBtn, true);
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
        description: 'Create a simple launch plan for a new product or service.',
        goal: 'create a simple launch plan for a new product or service for a small business',
        audience: 'busy small business owner',
        constraints: 'plain English, practical next steps, no jargon, do not assume a specific industry unless the user provides one',
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
  const previousMode = state.setupMode;
  const modeChanged = previousMode && previousMode !== mode;

  state.setupMode = mode;

  if (modeChanged) {
    state.confirmedUseCase = null;
    state.confirmedUseCaseLabel = null;
    hideConfirmedContext();
    updateLevelButtonsVisibility();
  }
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
  hideConfirmedContext();
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

function mergeOptionalContext(baseContext, optionalContext) {
  const base = String(baseContext || '').trim();
  const extra = String(optionalContext || '').trim();
  if (!extra) return base;
  if (!base) return extra;
  return `${base}\nUser refinement: ${extra}`;
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
    state.confirmedUseCase = null;
    state.confirmedUseCaseLabel = null;
    hideConfirmedContext();

    if (refs.selectionLabel) {
      refs.selectionLabel.textContent = 'Enter your goal to enable confirmation.';
    }
    if (refs.confirmBtn) refs.confirmBtn.disabled = true;

    clearOutput('Custom use case changed. Add a clear goal, then confirm direction again.');
    updateLevelButtonsVisibility();
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
  hideConfirmedContext();
  if (refs.selectionLabel) refs.selectionLabel.textContent = `Selected custom use case: ${state.customUseCaseGoal.slice(0, 72)}`;
  if (refs.confirmBtn) refs.confirmBtn.disabled = false;
  clearOutput('Custom use case updated. Confirm direction to continue.');
  updateLevelButtonsVisibility();
}

on(el('start-btn'), 'click', () => {
  onboarding.openApp();
  state.selectedUseCaseContext = '';
  hideConfirmedContext();
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
on(refs.contextInput, 'input', () => {
  if (!state.confirmedUseCase) return;
  state.confirmedUseCase = null;
  state.confirmedUseCaseLabel = null;
  if (refs.selectionLabel) {
    refs.selectionLabel.textContent = 'Context changed. Confirm this direction again before running.';
  }
  if (refs.confirmBtn) refs.confirmBtn.disabled = false;
  updateLevelButtonsVisibility();
  hideConfirmedContext();
});
on(refs.confirmBtn, 'click', () => {
  if (!state.selectedUseCase) return clearOutput('Select a use case before confirming direction.');
  const optionalContext = refs.contextInput?.value.trim() || '';
  if (state.setupMode === 'example') {
    state.selectedUseCaseContext = optionalContext;
  }
  if (state.setupMode === 'surprise') {
    const baseContext = state.selectedCustomScenario
      ? [
          `Goal: ${state.selectedCustomScenario.goal}`,
          `Audience: ${state.selectedCustomScenario.audience}`,
          `Constraints: ${state.selectedCustomScenario.constraints}`,
        ].filter(Boolean).join('\n')
      : state.selectedUseCaseContext;
    state.selectedUseCaseContext = mergeOptionalContext(baseContext, optionalContext);
  }
  if (state.setupMode === 'custom') {
    if (!state.selectedUseCaseContext) return clearOutput('Add a clear custom goal before confirming.');
    state.selectedUseCaseContext = mergeOptionalContext(buildCustomContext(), optionalContext);
  }
  state.confirmedUseCase = state.selectedUseCase;
  state.confirmedUseCaseLabel = state.selectedUseCaseLabel || state.selectedUseCase;
  const label = state.confirmedUseCaseLabel;
  const hasContext = Boolean(state.selectedUseCaseContext && state.selectedUseCaseContext.trim());
  if (refs.selectionLabel) {
    refs.selectionLabel.textContent = `Confirmed direction: ${label}. Context included: ${hasContext ? 'yes' : 'no'}.`;
  }
  clearOutput('Direction confirmed. Choose a level to run.');
  updateLevelButtonsVisibility();
  showConfirmedContext();
  onboarding.onConfirmed();
});
on(refs.replayBtn, 'click', runReplay);

on(refs.copyOutputBtn, 'click', async () => {
  const text = refs.finalOutputBody?.textContent?.trim() || '';
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    if (refs.copyOutputBtn) refs.copyOutputBtn.textContent = 'Copied';
    setTimeout(() => {
      if (refs.copyOutputBtn) refs.copyOutputBtn.textContent = 'Copy output';
    }, 1400);
  } catch (err) {
    console.warn('Copy output failed', err);
    appendMessage('system', 'Could not copy output automatically. You can select and copy it manually.');
  }
});

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

function renderQuickCompareActions(level) {
  if (!refs.quickCompareActions) return;
  refs.quickCompareActions.textContent = '';
  if (!state.confirmedUseCase) return;
  const labelByLevel = { 1: 'Compare Level 1', 3: 'Compare Level 3', 8: 'Compare Level 8' };
  [1, 3, 8].filter((targetLevel) => targetLevel !== level).forEach((targetLevel) => {
    const button = createEl('button', 'ghost', labelByLevel[targetLevel] || `Compare Level ${targetLevel}`);
    button.type = 'button';
    button.addEventListener('click', () => runLevel(targetLevel));
    refs.quickCompareActions.appendChild(button);
  });
}
