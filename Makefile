

test:
	uv run python -m pytest tests -vs



cov:
	uv run python -m pytest --cov=incognito --doctest-modules incognito tests
