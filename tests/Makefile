.PHONY: help test

.DEFAULT_GOAL := help

help:
	@grep ": ##" Makefile | grep -v grep | tr -d '#'

test: ## Run the test suite
	cd .. && python -m pytest tests
