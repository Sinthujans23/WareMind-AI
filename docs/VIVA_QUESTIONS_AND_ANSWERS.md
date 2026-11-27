# WareMind AI Viva Questions and Answers

## 1. What is an autonomous agent?
An autonomous agent is a software component that observes the environment and acts independently toward a goal. En Tamil, robot agent-இது battery, position, task state use panni خود decision edukum.

## 2. What is a multi-agent system?
It is a system of multiple interacting agents. Here, three robots negotiate tasks and coordinate in one warehouse.

## 3. What is Mesa?
Mesa is a Python agent-based modelling framework used to schedule agents and maintain the simulation model.

## 4. What is Pygame used for?
Pygame provides the visual grid, robot rendering, controls, and status display.

## 5. What is the Contract Net Protocol?
The manager announces a task, eligible robots submit bids, the manager selects a winner, and sends award/reject messages.

## 6. How is bidding performed?
The safety rules first reject unsafe robots. A* estimates travel for pickup and delivery, and the selected strategy ranks bids.

## 7. What does battery-aware allocation do?
It penalizes low-battery robots and favors safer battery states while preserving the existing bid formula.

## 8. What is A*?
A* is a shortest-path search algorithm using the Manhattan heuristic.

## 9. Why Manhattan distance?
The warehouse is a 4-direction grid, so Manhattan distance is a consistent estimate for movement cost.

## 10. What is Experta?
Experta runs rule-based safety facts and actions for charging, busy robots, charging robots, and battery feasibility.

## 11. What is a deadlock?
A deadlock is a cycle in which robots wait behind each other and cannot progress.

## 12. How is circular waiting detected?
The warehouse maps each stuck robot to the robot occupying its task goal and searches for a cycle.

## 13. How does recovery work?
A cooperative yielding robot moves to a safe adjacent cell without changing its order assignment.

## 14. Does cooperative recovery preserve assignments?
Yes. Recovery changes position and battery only; order ID and carrying state remain unchanged.

## 15. What collision guarantee is tested?
Tests and metrics verify no overlap at tick boundaries. They do not claim stronger movement-level collision verification.

## 16. How is depot congestion prevented?
An idle robot at the depot is moved to a safe parking cell before allocation.

## 17. What are the 180 experiments?
Six scenarios, three strategies, and seeds 0–9 produce 180 runs.

## 18. What is full-run success?
It means every order in one experiment completed within 500 ticks.

## 19. What is order completion rate?
It is the number of delivered orders divided by all created orders.

## 20. How many optimized runs succeeded?
180 out of 180, with 100% order completion.

## 21. What did the baseline contain?
168/180 successful runs and 97.26% order completion.

## 22. What was the mean optimized tick count?
78.51 ticks across all 180 runs.

## 23. What was the mean baseline tick count?
100.46 ticks across all 180 runs.

## 24. Are these 180 results proof of universal performance?
No. They cover only fixed scenarios and seeds.

## 25. What is the battery reserve?
The required-battery estimate retains a 15-point reserve after estimating actual movement cost.

## 26. What battery cost is used per movement?
`BATTERY_PER_MOVE` is 0.5 battery points.

## 27. Why was the heuristic corrected?
It previously combined grid steps with battery points, potentially rejecting feasible far-away tasks.

## 28. What is a dynamic obstacle?
An obstacle that can be inserted or removed during simulation.

## 29. Is battery-aware always fastest?
No. The three strategies tie or vary depending on scenario.

## 30. Which strategy is best for reliability?
All three achieved 180/180 in the optimized run.

## 31. What is estimated energy?
It is movement distance multiplied by `BATTERY_PER_MOVE`, not physical battery telemetry.

## 32. What is observed distance?
It is the sum of Manhattan grid steps moved in each recorded experiment.

## 33. How many tests pass?
60 tests pass in the current project.

## 34. What test frameworks are used?
Pytest, CSV validation, and deterministic seeded simulations.

## 35. What is the replay result for high workload seed 4?
15/15 orders completed in 123 ticks with zero recoveries.

## 36. What is the replay result for combined stress seed 4?
15/15 orders completed in 151 ticks with zero recoveries.

## 37. What is randomized allocation?
It selects among eligible robots without geometric preference.

## 38. What is nearest allocation?
It selects the eligible robot with the lowest bid distance score.

## 39. What is a limitation of the simulator?
It is a 16×12 educational grid, not a physical warehouse.

## 40. What is the Pygame GUI limitation?
Graphical verification depends on display support on the demonstration machine.
