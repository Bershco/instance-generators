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


def generate_block_names(num_blocks: int) -> list[str]:
    return [f"b{i}" for i in range(1, num_blocks + 1)]


def generate_coordinate_pairs(num_blocks: int, max_values: int) -> list[tuple[int, int]]:
    if max_values <= 0:
        raise ValueError("max_values must be positive")

    total_cells = max_values * max_values
    if total_cells >= num_blocks:
        picks = random.sample(range(total_cells), num_blocks)
        return [
            (pick % max_values + 1, pick // max_values + 1)
            for pick in picks
        ]

    return [
        (
            random.randint(1, max_values),
            random.randint(1, max_values),
        )
        for _ in range(num_blocks)
    ]


def choose_num_groups(num_blocks: int, min_groups: int, max_groups: int) -> int:
    min_groups = max(1, min(min_groups, num_blocks))
    max_groups = max(min_groups, min(max_groups, num_blocks))
    return random.randint(min_groups, max_groups)


def partition_blocks(blocks: list[str], num_groups: int) -> list[list[str]]:
    if num_groups <= 1:
        return [blocks[:]]

    if num_groups >= len(blocks):
        return [[block] for block in blocks]

    shuffled_blocks = blocks[:]
    random.shuffle(shuffled_blocks)

    cut_points = sorted(random.sample(range(1, len(blocks)), num_groups - 1))
    sizes = []
    previous = 0
    for cut_point in cut_points + [len(blocks)]:
        sizes.append(cut_point - previous)
        previous = cut_point

    groups = []
    cursor = 0
    for size in sizes:
        groups.append(shuffled_blocks[cursor:cursor + size])
        cursor += size

    return groups


def build_group_index(groups: list[list[str]]) -> dict[str, int]:
    mapping = {}
    for group_index, group in enumerate(groups):
        for block in group:
            mapping[block] = group_index
    return mapping


def generate_goal_constraints(blocks: list[str], group_index: dict[str, int]) -> list[str]:
    goal_constraints = []

    for i, left_block in enumerate(blocks):
        for right_block in blocks[i + 1:]:
            if group_index[left_block] == group_index[right_block]:
                goal_constraints.append(f"(= (x {left_block}) (x {right_block}))")
                goal_constraints.append(f"(= (y {left_block}) (y {right_block}))")
            else:
                goal_constraints.append(
                    f"(or (not (= (x {left_block}) (x {right_block}))) "
                    f"(not (= (y {left_block}) (y {right_block}))))"
                )

    return goal_constraints


def generate_instance(
        instance_name: str,
        num_blocks: int,
        max_values: int,
        num_groups: int,
) -> str:
    template = get_problem_template(TEMPLATE_FILE_PATH)

    blocks = generate_block_names(num_blocks)
    coordinates = generate_coordinate_pairs(num_blocks, max_values)
    groups = partition_blocks(blocks, num_groups)
    group_index = build_group_index(groups)

    initial_fluents = []
    for block, (x_value, y_value) in zip(blocks, coordinates):
        initial_fluents.append(f"(= (x {block}) {x_value})")
        initial_fluents.append(f"(= (y {block}) {y_value})")

    initial_fluents.extend(
        [
            f"(= (max_x) {max_values} )",
            "(= (min_x) 1 )",
            f"(= (max_y) {max_values} )",
            "(= (min_y) 1 )",
        ]
    )

    template_mapping = {
        "instance_name": instance_name,
        "blocks_list": " ".join(blocks),
        "initial_fluents": "\n    ".join(initial_fluents),
        "goal_constraints": "\n    ".join(generate_goal_constraints(blocks, group_index)),
    }

    return template.substitute(template_mapping)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate block-grouping planning instances")
    parser.add_argument("--min_blocks", required=True)
    parser.add_argument("--max_blocks", required=True)
    parser.add_argument("--min_groups", required=True)
    parser.add_argument("--max_groups", required=True)
    parser.add_argument("--max_values", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--total_num_problems", default=200)
    parser.add_argument("--num_prev_instances", default=0)
    return parser.parse_args()


def generate_multiple_problems(
        output_folder: Path,
        total_num_problems: int,
        num_prev_instances: int = 0,
        **difficulty_kwargs,
) -> None:
    min_blocks = int(difficulty_kwargs.get("min_blocks", 5))
    max_blocks = int(difficulty_kwargs.get("max_blocks", 40))
    min_groups = int(difficulty_kwargs.get("min_groups", 2))
    max_groups = int(difficulty_kwargs.get("max_groups", 10))
    max_values = int(difficulty_kwargs.get("max_values", 100))

    output_folder.mkdir(parents=True, exist_ok=True)

    for offset in range(total_num_problems):
        num_blocks = random.randint(min_blocks, max_blocks)
        num_groups = choose_num_groups(num_blocks, min_groups, max_groups)
        variant = random.randint(1, 3)

        with open(output_folder / f"pfile{num_prev_instances + offset}.pddl", "wt") as problem_file:
            problem_file.write(
                generate_instance(
                    instance_name=f"instance_{max_values}_{num_blocks}_{num_groups}_{variant}",
                    num_blocks=num_blocks,
                    max_values=max_values,
                    num_groups=num_groups,
                )
            )


def main():
    args = parse_arguments()

    generate_multiple_problems(
        output_folder=Path(args.output_path),
        total_num_problems=int(args.total_num_problems),
        num_prev_instances=int(args.num_prev_instances),
        min_blocks=int(args.min_blocks),
        max_blocks=int(args.max_blocks),
        min_groups=int(args.min_groups),
        max_groups=int(args.max_groups),
        max_values=int(args.max_values),
    )


if __name__ == "__main__":
    main()
