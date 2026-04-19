# Contributing to mbbank-lib

Thanks for your interest in contributing! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/thedtvn/MBBank.git
cd MBBank

# Install dependencies with dev tools
uv sync --group dev

# Or with pip
pip install -e ".[dev]"
```

## Development Workflow

### Code Quality

This project uses the following dev tools:

| Tool                                  | Purpose                  | Command                      |
|---------------------------------------|--------------------------|------------------------------|
| [Ruff](https://docs.astral.sh/ruff/)  | Linting & formatting     | `ruff check` / `ruff format` |
| [ty](https://github.com/astral-sh/ty) | Type checking            | `ty check`                   |
| [pdoc](https://pdoc.dev/)             | Documentation generation | `python docs_gen.py`         |

Before submitting a PR, make sure all checks pass:

```bash
ruff check .
ruff format --check .
ty check
```

### Commit Messages

Write clear, concise commit messages. Use the present tense ("Add feature" not "Added feature").

## Submitting Changes

1. **Fork** the repository
2. **Create a branch** from `main` (`git checkout -b my-change`)
3. **Make your changes** — keep them focused and minimal
4. **Run the checks** listed above
5. **Push** and open a **Pull Request**

### PR Guidelines

- One logical change per PR
- Fill out the PR template completely
- Link related issues
- Keep diffs small and reviewable

## Reporting Bugs

Use the [Bug Report](https://github.com/thedtvn/MBBank/issues/new?template=bug_report.yml) template.

**Important**: Never include real banking credentials, account numbers, or tokens in issues or PRs.

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) for instructions.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
