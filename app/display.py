import random
import shutil
import time
from app.exporter import export_maze
from mazegen.generator import EAST, MazeGenerator, NORTH, SOUTH, WEST

Coord = tuple[int, int]

RESET: str = "\033[0m"
WALL_COLOR: str = "\033[1;97m"  # Bright white bold wall lines

# Pastel background palettes (256-color ANSI codes)
BG_THEMES: list[tuple[str, list[int]]] = [
    ("Pastel Rainbow", [218, 217, 223, 229, 193, 158, 159, 189, 225]),
    ("Cotton Candy", [225, 219, 218, 217, 224, 189, 183, 159, 195]),
    ("Mint & Peach", [158, 194, 229, 223, 217, 216, 223, 229, 194]),
    ("Spring Sky", [195, 159, 153, 189, 183, 189, 153, 159]),
]

# Solid "42" block neon styles (matches the neon pink path by default)
PATTERN_THEMES: list[tuple[str, str]] = [
    ("Neon Pink", "\033[48;5;201m"),
    ("Electric Cyan", "\033[48;5;51m"),
    ("Neon Lime", "\033[48;5;46m"),
    ("Vibrant Violet", "\033[48;5;93m"),
]

# Fixed styles for entry, exit, and neon pink continuous path
STYLE_ENTRY: str = "\033[1;97;48;5;28m"
STYLE_EXIT: str = "\033[1;97;48;5;160m"
STYLE_PATH: str = "\033[1;97;48;5;201m"

# 16 Box Drawing Heavy corner characters: (Up, Right, Down, Left) -> Char
CORNERS: dict[tuple[bool, bool, bool, bool], str] = {
    (False, False, False, False): " ",
    (True, False, False, False): "╹",
    (False, True, False, False): "╺",
    (True, True, False, False): "┗",
    (False, False, True, False): "╻",
    (True, False, True, False): "┃",
    (False, True, True, False): "┏",
    (True, True, True, False): "┣",
    (False, False, False, True): "╸",
    (True, False, False, True): "┛",
    (False, True, False, True): "━",
    (True, True, False, True): "┻",
    (False, False, True, True): "┓",
    (True, False, True, True): "┫",
    (False, True, True, True): "┳",
    (True, True, True, True): "╋",
}


def get_solution_coords(entry: Coord, path_str: str) -> list[Coord]:
    """Convert a direction string ('NESW...') into a list of (x, y) coords.

    Args:
        entry: Starting (x, y) coordinate of the maze.
        path_str: String of step directions ('N', 'E', 'S', 'W').

    Returns:
        Ordered list of (x, y) coordinates from entry to exit.
    """
    if not path_str or path_str == "exit unreachable":
        return [entry]

    x, y = entry
    coords: list[Coord] = [(x, y)]
    moves: dict[str, tuple[int, int]] = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0),
    }

    for step in path_str:
        if step in moves:
            dx, dy = moves[step]
            x += dx
            y += dy
            coords.append((x, y))

    return coords


