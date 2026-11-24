.PHONY: help

PYTHON=$(shell which python)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install-develop: ## Activate the development install
	$(PYTHON) setup.py develop

uninstall-develop: ## De-activate the development install
	$(PYTHON) setup.py develop --uninstall

install: ## Install the package
	$(PYTHON) setup.py install

check: ## Run all tests (remember to git submodule update --init)
	$(PYTHON) setup.py test
