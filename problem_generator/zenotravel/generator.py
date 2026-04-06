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


def build_names(prefix: str, count: int, start: int = 1) -> list[str]:
    return [f"{prefix}{idx}" for idx in range(start, start + count)]


def build_city_names(count: int) -> list[str]:
    return [f"city{idx}" for idx in range(count)]


def choose_aircraft_count(num_cities: int) -> int:
    if num_cities <= 3:
        return 1
    if num_cities <= 6:
        return random.randint(2, 3)
    if num_cities <= 22:
        return random.randint(3, 5)
    return 5


def choose_distance_regime(num_cities: int) -> tuple[int, int]:
    if num_cities >= 25:
        return 25, 49
    return 550, 999


def build_distance_fluents(cities: list[str]) -> list[str]:
    lower, upper = choose_distance_regime(len(cities))
    distances = {}

    for city in cities:
        distances[(city, city)] = 0

    for index, source in enumerate(cities):
        for target in cities[index + 1:]:
            distance = random.randint(lower, upper)
            distances[(source, target)] = distance
            distances[(target, source)] = distance

    return [
        f"(= (distance {source} {target}) {distances[(source, target)]})"
        for source in cities
        for target in cities
    ]


def build_aircraft_fluents(aircraft: list[str], cities: list[str]) -> tuple[list[str], list[str]]:
    predicates = []
    fluents = []
    compact_regime = len(cities) >= 25

    for plane in aircraft:
        predicates.append(f"(located {plane} {random.choice(cities)})")

        if compact_regime:
            capacity = random.randint(120, 750)
            fuel = random.randint(6, 200)
        else:
            capacity = random.randint(2200, 15500)
            fuel = random.randint(50, 4800)

        slow_burn = random.randint(1, 5)
        fast_burn = random.randint(max(2, slow_burn + 1), max(6, slow_burn * 4))
        zoom_limit = random.randint(1, 10)

        fluents.extend(
            [
                f"(= (capacity {plane}) {capacity})",
                f"(= (fuel {plane}) {fuel})",
                f"(= (slow-burn {plane}) {slow_burn})",
                f"(= (fast-burn {plane}) {fast_burn})",
                f"(= (onboard {plane}) 0)",
                f"(= (zoom-limit {plane}) {zoom_limit})",
            ]
        )

    return predicates, fluents


def build_people(cities: list[str], count: int) -> tuple[list[str], list[str], list[str]]:
    people = build_names("person", count)
    predicates = []
    goals = []

    for person in people:
        start = random.choice(cities)
        goal = random.choice(cities)
        if len(cities) > 1 and random.random() < 0.85:
            while goal == start:
                goal = random.choice(cities)

        predicates.append(f"(located {person} {start})")
        goals.append(f"(located {person} {goal})")

    return people, predicates, goals


def generate_instance(
        instance_name: str,
        num_cities: int,
        num_people: int,
        num_aircraft: int,
) -> str:
    template = get_problem_template(TEMPLATE_FILE_PATH)

    cities = build_city_names(num_cities)
    aircraft = build_names("plane", num_aircraft)
    people, people_predicates, goal_conditions = build_people(cities, num_people)
    aircraft_predicates, aircraft_fluents = build_aircraft_fluents(aircraft, cities)
    distance_fluents = build_distance_fluents(cities)

    initial_predicates = aircraft_predicates + people_predicates
    initial_fluents = aircraft_fluents + distance_fluents + ["(= (total-fuel-used) 0)"]

    metric_expression = "(total-fuel-used)"
    if random.random() < 0.75:
        metric_expression = f"(+ (* {random.randint(1, 5)} (total-time))  (* {random.randint(1, 5)} (total-fuel-used)))"

    return template.substitute(
        {
            "instance_name": instance_name,
            "aircraft_list": "\n\t".join(aircraft),
            "people_list": "\n\t".join(people),
            "cities_list": "\n\t".join(cities),
            "initial_predicates": "\n\t".join(initial_predicates),
            "initial_fluents": "\n\t".join(initial_fluents),
            "goal_conditions": "\n\t".join(goal_conditions),
            "metric_expression": metric_expression,
        }
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate zenotravel planning instances")
    parser.add_argument("--min_cities", required=True)
    parser.add_argument("--max_cities", required=True)
    parser.add_argument("--min_people", required=True)
    parser.add_argument("--max_people", required=True)
    parser.add_argument("--min_aircraft", required=True)
    parser.add_argument("--max_aircraft", required=True)
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
    min_cities = int(difficulty_kwargs.get("min_cities", 3))
    max_cities = int(difficulty_kwargs.get("max_cities", 35))
    min_people = int(difficulty_kwargs.get("min_people", 2))
    max_people = int(difficulty_kwargs.get("max_people", 40))
    min_aircraft = int(difficulty_kwargs.get("min_aircraft", 1))
    max_aircraft = int(difficulty_kwargs.get("max_aircraft", 5))

    output_folder.mkdir(parents=True, exist_ok=True)

    for offset in range(total_num_problems):
        num_cities = random.randint(min_cities, max_cities)
        num_people = random.randint(min_people, max_people)
        lower_aircraft = max(min_aircraft, 1)
        upper_aircraft = min(max_aircraft, choose_aircraft_count(num_cities))
        if upper_aircraft < lower_aircraft:
            lower_aircraft = upper_aircraft
        num_aircraft = random.randint(lower_aircraft, upper_aircraft)

        with open(output_folder / f"pfile{num_prev_instances + offset}.pddl", "wt") as problem_file:
            problem_file.write(
                generate_instance(
                    instance_name=f"ZTRAVEL-{num_prev_instances + offset}",
                    num_cities=num_cities,
                    num_people=num_people,
                    num_aircraft=num_aircraft,
                )
            )


def main():
    args = parse_arguments()
    generate_multiple_problems(
        output_folder=Path(args.output_path),
        total_num_problems=int(args.total_num_problems),
        num_prev_instances=int(args.num_prev_instances),
        min_cities=int(args.min_cities),
        max_cities=int(args.max_cities),
        min_people=int(args.min_people),
        max_people=int(args.max_people),
        min_aircraft=int(args.min_aircraft),
        max_aircraft=int(args.max_aircraft),
    )


if __name__ == "__main__":
    main()
