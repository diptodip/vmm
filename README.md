# Virtual Machine Migration

**Note:** This project is over and incomplete.

## Introduction

Virtual machines are a key component of the workflow at large scale data centers around the world. For the purposes of load balancing, virtual machines are often migrated to different physical machines within a cluster. However, the movement of virtual machines can introduce more network traffic into a system. It is prudent to minimize the amount of network traffic in a given cluster in order to efficiently scale to larger problems involving big data. Motivated by this practial problem, we propose the use of linear programming and approximation heuristics in order to determine an optimal assignment of virtual machines to physical machines such that the network traffic demand is minimized while staying within the limits of the capacity of each physical machine (not assigning more work/virtual machines to a physical machine than that physical machine can handle). We propose formulating this optimization problem as an integer linear program and solving large problems using ``CPLEX`` in order to gain an intution of the behavior of the linear program (``LP``) at large scales. We will use this intution in order to determine heuristics that improve the rounding scheme for an integral ``LP`` formulation of this problem that can scale to larger problem instances than the current best.

## Structure

This repository is organized into folders by purpose. Currently there is only the ``pysrc`` folder and ``src`` folder, which contain simple proof of concept Python/Numpy scripts and a C++ problem file reader.
