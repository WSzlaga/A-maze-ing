"""Configuration parser and validator for the A-Maze-ing generator."""

from dataclasses import dataclass

Coord = tuple[int, int]
MAX_DIMENSION: int = 500


@dataclass
class MazeConfig:
    """Validated configuration parameters for maze generation.

    Attributes:
        width: Number of maze columns.
        height: Number of maze rows.
        entry: Starting (x, y) coordinate.
        exit_pos: Target exit (x, y) coordinate.
        output_file: Destination path for exporting the generated maze.
        perfect: Whether the maze should be perfect (single unique path).
        seed: Optional random seed for deterministic generation.
    """

    width: int
    height: int
    entry: Coord
    exit_pos: Coord
    output_file: str
    perfect: bool
    seed: int | None = None


def parse_coord(coord_str: str) -> Coord:
    """Parse an 'x,y' coordinate string into a tuple of two integers.

    Args:
        coord_str: Coordinate string in 'x,y' format.

    Returns:
        Tuple of (x, y) integer coordinates.

    Raises:
        ValueError: If the coordinate format is invalid.
    """
    parts: list[str] = coord_str.split(",")
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate format: '{coord_str}'")
    return (int(parts[0].strip()), int(parts[1].strip()))


def parse_config(filepath: str) -> MazeConfig:
    """Parse and validate the maze configuration file.

    Args:
        filepath: Path to the configuration file (e.g., config.txt).

    Returns:
        MazeConfig instance with validated configuration parameters.

    Raises:
        ValueError: If required keys are missing or values are out of bounds.
    """
    raw: dict[str, str] = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Invalid syntax in config: '{line}'")
            key, value = line.split("=", 1)
            raw[key.strip().upper()] = value.strip()

    required: set[str] = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    }
    missing: set[str] = required - set(raw.keys())
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    width: int = int(raw["WIDTH"])
    height: int = int(raw["HEIGHT"])
    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be positive integers.")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            f"WIDTH and HEIGHT cannot exceed {MAX_DIMENSION}."
        )

    entry: Coord = parse_coord(raw["ENTRY"])
    exit_pos: Coord = parse_coord(raw["EXIT"])
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ValueError("ENTRY coordinates are out of maze bounds.")
    if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
        raise ValueError("EXIT coordinates are out of maze bounds.")
    if entry == exit_pos:
        raise ValueError("ENTRY and EXIT must be different cells.")

    perfect_raw: str = raw["PERFECT"].lower()
    if perfect_raw not in ("true", "false"):
        raise ValueError("PERFECT must be 'True' or 'False'.")

    seed: int | None = int(raw["SEED"]) if "SEED" in raw else None

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit_pos=exit_pos,
        output_file=raw["OUTPUT_FILE"],
        perfect=perfect_raw == "true",
        seed=seed,
    )
