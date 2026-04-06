#!/usr/bin/python3
import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

try:
    from problem_generator.common import get_problem_template
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from problem_generator.common import get_problem_template

TEMPLATE_FILE_PATH = Path(__file__).parent / "template.pddl"
MODES = ["colour", "high_res", "low_res"]
ROVER_CAPABILITIES = [
    "equipped_for_soil_analysis",
    "equipped_for_rock_analysis",
    "equipped_for_imaging",
]


def generate_names(prefix: str, count: int, suffix: str = "") -> list[str]:
    return [f"{prefix}{idx}{suffix}" for idx in range(count)]


def make_bidirectional_edges(nodes: list[str], target_edges: int) -> list[tuple[str, str]]:
    if len(nodes) < 2:
        return []

    edges = set()
    shuffled = nodes[:]
    random.shuffle(shuffled)

    for idx in range(1, len(shuffled)):
        source = shuffled[idx]
        target = random.choice(shuffled[:idx])
        edge = tuple(sorted((source, target)))
        edges.add(edge)

    possible_edges = [
        tuple(sorted((a, b)))
        for i, a in enumerate(nodes)
        for b in nodes[i + 1 :]
    ]
    random.shuffle(possible_edges)

    for edge in possible_edges:
        if len(edges) >= target_edges:
            break
        edges.add(edge)

    directed = []
    for source, target in sorted(edges):
        directed.append((source, target))
        directed.append((target, source))
    return directed


