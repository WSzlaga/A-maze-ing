"""Maze generator and solver (reusable module)"""

import random
from collections import deque

"""współrzędne ENTRY i EXIT w config.txt są w formacie (x, y)
(kolumna, wiersz), ale
w tablicy 2D w Pythonie indeksuje się zazwyczaj grid[y][x]
"""
Coord = tuple[int, int]  # (x, y)

NORTH = 1  # 0001
EAST = 2   # 0010
SOUTH = 4  # 0100
WEST = 8   # 1000


class MazeGenerator:
    """Generate a maze, store it as wall bitmasks, and solve it.
    The grid is a list of rows: grid[y][x]. Each cell is a number 0-15.
    A bit set to 1 means a closed wall (N=1, E=2, S=4, W=8).
    """

    def __init__(self, width: int, height: int) -> None:
        """Create a maze where all walls are closed.

        Args:
        width: Number of columns (must be positive).
        height: Number of rows (must be positive).

        Raises:
        ValueError: If wodth or height is not positive.
        """
        self.width = width
        self.height = height
        # siatka[height][width] wypełniona 15(wszystkie ściany zamknięte)
        self.grid = []
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        for y in range(height):
            row = []
            for x in range(width):
                row.append(15)
            self.grid.append(row)

    def remove_wall(self, cell_a: Coord, cell_b: Coord) -> None:
        # Burzenie wspólnej ściany między sąsiednimi komórkami (x, y).
        x1, y1 = cell_a
        x2, y2 = cell_b
        dx = x2 - x1
        dy = y2 - y1

        if dx == 1 and dy == 0:      # cell_b jest na Wschód od cell_a
            self.grid[y1][x1] &= ~EAST
            self.grid[y2][x2] &= ~WEST
        elif dx == -1 and dy == 0:   # cell_b jest na Zachód od cell_a
            self.grid[y1][x1] &= ~WEST
            self.grid[y2][x2] &= ~EAST
        elif dx == 0 and dy == 1:    # cell_b jest na Południe od cell_a
            self.grid[y1][x1] &= ~SOUTH
            self.grid[y2][x2] &= ~NORTH
        elif dx == 0 and dy == -1:   # cell_b jest na Północ od cell_a
            self.grid[y1][x1] &= ~NORTH
            self.grid[y2][x2] &= ~SOUTH

    def add_wall(self, cell_a: Coord, cell_b: Coord) -> None:
        """Close the wall between two neighbor cells.

        Args:
        cell_a: First cell as (x, y).
        cell_b: Second cell as (x, y), next to cell_a
        """

        # Dodawanie wspólnej ściany między sąsiednimi komórkami (x, y).
        x1, y1 = cell_a
        x2, y2 = cell_b
        dx = x2 - x1
        dy = y2 - y1

        if dx == 1 and dy == 0:      # cell_b jest na Wschód od cell_a
            self.grid[y1][x1] |= EAST
            self.grid[y2][x2] |= WEST
        elif dx == -1 and dy == 0:   # cell_b jest na Zachód od cell_a
            self.grid[y1][x1] |= WEST
            self.grid[y2][x2] |= EAST
        elif dx == 0 and dy == 1:    # cell_b jest na Południe od cell_a
            self.grid[y1][x1] |= SOUTH
            self.grid[y2][x2] |= NORTH
        elif dx == 0 and dy == -1:   # cell_b jest na Północ od cell_a
            self.grid[y1][x1] |= NORTH
            self.grid[y2][x2] |= SOUTH

    def get_unvisited_neighbors(
        self, cell: Coord, visited: set[Coord]
    ) -> list[Coord]:
        """Return neighbors of a cell that are inside the maze and new

        Args:
        cell: Current cell as (x, y).
        visited: Cells that were already visited.

        Returns:
        List of free neighbor cells (north, east, south, west).
        """
        x, y = cell
        candidates = [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]
        result: list[Coord] = []

        for nx, ny in candidates:
            if (
                0 <= nx < self.width
                and 0 <= ny < self.height
                and (nx, ny) not in visited
            ):
                result.append((nx, ny))
        return result

    def _get_42(self) -> set[Coord]:
        """Return the cells that draw the "42" in the middle of the maze.
        Args:
        warn: If True, print a message when the maze is too small.

        Returns:
        Set of (x, y) cells. Empty if the maze is too small.
        """
        if (self.width < 9 or self.height < 7):
            return set()

        pattern = [
            "#...###",
            "#.....#",
            "###.###",
            "..#.#..",
            "..#.###",
        ]

        offset_x = (self.width - 7) // 2
        offset_y = (self.height - 5) // 2

        cells: set[Coord] = set()
        for dy, row in enumerate(pattern):
            for dx, char in enumerate(row):
                if char == '#':
                    cells.add((offset_x + dx, offset_y + dy))
        return cells

    def is_open_3x3(self, sx: int, sy: int) -> bool:
        """Check one 3x3 window for an open area.

        Args:
        sx: Left column of the window.
        sy: Top row of the window.

        Returns:
        True if the window has no inner walls (a 3x3 open area).
        """
        for dy in range(3):
            for dx in range(2):
                if self.grid[sy + dy][sx + dx] & EAST:
                    return False
        for dy in range(2):
            for dx in range(3):
                if self.grid[sy + dy][sx + dx] & SOUTH:
                    return False
        return True

    def has_open_3x3(self) -> bool:
        for sy in range(self.height - 2):
            for sx in range(self.width - 2):
                if self.is_open_3x3(sx, sy):
                    return True
        return False

    def has_open_3x3_near(self, cell: Coord) -> bool:
        """Check only the windows that contain 'cell' (at most 9). """

        x, y = cell
        for sy in range(max(0, y - 2), min(y, self.height - 3) + 1):
            for sx in range(max(0, x - 2), min(x, self.width - 3) + 1):
                if self.is_open_3x3(sx, sy):
                    return True
        return False

    def remove_dead_ends(self, rng: random.Random) -> None:
        directions = [
            (0, -1, NORTH),
            (1, 0, EAST),
            (0, 1, SOUTH),
            (-1, 0, WEST),
        ]

        for y in range(self.height):
            for x in range(self.width):
                # sprawdzenie czy komorka to slepy zaulek (3sciany zamkniete)
                if (self.grid[y][x] not in (7, 11, 13, 14)):
                    continue
                # szukanie legal sasiadow za zamknieta sciana
                candidates: list[Coord] = []
                for dx, dy, wall_bit in directions:
                    nx = x + dx
                    ny = y + dy
                    # czy jest sciana i czy w planszy i nie 42
                    if (
                        (self.grid[y][x] & wall_bit)
                        and 0 <= nx < self.width
                        and 0 <= ny < self.height
                        and self.grid[ny][nx] != 15
                    ):
                        candidates.append((nx, ny))

                rng.shuffle(candidates)
                for nx, ny in candidates:
                    self.remove_wall((x, y), (nx, ny))
                    if (self.has_open_3x3_near((x, y))
                            or self.has_open_3x3_near((nx, ny))):
                        self.add_wall((x, y), (nx, ny))
                    else:
                        break

    def generate(
        self,
        start: Coord = (0, 0),
        exit_pos: Coord | None = None,
        seed: int | None = None,
        perfect: bool = False
    ) -> list[list[int]]:
        """Generate a maze with an iterative DFS (recursive backtracker).
        If perfect is False, dead-ends are removed afterwards, so the
        maze gets loops (but never a 3x3 open area).

        Args:
            start: Entry cell as (x, y).
            exit_pos: Exit cell as (x, y), or None to skip the checks.
            seed: Random seed. The same seed gives the same maze.
            perfect: True for one single path, False for a looped maze.

        Returns:
            The grid as a list of rows, with wall bitmasks 0-15.

        Raises:
            ValueError: If start or exit is in the "42", out of bounds,
                or if start and exit are the same cell.
        """
        rng = random.Random(seed)
        blocked = self._get_42()
        if start in blocked:
            raise ValueError("Start inside 42 pattern!")
        if exit_pos is not None and exit_pos in blocked:
            raise ValueError("End inside 42 pattern!")
        sx, sy = start
        if not (0 <= sx < self.width and 0 <= sy < self.height):
            raise ValueError("Start out of maze bounds!")
        if exit_pos is not None:
            ex, ey = exit_pos
            if not (0 <= ex < self.width and 0 <= ey < self.height):
                raise ValueError("Exit out of maze bounds!")
            if start == exit_pos:
                raise ValueError("Start and exit cannot be the same!")
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(15)
            self.grid.append(row)
        visited: set[Coord] = set(blocked)
        visited.add(start)
        stack: list[Coord] = [start]

        while stack:
            current = stack[-1]
            neighbors = self.get_unvisited_neighbors(current, visited)
            if neighbors:
                nxt = rng.choice(neighbors)
                self.remove_wall(current, nxt)
                visited.add(nxt)
                stack.append(nxt)
            else:
                stack.pop()
        if not perfect:
            self.remove_dead_ends(rng)
        return self.grid

    def solve(self, entry: Coord, exit_pos: Coord) -> str:
        """Find the shortest path with BFS.
        Args:
            entry: Start cell as (x, y).
            exit_pos: Target cell as (x, y).

        Returns:
            Path as a string of N, E, S, W letters, or "exit unreachable".
        """
        queue: deque[Coord] = deque([entry])
        visited: set[Coord] = {entry}
        parent: dict[Coord, tuple[Coord, str]] = {}
        directions = [(0, -1, NORTH, "N"),
                      (1, 0, EAST, "E"),
                      (0, 1, SOUTH, "S"),
                      (-1, 0, WEST, "W")]
        while queue:
            current = queue.popleft()
            x, y = current
            if current == exit_pos:
                break
            for dx, dy, wall_bit, letter in directions:
                if (self.grid[y][x] & wall_bit == 0):
                    nx = x + dx
                    ny = y + dy
                    if (
                        0 <= nx < self.width
                        and 0 <= ny < self.height
                        and self.grid[ny][nx] != 15
                            ):
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            parent[(nx, ny)] = (current, letter)
                            queue.append((nx, ny))

        path: list[str] = []
        curr = exit_pos
        if exit_pos not in parent and exit_pos != entry:
            return "exit unreachable"
        while curr != entry:
            prev_cell, letter = parent[curr]
            path.append(letter)
            curr = prev_cell

        path.reverse()
        return ("".join(path))


if __name__ == "__main__":
    gen = MazeGenerator(width=20, height=20)
    grid = gen.generate(start=(0, 0), exit_pos=(6, 7), seed=42)

    with open("test_maze.txt", "w", encoding="utf-8") as f:
        for row in grid:
            f.write("".join(format(cell, "x") for cell in row) + "\n")
        f.write("\n0,0\n4,4\n")
        f.write(gen.solve((0, 0), (4, 4)) + "\n")
        print(gen.solve((0, 0), (4, 4)))
