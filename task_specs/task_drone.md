# Task: Implement drone instance generator

## Objective

Create a random instance generator for the IPC2023 numeric planning domain:

`drone`

using only the problem instance corpus located under:

`problems/numeric/drone/`

## Git and GitHub are essential

Git and GitHub are mandatory for this task.

- Work inside the shared repository for all domains
- Never commit directly to `main`
- Use a dedicated branch for this domain:
  - `feature/drone-generator`
- Commit `template.pddl` before `generator.py`
- Push this branch to GitHub after each commit
- If GitHub repo creation, authentication, or push fails, ask the user for help immediately
- If GitHub CLI is available and authenticated, prefer using it automatically

## Mandatory startup actions

### 1. Ensure Git repo exists

If the current directory is not a Git repository, initialize it:

```bash
git init
git add .
git commit -m "Initial repository setup"
```

### 2. Ensure GitHub remote exists

Check remotes:

```bash
git remote -v
```

If no `origin` remote exists, try to create the GitHub repo automatically:

```bash
gh repo create numeric-ipc23-instance-generators --private --source=. --push
```

If that fails, stop and ask the user for help with GitHub setup.

### 3. Create the feature branch

```bash
git checkout main
git pull --ff-only
git checkout -b feature/drone-generator
```

## High-level goal

The final output for this domain must be:

- `problem_generator/drone/template.pddl`
- `problem_generator/drone/generator.py`

The generator must follow the structure of:

- `problem_generator/counters/generator.py`

and be compatible with the runtime pipeline that calls:

```python
generate_multiple_problems(
    output_folder,
    total_num_problems,
    num_prev_instances=0,
    **difficulty_kwargs
)
```

## Important inference rules

- Do **not** rely on `domain.pddl`
- Infer structure only from the problem instance corpus
- Search recursively under `problems/numeric/drone/`
- Some domains may use nested folders instead of `instances/`
- Only inspect `.pddl` problem files
- Do not reuse assumptions from other domains unless the corpus clearly supports them

## Stage 1 — infer and create template

Inspect the corpus and infer:

drones, locations, packages/tasks if present, battery or energy fluents, movement topology, and goals

Create:

`problem_generator/drone/template.pddl`

The template should include placeholders for generated sections such as:

- objects
- initial predicates
- initial fluent values
- goals

### Stage 1 Git actions

After creating the template:

```bash
git add problem_generator/drone/template.pddl
git commit -m "Add template.pddl for drone"
git push -u origin feature/drone-generator
```

Then stop and wait for the user's approval before continuing.

## Stage 2 — implement generator

After approval, create:

`problem_generator/drone/generator.py`

The file must implement:

```python
generate_multiple_problems(
    output_folder,
    total_num_problems,
    num_prev_instances=0,
    **difficulty_kwargs
)
```

### Required behavior

- Generate exactly `total_num_problems` files
- Output filenames must be:
  - `pfile{num_prev_instances}.pddl`
  - `pfile{num_prev_instances+1}.pddl`
  - etc.
- Use the template file for generation
- Use Python `random` and/or `numpy.random`
- Do not introduce a separate seed argument
- Keep the code consistent with the counters generator style

## Difficulty kwargs

Choose clear and meaningful difficulty knobs for this domain.

Suggested knobs:

- `min_drones`
- `max_drones`
- `min_locations`
- `max_locations`
- `min_packages`
- `max_packages`
- `max_battery`

These should mainly scale object counts and numeric ranges.

## Stage 2 Git actions

After implementing the generator:

```bash
git add problem_generator/drone/generator.py
git commit -m "Add generator.py for drone"
git push
```

If GitHub CLI is available, optionally create a pull request:

```bash
gh pr create --title "Add drone generator" --body "Adds template and generator implementation for drone"
```

After finalizing Stage 2 for this domain:

- update `.gitignore` so unwanted untracked workflow artifacts remain ignored
- update all domain task markdown files under `task_specs/` and `task_specs/WORKFLOW.md` with this same post-Stage-2 requirement
- commit and push those documentation or hygiene updates if anything changed

## Constraints

- Do not add external packages
- Keep the implementation minimal and readable
- Match the observed corpus structure as closely as reasonable
- Prefer solvable-looking random instances
- Reuse helper patterns from the counters generator where appropriate
