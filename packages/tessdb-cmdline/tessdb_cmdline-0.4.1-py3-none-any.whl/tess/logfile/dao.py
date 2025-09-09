from lica.sqlalchemy.noasync.dbase import create_engine_sessionclass

engine_tdb, TdbSession = create_engine_sessionclass(env_var="TESSDB_URL", tag="tessdb")
engine_zpt, ZptSession = create_engine_sessionclass(env_var="ZPTESS_URL", tag="zptess")

__all__ = ["engine_tdb", "TdbSession", "engine_zpt", "ZptSession"]
