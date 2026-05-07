import { el, refs } from './dom.js';
import { clearOutput, updateLevelButtonsVisibility } from './run-ui.js';
import { state } from './state.js';

const GUIDE_KEY = 'glytch.firstRunGuide.completed';
const GUIDED_SCENARIO = 'uk_year10_teacher';
const GUIDED_CONTEXT = 'Year 10 revision lesson on nutrition and healthy eating';
const RECOMMENDED_LEVEL = 1;

function focusGuideCard() {
  if (!refs.guideCard || refs.guideCard.classList.contains('hidden')) return;
  refs.guideCard.focus({ preventScroll: true });
}

function setGuideStep(text, muted = '') {
  if (refs.guideStep) refs.guideStep.textContent = text;
  if (refs.guideMuted) refs.guideMuted.textContent = muted;
  focusGuideCard();
}

function on(node, event, handler) {
  if (!node) return;
  node.addEventListener(event, handler);
}

function readGuideCompleted() {
  try {
    return localStorage.getItem(GUIDE_KEY) === 'completed';
  } catch {
    return false;
  }
}

function writeGuideCompleted() {
  try {
    localStorage.setItem(GUIDE_KEY, 'completed');
  } catch {
    // ignore storage failure; guide should still work for this session
  }
}

function setGuideReplayControlsVisible(visible) {
  if (refs.guideReplayBtn) refs.guideReplayBtn.hidden = !visible;
  if (refs.guideInlineBtn) refs.guideInlineBtn.hidden = !visible;
}

function highlight(id) {
  document.querySelectorAll('.guide-highlight').forEach((n) => n.classList.remove('guide-highlight'));
  const node = el(id);
  if (node) node.classList.add('guide-highlight');
}

