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

from pydantic import ValidationError

from lica.cli import execute
from lica.sqlalchemy import sqa_logging

from tessdbdao import RegisterState
from tessdbapi.model import PhotometerInfo
from tessdbapi.noasync.photometer.register import photometer_register

# --------------
# local imports
# -------------

from ..._version import __version__
from .. import parser as prs
from .dao import engine, Session

# ----------------
# Global variables
# ----------------

package = ".".join(__name__.split(".")[:-1])
log = logging.getLogger(__name__.split(".")[-1])

# ================
# MAIN ENTRY POINT
# ================


def cli_photom_register(args: Namespace) -> None:
    try:
        candidate = PhotometerInfo(
            name=args.name,
            mac_address=args.mac_address,
            model=args.model,
            firmware=args.firmware,
            authorised=args.authorise,
            registered=RegisterState.MANUAL,
            zp1=args.zp1,
            filter1=args.filter1,
            offset1=args.offset1,
            zp2=args.zp2,
            filter2=args.filter2,
            offset2=args.offset2,
            zp3=args.zp3,
            filter3=args.filter3,
            offset3=args.offset3,
            zp4=args.zp4,
            filter4=args.filter4,
            offset4=args.offset4,
            tstamp=args.timestamp,
        )
    except ValidationError as e:
        log.error("Validation Error")
        log.info(e)
    else:
        with Session() as session:
            with session.begin():
                log.info("Registering photometer: %s", dict(candidate))
                photometer_register(
                    session,
                    candidate=candidate,
                    place=args.place,
                    observer_name=args.observer,
                    observer_type=args.type,
                    dry_run=args.dry_run,
                )


def add_args(parser: ArgumentParser) -> None:
    subparser = parser.add_subparsers(dest="command", required=True)
    p = subparser.add_parser(
        "register",
        parents=[prs.tstamp(), prs.photom(), prs.location(), prs.observer(), prs.dry()],
        help="Register a new photometer",
    )
    p.set_defaults(func=cli_photom_register)


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
