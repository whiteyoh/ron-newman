import { appendKV, createEl, pretty, refs } from './dom.js';
import { humanizeStatus, normalizeStatus } from './render-theatre.js';

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
  let visibleColumns = 0;
  columns.forEach((status) => {
    const workers = normalized.filter((r) => r.status === status);
    if (!workers.length) return;
    visibleColumns += 1;
    const col = createEl('section', 'taskboard-column');
    col.appendChild(createEl('h4', '', humanizeStatus(status)));
    workers.forEach((w) => {
      const wc = createEl('article', `worker-card ${w.status}`);
      appendKV(wc, 'Worker', w.worker_name); appendKV(wc, 'Role', w.worker_role); appendKV(wc, 'Task', w.task);
      appendKV(wc, 'Status', `${humanizeStatus(w.status)} · Worker: ${humanizeStatus(w.worker_status)}`); appendKV(wc, 'Attempt', String(w.attempt)); appendKV(wc, 'Output', w.output);
      if (w.error) wc.appendChild(createEl('div', 'pill blocked', `Error: ${w.error}`));
      col.appendChild(wc);
    });
    wrap.appendChild(col);
  });
  if (!visibleColumns) wrap.appendChild(createEl('p', 'muted', 'No pending, running, review, or failed workers.'));
  refs.taskboardEl.appendChild(wrap);
  const approval = data?.approval_summary || {};
  const panel = createEl('section', 'panel approval-panel');
  panel.appendChild(createEl('h4', '', 'Review and merge simulation'));
  appendKV(panel, 'Verifier result', pretty(approval.verifier_result, 'Available after run'));
  appendKV(panel, 'Review required', pretty(approval.approval_required, 'Available after run'));
  appendKV(panel, 'Simulated review outcome', pretty(approval.approved, 'Available after run'));
  appendKV(panel, 'Simulated merge decision', pretty(approval.merge_decision, 'Available after run'));
  appendKV(panel, 'Merge policy', pretty(approval.merge_policy, 'Workshop-safe simulation'));
  appendKV(panel, 'Simulation status', pretty(approval.final_status || approval.merge_decision, 'Available after run'));
  const decision = String(approval.merge_decision || '').toLowerCase();
  panel.appendChild(createEl('p', 'muted', decision.includes('approved') ? 'Verifier supported the output. In a real workflow, this would wait for human approval before merge.' : 'Needs human review — simulated merge would not proceed.'));
  refs.taskboardEl.appendChild(panel);
}
