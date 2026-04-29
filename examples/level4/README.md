# Level 4: Retrieval + Grounding

## Scenario this level demonstrates

Grounded Q&A using retrieved local evidence so answers stay tied to source facts.

## Tangible things this example can handle

- Answering service-port questions from local facts (Postgres, Redis, Nginx).
- Refusing unsupported facts when evidence is missing.

## How to trigger this example

1. Start the app:
   
   ```bash
   export OPENAI_API_KEY="your_key_here"
   python app.py
   ```
2. Open <http://127.0.0.1:8000>.
3. Click **Level 4**.
4. Review the trace output shown in the dashboard.

## AI behavior demonstrated

This level runs a live LLM-backed workflow from `app.py` and prints the execution trace in the dashboard.
