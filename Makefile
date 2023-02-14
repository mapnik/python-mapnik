.PHONY: help test test_verbose tdd test_failed

TEST := nosetests --logging-clear-handlers --with-id

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  test              to run all the test suite"
	@echo "  test_verbose      to run all the test suite without output capture"
	@echo "  tdd               to run all the test suite, but stop on the first error"
	@echo "  test_failed       to rerun the failed tests from the previous run"

test:
	$(TEST) $(filter-out $@,$(MAKECMDGOALS))

test_verbose:
	$(TEST) -s $(filter-out $@,$(MAKECMDGOALS))

tdd:
	$(TEST) --stop --pdb $(filter-out $@,$(MAKECMDGOALS))

test_failed:
	python setup.py nosetests --logging-clear-handlers --with-id -vv --failed $(ARGS)

$(phony %):
	@:
