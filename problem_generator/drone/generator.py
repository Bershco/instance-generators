#!/usr/bin/python3
import argparse
import random
import sys
from pathlib import Path

try:
    from problem_generator.common import get_problem_template
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from problem_generator.common import get_problem_template

TEMPLATE_FILE_PATH = Path(__file__).parent / "template.pddl"


def generate_location_names(max_x: int, max_y: int, max_z: int) -> list[str]:
    locations = []
    for x in range(max_x):
        for y in range(max_y):
            for z in range(max_z):
                locations.append(f"x{x}y{y}z{z}")
    return locations


def generate_coordinate_values(max_x: int, max_y: int, max_z: int) -> str:
    lines = []
    for x in range(max_x):
        for y in range(max_y):
            for z in range(max_z):
                location = f"x{x}y{y}z{z}"
                lines.append(f"(= (xl {location}) {x})")
                lines.append(f"(= (yl {location}) {y})")
                lines.append(f"(= (zl {location}) {z})")
    return "\n".join(lines)


def generate_goal_conditions(location_names: list[str]) -> str:
    return "\n".join(f"(visited {location})" for location in location_names) + "\n"


def resolve_axis_range(
        difficulty_kwargs: dict,
        axis: str,
        default_min: int,
        default_max: int,
) -> tuple[int, int]:
    axis_min = difficulty_kwargs.get(f"min_{axis}")
    axis_max = difficulty_kwargs.get(f"max_{axis}")

    if axis_min is None and axis_max is None:
        axis_min = difficulty_kwargs.get("min_drones")
        axis_max = difficulty_kwargs.get("max_drones")

    if axis_min is None and axis_max is None:
        axis_min = difficulty_kwargs.get("min_locations")
        axis_max = difficulty_kwargs.get("max_locations")

    if axis_min is None:
        axis_min = default_min
    if axis_max is None:
        axis_max = default_max

    return int(axis_min), int(axis_max)


def choose_dimensions(difficulty_kwargs: dict) -> tuple[int, int, int]:
    min_x, max_x = resolve_axis_range(difficulty_kwargs, "x", 1, 10)
    min_y, max_y = resolve_axis_range(difficulty_kwargs, "y", 1, 10)
    min_z, max_z = resolve_axis_range(difficulty_kwargs, "z", 1, 5)
    max_battery = difficulty_kwargs.get("max_battery")

    for _ in range(200):
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        z = random.randint(min_z, max_z)
        battery = 2 * (x + y + z) + 1
        if max_battery is None or battery <= int(max_battery):
            return x, y, z

    x = min_x
    y = min_y
    z = min_z
    return x, y, z


def generate_instance(instance_name: str, max_x: int, max_y: int, max_z: int) -> str:
    template = get_problem_template(TEMPLATE_FILE_PATH)
    locations = generate_location_names(max_x, max_y, max_z)
    battery_level = 2 * (max_x + max_y + max_z) + 1

    template_mapping = {
        "max_x": max_x,
        "max_y": max_y,
        "max_z": max_z,
        "instance_name": instance_name,
        "location_objects": "\n".join(f"{location} - location" for location in locations),
        "coordinate_values": generate_coordinate_values(max_x, max_y, max_z),
        "battery_level": battery_level,
        "goal_conditions": generate_goal_conditions(locations),
    }

    return template.substitute(template_mapping)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate drone planning instances")
    parser.add_argument("--min_x", required=False)
    parser.add_argument("--max_x", required=False)
    parser.add_argument("--min_y", required=False)
    parser.add_argument("--max_y", required=False)
    parser.add_argument("--min_z", required=False)
    parser.add_argument("--max_z", required=False)
    parser.add_argument("--min_locations", required=False)
    parser.add_argument("--max_locations", required=False)
    parser.add_argument("--min_drones", required=False)
    parser.add_argument("--max_drones", required=False)
    parser.add_argument("--max_battery", required=False)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--total_num_problems", required=True)
    parser.add_argument("--num_prev_instances", default=0)
    return parser.parse_args()


def generate_multiple_problems(
        output_folder: Path,
        total_num_problems: int,
        num_prev_instances: int = 0,
        **difficulty_kwargs,
) -> None:
    output_folder.mkdir(parents=True, exist_ok=True)

    for offset in range(total_num_problems):
        max_x, max_y, max_z = choose_dimensions(difficulty_kwargs)
        instance_id = num_prev_instances + offset
        with open(output_folder / f"pfile{instance_id}.pddl", "wt") as problem_file:
            problem_file.write(
                generate_instance(
                    f"droneprob_{max_x}_{max_y}_{max_z}",
                    max_x=max_x,
                    max_y=max_y,
                    max_z=max_z,
                )
            )


def main():
    args = parse_arguments()
    generate_multiple_problems(
        output_folder=Path(args.output_path),
        total_num_problems=int(args.total_num_problems),
        num_prev_instances=int(args.num_prev_instances),
        min_x=args.min_x,
        max_x=args.max_x,
        min_y=args.min_y,
        max_y=args.max_y,
        min_z=args.min_z,
        max_z=args.max_z,
        min_locations=args.min_locations,
        max_locations=args.max_locations,
        min_drones=args.min_drones,
        max_drones=args.max_drones,
        max_battery=args.max_battery,
    )


if __name__ == "__main__":
    main()
