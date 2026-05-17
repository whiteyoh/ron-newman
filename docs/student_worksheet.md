# Kairo Student Worksheet

## Big Idea

LLMs predict what text token is likely to come next. They do not “understand” like humans.

## Activity 1: Token Hunt

1. Write a short prompt: `The moon base was`
2. Break it into small pieces (tokens) as shown by the tool.
3. Record 3 tokens you did not expect.

**Questions**
- Why might splitting text this way help a model?
- Which token surprised you most?

## Activity 2: Guess the Next Token

Prompt: `The robot opened the`

1. Predict three possible next tokens.
2. Check model probabilities.
3. Compare your guesses to top results.

| Your guess | In top predictions? | Estimated probability |
|---|---|---|
|   |   |   |
|   |   |   |
|   |   |   |

## Activity 3: Before/After Retrain Comparison

1. Train on space text.
2. Generate output for a fixed prompt.
3. Retrain on pirate text.
4. Generate again with same prompt.

**Observe**
- Vocabulary changes
- Tone changes
- Repetition differences

## Activity 4: Probability Prediction

Before revealing model results, predict:

- Which next token is most likely?
- Which token is possible but unlikely?
- How does temperature change the result?

## Activity 5: Reflection Prompts

- What did the model do well?
- What looked wrong or weird?
- How did retraining affect output?
- Why can confident output still be incorrect?
- What rule should we follow when using AI-generated text?

## Glossary

- **Token**: a piece of text the model processes.
- **Loss**: a score of prediction error during training.
- **Probability**: how likely the model thinks a token is next.
- **Retraining**: continuing training on new text.
- **Dataset**: the text collection used to train the model.
