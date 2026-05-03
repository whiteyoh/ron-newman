# Frontend QA checklist

- [ ] Quiz result shows an estimated Yegge stage, confidence, risk warning, next safe step, and suggested Glytch level.
- [ ] Quiz result updates immediately when selecting segmented Yes/No buttons.
- [ ] Startup API failure shows: "Glytch could not load the demo data. No action was taken. Please refresh and try again."
- [ ] Startup failure sets status to "Startup failed" and keeps non-loaded sections explained (no blank mystery areas).
- [ ] Run failure logs the real error in the browser console and shows: "Something went wrong while running the simulation. No action was taken. Please try again."
- [ ] Running a level never leaves UI stuck in running state.
- [ ] Level 8 approval panel final status reflects run outcome (not level name).
- [ ] No raw `undefined`, `null`, or `n/a` appears in normal UI.
- [ ] Level 7 theatre shows actual action value from trace.
- [ ] Level 8 taskboard renders real worker records from orchestrator run state.
- [ ] Replay works after a successful run.
- [ ] Replay remains disabled after a failed run.
- [ ] Mobile quiz segmented Yes/No buttons remain tappable and use `aria-pressed`.
- [ ] Preview layout toggle is hidden unless `?debug=1`.
- [ ] Transcript remains read-only and does not ask the user for input.
- [ ] No horizontal scroll on iPhone-sized viewport.
- [ ] Page remains mobile-friendly after startup or run failures.
