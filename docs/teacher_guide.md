# Kairo Teacher Guide

> Core reminder for students: **LLMs predict patterns; they do not think like humans.**

## 1) Classroom Setup Checklist

- [ ] Install Python 3.10+
- [ ] Clone repo and run `pip install -e .`
- [ ] (Optional UI) run `pip install -e ".[learn]"`
- [ ] Prepare one safe starter dataset (space/science text)
- [ ] Prepare one contrast dataset (pirate/fantasy tone)
- [ ] Test train/generate/evaluate commands before class
- [ ] Decide moderation mode (strict vs exploratory)
- [ ] Share classroom rules before first prompt

## 2) Estimated Timings (60–90 min session)

- Intro + safety framing: 10 min
- Train first model: 15–20 min
- Generate + inspect outputs: 15 min
- Retrain experiment: 15–20 min
- Reflection discussion: 10–15 min

## 3) Hardware Expectations

- CPU-only is fine for classroom demos.
- 8GB RAM is usually enough for tiny runs.
- Faster CPUs reduce training wait time.
- No GPU required for baseline lesson.

## 4) Example Safe Datasets

- Public-domain science fiction excerpts
- Teacher-authored short story text
- Curriculum-aligned topic summaries
- Synthetic classroom text written by staff

Avoid:

- Personal student writing with identifiers
- Sensitive personal data
- Toxic or unreviewed scraped internet dumps

## 5) Teacher Moderation Workflow

1. Pre-screen training data.
2. Run in safe mode defaults.
3. Review student prompts during initial rounds.
4. Stop and discuss harmful/odd outputs immediately.
5. Reinforce that generation reflects data patterns.
6. Record key surprises for debrief.

## 6) Classroom Rules

- No personal data in prompts or datasets.
- No abusive or targeted harmful prompts.
- Stay on lesson objectives.
- Report surprising outputs, do not hide them.
- Treat AI outputs as hypotheses, not truth.

## 7) What to Say When Outputs Look Strange

Use short scripts:

- “This is a probability engine, not a thinker.”
- “It copied a pattern from training style.”
- “High confidence does not guarantee correctness.”
- “Let’s inspect tokens/probabilities before judging.”

## 8) Troubleshooting Tips

- **Install error**: verify Python version and virtual environment.
- **Slow training**: reduce `d_model`, `n_layers`, or `seq_len`.
- **Bad output quality**: check dataset size/cleanliness first.
- **Checkpoint missing**: confirm `--out_dir` and training completion.
- **Streamlit not launching**: install optional learn dependencies.

## 9) Extension Challenges

- Compare top-k vs top-p on same prompt.
- Run 3 temperature values and rate coherence.
- Retrain on second domain and quantify style drift.
- Ask students to predict next token before revealing model top-5.

## 10) Learning Outcomes

By end of lesson, students should be able to:

- Explain tokens and next-token prediction.
- Describe how loss changes through training.
- Explain why retraining changes behavior.
- Identify limits of tiny models.
- Discuss why data quality matters for safety and performance.
