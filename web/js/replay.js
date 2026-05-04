import { appendMessage } from './run-ui.js';
import { refs } from './dom.js';
import { prefersReducedMotion, sleep, state } from './state.js';

export async function runReplay() {
  if (!state.lastReplaySteps.length || state.runInProgress) return;
  refs.replayBtn.disabled = true;
  for (let i = 0; i < state.lastReplaySteps.length; i += 1) {
    state.theatreCards.forEach((c) => c.classList.remove('active-replay'));
    state.theatreCards[i]?.classList.add('active-replay');
    appendMessage('system', `Replay: ${state.lastReplaySteps[i]}`);
    await sleep(prefersReducedMotion ? 0 : 300);
  }
  refs.replayBtn.disabled = false;
  refs.replayState.textContent = 'Replay finished';
}