def choose_sample_waypoints(waypoints: list[str]) -> tuple[set[str], set[str], set[str]]:
    soil_count = random.randint(1, max(1, len(waypoints) // 2))
    rock_count = random.randint(1, max(1, len(waypoints) // 2))
    sun_count = random.randint(1, max(1, len(waypoints) // 2))

    soil = set(random.sample(waypoints, soil_count))
    rock = set(random.sample(waypoints, rock_count))
    sun = set(random.sample(waypoints, sun_count))

    return soil, rock, sun


def choose_rover_capabilities(num_rovers: int) -> list[set[str]]:
    capabilities = []
    for _ in range(num_rovers):
        count = random.randint(1, len(ROVER_CAPABILITIES))
        capabilities.append(set(random.sample(ROVER_CAPABILITIES, count)))

    if not any("equipped_for_soil_analysis" in caps for caps in capabilities):
        capabilities[0].add("equipped_for_soil_analysis")
    if not any("equipped_for_rock_analysis" in caps for caps in capabilities):
        capabilities[0].add("equipped_for_rock_analysis")
    if not any("equipped_for_imaging" in caps for caps in capabilities):
        capabilities[0].add("equipped_for_imaging")

    return capabilities


def generate_instance(
        instance_name: str,
        num_rovers: int,
        num_waypoints: int,
        num_objectives: int,
        max_energy: int,
) -> str:
    template = get_problem_template(TEMPLATE_FILE_PATH)

    rovers = generate_names("rover", num_rovers)
    stores = [f"{name}store" for name in rovers]
    waypoints = generate_names("waypoint", num_waypoints)
    cameras = generate_names("camera", max(1, random.randint(max(1, num_rovers - 1), num_rovers + 3)))
    objectives = generate_names("objective", num_objectives)

    visible_edges = make_bidirectional_edges(
        waypoints,
        target_edges=random.randint(
            len(waypoints) - 1,
            min(len(waypoints) * (len(waypoints) - 1) // 2, len(waypoints) * 4),
        ),
    )

    soil_waypoints, rock_waypoints, sun_waypoints = choose_sample_waypoints(waypoints)
    rover_capabilities = choose_rover_capabilities(num_rovers)
    start_positions = random.sample(waypoints, k=min(num_rovers, len(waypoints)))
    while len(start_positions) < num_rovers:
        start_positions.append(random.choice(waypoints))

    camera_specs = []
    for camera in cameras:
        rover = random.choice(rovers)
        objective = random.choice(objectives)
        support_count = random.randint(1, len(MODES))
        supports = random.sample(MODES, support_count)
        camera_specs.append((camera, rover, objective, supports))

    objective_visibility: dict[str, set[str]] = defaultdict(set)
    for objective in objectives:
        visible_count = random.randint(1, min(len(waypoints), 5))
        objective_visibility[objective].update(random.sample(waypoints, visible_count))

    initial_fluents = ["(= (recharges) 0)"]
    for rover in rovers:
        initial_fluents.append(f"(= (energy {rover}) {max_energy})")

    initial_predicates = []
    for source, target in visible_edges:
        initial_predicates.append(f"(visible {source} {target})")

    for waypoint in sorted(soil_waypoints):
        initial_predicates.append(f"(at_soil_sample {waypoint})")
    for waypoint in sorted(rock_waypoints):
        initial_predicates.append(f"(at_rock_sample {waypoint})")
    for waypoint in sorted(sun_waypoints):
        initial_predicates.append(f"(in_sun {waypoint})")

    lander_waypoint = random.choice(waypoints)
    initial_predicates.append(f"(at_lander general {lander_waypoint})")
    initial_predicates.append("(channel_free general)")

    for rover, store, start_waypoint, caps in zip(
            rovers, stores, start_positions, rover_capabilities
    ):
        initial_predicates.append(f"(in {rover} {start_waypoint})")
        initial_predicates.append(f"(available {rover})")
        initial_predicates.append(f"(store_of {store} {rover})")
        initial_predicates.append(f"(empty {store})")
        for capability in sorted(caps):
            initial_predicates.append(f"({capability} {rover})")
        for source, target in visible_edges:
            initial_predicates.append(f"(can_traverse {rover} {source} {target})")

    for camera, rover, objective, supports in camera_specs:
        initial_predicates.append(f"(on_board {camera} {rover})")
        initial_predicates.append(f"(calibration_target {camera} {objective})")
        for mode in sorted(supports):
            initial_predicates.append(f"(supports {camera} {mode})")

    for objective, visible_waypoints in objective_visibility.items():
        for waypoint in sorted(visible_waypoints):
            initial_predicates.append(f"(visible_from {objective} {waypoint})")

    goal_conditions = []

    soil_goal_candidates = sorted(soil_waypoints)
    if soil_goal_candidates:
        for waypoint in random.sample(
                soil_goal_candidates,
                random.randint(1, len(soil_goal_candidates)),
        ):
            goal_conditions.append(f"(communicated_soil_data {waypoint})")

    rock_goal_candidates = sorted(rock_waypoints)
    if rock_goal_candidates:
        for waypoint in random.sample(
                rock_goal_candidates,
                random.randint(1, len(rock_goal_candidates)),
        ):
            goal_conditions.append(f"(communicated_rock_data {waypoint})")

    image_goal_cameras = random.sample(
        camera_specs,
        random.randint(1, min(len(camera_specs), len(objectives))),
    )
    for camera, _, objective, supports in image_goal_cameras:
        goal_conditions.append(
            f"(communicated_image_data {objective} {random.choice(sorted(supports))})"
        )

    template_mapping = {
        "instance_name": instance_name,
        "rovers_list": " ".join(rovers),
        "stores_list": " ".join(stores),
        "waypoints_list": " ".join(waypoints),
        "cameras_list": " ".join(cameras),
        "objectives_list": " ".join(objectives),
        "initial_fluents": "\n\t".join(initial_fluents),
        "initial_predicates": "\n\t".join(initial_predicates),
        "goal_conditions": "\n\t".join(goal_conditions),
    }

    return template.substitute(template_mapping)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate rover planning instances")
    parser.add_argument("--min_rovers", required=True)
    parser.add_argument("--max_rovers", required=True)
    parser.add_argument("--min_waypoints", required=True)
    parser.add_argument("--max_waypoints", required=True)
    parser.add_argument("--min_objectives", required=True)
    parser.add_argument("--max_objectives", required=True)
    parser.add_argument("--max_energy", required=True)
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
    min_rovers = int(difficulty_kwargs.get("min_rovers", 1))
    max_rovers = int(difficulty_kwargs.get("max_rovers", 8))
    min_waypoints = int(difficulty_kwargs.get("min_waypoints", 4))
    max_waypoints = int(difficulty_kwargs.get("max_waypoints", 25))
    min_objectives = int(difficulty_kwargs.get("min_objectives", 2))
    max_objectives = int(difficulty_kwargs.get("max_objectives", 8))
    max_energy = int(difficulty_kwargs.get("max_energy", 50))

    output_folder.mkdir(parents=True, exist_ok=True)

    for offset in range(total_num_problems):
        num_rovers = random.randint(min_rovers, max_rovers)
        num_waypoints = random.randint(min_waypoints, max_waypoints)
        num_objectives = random.randint(min_objectives, max_objectives)

        with open(
                output_folder / f"pfile{num_prev_instances + offset}.pddl",
                "wt",
        ) as problem_file:
            problem_file.write(
                generate_instance(
                    instance_name=f"roverprob{random.randint(1000, 9999)}",
                    num_rovers=num_rovers,
                    num_waypoints=num_waypoints,
                    num_objectives=num_objectives,
                    max_energy=max_energy,
                )
            )


def main():
    args = parse_arguments()

    generate_multiple_problems(
        output_folder=Path(args.output_path),
        total_num_problems=int(args.total_num_problems),
        num_prev_instances=int(args.num_prev_instances),
        min_rovers=int(args.min_rovers),
        max_rovers=int(args.max_rovers),
        min_waypoints=int(args.min_waypoints),
        max_waypoints=int(args.max_waypoints),
        min_objectives=int(args.min_objectives),
        max_objectives=int(args.max_objectives),
        max_energy=int(args.max_energy),
    )


if __name__ == "__main__":
    main()