def get_bg_code(x: int, y: int, palette: list[int]) -> str:
    """Calculate the ANSI background color code for a diagonal gradient.

    Args:
        x: Horizontal cell coordinate.
        y: Vertical cell coordinate.
        palette: List of 256-color ANSI background codes.

    Returns:
        ANSI escape sequence setting the background color.
    """
    color_id: int = palette[((x + y) // 2) % len(palette)]
    return f"\033[48;5;{color_id}m"


def paint_wall(char: str, bg_code: str) -> str:
    """Render a white wall character over the given pastel background.

    Args:
        char: Box Drawing wall or corner character to render.
        bg_code: ANSI escape sequence for the cell's background color.

    Returns:
        Formatted string containing the colored character and reset sequence.
    """
    return f"{WALL_COLOR}{bg_code}{char}{RESET}"


def get_corner(maze: MazeGenerator, vx: int, vy: int) -> str:
    """Select the appropriate Box Drawing Heavy corner for vertex (vx, vy).

    Args:
        maze: MazeGenerator instance containing grid walls and dimensions.
        vx: Horizontal vertex coordinate (from 0 to maze.width).
        vy: Vertical vertex coordinate (from 0 to maze.height).

    Returns:
        Single Unicode Box Drawing Heavy character matching connected walls.
    """
    up: bool = False
    right: bool = False
    down: bool = False
    left: bool = False

    if vy > 0:
        if vx > 0 and (maze.grid[vy - 1][vx - 1] & EAST):
            up = True
        if vx < maze.width and (maze.grid[vy - 1][vx] & WEST):
            up = True

    if vx < maze.width:
        if vy > 0 and (maze.grid[vy - 1][vx] & SOUTH):
            right = True
        if vy < maze.height and (maze.grid[vy][vx] & NORTH):
            right = True

    if vy < maze.height:
        if vx > 0 and (maze.grid[vy][vx - 1] & EAST):
            down = True
        if vx < maze.width and (maze.grid[vy][vx] & WEST):
            down = True

    if vx > 0:
        if vy > 0 and (maze.grid[vy - 1][vx - 1] & SOUTH):
            left = True
        if vy < maze.height and (maze.grid[vy][vx - 1] & NORTH):
            left = True

    return CORNERS[(up, right, down, left)]


def render_ascii(
    maze: MazeGenerator,
    entry: Coord,
    exit_pos: Coord,
    solution_coords: list[Coord],
    pattern_42: set[Coord],
    palette: list[int],
    pattern_style: str,
    show_path: bool = True,
    path_limit: int | None = None,
    old_palette: list[int] | None = None,
    split_y: int = 0,
) -> None:
    """Render the maze in ASCII with theme transitions and path animation.

    Args:
        maze: MazeGenerator instance containing the grid and dimensions.
        entry: Entry (x, y) coordinate.
        exit_pos: Exit (x, y) coordinate.
        solution_coords: Ordered list of (x, y) coordinates for the path.
        pattern_42: Set of (x, y) coordinates forming the "42" block.
        palette: Active list of 256-color ANSI background codes.
        pattern_style: ANSI escape sequence styling the solid "42" block.
        show_path: Whether to display the shortest path from entry to exit.
        path_limit: Optional number of path steps to render during animation.
        old_palette: Previous background palette used during wipe transitions.
        split_y: Row index separating the new palette from the old palette.

    Returns:
        None. Outputs the rendered maze directly to standard output.
    """
    needed_cols: int = maze.width * 3 + 1
    term_cols: int = shutil.get_terminal_size().columns
    if term_cols < needed_cols:
        print(
            f"Terminal too narrow ({term_cols} cols). "
            f"Need at least {needed_cols} cols to render the maze."
        )
        return

    if not show_path:
        path_set: set[Coord] = set()
    elif path_limit is not None:
        path_set = set(solution_coords[:path_limit])
    else:
        path_set = set(solution_coords)

    steps: int = max(0, len(solution_coords) - 1)

    lines: list[str] = [
        "\033[H"
        f"Size: {maze.width}x{maze.height} | Steps: {steps} | "
        f"{STYLE_ENTRY} EN {RESET} Entry  "
        f"{STYLE_EXIT} EX {RESET} Exit  "
        f"{STYLE_PATH}    {RESET} Path\n"
    ]

    # 1. Top border of the maze
    active_top: list[int] = (
        old_palette if (old_palette is not None and split_y == 0) else palette
    )
    top_bg: str = get_bg_code(0, 0, active_top)
    top_line: str = paint_wall(get_corner(maze, 0, 0), top_bg)
    for x in range(maze.width):
        bg: str = get_bg_code(x, 0, active_top)
        horiz: str = "━━" if (maze.grid[0][x] & NORTH) else "  "
        corner: str = get_corner(maze, x + 1, 0)
        top_line += paint_wall(horiz, bg) + paint_wall(corner, bg)
    lines.append(top_line)

    # 2. Cell rows
    for y in range(maze.height):
        row_palette: list[int] = (
            old_palette if (old_palette is not None and y >= split_y)
            else palette
        )

        left_bg: str = get_bg_code(0, y, row_palette)
        left_char: str = "┃" if (maze.grid[y][0] & WEST) else " "
        row_mid: str = paint_wall(left_char, left_bg)
        row_bot: str = paint_wall(get_corner(maze, 0, y + 1), left_bg)

        for x in range(maze.width):
            cell: int = maze.grid[y][x]
            bg = get_bg_code(x, y, row_palette)
            is_42: bool = (x, y) in pattern_42
            is_path: bool = (x, y) in path_set

            # Cell interior (2 characters wide)
            if (x, y) == entry:
                body: str = f"{STYLE_ENTRY}EN{RESET}"
            elif (x, y) == exit_pos:
                body = f"{STYLE_EXIT}EX{RESET}"
            elif is_42:
                body = f"{pattern_style}  {RESET}"
            elif is_path:
                body = f"{STYLE_PATH}  {RESET}"
            else:
                body = f"{bg}  {RESET}"

            # East wall / passage (merge adjacent "42" or open path cells)
            if is_42 and (x + 1, y) in pattern_42:
                east_part: str = f"{pattern_style} {RESET}"
            elif not (cell & EAST) and is_path and (x + 1, y) in path_set:
                east_part = f"{STYLE_PATH} {RESET}"
            else:
                east_char: str = "┃" if (cell & EAST) else " "
                east_part = paint_wall(east_char, bg)

            # South wall / passage (merge adjacent "42" or open path cells)
            if is_42 and (x, y + 1) in pattern_42:
                south_part: str = f"{pattern_style}  {RESET}"
            elif not (cell & SOUTH) and is_path and (x, y + 1) in path_set:
                south_part = f"{STYLE_PATH}  {RESET}"
            else:
                south_char: str = "━━" if (cell & SOUTH) else "  "
                south_part = paint_wall(south_char, bg)

            # Bottom-right corner
            if (
                is_42
                and (x + 1, y) in pattern_42
                and (x, y + 1) in pattern_42
                and (x + 1, y + 1) in pattern_42
            ):
                corner_part: str = f"{pattern_style} {RESET}"
            else:
                corner_char: str = get_corner(maze, x + 1, y + 1)
                corner_part = paint_wall(corner_char, bg)

            row_mid += body + east_part
            row_bot += south_part + corner_part

        lines.append(row_mid)
        lines.append(row_bot)

    print("\n".join(lines))


def run_interactive_ui(
    maze: MazeGenerator,
    entry: Coord,
    exit_pos: Coord,
    output_file: str,
    perfect: bool = False,
) -> None:
    """Run the interactive terminal menu loop.

    Args:
        maze: MazeGenerator instance to display and regenerate on demand.
        entry: Entry (x, y) coordinate.
        exit_pos: Exit (x, y) coordinate.
        output_file: Destination file path for exporting regenerated mazes.
        perfect: Whether regenerated mazes should be perfect (no loops).

    Returns:
        None. Runs until the user chooses to quit or interrupts execution.
    """
    show_path: bool = True
    bg_idx: int = 0
    pat_idx: int = 0

    pattern_42: set[Coord] = maze._get_42()
    warning: str = ""
    if not pattern_42:
        warning = (
            "Error: maze too small for the '42' pattern."
            "You need at least 9x7."
        )
    path_str: str = maze.solve(entry, exit_pos)
    solution_coords: list[Coord] = get_solution_coords(entry, path_str)

    print("\033[H\033[J", end="")

    while True:
        bg_name, palette = BG_THEMES[bg_idx]
        pat_name, pat_style = PATTERN_THEMES[pat_idx]

        render_ascii(
            maze,
            entry=entry,
            exit_pos=exit_pos,
            solution_coords=solution_coords,
            pattern_42=pattern_42,
            palette=palette,
            pattern_style=pat_style,
            show_path=show_path,
        )

        if warning:
            print(warning)
        print("\n=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print(f"2. Show/Hide shortest path ({'ON' if show_path else 'OFF'}) ")
        print(f"3. Change pastel background ({bg_name})   ")
        print(f"4. Change '42' pattern style ({pat_name})   ")
        print("5. Quit")

        try:
            choice: str = input("Choice? (1-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if choice == "1":
            # Reset grid walls to 15 before generating a fresh maze
            maze.grid = [
                [15 for _ in range(maze.width)] for _ in range(maze.height)
            ]
            maze.generate(
                start=entry,
                seed=random.randint(0, 999999),
                perfect=perfect,
            )
            path_str = maze.solve(entry, exit_pos)
            solution_coords = get_solution_coords(entry, path_str)
            export_maze(maze, entry, exit_pos, path_str, output_file)
        elif choice == "2":
            show_path = not show_path
            if show_path:
                # Animate shortest path step by step from EN to EX
                for step in range(1, len(solution_coords) + 1):
                    render_ascii(
                        maze,
                        entry=entry,
                        exit_pos=exit_pos,
                        solution_coords=solution_coords,
                        pattern_42=pattern_42,
                        palette=palette,
                        pattern_style=pat_style,
                        show_path=True,
                        path_limit=step,
                    )
                    time.sleep(0.015)
        elif choice == "3":
            _, old_palette = BG_THEMES[bg_idx]
            bg_idx = (bg_idx + 1) % len(BG_THEMES)
            _, new_palette = BG_THEMES[bg_idx]

            # Smoothly wipe the old background palette with the new one
            for step in range(1, maze.height + 1):
                render_ascii(
                    maze,
                    entry=entry,
                    exit_pos=exit_pos,
                    solution_coords=solution_coords,
                    pattern_42=pattern_42,
                    palette=new_palette,
                    pattern_style=pat_style,
                    show_path=show_path,
                    old_palette=old_palette,
                    split_y=step,
                )
                time.sleep(0.02)
        elif choice == "4":
            pat_idx = (pat_idx + 1) % len(PATTERN_THEMES)
        elif choice == "5":
            print("Bye!")
            break
