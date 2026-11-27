# WareMind AI — Multi-Agent Warehouse Robot Coordination

**CM3630 — Multi-Agent Systems Project**

WareMind AI is a Python-based multi-agent warehouse simulation in which autonomous robots coordinate to collect and deliver orders.

The system demonstrates agent communication, decentralized task bidding, intelligent pathfinding, collision avoidance, battery management, and performance evaluation.

## 1. Project Overview

WareMind AI simulates three autonomous warehouse robots operating in a shared grid environment.

Each robot can participate in task allocation, navigate around obstacles, pick up assigned orders, and deliver them to a central depot.

The simulation uses a simplified Contract Net Protocol (CNP) for task allocation and A* pathfinding for navigation.

## 2. Key Features

- Multi-agent warehouse simulation using Python and Mesa
- Three autonomous robots with independent task and battery states
- Simplified Contract Net Protocol for task negotiation
- A* pathfinding and obstacle avoidance
- Dynamic obstacle management
- Collision avoidance and robot coordination
- Battery monitoring and charging behavior
- Stuck robot detection and basic deadlock recovery
- Automatic depot clearing
- Interactive Pygame simulation dashboard
- Performance monitoring and CSV export
- Multi-scenario workload evaluation
- Automated testing using pytest

## 3. Technologies

| Technology | Purpose |
|---|---|
| Python | Core simulation and agent logic |
| Mesa | Agent-based simulation framework |
| Pygame | Interactive warehouse visualization |
| A* Algorithm | Robot pathfinding |
| Contract Net Protocol | Multi-agent task allocation |
| Matplotlib | Performance graphs |
| CSV | Experimental result storage |
| pytest | Automated testing |

## 4. System Architecture

The simulation contains the following components:

**Warehouse Environment:** Maintains the grid, shelves, depot, charging station, robots, and orders.

**Robot Agents:** Maintain individual positions, batteries, assigned tasks, and delivery states.

**Negotiation System:** Uses a simplified Contract Net Protocol to distribute available orders among eligible robots.

**Navigation System:** Uses A* pathfinding to calculate routes while considering obstacles and occupied cells.

**Coordination System:** Handles occupied-cell avoidance, blocked robot detection, recovery, and depot clearing.

**Visualization:** Displays the warehouse and robot states through Pygame.

**Evaluation:** Records simulation metrics and compares workloads.

## 5. Installation

### Requirements

- Python 3.13 or a compatible Python 3 version
- Windows PowerShell or another supported terminal

### Setup

```powershell
git clone https://github.com/Sinthujans23/WareMind-AI.git
cd WareMind-AI
git switch feature/multi-robot-coordination

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python -m pip install matplotlib
```

### Run Simulation

```powershell
python main.py
```

## 6. Simulation Controls

| Key | Action |
|---|---|
| O | Add a random order |
| B | Add a dynamic obstacle |
| R | Remove a dynamic obstacle |
| SPACE | Pause or resume |
| ESC | Exit |

## 7. Task Allocation Workflow

1. A new warehouse order is created.
2. The negotiation system announces the task to eligible robots.
3. Robots calculate and submit bids.
4. The winning robot receives the order.
5. The robot uses A* navigation to reach the pickup location.
6. The robot collects the package.
7. The robot navigates to the depot.
8. The order is marked as completed.
9. An idle robot at the depot can move aside to allow further deliveries.

## 8. Performance Evaluation

Run the performance evaluation:

```powershell
python -m scripts.evaluate_performance
```

Generate performance graphs:

```powershell
python -m scripts.plot_performance
```

Compare different workloads:

```powershell
python -m scripts.compare_scenarios
```

Generate scenario comparison graphs:

```powershell
python -m scripts.plot_scenarios
```

Results are saved in the `results/` directory.

## 9. Experimental Results

The following results were obtained from three workload scenarios using three warehouse robots.

| Orders | Completed | Completion Rate | Simulation Ticks | Messages |
|---|---|---|---|---|
| 3 | 3 | 100% | 30 | 24 |
| 5 | 5 | 100% | 50 | 138 |
| 10 | 10 | 100% | 116 | 945 |

All orders were completed in these evaluation runs.

Communication overhead increased significantly as the workload increased, indicating an opportunity to improve negotiation efficiency.

These results represent the tested scenarios and do not establish performance for all warehouse configurations.

## 10. Performance Graphs

The `results/graphs/` directory contains:

- `order_completion.png`
- `completion_rate.png`
- `average_battery.png`
- `communication_overhead.png`
- `scenario_ticks.png`
- `scenario_messages.png`
- `scenario_completion.png`
- `scenario_average_completion.png`

## 11. Automated Testing

Run all automated tests:

```powershell
python -m pytest -q
```

Latest verified result:

**60 tests passed.**

Tests cover core warehouse operations, navigation, negotiation, robot coordination, battery charging, and recovery behavior.

## 12. Limitations

- The warehouse uses a simplified grid environment rather than physical robots.
- The negotiation system implements a simplified Contract Net Protocol.
- Navigation and collision avoidance operate within a discrete simulation.
- Communication overhead increases with larger workloads.
- Experimental results are based on selected scenarios.
- The system is intended for education and research, not safety-critical industrial deployment.

## 13. Future Improvements

- Improve communication efficiency during task allocation
- Add more extensive randomized workload experiments
- Introduce additional robot failure scenarios
- Compare task allocation strategies
- Evaluate performance with larger robot populations

## 14. Project Repository

GitHub: https://github.com/Sinthujans23/WareMind-AI

**Project:** WareMind AI

**Module:** CM3630 — Multi-Agent Systems