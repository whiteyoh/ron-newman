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

export function humanizeStatus(status) {
  const text = String(status || 'pending').replaceAll('_', ' ');
  return text.charAt(0).toUpperCase() + text.slice(1);
}
