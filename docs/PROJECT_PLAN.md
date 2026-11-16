# Project Plan — CM3630

## Problem
Coordinate autonomous robots to fulfill warehouse pickup/delivery requests under constraints such as distance, battery, and shared pathways.

## Agents and environment
- Robot agents: local state, task bidding, navigation, delivery
- Warehouse environment: 2D grid, shelves, depot, pending orders
- Coordination: simplified Contract Net Protocol, lowest bid wins

## Research and framework selection
Compare Mesa (Python agent-based modeling), NetLogo (modeling environment), and JADE (Java agent framework). Choose Mesa for planned formal MAS integration; document selection using official documentation and course criteria.

## Milestones
1. Starter simulation (included)
2. Mesa Model/Agent migration and proper step scheduling
3. A* routing, conflict resolution, deadlock tests
4. Experta safety/charging rules
5. Optional dashboard, LLM explanations, RAG
6. Experiments: random vs nearest-first vs battery-aware auction
7. Report: architecture, agent communication, results, limitations

## Suggested evaluation metrics
Order completion rate, mean fulfillment time, travel distance, energy consumed, collision/deadlock count, fairness of work allocation. Use controlled seeds and repeated runs.

## Academic integrity
Do not report unimplemented features as complete or claim results without running experiments. Cite any libraries and external sources used.
