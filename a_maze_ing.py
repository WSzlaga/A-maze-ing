from mazegen.generator import MazeGenerator, NORTH, WEST


def print_maze(grid: list[list[int]]) -> None:
    """Rysuje labirynt w terminalu w prostym ASCII."""
    width = len(grid[0])

    for row in grid:
        # 1. Górne ściany (NORTH)
        top = ""
        for cell in row:
            top += "+---" if (cell & NORTH) else "+   "
        print(top + "+")

        # 2. Środek komórek + lewe ściany (WEST)
        mid = ""
        for cell in row:
            wall = "|" if (cell & WEST) else " "
            body = "###" if cell == 15 else "   "
            mid += wall + body
        print(mid + "|")

    # 3. Dolna krawędź całego labiryntu
    print("+---" * width + "+")


if __name__ == "__main__":
    gen = MazeGenerator(width=5, height=5)
    grid = gen.generate(start=(0, 0), seed=42)
    print_maze(grid)

    with open("test_maze.txt", "w", encoding="utf-8") as f:
        for row in grid:
            f.write("".join(format(cell, "x") for cell in row) + "\n")
        f.write("\n0,0\n4,4\n")

    print("Wygenerowano test_maze.txt!")
