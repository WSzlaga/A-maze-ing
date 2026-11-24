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


def parse_int(key: str, value: str) -> int:
    """Convert a config value to an integer with a readable error.

    Args:
        key: Name of the config key (used in the error message).
        value: Raw string value from the config file.

    Returns:
        The parsed integer.

    Raises:
        ValueError: If the value is not a valid integer.
    """
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{key} must be an integer, got '{value}'.") from None


def parse_coord(key: str, coord_str: str) -> Coord:
    """Parse an 'x,y' coordinate string into a tuple of two integers.

    Args:
        key: Name of the config key (used in the error message).
        coord_str: Coordinate string in 'x,y' format.

    Returns:
        Tuple of (x, y) integer coordinates.

    Raises:
        ValueError: If the coordinate format is invalid.
    """
    parts: list[str] = coord_str.split(",")
    if len(parts) != 2:
        raise ValueError(
            f"{key} must be in 'x,y' format, got '{coord_str}'."
        )
    return (parse_int(key, parts[0].strip()), parse_int(key, parts[1].strip()))


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

    width: int = parse_int("WIDTH", raw["WIDTH"])
    height: int = parse_int("HEIGHT", raw["HEIGHT"])
    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be positive integers.")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            f"WIDTH and HEIGHT cannot exceed {MAX_DIMENSION}."
        )

    entry: Coord = parse_coord("ENTRY", raw["ENTRY"])
    exit_pos: Coord = parse_coord("EXIT", raw["EXIT"])
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ValueError("ENTRY coordinates are out of maze bounds.")
    if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
        raise ValueError("EXIT coordinates are out of maze bounds.")
    if entry == exit_pos:
        raise ValueError("ENTRY and EXIT must be different cells.")

    perfect_raw: str = raw["PERFECT"].lower()
    if perfect_raw not in ("true", "false"):
        raise ValueError("PERFECT must be 'True' or 'False'.")

    seed: int | None = None
    if "SEED" in raw:
        seed = parse_int("SEED", raw["SEED"])

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit_pos=exit_pos,
        output_file=raw["OUTPUT_FILE"],
        perfect=perfect_raw == "true",
        seed=seed,
    )
