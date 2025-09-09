# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging

from argparse import ArgumentParser, Namespace

# -------------------
# Third party imports
# -------------------º

from lica.cli import execute
from lica.sqlalchemy import sqa_logging

from tessdbapi.model import ObserverInfo 
from tessdbapi.noasync.observer import observer_create, observer_update

# --------------
# local imports
# -------------

from .._version import __version__
from . import parser as prs


from .dao import engine, Session

# ----------------
# Global variables
# ----------------

log = logging.getLogger(__name__.split(".")[-1])

# ================
# MAIN ENTRY POINT
# ================


def cli_observer_create(args: Namespace) -> None:
    candidate = ObserverInfo(
        type=args.type,
        name=args.name,
        affiliation=args.affiliation,
        acronym=args.acronym,
        website_url=args.website_url,
        email=args.email,
    )
    with Session() as session:
        with session.begin():
            log.info("Registering observer: %s", dict(candidate))
            observer_create(
                session,
                candidate,
                args.dry_run,
            )


def cli_observer_update(args: Namespace) -> None:
    candidate = ObserverInfo(
        type=args.type,
        name=args.name,
        affiliation=args.affiliation,
        acronym=args.acronym,
        website_url=args.website_url,
        email=args.email,
    )
    with Session() as session:
        with session.begin():
            log.info("Updating observer: %s", dict(candidate))
            observer_update(
                session,
                candidate,
                args.fix,
                args.dry_run,
            )


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "create",
        parents=[prs.observer(), prs.dry()],
        help="Create new observer",
    )
    p.set_defaults(func=cli_observer_create)
    p = subparser.add_parser(
        "update",
        parents=[prs.observer(), prs.dry(), prs.fix()],
        help="Update existing observer",
    )
    p.set_defaults(func=cli_observer_update)


def cli_main(args: Namespace) -> None:
    sqa_logging(args)
    args.func(args)
    engine.dispose()


def main():
    execute(
        main_func=cli_main,
        add_args_func=add_args,
        name=__name__,
        version=__version__,
        description="TESSDB Observer tool",
    )
