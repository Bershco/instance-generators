# IPC2023 Numeric Generator Workflow

## Goal

Implement random instance generators for IPC2023 numeric planning domains.

The implementation must follow the existing counters generator structure and must be compatible with the runtime pipeline that calls:

```python
generate_multiple_problems(
    output_folder,
    total_num_problems,
    num_prev_instances=0,
    **difficulty_kwargs,
)
```

Each generator must create files named:

```text
pfile{index}.pddl
```

starting from `num_prev_instances`.

## Repository and GitHub are essential

Git and GitHub are mandatory for this workflow.

- There is one single repository for all domains
- Never commit directly to `main`
- Use one feature branch per domain
- Commit the template before the generator
- Push every domain branch to GitHub
- If GitHub remote does not exist, create it if possible
- If GitHub authentication or repo creation is blocked, ask the user for help immediately

## Recommended repository structure

```text
numeric-ipc23-instance-generators/
├── problems/
│   └── numeric/
│       ├── block-grouping/
│       ├── counters/
│       ├── delivery/
│       ├── drone/
│       ├── fo-counters/
│       ├── mprime/
│       ├── rover/
│       ├── tpp/
│       └── zenotravel/
├── problem_generator/
│   ├── counters/
│   │   ├── generator.py
│   │   └── template.pddl
│   ├── block-grouping/
│   ├── delivery/
│   ├── drone/
│   ├── fo-counters/
│   ├── mprime/
│   ├── rover/
│   ├── tpp/
│   └── zenotravel/
├── generator_utils.py
└── task_specs/
```

## Global rules

- Do **not** rely on `domain.pddl`
- Infer structure only from the instance corpus under `problems/numeric/{domain}/`
- Search recursively for `.pddl` problem files because some domains may not use an `instances/` folder
- Follow the style of `problem_generator/counters/generator.py`
- Use template-based generation
- Use `random` and/or `numpy.random`
- No additional seed argument is needed
- Difficulty kwargs should mainly control object counts and numeric ranges
- Goal complexity can stay relatively stable unless the corpus strongly suggests otherwise

## Mandatory Git bootstrap

At the start of the overall workflow, do the following.

### 1. Check whether this is already a Git repo

If not, run:

```bash
git init
git add .
git commit -m "Initial repository setup"
```

### 2. Check whether GitHub remote exists

Run:

```bash
git remote -v
```

If no `origin` exists, GitHub setup is mandatory.

### 3. Try to create and connect a GitHub repo automatically

If GitHub CLI is available and authenticated, run:

```bash
gh repo create numeric-ipc23-instance-generators --private --source=. --push
```

If that fails for any reason, stop and ask the user for help with one or more of:

- GitHub login/authentication
- repo creation
- remote URL
- push permissions

Do not continue domain work without GitHub connectivity unless the user explicitly says so.

## Per-domain branch workflow

For every domain, use a dedicated feature branch:

```bash
git checkout main
git pull --ff-only
git checkout -b feature/{domain}-generator
```

Examples:

```text
feature/delivery-generator
feature/rover-generator
feature/tpp-generator
```

## Per-domain two-stage workflow

### Stage 1: template only

1. Inspect `problems/numeric/{domain}/` recursively
2. Infer the structure
3. Create `problem_generator/{domain}/template.pddl`
4. Commit it
5. Push the branch to GitHub
6. Stop and wait for the user's approval

Commands:

```bash
git add problem_generator/{domain}/template.pddl
git commit -m "Add template.pddl for {domain}"
git push -u origin feature/{domain}-generator
```

### Stage 2: generator

After approval:

1. Create `problem_generator/{domain}/generator.py`
2. Commit it
3. Push to GitHub
4. Optionally create a PR if possible

Commands:

```bash
git add problem_generator/{domain}/generator.py
git commit -m "Add generator.py for {domain}"
git push
```

Optional PR:

```bash
gh pr create --title "Add {domain} generator" --body "Adds template and generator implementation for {domain}"
```

After Stage 2 is finalized for a domain:

1. Update `.gitignore` so unwanted untracked artifacts for the workflow stay ignored
2. Update all per-domain task markdown files under `task_specs/` and this workflow file to preserve that requirement for future domains
3. Commit and push those documentation or hygiene updates if they changed

## Required generator API

Every generator must implement:

```python
generate_multiple_problems(
    output_folder,
    total_num_problems,
    num_prev_instances=0,
    **difficulty_kwargs,
)
```

### Required behavior

- Generate exactly `total_num_problems` files
- Use filenames:
  - `pfile{num_prev_instances}.pddl`
  - `pfile{num_prev_instances+1}.pddl`
  - etc.
- Match the runtime expectations used by `get_realtime_instance()`
- Use the template file for final text generation

## Quality bar

Generated instances should:

- resemble the observed corpus structure
- be syntactically valid problem files
- be reasonably solvable-looking
- avoid obvious contradictions in initialization and goals

## Commit message style

Use messages like:

```text
Add template.pddl for delivery
Add generator.py for delivery
Adjust difficulty kwargs for delivery
Fix generation bug in delivery
```

Avoid vague messages.
