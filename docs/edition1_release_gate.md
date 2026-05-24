# Tech I Can | Glytch — Edition 1 Release Gate

## Purpose

This gate is the final checklist for shipping Glytch classroom materials and the workshop-safe demo at Edition 1 quality.

## Release criteria

### Product readiness

- [ ] Demo launches locally with `python app.py`
- [ ] Levels 1-8 execute without runtime regression in smoke checks
- [ ] Score panel, workflow detail, and replay render as expected
- [ ] Level 8 taskboard and merge summary remain visible and understandable

### Documentation readiness

- [ ] `README.md` includes setup, demo usage, and docs map
- [ ] `STEP_BY_STEP.md` reflects current workflow and commands
- [ ] Canonical docs exist in `docs/`:
  - `first_lesson_walkthrough.md`
  - `teacher_guide.md`
  - `student_worksheet.md`
  - `architecture.md`
  - `how_llms_work.md`
- [ ] Book manuscript exists: `docs/tech_i_can_glytch_book.md`

### Printable readiness

- [ ] Printable PDFs generated and committed in `docs/printable/`
- [ ] Aliases exist for teacher guide, student worksheet, and first lesson walkthrough
- [ ] Book PDF generated: `Tech_I_Can_Glytch_Book.pdf`

### Classroom safety readiness

- [ ] School-safe boundaries are documented and visible
- [ ] No personal data requirements in walkthroughs or worksheets
- [ ] Human review requirements are explicit in teaching materials

### Quality gate

- [ ] Documentation integrity tests pass
- [ ] Book manuscript quality tests pass
- [ ] Existing regression and behavior tests pass

## Sign-off

Release owner: __________________________

Date: _________________________________

Notes / known limitations:

```text

```
