#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Does 2 things which can are necessary for producing LaTeX documentation
that produces the Mathics3 PDF.

1. Extracts tests and runs them from static mdoc files and docstrings from
   Mathics3 built-in functions
2. Creates/updates internal documentation data
"""

import sys

from mathics.core.load_builtin import import_and_load_builtins
from mathics.docpipeline import (
    DocTestPipeline,
    build_arg_parser,
    test_all,
    test_chapters,
    test_sections,
)

# Global variables
logfile = None

# Input doctest PCL FILE. This contains just the
# tests and test results.
#
# This information is stitched in with information comes from
# docstrings that are loaded from load Mathics3 builtins and external modules.

def main():
    args = build_arg_parser()

    test_pipeline = DocTestPipeline(
        args, output_format="latex",
    )
    test_status = test_pipeline.status

    if args.sections:
        include_sections = set(args.sections.split(","))
        exclude_subsections = set(args.exclude.split(","))
        test_sections(
            test_pipeline, include_sections, exclude_subsections, output_format="latex"
        )
    elif args.chapters:
        include_chapters = set(args.chapters.split(","))
        exclude_sections = set(args.exclude.split(","))
        test_chapters(
            test_pipeline, include_chapters, exclude_sections, output_format="latex"
        )
    else:
        test_all(test_pipeline, output_format="latex")

    if test_pipeline.logfile:
        test_pipeline.logfile.close()

    if test_status.failed == 0:
        print("\nOK")
    else:
        print("\nFAILED")
        sys.exit(1)  # Travis-CI knows the tests have failed


if __name__ == "__main__":
    import_and_load_builtins()
    main()
