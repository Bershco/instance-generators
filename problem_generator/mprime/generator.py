#!/usr/bin/python3
import argparse
import random
import re
import sys
from pathlib import Path

try:
    from problem_generator.common import get_problem_template
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from problem_generator.common import get_problem_template

TEMPLATE_FILE_PATH = Path(__file__).parent / "template.pddl"
CORPUS_DIR = Path(__file__).resolve().parents[2] / "problems" / "numeric" / "mprime" / "instances"


def extract_name_pools() -> tuple[list[str], list[str], list[str]]:
    foods = set()
    pleasures = set()
    pains = set()

    for path in sorted(CORPUS_DIR.glob("*.pddl")):
        text = path.read_text()

        food_block = re.search(r":objects\s+(.*?)\s*- food", text, re.S)
        if food_block:
            foods.update(food_block.group(1).split())

        pleasure_block = re.search(r"- food\s+(.*?)\s*- pleasure", text, re.S)
        if pleasure_block:
            pleasures.update(pleasure_block.group(1).split())

        pain_block = re.search(r"- pleasure\s+(.*?)\s*- pain", text, re.S)
        if pain_block:
            pains.update(pain_block.group(1).split())

    return sorted(foods), sorted(pleasures), sorted(pains)


FOOD_POOL, PLEASURE_POOL, PAIN_POOL = extract_name_pools()


def take_names(pool: list[str], count: int, prefix: str) -> list[str]:
    if count <= len(pool):
        return random.sample(pool, count)

    names = random.sample(pool, len(pool))
    for index in range(count - len(pool)):
        names.append(f"{prefix}-{index + 1}")
    return names


def choose_goal_count(num_pains: int) -> int:
    goal_count = 1
    if num_pains > 1 and random.random() < 0.4:
        goal_count += 1
    if num_pains > 8 and random.random() < 0.1:
        goal_count += 1
    return goal_count


def build_eats_relations(foods: list[str]) -> list[str]:
    relations = set()
    for food in foods:
        out_degree = random.randint(2, min(4, len(foods)))
        for target in random.sample(foods, out_degree):
            relations.add(f"(eats {food} {target})")
        if random.random() < 0.25:
            relations.add(f"(eats {food} {food})")
    return sorted(relations)


def build_craves_relations(
        pleasures: list[str], pains: list[str], foods: list[str]
) -> list[str]:
    relations = set()
    for craving in pleasures + pains:
        target_count = 1 + int(len(foods) > 1 and random.random() < 0.3)
        for target in random.sample(foods, target_count):
            relations.add(f"(craves {craving} {target})")
    return sorted(relations)


def build_locale_values(foods: list[str], max_locale: int) -> list[str]:
    return [f"(= (locale {food}) {random.randint(0, max_locale)})" for food in foods]


def build_harmony_values(pleasures: list[str], max_harmony: int) -> list[str]:
    upper = max(1, max_harmony)
    return [f"(= (harmony {pleasure}) {random.randint(1, upper)})" for pleasure in pleasures]


def build_goal_conditions(
        pains: list[str],
        foods: list[str],
        initial_craves_pairs: set[tuple[str, str]],
) -> list[str]:
    goal_count = choose_goal_count(len(pains))
    goals = []
    used = set()
    attempts = 0
    max_attempts = 200

    while len(goals) < goal_count and attempts < max_attempts:
        pair = (random.choice(pains), random.choice(foods))
        attempts += 1
        if pair in used or pair in initial_craves_pairs:
            continue
        used.add(pair)
        goals.append(f"(craves {pair[0]} {pair[1]})")

    while len(goals) < goal_count:
        pair = (random.choice(pains), random.choice(foods))
        if pair in used:
            continue
        used.add(pair)
        goals.append(f"(craves {pair[0]} {pair[1]})")

    return goals


def generate_instance(
        instance_name: str,
        num_foods: int,
        num_pleasures: int,
        num_pains: int,
        max_locale: int,
        max_harmony: int,
) -> str:
    template = get_problem_template(TEMPLATE_FILE_PATH)

    foods = take_names(FOOD_POOL, num_foods, "food")
    pleasures = take_names(PLEASURE_POOL, num_pleasures, "pleasure")
    pains = take_names(PAIN_POOL, num_pains, "pain")

    initial_eats = build_eats_relations(foods)
    initial_craves = build_craves_relations(pleasures, pains, foods)
    initial_craves_pairs = {
        tuple(re.match(r"\(craves ([^\s)]+) ([^\s)]+)\)", fact).groups())
        for fact in initial_craves
    }
    initial_fluents = build_locale_values(foods, max_locale) + build_harmony_values(pleasures, max_harmony)
    goal_conditions = build_goal_conditions(pains, foods, initial_craves_pairs)

    template_mapping = {
        "instance_name": instance_name,
        "foods_list": " ".join(foods),
        "pleasures_list": " ".join(pleasures),
        "pains_list": " ".join(pains),
        "initial_eats": "\n    ".join(initial_eats),
        "initial_craves": "\n    ".join(initial_craves),
        "initial_fluents": "\n    ".join(initial_fluents),
        "goal_conditions": "\n    ".join(goal_conditions),
    }

    return template.substitute(template_mapping)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate mprime planning instances")
    parser.add_argument("--min_foods", required=True)
    parser.add_argument("--max_foods", required=True)
    parser.add_argument("--min_pleasures", required=True)
    parser.add_argument("--max_pleasures", required=True)
    parser.add_argument("--min_pains", required=True)
    parser.add_argument("--max_pains", required=True)
    parser.add_argument("--max_locale", required=True)
    parser.add_argument("--max_harmony", required=True)
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
    min_foods = int(difficulty_kwargs.get("min_foods", 4))
    max_foods = int(difficulty_kwargs.get("max_foods", 22))
    min_pleasures = int(difficulty_kwargs.get("min_pleasures", 1))
    max_pleasures = int(difficulty_kwargs.get("max_pleasures", 8))
    min_pains = int(difficulty_kwargs.get("min_pains", 2))
    max_pains = int(difficulty_kwargs.get("max_pains", 20))
    max_locale = int(difficulty_kwargs.get("max_locale", 12))
    max_harmony = int(difficulty_kwargs.get("max_harmony", 3))

    output_folder.mkdir(parents=True, exist_ok=True)

    for offset in range(total_num_problems):
        num_foods = random.randint(min_foods, max_foods)
        num_pleasures = random.randint(min_pleasures, max_pleasures)
        num_pains = random.randint(min_pains, max_pains)

        with open(output_folder / f"pfile{num_prev_instances + offset}.pddl", "wt") as problem_file:
            problem_file.write(
                generate_instance(
                    instance_name=f"mprime-generated-{num_prev_instances + offset}",
                    num_foods=num_foods,
                    num_pleasures=num_pleasures,
                    num_pains=num_pains,
                    max_locale=max_locale,
                    max_harmony=max_harmony,
                )
            )


def main():
    args = parse_arguments()
    generate_multiple_problems(
        output_folder=Path(args.output_path),
        total_num_problems=int(args.total_num_problems),
        num_prev_instances=int(args.num_prev_instances),
        min_foods=int(args.min_foods),
        max_foods=int(args.max_foods),
        min_pleasures=int(args.min_pleasures),
        max_pleasures=int(args.max_pleasures),
        min_pains=int(args.min_pains),
        max_pains=int(args.max_pains),
        max_locale=int(args.max_locale),
        max_harmony=int(args.max_harmony),
    )


if __name__ == "__main__":
    main()
