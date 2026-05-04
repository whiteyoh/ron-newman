import { el, refs } from './dom.js';
import { clearOutput, updateLevelButtonsVisibility } from './run-ui.js';
import { state } from './state.js';

const GUIDE_KEY = 'glytch.firstRunGuide.completed';
const GUIDED_SCENARIO = 'uk_year10_teacher';
const GUIDED_CONTEXT = 'Year 10 revision lesson on nutrition and healthy eating';
const RECOMMENDED_LEVEL = 1;

function setGuideStep(text, muted = '') {
  refs.guideStep.textContent = text;
  refs.guideMuted.textContent = muted;
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
  state.guideCompleted = localStorage.getItem(GUIDE_KEY) === 'completed';
  refs.guideReplayBtn.hidden = false;

  const openApp = () => {
    el('entry').classList.add('hidden');
    el('app').classList.remove('hidden');
  };

  const startGuide = () => {
    openApp();
    state.guideActive = true;
    state.guideStep = 1;
    refs.guideCard.classList.remove('hidden');
    refs.guideReplayBtn.classList.add('hidden');
    refs.guideSkipBtn.classList.remove('hidden');
    refs.guideLevel3Btn.classList.add('hidden');

    state.selectedUseCase = GUIDED_SCENARIO;
    state.confirmedUseCase = null;
    state.selectedUseCaseContext = GUIDED_CONTEXT;
    refs.contextInput.value = GUIDED_CONTEXT;
    refs.confirmBtn.disabled = false;

    const options = [...refs.useCaseOptions.querySelectorAll('.option')];
    options.forEach((o) => o.classList.remove('active'));
    const match = options.find((o) => o.textContent.toLowerCase().includes('uk year10 teacher'));
    if (match) match.classList.add('active');

    refs.selectionLabel.textContent = 'Selected (not confirmed): uk year10 teacher';
    clearOutput('Guided setup ready. Confirm this direction, then run Level 1.');
    updateLevelButtonsVisibility();

    setGuideStep(
      'We’ll start with a familiar teaching example. Glytch works best when you start simple, then move up only when the task needs more control.',
      'For a first run, start at Level 1 or Level 2. Start with the lowest useful level.'
    );
    refs.guideRecommendation.textContent = 'Recommended: Level 1 — Baseline. This shows simple prompt-only AI. Run it first, then compare it with Level 3.';
    highlight('levels-title');
    ensureVisible('setup-title');
  };

  const completeGuide = () => {
    state.guideActive = false;
    state.guideCompleted = true;
    localStorage.setItem(GUIDE_KEY, 'completed');
    refs.guideCard.classList.add('hidden');
    refs.guideReplayBtn.classList.remove('hidden');
    document.querySelectorAll('.guide-highlight').forEach((n) => n.classList.remove('guide-highlight'));
  };

  refs.guideStartBtn.onclick = startGuide;
  refs.guideReplayBtn.onclick = startGuide;
  refs.guideSkipBtn.onclick = completeGuide;

  refs.guideLevel3Btn.onclick = async () => {
    if (!state.confirmedUseCase) {
      setGuideStep('Before trying Level 3, confirm this direction first.', 'Use Confirm this direction, then run Level 3.');
      highlight('confirm-btn');
      return;
    }
    await runLevel(3);
  };

  return {
    onConfirmed() {
      if (!state.guideActive) return;
      state.guideStep = 2;
      setGuideStep('Great. Now run Level 1 to see the baseline: prompt in, answer out, and human decides what to do next.');
      highlight('buttons');
    },
    onRunComplete(level) {
      if (!state.guideActive || level !== RECOMMENDED_LEVEL) return;
      state.guideStep = 3;
      setGuideStep(
        'This score panel shows capability, workflow control, and stage fidelity. Agentic theatre turns this run into a step-by-step visual story.',
        'Raw output transcript is read-only trace. If it looks like a question, it is part of the trace, not something you need to answer. Replay repeats the same steps and does not rerun AI. Level 8 adds a taskboard for orchestrator simulation.'
      );
      refs.guideLevel3Btn.classList.remove('hidden');
      highlight('score-panel');
      ensureVisible('dashboard-title');
    },
    isCompleted: () => state.guideCompleted,
    openApp,
  };
}
