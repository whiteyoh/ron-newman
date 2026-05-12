import { appendKV, createEl, pretty, refs } from './dom.js';
import { humanizeStatus, normalizeStatus } from './status-utils.js';

const summarizeOutput = (output) => (!output ? 'No output yet.' : String(output).slice(0, 180));
const humanizeApprovalValue = (value) => {
  if (value === true || value === 'true') return 'Yes';
  if (value === false || value === 'false') return 'No';
  const normalized = String(value || '').toLowerCase();
  if (normalized === 'needs_human_review') return 'Needs human review';
  if (normalized === 'merged') return 'Ready for review';
  if (normalized === 'approved') return 'Approved';
  if (normalized === 'blocked') return 'Blocked';
  return pretty(value, 'Available after run');
};

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
      appendKV(wc, 'Step', w.worker_name); appendKV(wc, 'Role', w.worker_role); appendKV(wc, 'What it worked on', w.task);
      appendKV(wc, 'Result', `${humanizeStatus(w.status)} · Step status: ${humanizeStatus(w.worker_status)}`); appendKV(wc, 'Try', String(w.attempt)); appendKV(wc, 'Summary', w.output);
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
  appendKV(panel, 'Verifier result', humanizeApprovalValue(approval.verifier_result));
  appendKV(panel, 'Review required', humanizeApprovalValue(approval.approval_required));
  appendKV(panel, 'Simulated review outcome', humanizeApprovalValue(approval.approved));
  appendKV(panel, 'Simulated merge decision', humanizeApprovalValue(approval.merge_decision));
  appendKV(panel, 'Merge policy', pretty(approval.merge_policy, 'Workshop-safe simulation'));
  appendKV(panel, 'Simulation status', humanizeApprovalValue(approval.final_status || approval.merge_decision));
  const decision = String(approval.merge_decision || '').toLowerCase();
  panel.appendChild(createEl('p', 'muted', decision.includes('approved') ? 'Verifier supported the output. In a real workflow, this would wait for human approval before merge.' : 'Needs human review — simulated merge would not proceed.'));
  refs.taskboardEl.appendChild(panel);
}
