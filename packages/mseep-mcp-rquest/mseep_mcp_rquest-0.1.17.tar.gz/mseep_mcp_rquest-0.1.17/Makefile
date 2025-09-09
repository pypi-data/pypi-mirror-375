.PHONY: clean lint build install dev

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .ruff_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +

lint:
	ruff check .
	black --check .

format:
	ruff check --fix .
	black .

build:
	python -m build

install:
	uv pip install .

dev:
	uv pip install -e ".[dev]"

# publish to testpypi： first clean dist folder, then build and publish
publish-test:
	rm -rf dist
	python -m build
	python -m twine upload --repository testpypi dist/*

# publish to pypi
publish:
	rm -rf dist
	python -m build
	python -m twine upload dist/*

bump-version-patch:
	uv tool install bump-my-version
	bump-my-version bump patch

bump-version-minor:
	uv tool install bump-my-version
	bump-my-version bump minor

bump-version-major:
	uv tool install bump-my-version
	bump-my-version bump major
