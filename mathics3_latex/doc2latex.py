#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Writes a LaTeX file containing the entire User Manual.

The information for this comes from:

* the docstrings from loading in Mathics3 core (mathics)

* the docstrings from loading Mathics3 modules that have been specified
  on the command line

* doctest tests and test result that have been stored in a Python
  Pickle file, from a previous docpipeline.py run.  Ideally the
  Mathics3 Modules given to docpipeline.py are the same as
  given on the command line for this program
"""

import os
import os.path as osp
import subprocess
import sys
from argparse import ArgumentParser
from typing import Final, Optional

from mpmath import __version__ as mpmathVersion
from numpy import __version__ as NumPyVersion
from PIL import __version__ as PILVersion
from sympy import __version__ as SymPyVersion

import mathics
from mathics import __version__, version_info, version_string
from mathics.core.definitions import Definitions
from mathics.core.load_builtin import import_and_load_builtins
from mathics.doc.latex_doc import LaTeXMathicsDocumentation
from mathics.doc.utils import load_doctest_data, open_ensure_dir
from mathics.eval.pymathics import PyMathicsLoadException, eval_LoadModule


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


# Global variables
logfile = None

ROOT_DATA_DIR: Final[str] = get_srcdir()

# LaTeX Output location information
DOC_DATA_DIR: Final[str] = os.environ.get("DOC_LATEX_DIR", ROOT_DATA_DIR)
DOC_LATEX_FILE: Final[str] = os.environ.get(
    "DOC_LATEX_FILE", osp.join(DOC_DATA_DIR, "documentation.tex"))

# Input PCL file
DOC_PCL_FILE: Final[str] = os.environ.get("DOC_PCL_FILE",
                                          osp.join(ROOT_DATA_DIR, "doctest_latex_data.pcl"))



def read_doctest_data(
    quiet=False, doctest_latex_data_path: str = ""
) -> Optional[dict[tuple, dict]]:
    """
    Read doctest information from PCL file and return this.
    This is a wrapper around laod_doctest_data().
    """
    if not quiet:
        print(f"Extracting internal doctest data for {version_string}")
    try:
        return load_doctest_data(doctest_latex_data_path)
    except KeyboardInterrupt:
        print("\nAborted.\n")
        return None


def get_versions():
    def try_cmd(cmd_list: tuple, stdout_or_stderr: str) -> str:
        status = subprocess.run(cmd_list, capture_output=True)
        if status.returncode == 0:
            out = getattr(status, stdout_or_stderr)
            return out.decode("utf-8").split("\n")[0]
        else:
            return "Unknown"

    versions = {
        "MathicsCoreVersion": __version__,
        "PythonVersion": sys.version,
        "NumPyVersion": NumPyVersion,
        "SymPyVersion": SymPyVersion,
        "mpmathVersion": mpmathVersion,
        "PILVersion": PILVersion,
    }

    for name, cmd, field in (
        ["AsymptoteVersion", ("asy", "--version"), "stderr"],
        ["XeTeXVersion", ("xetex", "--version"), "stdout"],
        ["GhostscriptVersion", ("gs", "--version"), "stdout"],
    ):
        versions[name] = try_cmd(cmd, field)
    versions.update(version_info)
    return versions


def write_latex(
    doc_data, quiet=False, filter_parts=None, filter_chapters=None, filter_sections=None
):
    documentation = LaTeXMathicsDocumentation()
    if not quiet:
        print(f"Writing LaTeX document to {DOC_LATEX_FILE}")
    with open_ensure_dir(DOC_LATEX_FILE, "wb") as doc:
        content = documentation.latex(
            doc_data,
            quiet=quiet,
            filter_parts=filter_parts,
            filter_chapters=filter_chapters,
            filter_sections=filter_sections,
        )
        content = content.encode("utf-8")
        doc.write(content)
    DOC_VERSION_FILE = osp.join(DOC_DATA_DIR, "version-info.tex")
    if not quiet:
        print(f"Writing Mathics3 Core Version Information to {DOC_VERSION_FILE}")
    with open(DOC_VERSION_FILE, "w") as doc:
        doc.write("%% Mathics3 core version number created via doc2latex.py\n\n")
        for name, version_str in get_versions().items():
            doc.write("""\\newcommand{\\%s}{%s}\n""" % (name, version_str))


def main():
    parser = ArgumentParser(description="Mathics3 test suite.", add_help=False)
    parser.add_argument(
        "--help", "-h", help="show this help message and exit", action="help"
    )
    parser.add_argument(
        "--version", "-v", action="version", version="%(prog)s " + mathics.__version__
    )
    parser.add_argument(
        "--chapters",
        "-c",
        dest="chapters",
        metavar="CHAPTER",
        help="only test CHAPTER(s). "
        "You can list multiple chapters by adding a comma (and no space) in between "
        "chapter names.",
    )
    parser.add_argument(
        "--sections",
        "-s",
        dest="sections",
        metavar="SECTION",
        help="only test SECTION(s). "
        "You can list multiple chapters by adding a comma (and no space) in between "
        "chapter names.",
    )
    parser.add_argument(
        "--load-module",
        "-l",
        dest="pymathics",
        metavar="MATHIC3-MODULES",
        help="load Mathics3 module MATHICS3-MODULES. "
        "You can list multiple Mathics3 Modules by adding a comma (and no space) in between "
        "module names.",
    )
    parser.add_argument(
        "--parts",
        "-p",
        dest="parts",
        metavar="PART",
        help="only test PART(s). "
        "You can list multiple parts by adding a comma (and no space) in between part names.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        dest="quiet",
        action="store_true",
        help="Don't show formatting progress tests",
    )
    args = parser.parse_args()

    # LoadModule Mathics3 modules to pull in modules, and
    # their docstrings

    import_and_load_builtins()

    if args.pymathics:
        definitions = Definitions(add_builtin=True)
        for module_name in args.pymathics.split(","):
            try:
                eval_LoadModule(module_name, definitions)
            except PyMathicsLoadException:
                print(f"Python module {module_name} is not a Mathics3 module.")

            except Exception as e:
                print(f"Python import errors with: {e}.")
            else:
                print(f"Mathics3 Module {module_name} loaded")

    doctest_data = read_doctest_data(
        quiet=args.quiet, doctest_latex_data_path=DOC_PCL_FILE
    )
    write_latex(
        doctest_data,
        quiet=args.quiet,
        filter_parts=args.parts,
        filter_chapters=args.chapters,
        filter_sections=args.sections,
    )


if __name__ == "__main__":
    main()
