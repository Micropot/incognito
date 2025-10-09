

test:
	uv run python -m pytest tests -vs



cov:
	uv run python -m pytest --cov=incognito_anonymizer --doctest-modules incognito_anonymizer tests
