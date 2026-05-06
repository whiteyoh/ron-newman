export const state = {
  quizAnswers: Array(8).fill(false),
  selectedUseCase: null,
  selectedUseCaseLabel: null,
  confirmedUseCase: null,
  confirmedUseCaseLabel: null,
  setupMode: 'example',
  customUseCaseGoal: '',
  customUseCaseAudience: '',
  customUseCaseConstraints: '',
  surpriseUseCases: [],
  selectedCustomScenario: null,
  selectedUseCaseContext: '',
  latestArtifact: null,
  runInProgress: false,
  lastReplaySteps: [],
  theatreCards: [],
  guideActive: false,
  guideStep: 0,
  guideCompleted: false,
  guidedScenarioKey: 'uk_year10_teacher',
  guidedContext: 'Year 10 revision lesson on nutrition and healthy eating',
  guidedRecommendedLevel: 1,
  waitingForLevel3Comparison: false,
  level3StartedFromGuide: false,
};

export const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
