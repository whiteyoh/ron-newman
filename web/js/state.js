export const state = {
  quizAnswers: Array(8).fill(false),
  selectedUseCase: null,
  confirmedUseCase: null,
  selectedUseCaseContext: '',
  latestArtifact: null,
  runInProgress: false,
  lastReplaySteps: [],
  theatreCards: [],
};

export const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
