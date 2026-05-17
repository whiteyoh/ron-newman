# How LLMs Work (Using Kairo)

## What Is a Token?

A token is a small unit of text. Kairo uses byte-level tokenization, so text is split into manageable pieces a model can process.

## What Does Prediction Mean?

At each step, the model predicts the **next token** based on previous tokens. It does this repeatedly to generate full text.

## How Training Works

During training, Kairo shows many token sequences. The model predicts next tokens, compares guesses to the real next token, and adjusts weights to improve.

## Why Loss Matters

Loss is the model’s error score. Lower loss usually means better predictions on similar text patterns.

## Why Models Hallucinate

Models generate likely-looking text, not guaranteed truth. If training data is incomplete or misleading, outputs can sound confident but be wrong.

## Why Tiny Models Fail More Often

Tiny models have limited capacity:
- fewer patterns remembered
- weaker long-context handling
- more repetition and odd jumps

These failures are useful in class because they make limits visible.

## Why Larger Models Feel Smarter

Larger models usually learn more patterns from more data and can track context better. They still predict probabilities, but with richer learned structure.

## Why Training Data Matters

Training data strongly shapes tone, facts, and style. Bad data causes bad behavior. Narrow data causes narrow outputs.

## What Retraining Changes

Retraining shifts the model toward new patterns. If you retrain a space-text model on pirate text, vocabulary and style will move in that direction.

That is the key lesson: model behavior is learned from data, not fixed intelligence.
