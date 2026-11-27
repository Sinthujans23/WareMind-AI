# WareMind AI — Intelligent Multi-Agent Warehouse Management System

**Module:** CM3630 — Multi-Agent Systems

**Note:** Student name, registration number, university name, and submission date are placeholders to be completed by the student.

## 1. Abstract

WareMind AI is a Python and Mesa warehouse simulation containing three autonomous robots that negotiate tasks, navigate obstacles, manage batteries, and deliver orders to a depot. The project compares random, nearest, and battery-aware allocation using reproducible scenarios and seeds.

## 2. Problem Statement

Multiple robots share a limited grid, depot, charger, and order locations. The system must prevent conflicts, assign feasible tasks, recharge safely, and recover from blocked states without losing task assignments.

## 3. Objectives

- Demonstrate autonomous agent behaviour and Contract Net Protocol communication.
- Implement A* navigation and dynamic obstacle avoidance.
- Apply battery-aware bidding and Experta safety reasoning.
- Detect and recover from circular waits.
- Evaluate performance over reproducible scenarios.

## 4. System Architecture

Pygame provides the interface. Mesa schedules a warehouse model. The warehouse coordinates robot agents, orders, messages, and obstacles. The negotiation module broadcasts CFP messages and awards tasks. A* calculates routes. Experta evaluates charging and battery safety. CSV and Matplotlib scripts collect and visualize performance.

## 5. Experimental Methodology

The evaluation uses six scenarios: normal, low battery, mixed battery, high workload, obstacles, and combined stress. It uses random, nearest, and battery-aware strategies with seeds 0–9: 6 × 3 × 10 = 180 experiments. The tick limit is 500.

## 6. Optimized Evaluation

The historical baseline preserved in `advanced_comparison_baseline.csv` contains 168/180 successful runs and 97.26% order completion. The optimized run contains 180/180 successes and 100% order completion.

Mean ticks fell from 100.46 in the baseline to 78.51 in the optimized run. Seed-4 regressions complete 15/15 in 123 ticks for high workload and 151 ticks for combined stress.

## 7. Strategy Discussion

Nearest and battery-aware allocation were equal or competitive in most scenarios. Random allocation was slower in high-workload and combined-stress runs. No universal superiority is claimed: performance depends on workload, batteries, obstacles, and seed.

## 8. Testing

The final suite contains 60 passing tests. Coverage includes negotiation, battery awareness, charging, navigation, obstacles, depot clearing, circular waits, task assignment preservation, and overlap prevention.

## 9. Limitations

- The warehouse is a small educational simulation.
- Movement and energy metrics are tick-level estimates.
- Tests verify no overlap at observed tick boundaries, not stronger continuous collision guarantees.
- Experta and the battery model are simplified.
- Task allocation uses a centralized warehouse manager.
- The experiment set contains limited scenarios and seeds.
- GUI verification requires a display-enabled demonstration machine.

## 10. Conclusion

The project demonstrates a complete multi-agent simulation from negotiation through task execution and recovery. Verified regression and experiment results support the current implementation, while the documented limitations keep conclusions appropriately scoped.
