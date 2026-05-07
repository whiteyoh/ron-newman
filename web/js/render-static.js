import { createEl, el, refs } from './dom.js';
import { clearOutput, updateLevelButtonsVisibility } from './run-ui.js';
import { hideConfirmedContext } from './confirmed-context.js';
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
      state.selectedUseCaseLabel = key.replaceAll('_', ' ');
      state.confirmedUseCase = null;
      state.confirmedUseCaseLabel = null;
      hideConfirmedContext();
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
      state.selectedUseCaseLabel = useCase.title;
      state.confirmedUseCase = null;
      state.confirmedUseCaseLabel = null;
      hideConfirmedContext();
      state.selectedCustomScenario = {
        key: 'custom',
        title: useCase.title,
        description: 'Surprise example scenario',
        goal: useCase.goal,
        audience: useCase.audience,
        constraints: useCase.constraints,
      };
      state.selectedUseCaseContext = useCase.context;
      if (refs.contextInput) refs.contextInput.value = "";
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

const beforeAfterCopy = {
  1: {
    before: 'You ask for help and receive one draft or suggestion.',
    controlled: 'The human reviews, edits and decides the next step.',
  },
  2: {
    before: 'The prompt may be vague or inconsistent.',
    controlled: 'The task follows clearer instructions, format and constraints.',
  },
  3: {
    before: 'The model may guess concrete facts or calculations.',
    controlled: 'A bounded tool is used and the result can be checked.',
  },
  4: {
    before: 'The answer may rely on general model knowledge.',
    controlled: 'The response is grounded in retrieved evidence.',
  },
  5: {
    before: 'A broad task comes back as one large answer.',
    controlled: 'The work is split into visible steps with a clearer plan.',
  },
  6: {
    before: 'The first draft is treated as the final answer.',
    controlled: 'The draft is critiqued and revised before review.',
  },
  7: {
    before: 'The human manually drives every step.',
    controlled: 'A bounded loop observes, acts, checks and stops safely.',
  },
  8: {
    before: 'One response tries to do all the work.',
    controlled: 'Multiple simulated workers coordinate through checks, review and merge policy.',
  },
};

export const renderBeforeAfter = (levels) => {
  refs.beforeAfter.textContent = '';
  Object.entries(levels).forEach(([id, l]) => {
    const copy = beforeAfterCopy[id] || {
      before: 'This level shows the basic capability.',
      controlled: 'Glytch makes the workflow more visible, reviewable and bounded.',
    };
    const c = createEl('article', 'card');
    c.append(
      createEl('h3', '', `Level ${id}: ${l.name}`),
      createEl('p', '', `Basic use: ${copy.before}`),
      createEl('p', '', `With more control: ${copy.controlled}`),
    );
    refs.beforeAfter.appendChild(c);
  });
};
export const renderMaturityStages = (stages) => stages.forEach((s) => { const c = createEl('article', 'card'); c.append(createEl('strong', '', `Stage ${s.id}: ${s.name}`), createEl('div', 'muted', s.plain_english_summary || '')); el('maturity-cards').appendChild(c); });
export const renderLevelCards = (levels, onClick) => {
  refs.buttons.textContent = '';
  const groupOrder = ['Prompting', 'Tool use', 'Workflow control', 'Orchestration'];
  const groupDescriptions = {
    Prompting: 'Ask and answer.',
    'Tool use': 'Use bounded tools.',
    'Workflow control': 'Add checks and structure.',
    Orchestration: 'Coordinate multiple workers.',
  };
  const groups = { Prompting: [], 'Tool use': [], 'Workflow control': [], Orchestration: [] };
  Object.entries(levels).forEach(([k, v]) => {
    const id = Number(k);
    const group = id <= 2 ? 'Prompting' : id <= 4 ? 'Tool use' : id <= 6 ? 'Workflow control' : 'Orchestration';
    groups[group].push([k, v]);
  });

  groupOrder.forEach((groupName) => {
    const section = createEl('section', 'level-group');
    section.appendChild(createEl('h3', '', groupName));
    section.appendChild(createEl('p', 'muted level-group-description', groupDescriptions[groupName]));
    const grid = createEl('div', 'level-group-grid');
    groups[groupName].forEach(([k, v]) => {
      const b = createEl('button', 'level-card');
      b.type = 'button';
      b.append(createEl('strong', '', `Level ${k}: ${v.name}`), createEl('span', '', v.description || ''), createEl('span', 'muted', 'Run to inspect workflow'), createEl('span', 'pill', 'Workshop-safe'));
      b.onclick = () => onClick(Number(k));
      grid.appendChild(b);
    });
    section.appendChild(grid);
    refs.buttons.appendChild(section);
  });
};
