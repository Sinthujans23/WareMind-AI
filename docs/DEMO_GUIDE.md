# WareMind AI Demo Guide

## Recommended 5–10 Minute Sequence

1. Open the project in PowerShell.
2. Run `.\.venv\Scripts\python.exe main.py`.
3. Start the normal simulation and point out three robots, shelves, depot, charger, and dynamic obstacles.
4. Show robot IDs, battery levels, assigned orders, carrying state, charging state, and event messages.
5. Add an order with `O` and explain CFP bids, award, pickup, and depot delivery.
6. Add a dynamic obstacle with `B` and show A* rerouting.
7. Run `python -m scripts.diagnose_failures` to demonstrate the two seed-4 regression scenarios.
8. Run `python -m scripts.compare_optimization` to show the verified before/after totals.

## Controls

- `O`: Add random order
- `B`: Add dynamic obstacle
- `R`: Remove dynamic obstacle
- `SPACE`: Pause/resume
- `ESC`: Exit
