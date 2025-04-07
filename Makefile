# The default target of this Makefile is:
all:: build

build: clean
	python -m build
	python -m twine check dist/*
.PHONY: build

install:
	python -m pip install .
.PHONY: install

install-build:
	python -m pip install -e '.[build]'
.PHONY: install-build

install-devtools:
	python -m pip install -e '.[lint]'
	pre-commit install
.PHONY: install-devtools

install-maintainer: install-build install-devtools
.PHONY: install-maintainer

install-dev:
	python -m pip install -e .
.PHONY: install-dev

dist: build
	python -m twine upload dist/*
.PHONY: dist

dist-test: build
	python -m twine upload --repository testpypi dist/*
.PHONY: dist-test

lint:
	ruff check
.PHONY: lint

clean:
	git clean -fxd
.PHONY: clean
