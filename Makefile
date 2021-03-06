lint:
	python -m isort -rc -y .
	python -m black .
	python -m pylama .
	python -m pydocstyle .
	python -m mypy nornir_scrapli/

cov:
	python -m pytest \
	--cov=nornir_scrapli \
	--cov-report html \
	--cov-report term \
	tests/

test:
	python -m pytest tests/

.PHONY: docs
docs:
	rm -rf docs/nornir_scrapli
	python -m pdoc \
	--html \
	--output-dir docs \
	nornir_scrapli \
	--force
