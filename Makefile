# The default target of this Makefile is:
all:: build

build: clean
	python -m build
	python -m twine check dist/*
.PHONY: build

install-build:
	python -m pip install -r .meta/requirements-build.txt
.PHONY: install-build

install:
	python -m pip install .
.PHONY: install

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
	flake8
.PHONY: lint

clean:
	git clean -fxd
.PHONY: clean
