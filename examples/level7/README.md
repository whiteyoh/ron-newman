![Glytch logo](../../assets/glytch-logo.svg)

## Scenario use case

This example maps to its scenario entry in `examples/SCENARIO_USE_CASES.md` (Given / When / Then) so each level has a clear, behavior-based use case.

## How to trigger this example

1. Export your API key and start the app:
   ```bash
   export OPENAI_API_KEY="your_key_here"
   python app.py
   ```
2. Open <http://127.0.0.1:8000>.
3. Click **Level 7**.
4. Review the execution trace shown in the dashboard.

## What this level specifically demonstrates

See the level title/description in the app UI and root `README.md` for the exact behavior focus for this level.


## Level 7 update: constrained agent loop

Level 7 now demonstrates a simple agent runtime that repeatedly:
1. Reads the objective and prior observations.
2. Chooses exactly one JSON action (`research`, `calculate`, `draft`, or `finish`).
3. Executes the selected tool/action.
4. Observes the result and replans the next step.
5. Stops on `finish` or after a fixed maximum number of iterations.

This keeps the implementation educational while showing genuine observe/act/replan behavior without external agent frameworks.
