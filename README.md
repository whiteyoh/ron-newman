# Kairo

**Build it. Train it. Talk to it. Understand it.**

Helping people understand AI beyond the chat box.

Kairo is an educational, beginner-friendly language model lab and workshop-safe demo environment that helps learners understand how LLMs actually work by building and exploring a small byte-level GPT from end to end. Instead of treating AI like a mystery black box, Kairo makes core ideas visible: tokens, next-token probabilities, training loss, sampling behavior, and what changes when you retrain on new data.

---

## A. What Kairo Is

Kairo is a practical learning environment for AI education.

- **Educational byte-level GPT lab**: learners can inspect and run each step.
- **Tiny transformer model**: intentionally small enough to understand, debug, and rerun.
- **Next-token prediction in practice**: train, generate, and inspect probabilities.
- **Built for learning contexts**: suitable for classrooms, workshops, and self-study.

---

## B. What Kairo Is NOT

Kairo is intentionally limited, and this is a feature for learning.

- Not production-ready.
- Not instruction-tuned.
- Not a chatbot replacement.
- Not fully moderated.
- Not a large-scale foundation model.
- Outputs depend entirely on training data quality and scope.

---

## C. Why Kairo Exists

Many people use AI tools daily but never see how language models make decisions. Kairo exists to make the mechanics visible and discussable.

With Kairo, learners can observe:

- Tokens and token boundaries
- Next-token probabilities
- Training loss trends
- Retraining effects
- Sampling behavior (temperature, top-k, top-p)

The goal is **demystification, not hype**.

---

## D. Core Learning Journey

1. **Build it**  
   Learners run the project and inspect model/data components.  
   *Observe:* how text becomes tokens and batches.  
   *Why it matters:* understanding starts with structure.

2. **Train it**  
   Learners train a small model on a controlled dataset.  
   *Observe:* loss decreases, checkpoints are created.  
   *Why it matters:* models learn statistical patterns, not facts.

3. **Talk to it**  
   Learners prompt the trained model to generate text.  
   *Observe:* style mimicry, repetition, errors, and surprises.  
   *Why it matters:* output quality reflects data and sampling choices.

4. **Retrain it**  
   Learners continue training on new domain text.  
   *Observe:* outputs shift toward new style and vocabulary.  
   *Why it matters:* behavior is malleable and data-dependent.

5. **Understand it**  
   Learners compare runs, inspect probabilities, and explain outcomes.  
   *Observe:* why confidence can still be wrong.  
   *Why it matters:* builds critical AI literacy and responsible use.

---

## E. Features

- Byte-level tokenizer
- Tiny GPT model
- Training with checkpoints
- Text generation
- Evaluation/perplexity
- Chat mode
- Learn Mode UI (Streamlit)
- Token visualization
- Next-token probability viewer
- Retrain comparison flow
- Classroom safety mode
- CPU-friendly operation
- Tests + CI support

---

## F. Installation

### Supported Python

- Python **3.10+** recommended

### Install

```bash
git clone https://github.com/whiteyoh/my-llm.git
cd my-llm
pip install -e .
```

### Optional Learn Mode dependencies

```bash
pip install -e ".[learn]"
```

---

## G. Quick Start

### 1) Train

```bash
python src/train.py --input_file data/samples/space_adventure.txt --out_dir runs/demo --epochs 1 --batch_size 4 --seq_len 32 --d_model 64 --n_heads 4 --n_layers 2 --device cpu
```

### 2) Generate

```bash
python src/generate.py --checkpoint runs/demo/best.pt --prompt "The robot opened the door" --max_new_tokens 20 --device cpu
```

### 3) Evaluate

```bash
python src/evaluate.py --checkpoint runs/demo/best.pt --input_file data/samples/space_adventure.txt --device cpu
```

### 4) Chat

```bash
python src/chat.py --checkpoint runs/demo/best.pt --device cpu
```

---

## H. Learn Mode

Learn Mode is a Streamlit-based educational UI designed for guided teaching and independent exploration.

It includes:

- Guided workflow from training to analysis
- Token viewer
- Loss charts
- Next-token prediction viewer
- Retraining comparison

Run Learn Mode:

```bash
streamlit run src/kairo_learn.py
```

Screenshot placeholders:

- _Screenshot idea: Learn Mode home_
- _Screenshot idea: token viewer_
- _Screenshot idea: loss chart_
- _Screenshot idea: retrain comparison_

---

## I. Classroom Safety

Kairo includes lightweight classroom guardrails, but teacher oversight is still required.

- Safe mode defaults for classroom sessions
- Prompt filtering support
- Output filtering support
- Training text warnings
- Personal-data warnings

Important limits:

- Not full moderation
- Not safeguarding-complete
- Not suitable for unsupervised public deployment

---

## J. Educational Concepts

- **Token**: a chunk of text (in Kairo, byte-level pieces) the model processes.
- **Next-token prediction**: the model guesses what comes next based on previous tokens.
- **Loss**: a training error score; lower usually means better prediction on seen-style data.
- **Perplexity**: an easier-to-compare form of prediction uncertainty; lower is usually better.
- **Top-k sampling**: choose next token from the k most likely options.
- **Top-p sampling**: choose from the smallest set whose total probability reaches p.
- **Retraining effects**: additional training shifts style, vocabulary, and likely continuations.

---

## K. Suggested Classroom Usage

Kairo can support:

- Secondary school computing classes (ages ~13–18)
- STEM clubs (ages ~11–18, teacher-guided)
- AI workshops (mixed beginner groups)
- University intro labs (first-year CS / data science)
- Teacher-led demonstrations and discussions

---

## L. Example Experiments

1. Train on space-themed text and generate 5 sample outputs.
2. Retrain on pirate-themed text and compare tone shift.
3. Keep prompt fixed, vary temperature, and observe creativity vs coherence.
4. Inspect next-token probabilities before and after retraining.
5. Compare small dataset vs larger dataset outputs and loss/perplexity trends.

---

## M. Roadmap

- Attention visualization for classroom explanation
- Save/load Learn Mode sessions
- Teacher lesson packs
- Printable worksheets
- Richer token inspection tools
- Better retraining comparison reports
- Optional lightweight web deployment for local workshops

---

## N. Contributing

Beginner contributions are welcome, especially for docs, lesson activities, tests, and UI clarity.

Recommended checks:

```bash
ruff check .
python -m compileall src tests
pytest -q
```

Smoke checks:

```bash
python src/train.py --input_file data/samples/space_adventure.txt --out_dir runs/demo --epochs 1 --batch_size 4 --seq_len 32 --d_model 64 --n_heads 4 --n_layers 2 --device cpu
python src/generate.py --checkpoint runs/demo/best.pt --prompt "The robot opened the door" --max_new_tokens 20 --device cpu
python src/evaluate.py --checkpoint runs/demo/best.pt --input_file data/samples/space_adventure.txt --device cpu
```

---

## O. License

This project is licensed under the terms provided in the repository license file.


For workflow detail and output interpretation, see project docs and workshop materials.
