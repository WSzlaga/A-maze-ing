This project has been created as part of the curriculum 42 by _<jbartos> <wszlaga>_


# A-Maze-ing

## Description

**A-Maze-ing** is a Python maze generator, solver, and interactive terminal visualizer developed as part of the 42 Common Core. The program reads parameters from a configuration file, generates a random (and seed-reproducible) 2D maze containing a centered `"42"` pattern, computes the shortest path from entry to exit, exports the result in hexadecimal wall-bitmask format, and displays the maze in an interactive ASCII terminal interface.

The project supports two generation modes:
- **Perfect maze (`PERFECT=True`)**: a spanning-tree maze with exactly one unique path between any two reachable cells and no loops.
- **Pac-Man playable board (`PERFECT=False`, default)**: a braided maze with multiple independent routes (loops), open corners and center, no dead-ends, and no `3x3` open areas.

The core generation and solving logic is packaged as a standalone, reusable Python module (`mazegen`).

---

## Instructions

### Requirements
- Python **3.10+**
- `flake8`, `mypy`, and `build` (for linting and building the reusable package)

### Installation & Execution

1. Install development dependencies (or use the `Makefile`):
   make install
   or manually:
   pip install flake8 mypy build
   Run the application with the default configuration file:
   python3 a_maze_ing.py config.txt
   or via Makefile:
   make run

   Makefile Rules:
make install — install project dependencies.

make run — run a_maze_ing.py with config.txt.

make debug — run the program using Python's built-in debugger (pdb).

make lint — run flake8 and mypy with mandatory flags.

make clean — remove cache and temporary build files (__pycache__, .mypy_cache, etc.).

Interactive Menu:
While running, the terminal interface provides the following options:

1. Re-generate a new maze (updates the display and re-exports the output file)

2. Show/Hide shortest path (with step-by-step path animation)

3. Change pastel background (4 ANSI 256-color gradient palettes with animated wipe transition)

4. Change "42" pattern style (4 neon styles)

5. Quit

Building & Installing the mazegen Package
To rebuild the reusable package from source inside a virtual environment:

python3 -m build
pip install dist/mazegen-1.0.0-py3-none-any.whl

5

The configuration file is a plain text file containing one KEY=VALUE pair per line. Empty lines and lines starting with # are ignored.

WIDTH (required): Maze width, positive integer (e.g. WIDTH=20).

HEIGHT (required): Maze height, positive integer (e.g. HEIGHT=20).

ENTRY (required): Entry coordinates x,y inside maze bounds (e.g. ENTRY=0,0).

EXIT (required): Exit coordinates x,y inside maze bounds, different from ENTRY (e.g. EXIT=6,10).

OUTPUT_FILE (required): Path to the exported hex maze file (e.g. OUTPUT_FILE=maze.txt).

PERFECT (required): True for a perfect maze, False for Pac-Man mode (e.g. PERFECT=False).

SEED (optional): Integer seed for deterministic generation (e.g. SEED=123).

Example config.txt:

WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=6,10
OUTPUT_FILE=maze.txt
PERFECT=False
#SEED=123


Maze Generation Algorithm

Chosen Algorithms

Wall Representation (Bitmasks): Each cell stores a 4-bit integer (0–15) where 1 means a closed wall and 0 means an open passage:

NORTH = 1 (0001)

EAST = 2 (0010)

SOUTH = 4 (0100)

WEST = 8 (1000)

Fully closed cell = 15 (1111), used initially for all cells and permanently for the "42" pattern.

Iterative DFS (Recursive Backtracker): Starting from ENTRY, the generator uses an explicit stack (list) to carve corridors by knocking down shared walls between unvisited neighbors while respecting the reserved "42" cells.

Dead-End Removal (PERFECT=False): After DFS creates a fully connected spanning tree, the generator scans for dead-ends (cells with 3 closed walls: bitmask values 7, 11, 13, 14) and removes a random closed wall toward a valid non-"42" neighbor. Before keeping the change, has_open_3x3() checks that no 3x3 open area was created; if it was, the wall is restored and another candidate is tried.

Shortest Path Solver (BFS): Breadth-First Search using a queue and a parent dictionary guarantees the shortest valid path from ENTRY to EXIT, returned as a string of cardinal directions (N, E, S, W).

