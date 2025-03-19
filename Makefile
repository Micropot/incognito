

test:
	uv run python -m pytest tests -v



cov:
	uv run python -m pytest --cov=incognito --doctest-modules incognito tests
