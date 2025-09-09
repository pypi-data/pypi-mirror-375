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

from tessdbdao import ObserverType


def dry() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-dr",
        "--dry-run",
        default=False,
        action="store_true",
        help="Dry run, do not update database",
    )
    return parser

def fix() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-fx",
        "--fix",
        default=False,
        action="store_true",
        help="Fix latest entry",
    )
    return parser


def observer() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "-ty",
        "--type",
        type=ObserverType,
        default=None,
        help="Observer Type (person, organization)",
    )
    parser.add_argument(
        "-na",
        "--name",
        type=str,
        default=None,
        help="Observer name",
    )
    parser.add_argument(
        "-af",
        "--affiliation",
        type=str,
        default=None,
        help="Federal state, comunidad autonoma",
    )
    parser.add_argument(
        "-ac",
        "--acronym",
        type=str,
        default=None,
        help="Affiliation / Organization acronym",
    )
    parser.add_argument(
        "-we",
        "--website-url",
        type=str,
        default=None,
        help="Web site URL",
    )
    parser.add_argument(
        "-em",
        "--email",
        type=str,
        default=None,
        help="Contact email",
    )
    return parser