function ensureVisible(id) {
  const node = el(id);
  if (node) node.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

export function initOnboarding({ runLevel }) {
  state.guideCompleted = readGuideCompleted();
  setGuideReplayControlsVisible(state.guideCompleted);

  const openApp = () => {
    const entry = el('entry');
    const app = el('app');
    if (entry) entry.classList.add('hidden');
    if (app) app.classList.remove('hidden');
  };

  const startGuide = () => {
    openApp();
    state.guideActive = true;
    state.guideStep = 'setup';
    state.waitingForLevel3Comparison = false;
    state.level3StartedFromGuide = false;
    if (refs.guideCard) refs.guideCard.classList.remove('hidden');
    setGuideReplayControlsVisible(false);
    if (refs.guideSkipBtn) refs.guideSkipBtn.classList.remove('hidden');
    if (refs.guideLevel3Btn) refs.guideLevel3Btn.classList.add('hidden');
    if (refs.guideFinishBtn) refs.guideFinishBtn.classList.add('hidden');
    if (refs.guideRecommendation) refs.guideRecommendation.textContent = '';

    state.selectedUseCase = GUIDED_SCENARIO;
    state.confirmedUseCase = null;
    state.selectedUseCaseContext = GUIDED_CONTEXT;
    if (refs.contextInput) refs.contextInput.value = GUIDED_CONTEXT;
    if (refs.confirmBtn) refs.confirmBtn.disabled = false;

    const options = refs.useCaseOptions ? [...refs.useCaseOptions.querySelectorAll('.option')] : [];
    options.forEach((o) => o.classList.remove('active'));
    const match = options.find((o) => o.textContent.toLowerCase().includes('uk year10 teacher'));
    if (match) match.classList.add('active');

    if (refs.selectionLabel) refs.selectionLabel.textContent = 'Selected (not confirmed): uk year10 teacher';
    clearOutput('Guided setup ready. Confirm this direction, then run Level 1.');
    updateLevelButtonsVisibility();

    setGuideStep(
      'We’ll start with a familiar teaching example. Confirm this direction first, then Glytch will recommend a simple starting level.',
      'Start with the lowest useful level. For a first run, that means Level 1 or Level 2.'
    );
    if (refs.guideRecommendation) refs.guideRecommendation.textContent = 'Guided scenario: Year 10 revision lesson on nutrition and healthy eating.';
    highlight('confirm-btn');
    ensureVisible('confirm-btn');
  };

  const completeGuide = () => {
    state.guideActive = false;
    state.guideCompleted = true;
    state.waitingForLevel3Comparison = false;
    state.level3StartedFromGuide = false;
    writeGuideCompleted();
    if (refs.guideCard) refs.guideCard.classList.add('hidden');
    document.querySelectorAll('.guide-highlight').forEach((n) => n.classList.remove('guide-highlight'));
    setGuideReplayControlsVisible(true);
  };

  const dismissGuideForManualChoice = () => {
    if (!state.guideActive) return;
    state.guideActive = false;
    state.waitingForLevel3Comparison = false;
    state.level3StartedFromGuide = false;
    if (refs.guideCard) refs.guideCard.classList.add('hidden');
    if (refs.guideLevel3Btn) refs.guideLevel3Btn.classList.add('hidden');
    if (refs.guideFinishBtn) refs.guideFinishBtn.classList.add('hidden');
    document.querySelectorAll('.guide-highlight').forEach((n) => n.classList.remove('guide-highlight'));
    setGuideReplayControlsVisible(state.guideCompleted);
  };

  on(refs.guideStartBtn, 'click', startGuide);
  on(refs.guideReplayBtn, 'click', startGuide);
  on(refs.guideInlineBtn, 'click', startGuide);
  on(refs.guideSkipBtn, 'click', completeGuide);
  on(refs.guideFinishBtn, 'click', completeGuide);

  on(refs.guideLevel3Btn, 'click', async () => {
    if (!state.confirmedUseCase) {
      setGuideStep('Before trying Level 3, confirm this direction first.', 'Use Confirm this direction, then run Level 3.');
      highlight('confirm-btn');
      return;
    }
    state.level3StartedFromGuide = true;
    state.waitingForLevel3Comparison = true;
    state.guideStep = 'level3Comparison';
    if (refs.guideFinishBtn) refs.guideFinishBtn.classList.add('hidden');
    await runLevel(3);
  });

  return {
    onConfirmed() {
      if (!state.guideActive) return;
      state.guideStep = 'level1';
      setGuideStep('Great. Now run Level 1 to see the baseline: prompt in, answer out, and human decides what to do next.');
      if (refs.guideRecommendation) refs.guideRecommendation.textContent = 'Recommended: Level 1 — Baseline. This shows simple prompt-only AI. Run it first, then compare it with Level 3.';
      highlight('buttons');
    },
    onRunComplete(level) {
      if (!state.guideActive) return;
      if (level === RECOMMENDED_LEVEL) {
        state.guideStep = 'explainOutput';
        state.waitingForLevel3Comparison = true;
        state.level3StartedFromGuide = false;
        setGuideStep(
          'This score panel shows capability, workflow control, and stage fidelity. Agentic theatre turns this run into a step-by-step visual story.',
          'Raw output transcript is read-only trace. If it looks like a question, it is part of the trace, not something you need to answer. Replay repeats the same steps and does not rerun AI. Level 8 adds a taskboard for orchestrator simulation.'
        );
        if (refs.guideLevel3Btn) refs.guideLevel3Btn.classList.remove('hidden');
        if (refs.guideFinishBtn) refs.guideFinishBtn.classList.add('hidden');
        highlight('score-panel');
        ensureVisible('dashboard-title');
        return;
      }

      if (level === 3 && state.waitingForLevel3Comparison && state.level3StartedFromGuide) {
        state.guideStep = 'final';
        state.waitingForLevel3Comparison = false;
        state.level3StartedFromGuide = false;
        setGuideStep(
          'You’ve now compared Level 1 and Level 3. Level 1 showed simple prompt-only AI. Level 3 added a bounded tool path. That is the Glytch idea: start simple, then move up only when the task needs more control.',
          'You can now keep exploring the levels freely.'
        );
        if (refs.guideLevel3Btn) refs.guideLevel3Btn.classList.add('hidden');
        if (refs.guideFinishBtn) refs.guideFinishBtn.classList.remove('hidden');
        if (refs.guideRecommendation) refs.guideRecommendation.textContent = '';
        highlight('theatre-steps');
        ensureVisible('theatre-steps');
      }

      if (level !== RECOMMENDED_LEVEL) {
        state.guideStep = 'explore';
        state.waitingForLevel3Comparison = false;
        state.level3StartedFromGuide = false;
        setGuideStep(
          `You ran Level ${level}. Good — you can now compare it with Level 1 or continue exploring freely.`,
          'The higher the level, the more workflow control and review structure Glytch shows.'
        );
        if (refs.guideLevel3Btn) refs.guideLevel3Btn.classList.add('hidden');
        if (refs.guideFinishBtn) refs.guideFinishBtn.classList.remove('hidden');
        if (refs.guideRecommendation) refs.guideRecommendation.textContent = '';
      }
    },
    isCompleted: () => state.guideCompleted,
    dismissGuideForManualChoice,
    openApp,
  };
}
