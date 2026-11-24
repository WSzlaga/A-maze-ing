*This project has been created as part of the 42 curriculum by jbartos, wszlaga.*

# A-Maze-ing

A configurable maze generator written in Python 3, with an interactive terminal
visualisation and a reusable, pip-installable generator package (`mazegen`).

---

## Table of contents

1. [Description](#description)
2. [Instructions](#instructions)
3. [Configuration file](#configuration-file)
4. [Output file format](#output-file-format)
5. [Maze generation algorithm](#maze-generation-algorithm)
6. [Visual representation and interactions](#visual-representation-and-interactions)
7. [Reusable module: `mazegen`](#reusable-module-mazegen)
8. [Project structure](#project-structure)
9. [Team and project management](#team-and-project-management)
10. [Resources](#resources)

---

## Description

**A-Maze-ing** reads a plain-text configuration file, generates a random maze
(reproducible thanks to an optional seed), computes the shortest path between
the entry and the exit, writes everything to a file using a hexadecimal wall
encoding, and displays the maze in the terminal with colours and animations.

**Goal of the project**

- Generate valid mazes: entry and exit inside the bounds and different,
  closed outer border, coherent walls between neighbouring cells, no isolated
  cells (except the "42" pattern), no open area of 3x3 or larger.
- Support two modes selected by the `PERFECT` flag:
  - `PERFECT=True` - a *perfect* maze (exactly one path between any two cells),
  - `PERFECT=False` - a maze with loops (dead-ends are removed where possible),
    closer to a board usable by a Pac-Man-like game.
- Draw a visible **"42"** made of fully closed cells in the middle of the maze.
- Isolate the generation logic in a standalone class (`MazeGenerator`) packaged
  as `mazegen-1.0.0-py3-none-any.whl` so it can be reused in future projects.

**Overview of the pipeline**

```
 config.txt ──► parser.py ──► MazeConfig
                                 │
                                 ▼
                    mazegen.MazeGenerator
                    ├─ generate()  (iterative DFS + optional dead-end removal)
                    └─ solve()     (BFS shortest path)
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼
        exporter.py                            display.py
   (hex grid + entry + exit + path           (interactive terminal UI:
    written to OUTPUT_FILE)                   regenerate / path / colours)
```

---

## Instructions

### Requirements

- Python **3.10 or newer** (the code uses `X | None` type syntax).
- No runtime dependencies (standard library only).
- Development tools: `flake8` and `mypy`.
- A terminal with 256-colour and Unicode support, at least `3 * WIDTH + 1`
  columns wide (see [Visual representation](#visual-representation-and-interactions)).

### Installation (development tools)

It is recommended to work inside a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
make install        # pip install flake8 mypy
```

### Running

```bash
make run
# or, directly:
python3 a_maze_ing.py config.txt
```

The program takes exactly **one** argument: the path to the configuration file.
Any other number of arguments prints the usage message and exits with code 1.

### Makefile targets

| Target         | What it does                                                        |
|----------------|---------------------------------------------------------------------|
| `make install` | Installs `flake8` and `mypy`.                                       |
| `make run`     | Runs `python3 a_maze_ing.py config.txt`.                            |
| `make debug`   | Runs the program under `pdb`.                                       |
| `make clean`   | Removes `.mypy_cache` and all `__pycache__` directories.            |
| `make lint`    | Runs `flake8 .` and `mypy .` with the flags required by the subject.|

### Building the `mazegen` package from source

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install build
python3 -m build            # creates dist/mazegen-1.0.0-py3-none-any.whl
                            # and dist/mazegen-1.0.0.tar.gz
cp dist/mazegen-1.0.0-py3-none-any.whl .   # copy to the repo root
```

Installing the built package:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Error handling

The program never crashes with a traceback on bad input. Invalid
configuration, missing file, bad syntax, out-of-range values or impossible
parameters produce a one-line message (`Error: ...`) and exit code 1.
`Ctrl+C` and `Ctrl+D` are handled as well.

---

## Configuration file

One `KEY=VALUE` pair per line. Keys are case-insensitive, whitespace around
`=` is ignored, empty lines and lines starting with `#` are ignored.

| Key           | Required | Type / format        | Description                                         | Example            |
|---------------|----------|----------------------|-----------------------------------------------------|--------------------|
| `WIDTH`       | yes      | integer, 1 - 500     | Number of columns (cells).                          | `WIDTH=20`         |
| `HEIGHT`      | yes      | integer, 1 - 500     | Number of rows (cells).                             | `HEIGHT=15`        |
| `ENTRY`       | yes      | `x,y`                | Entry cell, `x` = column, `y` = row, origin top-left.| `ENTRY=0,0`        |
| `EXIT`        | yes      | `x,y`                | Exit cell, must differ from `ENTRY`.                | `EXIT=19,14`       |
| `OUTPUT_FILE` | yes      | path                 | File the maze is written to.                        | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | yes      | `True` / `False`     | Perfect maze (single path) or maze with loops.      | `PERFECT=True`     |
| `SEED`        | no       | integer              | Seed for reproducible generation. Random if absent. | `SEED=123`         |

Validation performed by the parser:

- all mandatory keys must be present,
- `WIDTH` and `HEIGHT` must be positive and not exceed 500,
- `ENTRY` and `EXIT` must be inside the maze and must be different,
- `PERFECT` must be `True` or `False` (case-insensitive),
- `ENTRY` and `EXIT` must not lie inside the "42" pattern (checked by the generator).

Default `config.txt` (provided in the repository):

```ini
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
#SEED = 123
```

---

## Output file format

Each cell is written as **one hexadecimal digit** (uppercase). A bit set to `1`
means the wall is **closed**, `0` means it is **open**.

| Bit | Value | Direction |
|-----|-------|-----------|
| 0 (LSB) | 1 | North |
| 1       | 2 | East  |
| 2       | 4 | South |
| 3       | 8 | West  |

```
        N (1)
         ┌───┐
 W (8)   │ A │   E (2)       A = 1010 = East + West closed
         └───┘               (corridor running North <-> South)
        S (4)
```

File layout:

```
<row 0 - WIDTH hex digits>
<row 1 - WIDTH hex digits>
...
<row HEIGHT-1>
<empty line>
<entry x,y>
<exit x,y>
<shortest path as a string of N, E, S, W>
```

- Rows are stored top to bottom, cells left to right.
- Every line ends with `\n`.
- Neighbouring cells always agree on their shared wall (a closed east wall in
  `(x, y)` is a closed west wall in `(x+1, y)`).
- The outer border is always closed.
- Cells of the "42" pattern are written as `F` (all four walls closed).
- If no path exists, the path line contains `exit unreachable`.

---

## Maze generation algorithm

### Chosen algorithm: iterative randomised Depth-First Search (recursive backtracker)

```
 1. Fill the grid with 15 (all walls closed).
 2. Mark the "42" cells as already visited -> they stay closed (value 15).
 3. Push the start cell on a stack and mark it visited.
 4. While the stack is not empty:
      current = top of the stack
      if current has unvisited neighbours:
           pick one at random (seeded RNG)
           remove the wall between current and the neighbour
           mark the neighbour visited, push it
      else:
           pop the stack  (backtrack)
```

```
 start ──► ──► ──┐            Walls are knocked down along a random
                 ▼            walk; when the walk gets stuck we backtrack
          ┌── ◄── ┘           to the last cell that still has options.
          ▼
```

The result is a **spanning tree** of all non-"42" cells: every cell is
reachable, there are no loops, hence exactly one path between entry and exit
(`PERFECT=True`).

### Non-perfect mode (`PERFECT=False`): dead-end removal

After the DFS, `remove_dead_ends()` scans the grid. For every cell with three
closed walls (values `7`, `11`, `13`, `14`) it tries, in random order, to open
the wall towards a neighbour that is inside the grid and is not a "42" cell.
After each attempt `has_open_3x3()` checks whether a forbidden 3x3 open area
appeared; if so the wall is restored and the next neighbour is tried. This
introduces loops and removes most dead-ends while respecting the "no 3x3
open area" rule.

### Shortest path: Breadth-First Search

`solve(entry, exit)` runs a BFS over open passages, stores each cell's parent
and the direction letter used to reach it, then rebuilds the path from the exit
back to the entry. BFS guarantees the **shortest** path in an unweighted grid.

### Why this algorithm?

- **Simple and robust** - easy to implement, explain and debug.
- **Iterative, not recursive** - an explicit stack avoids Python's recursion
  limit on large mazes (up to 500x500).
- **Long, winding corridors** - DFS produces mazes with a high "river" factor
  and few short branches, which look like classic mazes and make the shortest
  path interesting.
- **Easy to constrain** - pre-marking the "42" cells as visited is enough to
  keep them closed and isolated.
- **Reproducible** - a dedicated `random.Random(seed)` instance is used, so the
  same seed and parameters always give the same maze.
- **Natural base for loops** - starting from a spanning tree, opening a few
  walls is a straightforward way to build the non-perfect mode.

### The "42" pattern

A 7x5 block of fully closed cells is drawn at the centre of the maze:

```
 #...###        # = closed cell (part of "42")
 #.....#        . = normal cell
 ###.###
 ..#.#..
 ..#.###
```

The pattern requires `WIDTH >= 9` and `HEIGHT >= 7`. On smaller mazes it is
omitted and the message `Maze too small for 42 pattern` is printed.

---

## Visual representation and interactions

The maze is rendered in the **terminal** using Unicode box-drawing characters
(heavy lines) and 256-colour ANSI backgrounds.

| Element        | Rendering                                           |
|----------------|-----------------------------------------------------|
| Walls          | bold white box-drawing characters                   |
| Background     | pastel diagonal gradient (4 selectable palettes)    |
| Entry          | green cell labelled `EN`                            |
| Exit           | red cell labelled `EX`                              |
| Shortest path  | continuous neon pink corridor                       |
| "42" pattern   | solid neon block (4 selectable colours)             |

The header shows the maze size and the number of steps of the shortest path.
Each cell uses 3 terminal columns, so the terminal must be at least
`3 * WIDTH + 1` columns wide; otherwise a message explains how wide it needs
to be.

### Interactive menu

```
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show/Hide shortest path (ON)
3. Change pastel background (Pastel Rainbow)
4. Change '42' pattern style (Neon Pink)
5. Quit
Choice? (1-5):
```

| Choice | Action                                                                                         |
|--------|------------------------------------------------------------------------------------------------|
| 1      | Generates a new maze with a new random seed, solves it, re-exports it to `OUTPUT_FILE`.        |
| 2      | Toggles the shortest path; when shown, it is animated step by step from entry to exit.         |
| 3      | Cycles through the pastel palettes with a row-by-row wipe animation.                           |
| 4      | Cycles through the colours of the "42" pattern.                                                |
| 5      | Quits (`Ctrl+C` / `Ctrl+D` also exit cleanly).                                                 |

---

## Reusable module: `mazegen`

The generation logic lives in a single class, `MazeGenerator`
(`mazegen/generator.py`), with no dependency on the display or the parser. It is
shipped as `mazegen-1.0.0-py3-none-any.whl` at the root of the repository.

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic example

```python
from mazegen import MazeGenerator

# 1. Instantiate with the size of the maze (in cells)
maze = MazeGenerator(width=20, height=15)

# 2. Generate it
maze.generate(start=(0, 0), exit_pos=(19, 14), seed=42, perfect=True)

# 3. Get a solution
path = maze.solve((0, 0), (19, 14))
print(path)            # e.g. "ESEEENNES..."

# 4. Access the structure
print(maze.grid[0][0]) # wall bitmask of the top-left cell
```

### Custom parameters

| Parameter         | Where                  | Meaning                                                        |
|-------------------|------------------------|----------------------------------------------------------------|
| `width`, `height` | `MazeGenerator(...)`   | Size of the maze, positive integers.                           |
| `start`           | `generate(...)`        | Cell where the DFS starts, `(x, y)`. Default `(0, 0)`.         |
| `exit_pos`        | `generate(...)`        | Optional, used to validate the exit (in bounds, not in "42").  |
| `seed`            | `generate(...)`        | Integer for reproducible mazes. `None` = random.               |
| `perfect`         | `generate(...)`        | `True` = single path, `False` = remove dead-ends (loops).      |

The same `seed` with the same parameters always produces the same maze.

### Accessing the generated structure

- `maze.grid` - `list[list[int]]`, indexed **`grid[y][x]`** (row first).
  Each value is a 4-bit mask of **closed** walls:

  ```python
  from mazegen.generator import NORTH, EAST, SOUTH, WEST   # 1, 2, 4, 8

  cell = maze.grid[y][x]
  has_east_wall = bool(cell & EAST)
  ```
- `maze.generate(...)` also returns the grid.
- `maze.solve(entry, exit_pos)` - shortest path as a string of `N`, `E`, `S`, `W`
  (or `"exit unreachable"`).
- `maze.width`, `maze.height` - dimensions.
- `maze.remove_wall(a, b)` / `maze.add_wall(a, b)` - edit the shared wall of two
  neighbouring cells, keeping both cells coherent.
- `maze.has_open_3x3()` - `True` if the maze contains a forbidden 3x3 open area.

### What is reusable and how

| Part                          | Reusable? | Notes                                                           |
|-------------------------------|-----------|-----------------------------------------------------------------|
| `mazegen.MazeGenerator`       | **Yes**   | Standalone, standard library only. Packaged as a wheel.         |
| `app/parser.py`               | Partly    | Config parser; easy to adapt to other `KEY=VALUE` formats.      |
| `app/exporter.py`             | Partly    | Writes the subject's hexadecimal format.                        |
| `app/display.py`              | Partly    | Terminal renderer; depends on `MazeGenerator.grid` only.        |

---

## Project structure

```
.
├── a_maze_ing.py                   # main entry point
├── config.txt                      # default configuration
├── Makefile                        # install / run / debug / clean / lint
├── pyproject.toml                  # build configuration of the mazegen package
├── mazegen-1.0.0-py3-none-any.whl  # built reusable package
├── LICENSE.md                      # MIT license
├── README.md
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── parser.py                   # config parsing and validation
│   ├── exporter.py                 # output file writer
│   └── display.py                  # interactive terminal UI
└── mazegen/
    ├── __init__.py                 # exposes MazeGenerator
    └── generator.py                # MazeGenerator class (DFS + BFS)
```

### Licence

The project is released under the **MIT License** (see `LICENSE.md`), which
explicitly allows anyone, including our own future projects, to use, copy,
modify and distribute the maze generator.

---

## Team and project management

### Roles

| Member   | Login     | Responsibilities                                                                 |
|----------|-----------|----------------------------------------------------------------------------------|
| Witkoria Szlaga | `wszlaga` | Terminal visualisation (`display.py`), interactive menu, colours and animation, parsing and exporting, main file, README.md, LICENSE.md
| Jagoda Bartoś | `jbartoś` | Maze generation algorithm (`generator.py`), solver, Makefile, edge cases and error handling

### Planning: anticipated vs. actual

**Initial plan.** We planned to split the work in two from the start: one of us
would build the generation logic and the solver, the other would build the
terminal visualisation, while the parser, the exporter and the packaging would
be done together once the core worked. We expected to finish the mandatory part
first, then use the remaining time for polishing, linting and the README.

| Phase | Anticipated | What actually happened |
|-------|-------------|------------------------|
| Repository and project skeleton | First days, done together | Took longer than expected: we had to learn how to structure the project, split `mazegen` from the application code and set up shared Git work. |
| Config parser and exporter | Short task | Done as planned. Validation of edge cases (bounds, `ENTRY == EXIT`, missing keys) was extended later. |
| Generator (DFS + "42" pattern) | About one week | Basic DFS worked quickly. The "42" pattern and the rule against 3x3 open areas required several fixes. |
| Non-perfect mode | Simple extra step | Harder than expected. Removing dead-ends without creating 3x3 open areas needed extra checks, and it is still not fully guaranteed. |
| Solver (BFS) | Short task | Done as planned. |
| Terminal display and menu | Parallel to the generator | Grew beyond the minimum: colour themes, "42" colours and animations were added after the basic version worked. |
| Packaging (`mazegen`), README, lint | Last days | Started late and compressed into the final days. Building the wheel and fixing `flake8` / `mypy` warnings took more time than planned. |

**How the plan evolved.** The biggest changes were that the skeleton and the
Git workflow took longer than planned, that the non-perfect mode needed more
iterations than the perfect one, and that the packaging and the lint fixes were
pushed to the end. Next time we would set up the package and the linters on the
first day and run them continuously.

### What worked well

- **Clear separation of responsibilities.** The generation logic (`mazegen`) is
  independent from the parser, the exporter and the display, so we could work on
  the generator and on the terminal visualisation in parallel without blocking
  each other.
- **Bitmask representation.** Storing the walls of each cell as a 4-bit value
  kept the logic simple (opening or closing a wall is one bitwise operation)
  and matched the required output format directly.
- **Seed support.** A dedicated seeded random generator made bugs reproducible:
  we could regenerate exactly the same maze when something looked wrong.
- **Iterative DFS.** It handled large mazes (up to 500x500) without hitting
  Python's recursion limit.
- **Packaging the generator.** Building `mazegen` as a separate package forced
  us to keep the generator clean and free of dependencies on the rest of the
  project.
- **Interactive display.** Animations (path drawing, palette wipe) and several
  colour themes made the maze easy to inspect and to debug visually.

### What could be improved

- **Non-perfect mode guarantees.** Dead-end removal is a single pass, so a few
  dead-ends can remain, and we do not explicitly guarantee open corners and
  centre or at least two independent loops. A dedicated "braiding" step would
  fix this.
- **Automated tests.** We tested mostly by hand. Unit tests (pytest) for the
  parser, the generator (wall coherence, no 3x3 open area, connectivity) and
  the solver would have caught bugs earlier.
- **Git workflow.** We could have used feature branches and pull requests
  instead of working directly on the main branch, which would have reduced
  merge conflicts.
- **Earlier planning.** Starting the packaging and the README earlier, instead
  of at the end, would have saved time.
- **More features.** Supporting several generation algorithms (e.g. Prim,
  Kruskal) and animating the generation itself.
- **Code quality.** More consistent docstrings and type hints in the generator
  module, and keeping lines within the flake8 limit from the start.

### Tools used

- **Git / GitHub** - version control and collaboration,
- **Python 3** with `venv` - development environment,
- **flake8** and **mypy** - linting and static typing,
- **build** and **setuptools** - building the `mazegen` package,

---

## Resources

### References

- Maze generation algorithms (overview): <https://en.wikipedia.org/wiki/Maze_generation_algorithm>
- Depth-first search / recursive backtracker: <https://en.wikipedia.org/wiki/Depth-first_search>
- Breadth-first search: <https://en.wikipedia.org/wiki/Breadth-first_search>
- Jamis Buck, *Mazes for Programmers* and his blog series on maze algorithms: <https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap>
- Python documentation - `random`, `dataclasses`, `typing`: <https://docs.python.org/3/>
- Python Packaging User Guide (building wheels): <https://packaging.python.org/>
- PEP 8 / flake8: <https://peps.python.org/pep-0008/>, <https://flake8.pycqa.org/>
- mypy documentation: <https://mypy.readthedocs.io/>
- Box Drawing Unicode block: <https://en.wikipedia.org/wiki/Box-drawing_characters>
- ANSI escape codes (256 colours): <https://en.wikipedia.org/wiki/ANSI_escape_code>

### Use of AI

AI tools were used strictly as a learning and review assistant during the project:
Explaining algorithmic concepts (bitmask wall encoding, iterative DFS vs. recursion, BFS queue and parent backtracking) and Python typing syntax (int | None, tuple[int, int]).
Assisting with debugging edge cases (coordinate ordering (x, y) vs. grid[y][x], infinite loops in BFS, flake8/mypy errors).
Helping structure docstrings and drafting/translating the README.md according to the subject checklist.
All code was reviewed, tested, and verified by the team members to ensure full understanding of every component.