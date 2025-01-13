

test:
	 python -m pytest tests -vs

cov:
	python -m pytest --cov=incognito --doctest-modules incognito tests
