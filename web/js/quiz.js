import { createEl, el } from './dom.js';
import { state } from './state.js';

export function calculateAssessment(answers) {
  const [promptOnly, fileEdits, approveEveryAction, runsTools, terminalAgents, multipleAgents, taskboardReview, ownOrchestration] = answers.map(Boolean);
  let stage = 'Stage 1', confidence = 'low', summary = 'You are mostly using AI for prompt-and-response support.', riskWarning = 'Avoid treating first drafts as final answers.', nextSafeStep = 'Try a short checklist before you trust an output.', suggestedLevel = 1;
  if (ownOrchestration) { stage = 'Stage 8'; confidence = 'high'; summary = 'You are coordinating your own orchestration system in a workshop-safe way.'; riskWarning = 'Do not skip human approval when many steps interact.'; nextSafeStep = 'Add clear approval gates and stop conditions for every run.'; suggestedLevel = 8; }
  else if ((multipleAgents || taskboardReview) && (runsTools || terminalAgents) && (fileEdits || approveEveryAction)) { stage = 'Stage 6–7'; confidence = 'medium'; summary = 'You are coordinating multiple agents with review pressure.'; riskWarning = 'Coordination can hide mistakes when everyone assumes someone else checked.'; nextSafeStep = 'Use task-by-task verification with explicit human sign-off.'; suggestedLevel = 7; }
  else if ((runsTools || terminalAgents) && (fileEdits || approveEveryAction)) { stage = 'Stage 4–5'; confidence = 'medium'; summary = 'You are using AI beyond prompts with bounded tools or terminal-style agents.'; riskWarning = 'Tool output can still be wrong if inputs or checks are weak.'; nextSafeStep = 'Add independent verification before accepting results.'; suggestedLevel = 4; }
  else if (fileEdits && approveEveryAction) { stage = 'Stage 2–3'; confidence = 'medium'; summary = 'You are using AI edits with human supervision on every action.'; riskWarning = 'Over-trust can creep in if reviews become automatic.'; nextSafeStep = 'Practice bounded tool use with verification.'; suggestedLevel = 4; }
  else if (promptOnly) { stage = 'Stage 1–2'; confidence = 'medium'; summary = 'You are mainly in prompt-only mode with light workflow structure.'; riskWarning = 'Outputs may sound confident even when facts are weak.'; nextSafeStep = 'Start structured review before applying outputs.'; suggestedLevel = 2; }
  return { stage, confidence, summary, riskWarning, nextSafeStep, suggestedLevel };
}

export function renderAssessmentResult() {
  const result = calculateAssessment(state.quizAnswers);
  const root = el('assessment-result');
  root.textContent = '';
  root.appendChild(createEl('p', '', `You are probably around ${result.stage}. Confidence: ${result.confidence}. ${result.summary}`));
  root.appendChild(createEl('p', '', `Risk warning: ${result.riskWarning}`));
  root.appendChild(createEl('p', '', `Next safe step: ${result.nextSafeStep}`));
  root.appendChild(createEl('p', '', `Try Glytch Level ${result.suggestedLevel} next.`));
}

export function renderQuiz() {
  const q = el('quiz-questions');
  const qs = ['Only prompt AI', 'AI edits files', 'You approve every action', 'AI runs tools', 'Terminal agents', 'Multiple agents', 'Taskboard review', 'Own orchestration system'];
  q.textContent = '';
  qs.forEach((t, i) => {
    const c = createEl('article', 'quiz-card segmented-card'); c.appendChild(createEl('strong', '', `${i + 1}. ${t}`));
    const seg = createEl('div', 'segmented'); seg.setAttribute('role', 'group'); seg.setAttribute('aria-label', t);
    const no = createEl('button', `seg-btn ${!state.quizAnswers[i] ? 'active' : ''}`, 'No'); no.type = 'button'; no.dataset.q = String(i); no.dataset.v = '0'; no.setAttribute('aria-pressed', String(!state.quizAnswers[i]));
    const yes = createEl('button', `seg-btn ${state.quizAnswers[i] ? 'active' : ''}`, 'Yes'); yes.type = 'button'; yes.dataset.q = String(i); yes.dataset.v = '1'; yes.setAttribute('aria-pressed', String(state.quizAnswers[i]));
    seg.append(no, yes); c.appendChild(seg); q.appendChild(c);
  });
  q.onclick = (e) => { const b = e.target.closest('.seg-btn'); if (!b) return; const i = Number(b.dataset.q); state.quizAnswers[i] = b.dataset.v === '1'; renderQuiz(); renderAssessmentResult(); };
  renderAssessmentResult();
}
