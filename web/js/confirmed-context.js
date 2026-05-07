import { refs } from './dom.js';
import { state } from './state.js';

export function showConfirmedContext() {
  const context = String(state.selectedUseCaseContext || '').trim();
  if (!context || !refs.confirmedContextDetails || !refs.confirmedContextBody) {
    hideConfirmedContext();
    return;
  }
  refs.confirmedContextBody.textContent = context;
  refs.confirmedContextDetails.open = false;
  refs.confirmedContextDetails.classList.remove('hidden');
}

export function hideConfirmedContext() {
  if (refs.confirmedContextBody) refs.confirmedContextBody.textContent = '';
  if (refs.confirmedContextDetails) {
    refs.confirmedContextDetails.open = false;
    refs.confirmedContextDetails.classList.add('hidden');
  }
}
