# Frontend QA checklist

- [ ] Network/API failure shows friendly message: "Something went wrong while running the simulation. No action was taken. Please try again."
- [ ] Running a level never leaves UI stuck in running state.
- [ ] No raw `undefined`, `null`, or `n/a` appears in normal UI.
- [ ] Level 7 theatre shows actual action value from trace.
- [ ] Level 8 taskboard renders real worker records from orchestrator run state.
- [ ] Level 8 approval/merge panel appears and shows verifier + policy fields.
- [ ] Replay works after a successful run.
- [ ] Replay remains disabled after a failed run.
- [ ] Mobile quiz segmented Yes/No buttons remain tappable and use `aria-pressed`.
- [ ] Preview layout toggle is hidden unless `?debug=1`.
- [ ] Transcript remains read-only and does not ask the user for input.
- [ ] No horizontal scroll on iPhone-sized viewport.
