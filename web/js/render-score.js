import { createEl, pretty, refs, safeScore } from './dom.js';

export function renderScorePanel(agenticness, data) {
  refs.scorePanel.textContent = '';
  if (!agenticness) return;
  const sim = data?.yegge_simulation || {};
  const fields = [
    ['Capability', safeScore(agenticness.capability_score ?? data?.score_summary?.capability_score), 'Capability = what AI behaviour is being demonstrated'],
    ['Workflow control', safeScore(agenticness.agenticness_score ?? agenticness.score), 'Workflow control = how much workflow control/autonomy surrounds it'],
    ['Maturity match', safeScore(agenticness.yegge_alignment_score, 'Not applicable to this level'), 'Maturity match = how clearly this run demonstrates the intended level'],
  ];
  fields.forEach(([k, v, e]) => {
    const c = createEl('article', 'score-card');
    c.append(createEl('strong', '', k), createEl('div', '', v), createEl('div', 'muted', e));
    refs.scorePanel.appendChild(c);
  });
  [
    ['Closest maturity stage', pretty(agenticness.closest_yegge_stage || sim.closest_yegge_stage, 'Workshop-safe simulation')],
    ['Why this maps to the maturity model', pretty(sim.why_this_maps_to_yegge || agenticness.yegge_alignment_explanation, 'Workshop-safe simulation mapping shown after run')],
    ['Why this is not production', pretty(sim.why_not_production, 'Workshop-safe simulation')],
  ].forEach(([k, v]) => {
    const c = createEl('article', 'score-card');
    c.append(createEl('strong', '', k), createEl('div', '', v));
    refs.scorePanel.appendChild(c);
  });
}
