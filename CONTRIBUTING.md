# Contributing to DronLibreFirmwareTools

Thank you for your interest in contributing. This document outlines coding standards, tests, and the pull request workflow we prefer.

## Getting started

1. Fork the repository and create a feature branch using a descriptive name, e.g. `feature/add-squashfs-detection` or `fix/utils-entropy`.
2. Run tests locally and ensure your changes include tests for new behavior.

## Coding standards

- Language: Python 3.10+.
- Use type hints for public functions and methods.
- Keep modules small and focused; follow the existing project layout in `src/`.
- Write clear docstrings for new public functions (short summary + args/returns).
- Prefer explicit, readable code over clever one-liners.
- Use `black` for formatting and `ruff`/`flake8` for linting (recommended):

```bash
python -m pip install black ruff
black .
ruff check .
```

## Tests

- Add unit tests for new detection logic or behavior in `tests/`.
- Tests should be deterministic and avoid network access or external dependencies.
- Run tests with:

```bash
python -m pytest -q
```

## Commit messages

- Use clear, concise messages. We recommend the Conventional Commits style, e.g.:

```
feat: add squashfs signature detection
fix: correct entropy calculation for empty input
test: add unit tests for report generator
```

## Pull request process

1. Open an issue for large changes or format additions before implementing.
2. Push a branch to your fork and open a PR against `main` with a descriptive title.
3. In the PR description include:
   - What the change does and why
   - Any relevant sample files or test vectors (only share legally permitted samples)
   - How to reproduce and run tests
4. Maintain CI green (if CI is configured). Add tests for new features.
5. Address review comments; squash or rebase as requested. Keep a clean history for clarity.

## Code of conduct

Be respectful and constructive in issue and PR discussions. We aim to foster a helpful, professional community.

## Questions

If you are unsure about the best approach for a contribution, open an issue to discuss before submitting a large PR.
