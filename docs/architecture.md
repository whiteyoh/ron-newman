# Kairo Architecture (Beginner-Friendly)

This document explains the major parts of Kairo and how data flows through the system.

## 1) High-Level Flow

```text
Text data -> ByteTokenizer -> SequenceDataset -> TinyGPT ->
Training loop -> Checkpoint -> Generation / Evaluation / Chat / Learn Mode
```

## 2) Core Components

### ByteTokenizer
- Converts raw text into byte-level tokens.
- Keeps vocabulary compact and predictable.
- Works across many character types without custom rules.

### SequenceDataset
- Turns token stream into training windows.
- Produces `(input_tokens, target_tokens)` pairs.
- Supports batching for efficient training.

### TinyGPT
- Small transformer model for educational inspection.
- Learners can reason about layers/heads/embedding size.
- Trained for next-token prediction.

## 3) Training Loop

```text
Load dataset -> Batch tokens -> Forward pass -> Loss -> Backprop -> Optimizer step -> Save checkpoint
```

- Loss tracks prediction error.
- Checkpoints allow later generation/evaluation.
- Tiny settings keep CPU runs feasible.

## 4) Generation Pipeline

```text
Prompt -> Tokenize -> Predict next-token distribution -> Sample token -> Append -> Repeat
```

Sampling controls:
- Temperature
- Top-k
- Top-p

## 5) Evaluation

- Runs model on held-out or reference text.
- Reports loss/perplexity for comparison between runs.
- Useful for measuring retraining effects.

## 6) Learn Mode

- Streamlit interface for guided exploration.
- Displays tokens, charts, and next-token probabilities.
- Helps students connect code behavior with concepts.

## 7) Safety Layer

- Lightweight classroom guardrails.
- Prompt/output filtering hooks.
- Warnings for risky training text and personal-data concerns.

## 8) Explainability Layer

- Token visualization
- Next-token probability viewer
- Run-to-run comparison after retraining

Purpose: make internal behavior observable so learners can explain *why* outputs change.
