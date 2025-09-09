# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import os
import re
import glob
import logging
import datetime  # necessary for eval
from datetime import timedelta
from itertools import batched
from collections import defaultdict
import functools

from typing import Optional, List, Dict, Mapping, Tuple, Any

# -------------------
# Third party imports
# -------------------

from sqlalchemy import select, func

from tessdbdao.noasync import NameMapping
from zptessdao.noasync import SummaryView


# --------------
# local imports
# -------------

from .dao import TdbSession, ZptSession

# ----------------
# Global variables
# ----------------

package = ".".join(__name__.split(".")[:-1])
log = logging.getLogger(__name__.split(".")[-1])


def round_datetime(tstamp: datetime.datetime) -> Tuple[datetime.datetime, int, int]:
    """Round a timestamp to the nearest minute"""
    tstamp = (tstamp + timedelta(seconds=0.5)).replace(microsecond=0)
    date_id = tstamp.year * 10000 + tstamp.month * 100 + tstamp.day
    time_id = tstamp.hour * 10000 + tstamp.minute * 100 + tstamp.second
    return tstamp, date_id, time_id


def is_tess4c(readings: Mapping[str, Any]) -> bool:
    return "freq4" in readings


def windowed3(start: Optional[int], end: Optional[int], path: str) -> bool:
    path = os.path.basename(path)
    file_start = f"tessdb.log-{start}"
    file_end = f"tessdb.log-{end}"
    if start is not None and path < file_start:
        return False
    if end is not None and path > file_end:
        return False
    return True


def filtered_log_files(log_dir: str, start: Optional[int], end: Optional[int]) -> List[str]:
    template = os.path.join(log_dir, "tessdb.log-????????")
    files = glob.iglob(template)
    windowed = functools.partial(windowed3, start, end)
    return sorted(filter(windowed, files), reverse=True)


def context(registration_needed: bool, readings: List[Dict[str, Any]]) -> Dict[str, Any]:
    ctx = dict()
    ctx["registration_needed"] = registration_needed
    ctx["model"] = "TESS4C" if is_tess4c(readings[0]) else "TESS-W"
    ctx["readings"] = list(enumerate(batched(readings, 10000), start=1))
    return ctx


def collect_readings_for(
    name: str, log_dir: str, start: int, end: int, batch_size: int
) -> List[Dict[str, Any]]:
    pattern = (
        rf"(.{{24}}) \[dbase#warn\] TESSReadings.update\(\): No TESS {name} registered ! => (.+)"
    )
    pattern = re.compile(pattern)
    files = filtered_log_files(log_dir, start, end)
    readings = list()
    for i, batch in enumerate(batched(files, batch_size), start=1):
        batched_readings = list()
        batched_lengths = list()
        N = len(batch)
        for j, path in enumerate(batch, start=1):
            with open(path, "r") as fd:
                batched_lengths.append(len(batched_readings))
                log.info(
                    "Analyzing batch #%d (%02d/%02d), %s for %s readings, %d found",
                    i,
                    j,
                    N,
                    path,
                    name,
                    len(batched_readings),
                )
                for line in fd.readlines():
                    matchobj = pattern.search(line)
                    if matchobj:
                        reading = eval(matchobj.groups()[1])
                        batched_readings.append(reading)
        readings.extend(batched_readings)
        if all([batched_lengths[0] == n for n in batched_lengths]):
            log.warn("Stopping analysis in batch #%d . No activity was found.")
            break
    log.info("Sorting %s readings by timestamp", name)
    return sorted(readings, key=lambda x: x["tstamp"])


def already_registered(name: str) -> bool:
    with TdbSession() as session:
        query = select(func.count("*")).select_from(NameMapping).where(NameMapping.name == name)
        N = session.scalars(query).one()
        log.info("Found %d entries for %s", N, name)
        if N > 0:
            query = select(NameMapping).where(NameMapping.name == name)
            result_set = session.scalars(query)
            for result in result_set:
                log.info(result)
    return N > 0


def find_photometer_details(name: str) -> Tuple[str, float]:
    with ZptSession() as session:
        query = select(SummaryView.mac, SummaryView.zero_point).where(SummaryView.name == name)
        result_set = session.execute(query)
    return result_set


def collect_references(
    log_dir: str, start: int, end: int
) -> List[Tuple[str, str, int, str, str, bool, Any]]:
    pattern = (
        r"(.{24}) \[dbase#warn\] TESSReadings.update\(\): No TESS (stars\d{1,8}) registered ! => "
    )
    pattern = re.compile(pattern)
    names = set()
    counts = dict()
    files_per_name = defaultdict(set)
    files = filtered_log_files(log_dir, start, end)
    for path in files:
        with open(path, "r") as fd:
            log.info("Analyzing %s, %d photometers found so far", path, len(names))
            for line in reversed(fd.readlines()):
                matchobj = pattern.search(line)
                if matchobj:
                    name = matchobj.groups()[1]
                    names.add(name)
                    counts[name] = counts.get(name, 0) + 1
                    files_per_name[name].add(os.path.basename(path))
    summary_info = [
        (
            name,
            f"{counts[name]:8d}",
            sorted(files_per_name[name])[0],
            sorted(files_per_name[name])[-1],
            already_registered(name),
            tuple(find_photometer_details(name)),
        )
        for name  in names
    ]
    return sorted(summary_info, reverse=True, key=lambda x: x[3])

