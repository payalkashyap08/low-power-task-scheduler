# Low Power Task Scheduler
This project is an energy-efficient CPU Scheduler is an optimized CPU scheduling algorithm designed to minimize energy consumption without compromising system performance. It is specifically developed for  desktop, mobile and embedded systems, where power efficiency is crucial. 
Energy-Efficient CPU Scheduling in C.
Overview
This project implements a simplified energy-efficient CPU scheduling algorithm in C. It demonstrates how to reduce CPU power consumption by:

Prioritizing tasks based on urgency.

Simulating dynamic CPU frequency scaling (adjusting task execution dynamically).

Entering low-power (idle) states when no tasks are pending.

This project is ideal for college assignments or as a learning exercise for CPU scheduling and power management techniques.

Features
* Priority-Based Task Scheduling – Higher-priority tasks execute first.
* Task Classification – Differentiates urgent and background tasks.
* CPU Idle Simulation – Uses sleep functions to reduce CPU activity when no tasks are available.
* Energy Efficiency Simulation – Minimizes CPU wake-ups to simulate power-saving techniques.

Implementation Details
1. Task Structure
Each task is represented using a Task struct with the following properties:
Task ID – Unique identifier.
Priority – Lower value indicates higher priority.
Execution Time – Duration in seconds.

2. Priority-Based Scheduling
High-priority tasks execute first (sorted in ascending order of priority).
Low-priority tasks are delayed to optimize CPU utilization.

3. CPU Monitoring
Dynamic CPU load detection (simulated using system APIs).

Adaptive execution delay if CPU usage is too high (>75%).

4. Dynamic Frequency Simulation
Uses sleep intervals to simulate power-saving CPU adjustments.

Mimics low-power states when no tasks are available.
