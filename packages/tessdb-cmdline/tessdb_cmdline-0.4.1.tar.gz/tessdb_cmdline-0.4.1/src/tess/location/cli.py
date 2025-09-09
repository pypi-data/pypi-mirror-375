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
# -------------------

from lica.cli import execute
from lica.sqlalchemy import sqa_logging
from tessdbapi.model import LocationInfo 
from tessdbapi.noasync.location import location_create, location_update

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


def cli_location_create(args: Namespace) -> None:
    candidate = LocationInfo(
        longitude=args.longitude,
        latitude=args.latitude,
        height=args.height,
        place=args.place,
        town=args.town,
        sub_region=args.sub_region,
        region=args.region,
        country=args.country,
        timezone=args.timezone,
    )
    with Session() as session:
        with session.begin():
            log.info("Registering location: %s", dict(candidate))
            location_create(
                session,
                candidate,
                args.dry_run,
            )


def cli_location_update(args: Namespace) -> None:
    candidate = LocationInfo(
        longitude=args.longitude,
        latitude=args.latitude,
        height=args.height,
        place=args.place,
        town=args.town,
        sub_region=args.sub_region,
        region=args.region,
        country=args.country,
        timezone=args.timezone,
    )
    with Session() as session:
        with session.begin():
            log.info("Updating location: %s", dict(candidate))
            location_update(
                session,
                candidate,
                args.dry_run,
            )


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "create",
        parents=[prs.coords(), prs.place(), prs.nominatim(), prs.dry()],
        help="Create new location",
    )
    p.set_defaults(func=cli_location_create)
    p = subparser.add_parser(
        "update",
        parents=[prs.coords(), prs.place(), prs.nominatim(), prs.dry()],
        help="Update existing location",
    )
    p.set_defaults(func=cli_location_update)


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
        description="TESSDB Location tool",
    )
