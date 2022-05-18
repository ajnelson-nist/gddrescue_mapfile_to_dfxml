#!/usr/bin/make -f

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

SHELL := /bin/bash

PYTHON3 ?= python3

all: \
  .venv-pre-commit/var/.pre-commit-built.log

.PHONY: \
  check-docs \
  docs \
  docs-figs \
  docs-tests

.git_submodule_init.done.log: \
  .gitmodules
	git submodule init deps/dfxml
	git submodule update deps/dfxml
	$(MAKE) \
	  --directory deps/dfxml \
	  .git_submodule_init.done.log
	touch $@

.venv.done.log: \
  .git_submodule_init.done.log \
  setup.cfg
	rm -rf \
	  venv
	$(PYTHON3) -m venv \
	  venv
	source venv/bin/activate \
	  && pip install \
	    --upgrade \
	    pip \
	    setuptools \
	    wheel
	source venv/bin/activate \
	  && pip install \
	    deps/dfxml
	source venv/bin/activate \
	  && pip install \
	    --editable \
	    .
	touch $@

# This virtual environment is meant to be built once and then persist, even through 'make clean'.
# If a recipe is written to remove this flag file, it should first run `pre-commit uninstall`.
.venv-pre-commit/var/.pre-commit-built.log:
	rm -rf .venv-pre-commit
	test -r .pre-commit-config.yaml \
	  || (echo "ERROR:Makefile:pre-commit is expected to install for this repository, but .pre-commit-config.yaml does not seem to exist." >&2 ; exit 1)
	$(PYTHON3) -m venv \
	  .venv-pre-commit
	source .venv-pre-commit/bin/activate \
	  && pip install \
	    --upgrade \
	    pip \
	    setuptools \
	    wheel
	source .venv-pre-commit/bin/activate \
	  && pip install \
	    pre-commit
	source .venv-pre-commit/bin/activate \
	  && pre-commit install
	mkdir -p \
	  .venv-pre-commit/var
	touch $@

check: \
  .venv.done.log \
  .venv-pre-commit/var/.pre-commit-built.log
	$(MAKE) \
	  --directory tests \
	  check

check-docs: \
  check-docs-figs \
  check-docs-tests

check-docs-figs:
	$(MAKE) \
	  --directory figs \
	  check

check-docs-tests: \
  .venv.done.log
	$(MAKE) \
	  --directory tests \
	  check-docs

clean:
	@rm -rf venv
	@rm -f .*.done.log
	@$(MAKE) --directory figs clean
	@$(MAKE) --directory tests clean

docs: \
  docs-figs \
  docs-tests

docs-figs:
	$(MAKE) \
	  --directory figs

docs-tests:
	$(MAKE) \
	  --directory tests \
	  docs

download: \
  .venv.done.log
