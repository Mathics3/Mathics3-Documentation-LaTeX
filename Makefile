# A GNU Makefile to run various tasks - compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= admin-tools/git2cl
PYTHON ?= python3
PIP ?= pip3
BASH ?= bash
RM  ?= rm
PYTEST_OPTIONS ?=
DOCTEST_OPTIONS ?=

# Variable indicating Mathics3 Modules you have available on your system, in latex2doc option format
MATHICS3_MODULE_OPTION ?= --load-module pymathics.graph,pymathics.natlang

.PHONY: \
   all \
   ChangeLog-without-corrections \
   build \
   check \
   clean \
   clean-cache \
   develop \
   develop-full \
   dist \
   doc \
   doctest \
   doctest-data \
   latexdoc \
   pytest \
   pytest-x \
   rmChangeLog \
   test \
   texdoc

MATHICS3_SANDBOX	?=
ifeq ($(OS),Windows_NT)
	MATHICS3_SANDBOX = t
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Darwin)
		MATHICS3_SANDBOX = t
	endif
endif

#: Default target - same as "develop"
all: develop

# Note that we need ./setup.py develop
# because pip install doesn't handle
# INSTALL_REQUIRES properly
#: Set up to run from the source tree
develop:
	$(PIP) install --no-build-isolation -e .[dev]

# See note above on ./setup.py
#: Set up to run from the source tree with full dependencies
develop-full:
	$(PIP) install --no-build-isolation -e .[dev,full]

#: Make distribution: wheels, eggs, tarball
dist:
	./admin-tools/make-dist.sh

#: Remove derived files
clean:
	for dir in mathics3_latex ; do \
	   ($(MAKE) -C "$$dir" clean); \
	done; \
	rm -rf build || true

#: Run pytest tests. Use environment variable "PYTEST_OPTIONS" for pytest options
pytest:
	$(PYTHON) -m pytest $(PYTEST_OPTIONS) $(PYTEST_WORKERS) test

#: Run pytest tests stopping at first failure.
pytest-x :
	PYTEST_OPTIONS="-x" $(MAKE) pytest

#: Create LaTeX doctest test data and test results that is used to build LaTeX PDF
# For LaTeX docs we assume Unicode
latex-doctest-data: mathics/builtin/*.py mathics/doc/documentation/*.mdoc mathics/doc/documentation/images/*
	MATHICS_CHARACTER_ENCODING="UTF-8" $(PYTHON) mathics3_lastex/gather_latex_doc.py --output $(MATHICS3_MODULE_OPTION) --keep-going

#: Make Mathics3 PDF manual via Asymptote and LaTeX
latexdoc texdoc doc:
	$(MAKE) -C mathics3_latex doc --keep-going

#: Remove ChangeLog
rmChangeLog:
	$(RM) ChangeLog || true

#: Create ChangeLog from version control without corrections
ChangeLog-without-corrections:
	git log --pretty --numstat --summary | $(GIT2CL) >ChangeLog

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog ChangeLog-without-corrections
	patch ChangeLog < ChangeLog-spell-corrected.diff
