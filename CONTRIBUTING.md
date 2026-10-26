# Contributing

Contributions are welcome: bug reports, textbook problems that
pin a calculation down, new E6B functions, documentation, and
examples. This project aims to stay small, readable, dependency
free, and honest about what it does not yet compute.

## Getting set up

```bash
git clone https://github.com/sajidkabir/e6b.git
cd e6b
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
pytest -q
```

All tests should pass before you change anything. The package is
pure standard library, so there is nothing else to install.

## Making a change

1. Fork the repository and create a branch from `main`
   (`git checkout -b feature/short-name`).
2. Keep the change focused. One calculation group, one fix, or one
   feature per pull request.
3. Add or update tests. A new calculation needs a check against a
   textbook problem or a hand-computed case, and the test should say
   which problem pins the behavior down.
4. Run `pytest -q` and make sure it is green.

## Conventions

- Bearings are degrees clockwise from true north; wind direction is
  the direction the wind comes FROM.
- Headwind is positive against the course; crosswind is positive
  from the right. Do not flip a sign convention without updating
  every test and doc that states it.
- Inputs that cannot produce a meaningful answer raise ValueError
  (a crosswind stronger than TAS, a zero ground speed, a negative
  fuel quantity) instead of returning a guess.
