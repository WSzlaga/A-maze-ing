import random

# : współrzędne ENTRY i EXIT w config.txt są w formacie (x, y)
# (kolumna, wiersz), ale
# w tablicy 2D w Pythonie indeksuje się zazwyczaj grid[y][x]
Coord = tuple[int, int]  # (x, y)

NORTH = 1  # 0001
EAST = 2   # 0010
SOUTH = 4  # 0100
WEST = 8   # 1000


class MazeGenerator:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        # siatka[height][width] wypełniona 15(wszystkie ściany zamknięte)
        self.grid = []
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
        if (self.width < 9 or self.height < 7):
            print("Maze too small for 42 pattern")
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

    def has_open_3x3(self) -> bool:
        for sy in range(self.height - 2):
            for sx in range(self.width - 2):
                is_open = True
                for dy in range(3):
                    for dx in range(2):
                        if self.grid[sy + dy][sx + dx] & EAST:
                            is_open = False
                for dy in range(2):
                    for dx in range(3):
                        if self.grid[sy + dy][sx + dx] & SOUTH:
                            is_open = False
                if is_open:
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
                    if (self.has_open_3x3()):
                        self.add_wall((x, y), (nx, ny))
                    else:
                        break

    def generate(
        self, start: Coord = (0, 0), seed: int | None = None,
        perfect: bool = False
    ) -> list[list[int]]:
        """Generuje perfect maze za pomocą iteracyjnego DFS."""
        rng = random.Random(seed)
        blocked = self._get_42()
        if start in blocked:
            raise ValueError("Start inside 42 pattern!")
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
        queue: list[Coord] = [entry]
        visited: set[Coord] = {entry}
        parent = {}
        directions = [(0, -1, NORTH, "N"),
                      (1, 0, EAST, "E"),
                      (0, 1, SOUTH, "S"),
                      (-1, 0, WEST, "W")]
        while queue:
            current = queue.pop(0)
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

    # exitMaze()
# Inicjalizuj stos, exitCell, entryCell, currentCell = entryCel;
#     while currentCell != exitCell:
#         oznacz currentCell jako odwiedzoną;
#         wstaw na stos nieodwiedzonych sąsiadów currentCell:
#         if stos = []
#             return(0)
#         else:
#             zdejmij ze stosu komórkę, uczyń ją currentCell
#     sukces


if __name__ == "__main__":
    gen = MazeGenerator(width=5, height=5)
    grid = gen.generate(start=(0, 0), seed=42)

    with open("test_maze.txt", "w", encoding="utf-8") as f:
        for row in grid:
            f.write("".join(format(cell, "x") for cell in row) + "\n")
        # Stopka wymagana przez format wyjściowy (entry, exit, ścieżka)
        f.write("\n0,0\n4,4\n")
        f.write(gen.solve((0, 0), (4, 4)) + "\n")
        print(gen.solve((0, 0), (4, 4)))
