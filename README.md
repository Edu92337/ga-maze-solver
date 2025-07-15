# ga-maze-solver

## Description

`ga-maze-solver` is a genetic algorithm (GA) implementation designed to solve procedurally generated mazes. The algorithm evolves a population of paths to find the most efficient route from the start point to the maze's endpoint, avoiding obstacles.

The project uses Python and Pygame for real-time graphical visualization of the evolving solutions.

---

## Features

- Procedural maze generation using cellular automata with obstacles.
- Visual representation of the maze and candidate solutions using Pygame.
- Genetic Algorithm with:
  - Random initial population.
  - Fitness evaluation based on distance to the goal and path length.
  - Tournament selection with weighted probability.
  - Crossover between chromosomes.
  - Mutation including the possibility of directed (heuristic-guided) mutation.
- Display of the best paths each generation.
- Victory detection when a solution reaches the goal.

---

## Project Structure

- `maze_solver_genetic_algorithm.py`: main source code implementing the GA and maze.
- Dependencies:
  - Python 3.x
  - Pygame


