# Instance Generators

This repository contains lightweight Python generators for numeric IPC-style PDDL problem instances. Each domain generator renders problems from a `template.pddl` file and exposes the shared workflow entrypoint:

```python
generate_multiple_problems(
    output_folder,
    total_num_problems,
    num_prev_instances=0,
    **difficulty_kwargs,
)
```

## Domains

- `counters`
- `delivery`
- `drone`
- `fo-counters`
- `mprime`
- `rover`
- `tpp`
- `zenotravel`
- `block-grouping`

## Repository Layout

- [`problem_generator/`](problem_generator): per-domain generators and templates.
- [`problems/numeric/`](problems/numeric): original benchmark domains and reference instances used to infer structure.
- [`generator_utils.py`](generator_utils.py): shared domain registry, difficulty presets, and helper utilities.
- [`test/`](test): temporary parse-check workspace for copied domains and generated instances.

## Running a Generator

Use any generator module directly from Python:

```bash
python3 - <<'PY'
from pathlib import Path
import importlib.util

module_path = Path("problem_generator/tpp/generator.py").resolve()
spec = importlib.util.spec_from_file_location("tpp_generator", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

module.generate_multiple_problems(
    output_folder=Path("out/tpp"),
    total_num_problems=10,
    min_markets=4,
    max_markets=6,
    min_products=2,
    max_products=4,
    max_cost=30,
    max_capacity=10,
)
PY
```

Or use the shared registry:

```bash
python3 - <<'PY'
from generator_utils import Domain, InstanceDifficulty

Domain.TPP.generate_instances(
    difficulty=InstanceDifficulty.EASY,
    total_num_problems=10,
)
PY
```

## Notes

- The generators aim to preserve the object structure, fluent patterns, and goal style of the original instance corpora rather than reproduce exact historical distributions.
- Generated files follow the workflow convention `pfile{index}.pddl`.
- Temporary parse checks can be run with a permissive numeric-capable parser such as `unified-planning`'s `PDDLReader`.
