export const el = (id) => document.getElementById(id);

export const refs = {
  buttons: el('buttons'),
  log: el('log'),
  apiState: el('api-state'),
  meta: el('meta'),
  useCaseOptions: el('use-case-options'),
  selectionLabel: el('selection-label'),
  confirmBtn: el('confirm-btn'),
  downloadArtifactBtn: el('download-artifact'),
  useCaseModal: el('use-case-modal'),
  modalTitle: el('modal-title'),
  modalBody: el('modal-body'),
  modalCloseBtn: el('modal-close'),
  contextInput: el('context-input'),
  theatreSteps: el('theatre-steps'),
  replayBtn: el('replay-btn'),
  replayState: el('replay-state'),
  taskboardEl: el('taskboard'),
  scorePanel: el('score-panel'),
  beforeAfter: el('before-after'),
  previewTools: document.querySelector('.preview-tools'),
  maturityCards: el('maturity-cards'),
};

export const createEl = (tag, cls, text) => {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
};

export const appendKV = (parent, label, value) => {
  const row = createEl('div');
  row.appendChild(createEl('strong', '', `${label}: `));
  row.appendChild(document.createTextNode(value));
  parent.appendChild(row);
};

export const pretty = (value, fallback = 'Available after run') =>
  value === undefined || value === null || value === '' ? fallback : String(value);

export const safeScore = (value, fallback = 'Available after run') =>
  Number.isFinite(Number(value)) ? `${Number(value)}/10` : fallback;

export const setStatus = (label, type = '') => {
  refs.apiState.textContent = '';
  refs.apiState.appendChild(createEl('span', `pill ${type}`.trim(), label));
};
