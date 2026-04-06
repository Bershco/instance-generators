#!/usr/bin/python3
import argparse
import random
from pathlib import Path
import sys

try:
    from problem_generator.common import get_problem_template
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from problem_generator.common import get_problem_template

TEMPLATE_FILE_PATH = Path(__file__).parent / "template.pddl"


def generate_instance(instance_name: str, num_counters: int, max_value: int) -> str:
    """Generate a single fo-counters planning problem instance."""

    template = get_problem_template(TEMPLATE_FILE_PATH)
    max_int = min(max_value, num_counters * 2)

    template_mapping = {
        "instance_name": instance_name,
        "counters_list": " ".join([f"c{i}" for i in range(num_counters)]),
        "max_int_value": max_int,
        "counters_initial_values": "\n        ".join(
            [f"(= (value c{i}) 0)" for i in range(num_counters)]
        ),
        "counters_rate_values": "\n        ".join(
            [f"(= (rate_value c{i}) 0)" for i in range(num_counters)]
        ),
        "counters_final_values": "\n    ".join(
            [
                f"(<= (+ (value c{i}) 1) (value c{i + 1}))"
                for i in range(num_counters - 1)
            ]
        ),
    }

    return template.substitute(template_mapping)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate fo-counters planning instances")
    parser.add_argument("--min_counters", required=True)
    parser.add_argument("--max_counters", required=True)
    parser.add_argument("--max_value", required=True)
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
    min_counters = int(difficulty_kwargs.get("min_counters", 2))
    max_counters = int(difficulty_kwargs.get("max_counters", 21))
    max_value = int(difficulty_kwargs.get("max_value", 100))

    output_folder.mkdir(parents=True, exist_ok=True)

    for i in range(total_num_problems):
        num_counters = random.randint(min_counters, max_counters)
        with open(
                output_folder / f"pfile{i + num_prev_instances}.pddl",
                "wt",
        ) as problem_file:
            problem_file.write(
                generate_instance(
                    f"instance_{num_counters}",
                    num_counters,
                    max_value,
                )
            )


def main():
    args = parse_arguments()

    generate_multiple_problems(
        output_folder=Path(args.output_path),
        total_num_problems=int(args.total_num_problems),
        num_prev_instances=int(args.num_prev_instances),
        min_counters=int(args.min_counters),
        max_counters=int(args.max_counters),
        max_value=int(args.max_value),
    )


if __name__ == "__main__":
    main()
