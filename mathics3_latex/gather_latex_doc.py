#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Does 2 things which can are necessary for producing LaTeX documentation
that produces the Mathics3 PDF.

1. Extracts tests and runs them from static mdoc files and docstrings from
   Mathics3 built-in functions
2. Creates/updates internal documentation data
"""

import os
import os.path as osp
import pickle

from typing import Final
from mathics.core.load_builtin import import_and_load_builtins
from mathics.docpipeline import (
    DocTestPipeline,
    build_arg_parser,
    test_all,
    test_chapters,
    test_sections,
)

def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


# Global variables
logfile = None

#
# Input doctest PCL FILE. This contains just the
# tests and test results.
#
# This information is stitched in with information comes from
# docstrings that are loaded from load Mathics3 builtins and external modules.

# FIXME: DRY with doc2latex
ROOT_DATA_DIR: Final[str] = get_srcdir()

# PCL Output location information
DOC_PCL_DIR: Final[str]  = os.environ.get("DOC_PCL_DIR", ROOT_DATA_DIR)
DOC_PCL_FILE: Final[str] = os.environ.get("DOC_PCL_FILE",
                                          osp.join(DOC_PCL_DIR, "doctest_latex_data.pcl"))

# This information is stitched in with information comes from
# docstrings that are loaded from load Mathics3 builtins and external modules.

def main():
    args = build_arg_parser()

    doctest_pipeline = DocTestPipeline(
        args, output_format="latex",
        data_path=DOC_PCL_FILE
    )
    test_status = doctest_pipeline.status

    if args.sections:
        include_sections = set(args.sections.split(","))
        exclude_subsections = set(args.exclude.split(","))
        test_sections(
            doctest_pipeline, include_sections, exclude_subsections, output_format="latex"
        )
    elif args.chapters:
        include_chapters = set(args.chapters.split(","))
        exclude_sections = set(args.exclude.split(","))
        test_chapters(
            doctest_pipeline, include_chapters, exclude_sections, output_format="latex"
        )
    else:
        test_all(doctest_pipeline, output_format=None)
        # test_all(doctest_pipeline, output_format="latex")

    if doctest_pipeline.logfile:
        doctest_pipeline.logfile.close()

    if test_status.failed == 0:
        print("\nOK")
    else:
        print("\nFAILED")
        # sys.exit(1)  # Travis-CI knows the tests have failed
    save_doctest_data(doctest_pipeline)


def save_doctest_data(doctest_pipeline: DocTestPipeline):
    """
    Save doctest tests and test results to a Python PCL file.

    ``output_data`` is a dictionary of test results. The key is a tuple
    of:
    * Part name,
    * Chapter name,
    * [Guide Section name],
    * Section name,
    * Subsection name,
    * test number
    and the value is a dictionary of a Result.getdata() dictionary.
    """
    output_data: dict[tuple, dict] = doctest_pipeline.output_data

    if len(output_data) == 0:
        doctest_pipeline.print_and_log("output data is empty")
        return
    doctest_pipeline.print_and_log(f"saving {len(output_data)} entries")
    doctest_latex_data_path = doctest_pipeline.parameters.data_path
    doctest_pipeline.print_and_log(
        f"Writing internal document data to {doctest_latex_data_path}"
    )
    breakpoint()
    with open(doctest_latex_data_path, "wb") as output_file:
        pickle.dump(output_data, output_file, 4)

if __name__ == "__main__":
    import_and_load_builtins()
    main()
