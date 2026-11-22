from mazegen.generator import MazeGenerator

Coord = tuple[int, int]


def export_maze(
    maze: MazeGenerator,
    entry: Coord,
    exit_pos: Coord,
    path_str: str,
    filepath: str,
) -> None:
    """Export the maze grid, coordinates, and solution path to a file.

    Args:
        maze: MazeGenerator instance containing the wall bitmask grid.
        entry: Entry (x, y) coordinate.
        exit_pos: Exit (x, y) coordinate.
        path_str: Shortest path string composed of 'N', 'E', 'S', 'W'.
        filepath: Destination output file path.

    Returns:
        None. Writes the formatted maze representation to disk.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        for row in maze.grid:
            f.write("".join(format(cell, "X") for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit_pos[0]},{exit_pos[1]}\n")
        f.write(f"{path_str}\n")
