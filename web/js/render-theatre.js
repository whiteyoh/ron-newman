import { createEl, refs } from './dom.js';
import { state } from './state.js';

export function normalizeStatus(raw) {
  const value = (raw || 'pending').toString().toLowerCase().replace(/^taskstatus\./, '').trim();
  if (value.includes('needs human review') || value.includes('needs_human_review') || value.includes('needs review')) return 'needs_human_review';
  if (value.includes('merge')) return 'merged';
  if (value.includes('run')) return 'running';
  if (value.includes('complete')) return 'completed';
  if (value.includes('approve')) return 'approved';
  if (value.includes('block')) return 'blocked';
  if (value.includes('fail')) return 'failed';
  return 'pending';
}

export function renderTheatre(data) {
  refs.theatreSteps.textContent = '';
  state.theatreCards = [];
  const steps = data.theatre_steps || [];
  steps.forEach((s) => {
    const status = normalizeStatus(s.status);
    const card = createEl('article', `theatre-step ${status}`);
    const header = createEl('div', 'section-header');
    header.append(createEl('span', 'actor', (s.actor || 'agent').toLowerCase()), createEl('span', `pill ${status}`, status));
    card.append(header, createEl('strong', '', s.label || 'Step'), createEl('div', '', s.summary || ''), createEl('div', 'muted', s.detail || ''));
    state.theatreCards.push(card);
    refs.theatreSteps.appendChild(card);
  });
  state.lastReplaySteps = (data.replay_steps?.length ? data.replay_steps : steps.map((s) => s.summary || s.label)).filter(Boolean);
  refs.replayBtn.disabled = !state.lastReplaySteps.length;
}
