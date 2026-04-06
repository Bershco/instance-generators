#!/usr/bin/python3
import argparse
import math
import random
import sys
from pathlib import Path
from typing import NoReturn

try:
    from problem_generator.common import get_problem_template
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from problem_generator.common import get_problem_template


TEMPLATE_FILE_PATH = Path(__file__).parent / "template.pddl"


def generate_market_names(num_markets: int) -> list[str]:
    return [f"market{i}" for i in range(1, num_markets + 1)]


def generate_goods_names(num_goods: int) -> list[str]:
    return [f"goods{i}" for i in range(num_goods)]


def fmt_float(value: float) -> str:
    if abs(value) < 1e-9:
        return "0"
    return f"{value:.2f}"


def build_drive_costs(markets: list[str], max_cost: int) -> list[str]:
    coords = {"depot0": (0.0, 0.0)}
    for market in markets:
        coords[market] = (
            random.uniform(0.0, 100.0),
            random.uniform(0.0, 100.0),
        )

    scale_low = max(3.0, max_cost / 10.0)
    scale_high = max(6.0, max_cost / 4.0)
    scale = random.uniform(scale_low, scale_high)

    nodes = ["depot0"] + markets
    drive_costs = []

    for source in nodes:
        x1, y1 = coords[source]
        for target in nodes:
            if source == target:
                cost = 0.0
            else:
                x2, y2 = coords[target]
                cost = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) * scale
            drive_costs.append(f"(= (drive-cost {source} {target}) {fmt_float(round(cost, 2))})")

    return drive_costs


def build_price_fluents(
        markets: list[str],
        goods: list[str],
        max_cost: int,
) -> tuple[list[str], list[str]]:
    prices: dict[tuple[str, str], int] = {}
    sales: dict[tuple[str, str], int] = {}
    market_offer_counts = {market: 0 for market in markets}

    offer_low = max(1, len(markets) // 3)
    offer_high = max(offer_low, (2 * len(markets)) // 3)

    for good in goods:
        offered_count = random.randint(offer_low, offer_high)
        offered_markets = set(random.sample(markets, k=min(offered_count, len(markets))))

        for market in markets:
            if market in offered_markets:
                prices[(good, market)] = random.randint(1, max_cost)
                sales[(good, market)] = random.randint(0, max_cost)
                market_offer_counts[market] += 1
            else:
                prices[(good, market)] = 0
                sales[(good, market)] = 0

    for market, count in market_offer_counts.items():
        if count == 0:
            good = random.choice(goods)
            prices[(good, market)] = random.randint(1, max_cost)
            sales[(good, market)] = random.randint(0, max_cost)

    price_lines = []
    sale_lines = []

    for market in markets:
        for good in goods:
            price_lines.append(f"(= (price {good} {market}) {prices[(good, market)]})")
            sale_lines.append(f"(= (on-sale {good} {market}) {sales[(good, market)]})")

    return price_lines, sale_lines


def build_request_fluents(goods: list[str], max_capacity: int) -> tuple[list[str], list[str]]:
    bought_lines = []
    request_lines = []

    for good in goods:
        bought_lines.append(f"(= (bought {good}) 0)")
        request_lines.append(f"(= (request {good}) {random.randint(1, max_capacity)})")

    return bought_lines, request_lines


def generate_instance(
        instance_name: str,
        num_markets: int,
        num_goods: int,
        max_cost: int,
        max_capacity: int,
) -> str:
    template = get_problem_template(TEMPLATE_FILE_PATH)

    markets = generate_market_names(num_markets)
    goods = generate_goods_names(num_goods)

    price_lines, sale_lines = build_price_fluents(markets, goods, max_cost)
    drive_cost_lines = build_drive_costs(markets, max_cost)
    bought_lines, request_lines = build_request_fluents(goods, max_capacity)

    initial_fluents = []
    initial_fluents.extend(price_lines)
    initial_fluents.extend(sale_lines)
    initial_fluents.extend(drive_cost_lines)
    initial_fluents.append("(loc truck0 depot0)")
    initial_fluents.extend(bought_lines)
    initial_fluents.extend(request_lines)

    goal_conditions = [
        f"(>= (bought {good}) (request {good}))" for good in goods
    ]

    template_mapping = {
        "instance_name": instance_name,
        "markets_list": " ".join(markets),
        "goods_list": " ".join(goods),
        "initial_fluents": "\n\t".join(initial_fluents),
        "goal_conditions": "\n\t".join(goal_conditions),
    }

    return template.substitute(template_mapping)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate tpp planning instances")
    parser.add_argument("--min_markets", required=True)
    parser.add_argument("--max_markets", required=True)
    parser.add_argument("--min_products", required=True)
    parser.add_argument("--max_products", required=True)
    parser.add_argument("--max_cost", required=True)
    parser.add_argument("--max_capacity", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--total_num_problems", default=200)
    parser.add_argument("--num_prev_instances", default=0)
    return parser.parse_args()


def generate_multiple_problems(
        output_folder: Path,
        total_num_problems: int,
        num_prev_instances: int = 0,
        **difficulty_kwargs,
) -> NoReturn:
    min_markets = int(difficulty_kwargs.get("min_markets", 5))
    max_markets = int(difficulty_kwargs.get("max_markets", 40))
    min_products = int(difficulty_kwargs.get("min_products", 2))
    max_products = int(difficulty_kwargs.get("max_products", 39))
    max_cost = max(1, int(difficulty_kwargs.get("max_cost", 50)))
    max_capacity = max(1, int(difficulty_kwargs.get("max_capacity", 200)))

    if max_markets < min_markets:
        min_markets, max_markets = max_markets, min_markets
    if max_products < min_products:
        min_products, max_products = max_products, min_products

    output_folder.mkdir(parents=True, exist_ok=True)

    for idx in range(total_num_problems):
        num_markets = random.randint(min_markets, max_markets)
        num_products = random.randint(min_products, max_products)
        instance_index = num_prev_instances + idx

        with open(output_folder / f"pfile{instance_index}.pddl", "wt") as problem_file:
            problem_file.write(
                generate_instance(
                    instance_name=f"tpp_{num_markets}_{num_products}",
                    num_markets=num_markets,
                    num_goods=num_products,
                    max_cost=max_cost,
                    max_capacity=max_capacity,
                )
            )


def main() -> None:
    args = parse_arguments()

    generate_multiple_problems(
        output_folder=Path(args.output_path),
        total_num_problems=int(args.total_num_problems),
        num_prev_instances=int(args.num_prev_instances),
        min_markets=int(args.min_markets),
        max_markets=int(args.max_markets),
        min_products=int(args.min_products),
        max_products=int(args.max_products),
        max_cost=int(args.max_cost),
        max_capacity=int(args.max_capacity),
    )


if __name__ == "__main__":
    main()
