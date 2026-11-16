# WareMind AI — Multi-Agent Warehouse Robot Coordination

**CM3630 Multi-Agent Systems — starter project**

An educational, locally runnable Python warehouse simulation. Robots act autonomously, bid on new orders through a simplified Contract Net Protocol, navigate a grid, avoid occupied cells, and deliver packages to a depot.

## Setup (Windows PowerShell)

```powershell
cd WareMind-AI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

If activation is blocked, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.\.venv\Scripts\python.exe main.py` instead.

## Controls

- **O** — Add a random order
- **SPACE** — Pause/resume
- **ESC** — Exit

## Tests

```powershell
python -m pytest -q
```

## What's implemented

- Independent robot objects with local battery and task state
- Simplified task auction: call for proposals, bids, assignment
- Grid navigation with BFS shortest paths
- Basic occupied-cell avoidance
- Package pickup/delivery and live Pygame display
- Automated tests for paths, bidding, delivery and collisions

## Planned enhancements (NOT implemented)

- Integrate **Mesa** scheduler/model for formal agent-based simulation
- Replace BFS with A* and add robust multi-step reservation/deadlock handling
- Add **Experta** safety/charging rules
- Add charging behavior, battery depletion/recovery and fault handling
- Add Streamlit analytics and baseline experiments
- Optional CrewAI, Qdrant/RAG explanations (only if helpful)

**Note:** Mesa is listed as a dependency for the next stage, but the current core uses plain Python agent classes; do not claim Mesa integration is complete. This prototype is not a safety-critical robot controller.
