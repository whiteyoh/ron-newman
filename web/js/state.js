export const state = {
  quizAnswers: Array(8).fill(false),
  selectedUseCase: null,
  confirmedUseCase: null,
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
};

export const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
