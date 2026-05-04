import { appendKV, createEl, pretty, refs } from './dom.js';
import { normalizeStatus } from './render-theatre.js';

const summarizeOutput = (output) => (!output ? 'No output yet.' : String(output).slice(0, 180));

export function renderTaskboard(data) {
  refs.taskboardEl.textContent = '';
  const board = data?.taskboard;
  const records = Array.isArray(board) ? board : Array.isArray(board?.workers) ? board.workers : [];
  if (!records.length) {
    refs.taskboardEl.appendChild(createEl('p', 'muted', 'Run Level 8 to see the orchestrator dashboard.'));
    return;
  }
  const normalized = records.map((r) => ({
    worker_name: r.worker_name || r.worker || 'Worker',
    worker_role: r.worker_role || r.role || 'agent',
    task: r.task || 'No task description',
    status: normalizeStatus(r.status),
    worker_status: normalizeStatus(r.worker_status || r.status),
    attempt: r.attempt || 1,
    output: summarizeOutput(r.output || r.output_summary || r.summary),
    error: r.error || '',
  }));
  const columns = ['pending', 'running', 'completed', 'needs_human_review', 'merged', 'failed'];
  const wrap = createEl('div', 'taskboard-grid');
  columns.forEach((status) => {
    const col = createEl('section', 'taskboard-column');
    col.appendChild(createEl('h4', '', status.replaceAll('_', ' ')));
    normalized.filter((r) => r.status === status).forEach((w) => {
      const wc = createEl('article', `worker-card ${w.status}`);
      appendKV(wc, 'Worker', w.worker_name); appendKV(wc, 'Role', w.worker_role); appendKV(wc, 'Task', w.task);
      appendKV(wc, 'Status', `${w.status} · Worker: ${w.worker_status}`); appendKV(wc, 'Attempt', String(w.attempt)); appendKV(wc, 'Output', w.output);
      if (w.error) wc.appendChild(createEl('div', 'pill blocked', `Error: ${w.error}`));
      col.appendChild(wc);
    });
    if (!col.querySelector('.worker-card')) col.appendChild(createEl('div', 'muted', 'No workers in this state.'));
    wrap.appendChild(col);
  });
  refs.taskboardEl.appendChild(wrap);
  const approval = data?.approval_summary || {};
  const panel = createEl('section', 'panel approval-panel');
  panel.appendChild(createEl('h4', '', 'Approval and merge summary'));
  appendKV(panel, 'Verifier result', pretty(approval.verifier_result, 'Available after run'));
  appendKV(panel, 'Approval required', pretty(approval.approval_required, 'Available after run'));
  appendKV(panel, 'Approved for merge', pretty(approval.approved, 'Available after run'));
  appendKV(panel, 'Merge decision', pretty(approval.merge_decision, 'Available after run'));
  appendKV(panel, 'Merge policy', pretty(approval.merge_policy, 'Workshop-safe simulation'));
  appendKV(panel, 'Final status', pretty(approval.final_status || approval.merge_decision, 'Available after run'));
  const decision = String(approval.merge_decision || '').toLowerCase();
  panel.appendChild(createEl('p', 'muted', decision.includes('approved') ? 'Merged after verifier and approval gate.' : 'Needs human review — merge blocked by verifier or approval gate.'));
  refs.taskboardEl.appendChild(panel);
}
