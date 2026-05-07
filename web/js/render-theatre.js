import { createEl, refs } from './dom.js';
import { state } from './state.js';
import { humanizeStatus, normalizeStatus } from './status-utils.js';

function humanizeTheatreLabel(label) {
  if (label === 'Human approval gate') return 'Human review checkpoint';
  if (label === 'Approved') return 'Simulated approval';
  if (label === 'Final approved output') return 'Candidate output';
  if (label === 'Merge approved') return 'Merge would be allowed';
  return label;
}

export function renderTheatre(data) {
  refs.theatreSteps.textContent = '';
  state.theatreCards = [];
  const steps = data.theatre_steps || [];
  steps.forEach((s) => {
    const status = normalizeStatus(s.status);
    const card = createEl('article', `theatre-step ${status}`);
    const header = createEl('div', 'section-header');
    header.append(createEl('span', 'actor', (s.actor || 'agent').toLowerCase()), createEl('span', `pill ${status}`, humanizeStatus(status)));
    card.append(header, createEl('strong', '', humanizeTheatreLabel(s.label || 'Workflow step')), createEl('div', '', s.summary || ''), createEl('div', 'muted', s.detail || ''));
    state.theatreCards.push(card);
    refs.theatreSteps.appendChild(card);
  });
  state.lastReplaySteps = (data.replay_steps?.length ? data.replay_steps : steps.map((s) => s.summary || s.label)).filter(Boolean);
  refs.replayBtn.disabled = !state.lastReplaySteps.length;
}
