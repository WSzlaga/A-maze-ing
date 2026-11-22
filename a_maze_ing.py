"""Main entry point for the A-Maze-ing maze generator application."""

import sys
from app.display import run_interactive_ui
from app.exporter import export_maze
from app.parser import parse_config
from mazegen.generator import MazeGenerator


def main() -> None:
    """Parse config, generate and export the maze, and launch the UI.

    Returns:
        None. Exits with status code 1 if arguments or config are invalid.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    try:
        cfg = parse_config(sys.argv[1])

        maze = MazeGenerator(width=cfg.width, height=cfg.height)
        maze.generate(start=cfg.entry, seed=cfg.seed, perfect=cfg.perfect)
        path_str: str = maze.solve(cfg.entry, cfg.exit_pos)

        export_maze(maze, cfg.entry, cfg.exit_pos, path_str, cfg.output_file)
        run_interactive_ui(
            maze=maze,
            entry=cfg.entry,
            exit_pos=cfg.exit_pos,
            output_file=cfg.output_file,
            perfect=cfg.perfect,
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
