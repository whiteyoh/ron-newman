import { createEl, el, refs } from './dom.js';
import { clearOutput, updateLevelButtonsVisibility } from './run-ui.js';
import { state } from './state.js';

const GUIDED_CONTEXT = 'Year 10 revision lesson on nutrition and healthy eating';

function clearPresetSelectionState() {
  state.selectedCustomScenario = null;
  state.customUseCaseGoal = '';
  state.customUseCaseAudience = '';
  state.customUseCaseConstraints = '';
}

export function renderUseCases(data) {
  refs.useCaseOptions.textContent = '';
  Object.entries(data).forEach(([key, text], i) => {
    const b = createEl('button', 'option');
    b.type = 'button';
    b.append(createEl('strong', '', `${i + 1}. ${key.replaceAll('_', ' ')}`), createEl('div', 'muted', `${text.split('.')[0]}.`), createEl('span', 'pill', 'Select scenario'));
    b.onclick = () => {
      state.selectedUseCase = key;
      state.confirmedUseCase = null;
      clearPresetSelectionState();
      if (state.selectedUseCaseContext === GUIDED_CONTEXT) state.selectedUseCaseContext = '';
      if (refs.contextInput?.value.trim() === GUIDED_CONTEXT) refs.contextInput.value = '';
      refs.confirmBtn.disabled = false;
      refs.selectionLabel.textContent = `Selected (not confirmed): ${key.replaceAll('_', ' ')}`;
      document.querySelectorAll('.option').forEach((o) => o.classList.remove('active'));
      b.classList.add('active');
      clearOutput('Use case changed. Confirm direction to continue.');
      updateLevelButtonsVisibility();
    };
    b.ondblclick = () => {
      refs.modalTitle.textContent = `Use case context: ${key.replaceAll('_', ' ')}`;
      refs.modalBody.textContent = text;
      refs.useCaseModal.classList.remove('hidden');
    };
    refs.useCaseOptions.appendChild(b);
  });
}

export function renderSurpriseUseCases(cases) {
  refs.surpriseUseCaseOptions.textContent = '';
  cases.forEach((useCase) => {
    const card = createEl('button', 'option surprise-card');
    card.type = 'button';
    card.append(
      createEl('strong', '', useCase.title),
      createEl('div', 'muted', useCase.description),
      createEl('span', 'pill', 'Select scenario'),
    );
    card.onclick = () => {
      state.selectedUseCase = 'custom';
      state.confirmedUseCase = null;
      state.selectedCustomScenario = {
        key: 'custom',
        title: useCase.title,
        description: 'Surprise example scenario',
        goal: useCase.goal,
        audience: useCase.audience,
        constraints: useCase.constraints,
      };
      state.selectedUseCaseContext = useCase.context;
      refs.confirmBtn.disabled = false;
      refs.selectionLabel.textContent = `Selected surprise use case: ${useCase.title}`;
      document.querySelectorAll('.surprise-card').forEach((o) => o.classList.remove('active'));
      card.classList.add('active');
      clearOutput('Surprise scenario selected. Confirm direction to continue.');
      updateLevelButtonsVisibility();
    };
    refs.surpriseUseCaseOptions.appendChild(card);
  });
}

export const renderBeforeAfter = (levels) => { refs.beforeAfter.textContent = ''; Object.entries(levels).forEach(([id, l]) => { const c = createEl('article', 'card'); c.append(createEl('h3', '', `Level ${id}: ${l.name}`), createEl('p', '', `Before: ${l.before || 'Raw model capability.'}`), createEl('p', '', `Agentic: ${l.agentic || 'Adds checks, approval, and traceable decisions.'}`)); refs.beforeAfter.appendChild(c); }); };
export const renderMaturityStages = (stages) => stages.forEach((s) => { const c = createEl('article', 'card'); c.append(createEl('strong', '', `Stage ${s.id}: ${s.name}`), createEl('div', 'muted', s.plain_english_summary || '')); el('maturity-cards').appendChild(c); });
export const renderLevelCards = (levels, onClick) => Object.entries(levels).forEach(([k, v]) => { const b = createEl('button', 'level-card'); b.type = 'button'; b.append(createEl('strong', '', `Level ${k}: ${v.name}`), createEl('span', '', v.description || ''), createEl('span', 'muted', 'Run to inspect workflow'), createEl('span', 'pill', 'Workshop-safe')); b.onclick = () => onClick(Number(k)); refs.buttons.appendChild(b); });