Why We Chose This Algorithm

Simplicity and readability: Iterative DFS with an explicit stack is easy to reason about, debug, and explain without risking Python's recursion depth limit on large grids.

Guaranteed properties: DFS naturally guarantees 100% connectivity and produces a valid perfect maze when PERFECT=True.

Clean extension to Pac-Man mode: Removing dead-ends on top of a perfect maze while checking the 3x3 constraint reliably creates braided boards with multiple routes and zero dead-ends (passing maze_analyzer.py --max-dead-ends 0).

Optimal pathfinding: BFS is guaranteed to find the shortest path in an unweighted grid.

Reusable Module (mazegen)

The mazegen package provides the standalone MazeGenerator class, which can be installed via pip (mazegen-1.0.0-py3-none-any.whl or .tar.gz) and imported into other Python projects.

Basic Usage Example

from mazegen import MazeGenerator

# 1. Instantiate the generator with custom dimensions
gen = MazeGenerator(width=20, height=15)

# 2. Generate a maze with custom parameters (start, exit, seed, mode)
grid = gen.generate(
    start=(0, 0),
    exit_pos=(19, 14),
    seed=42,
    perfect=False,
)

# 3. Access the generated structure (2D list indexed as grid[y][x])
# Each value is an integer 0..15 representing closed N/E/S/W wall bits
print(f"Top-left cell bitmask: {grid[0][0]:X}")

# 4. Access the shortest solution path as a 'NESW' string
path = gen.solve(entry=(0, 0), exit_pos=(19, 14))
print("Shortest path:", path)


Team and Project Management

Roles

jbartos: Core maze generation and solving engine (mazegen/generator.py, mazegen/__init__.py), bitmask wall logic, iterative DFS, "42" pattern reservation, dead-end removal with 3x3 validation, BFS shortest-path solver, parameter validation, and packaging setup (pyproject.toml).

wszlaga: Application entry point (a_maze_ing.py), configuration file parser and validator (app/parser.py), hex output exporter (app/exporter.py), and interactive terminal ASCII renderer with themes and animations (app/display.py).

Planning & Evolution

Initial plan: Define a shared interface (MazeGenerator returning grid[y][x] bitmasks and solve() returning a NESW string) so both team members could work in parallel on the algorithm and the UI/config layers.

Mid-project adjustments: After integrating app/ with mazegen/, we added stricter edge-case validation (preventing ENTRY or EXIT inside the "42" pattern, resetting grid on regeneration) and refined the ASCII renderer with Box Drawing Heavy characters, pastel themes, and animations.

Finalization: Verified both PERFECT=True and PERFECT=False outputs with maze_analyzer.py, ensured flake8 and mypy compliance, packaged mazegen, and finalized documentation.

What Worked Well & What Could Be Improved

Worked well: Splitting the codebase cleanly into mazegen/ (reusable library) and app/ (CLI, parser, exporter, display) allowed independent development and smooth integration. Using maze_analyzer.py early helped catch edge cases quickly.

Could be improved: Agreeing on all function signatures and type annotations (mypy strictness) earlier in the project would have reduced small integration adjustments at the end.

Tools Used

Python 3.10+ & standard library (random, dataclasses, shutil, time, sys)

flake8 & mypy for style and static type checking

setuptools & build for building the mazegen wheel/sdist package

maze_analyzer.py (provided verification script)

Git, Makefile, and VS Code

Resources

References

Python Official Documentation

PEP 257 — Docstring Conventions

PEP 8 — Style Guide for Python Code

Packaging Python Projects (pyproject.toml)

Maze Generation Algorithms (Wikipedia)

Breadth-First Search (Wikipedia)

Use of AI

AI tools were used strictly as a learning and review assistant during the project:

Explaining algorithmic concepts (bitmask wall encoding, iterative DFS vs. recursion, BFS queue and parent backtracking) and Python typing syntax (int | None, tuple[int, int]).

Assisting with debugging edge cases (coordinate ordering (x, y) vs. grid[y][x], infinite loops in BFS, flake8/mypy errors).

Helping structure docstrings and drafting/translating the README.md according to the subject checklist.

All code was reviewed, tested, and verified by the team members to ensure full understanding of every component.