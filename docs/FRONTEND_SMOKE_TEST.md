# Frontend smoke test (workshop-safe simulation)

1. Run `python app.py`.
2. Open `http://127.0.0.1:8080`.
3. Confirm hero section loads and Start button is visible.
4. Click **Start the demo**.
5. Select a scenario card.
6. Add optional context text.
7. Click **Confirm this direction**.
8. Run **Level 1**.
9. Confirm score panel, theatre, and transcript render.
10. Click **Replay this run** and confirm theatre highlight steps animate.
11. Run **Level 8**.
12. Confirm taskboard columns and approval/merge summary render.
13. Use quiz Yes/No segmented buttons.
14. Confirm assessment result updates immediately.
15. Switch browser to mobile width (~390px) and verify no horizontal scroll.
16. Open `?debug=1` and verify preview layout tools appear.
17. Startup failure check: temporarily break one startup API route and verify startup failure message is shown.
18. Run failure check: submit an invalid level payload and verify plain-English run failure message is shown (no real external action).
