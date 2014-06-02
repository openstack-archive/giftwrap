all: test

deps:
	@echo "--> Installing dependencies"
	@pip install tox

test: deps
	@echo "--> Running tests"
	@tox

.PHONY: all deps test
