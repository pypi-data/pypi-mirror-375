# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

from argparse import ArgumentParser

# ---------------------------
# Third-party library imports
# ----------------------------

from lica.validators import vdir


def name() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        help="photometer name",
    )
    return parser


def logdir() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ld",
        "--log-dir",
        type=vdir,
        required=True,
        help="Log files directory",
    )
    return parser


def ofile() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-of",
        "--output-file",
        type=str,
        required=True,
        help="Output file with photometer names",
    )
    return parser

def batch() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-bs",
        "--batch-size",
        type=int,
        default=30,
        help="Batch size when analyzing log files",
    )
    return parser

def range() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-st",
        "--start",
        type=int,
        default=None,
        metavar="<YYYYMMDD>",
        help="Earliest log file date (defaults to earliest available)",
    )
    parser.add_argument(
        "-en",
        "--end",
        type=int,
        default=None,
        metavar="<YYYYMMDD>",
        help="Latest log file date (defaults to latest available)",
    )
    return parser

def reg() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-re",
        "--registration",
        default=False,
        action="store_true",
        help="Generate registry SQL statements",
    )
    return parser