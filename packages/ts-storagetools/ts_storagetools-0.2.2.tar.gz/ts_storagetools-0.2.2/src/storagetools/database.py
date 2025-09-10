#
# This file is part of storagetools.
#
# Copyright (c) 2025 Mauritz Mälzer
#
# BSD-3-Clause License
#

"""Metadata database setup.

This module provides classes and functions for working with a SQLite metadata database.

It includes classes for working an in-memory or file-based representation of
the SQLite database, as well as functions for initializing the database,
creating tables and views, and adding property columns to the database.
"""

import logging
import os
import sqlite3
import uuid

from storagetools.context import Context
from typeguard import typechecked

DB_SCHEMA_FILE = "database_schema.sql"
DB_LOOKUP_VIEW_FILE = "database_lookup_view.sql"

log = logging.getLogger(__name__)


class Database:
    """
    A class for working with a SQLite (sqlite3) database.

    The class provides a context manager for working with the database,
    and provides methods for executing SQL queries.

    Note on UUIDs:
    UUIDs are not natively supported by SQLite. String representation requires
    32-36 bytes storage depending on notation, whereas a binary representation
    only 16 bytes. GUID columns are thus registered as 'memoryview' to keep
    metadata databases smaller.
    """

    @typechecked
    def __init__(self, ctx: Context) -> None:
        sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes=b))
        sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes))
        self.con = sqlite3.connect(
            f"file:{ctx.paths['database']}",
            detect_types=sqlite3.PARSE_DECLTYPES,
            uri=True,
        )
        self.cur = self.con.cursor()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, ext_type, exc_value, traceback) -> None:
        """
        Type hints missing here, also unused parameters.
        To be checked how this is implemented the deeper backend for proper resolution.
        """
        self.cur.close()
        if isinstance(exc_value, Exception):
            self.con.rollback()
        else:
            self.con.commit()
        self.con.close()


@typechecked
def initialize(ctx: Context) -> None:
    """
    Initializes the database by creating tables, adding property columns,
    and creating views.

    Args:
        ctx: The context object containing the paths to the database.
    """
    create_tables(ctx)
    add_property_columns(ctx)
    create_views_from_file(ctx)
    create_cc_repr_view(ctx)
    create_cc_view(ctx)
    create_sc_repr_view(ctx)


@typechecked
def create_tables(ctx: Context) -> None:
    """
    Creates tables in the database by executing SQL commands from a file.

    Args:
        ctx: The context object containing the paths to the database.
    """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(module_dir, "sql_scripts", DB_SCHEMA_FILE)
    with open(file_path, "r") as f:
        sql_script = f.read()
    with Database(ctx) as db:
        db.cur.executescript(sql_script)
    log.info("Empty tables created")


@typechecked
def create_views_from_file(ctx: Context) -> None:
    """
    Creates views in the database by executing SQL commands from a file.

    Args:
        ctx: The context object containing the paths to the database.
    """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    file_paths = []
    file_paths.append(os.path.join(module_dir, "sql_scripts", DB_LOOKUP_VIEW_FILE))
    for file_path in file_paths:
        with open(file_path, "r") as f:
            sql_script = f.read()
        with Database(ctx) as db:
            db.cur.executescript(sql_script)
        log.info(f"created view from {file_path}")


@typechecked
def create_cc_repr_view(ctx: Context) -> None:
    """
    Creates a view for all representations attached to a channel capture.

    Some scenarios make use of reprs that are attached to sensorcaptures
    directly (e.g. channel averages) or not to anything at all. Those reprs
    will not be viewable in the cc_repr_view. Dealing with partly overlapping
    columns and merging them into one view got so complicated that it was
    overthrown as idea.

    See also: create_sc_repr_view(ctx)

    Args:
        ctx: The context object containing the property columns for the experiment, sensor, and channel.
    """
    tmp = []
    for _, items in ctx.channel_properties.items():
        for item in items:  # type: ignore
            tmp.append(item)
    channel_properties = ", ".join(
        f'channel."{item}" as channel_{item}' for item in tmp
    )
    log.info(channel_properties)

    tmp = []
    for _, items in ctx.sensor_properties.items():
        for item in items:  # type: ignore
            tmp.append(item)
    sensor_properties = ", ".join(f'sensor."{item}" as sensor_{item}' for item in tmp)
    log.info(sensor_properties)

    tmp = []
    for _, items in ctx.experiment_properties.items():
        for item in items:  # type: ignore
            tmp.append(item)
    experiment_properties = ", ".join(
        f'experiment."{item}" as experiment_{item}' for item in tmp
    )
    log.info(experiment_properties)

    sql = f"""
    CREATE VIEW cc_repr_view AS
    SELECT
    ts_representation."guid" as ts_representation_guid,
    ts_representation."name" as ts_representation_name,
    ts_representation."type" as ts_representation_type,
    channel."guid" as channel_guid,
    {channel_properties}{"," if channel_properties else ""}
    cc."guid" as channelcapture_guid,
    sensor."guid" as sensor_guid,
    {sensor_properties}{"," if sensor_properties else ""}
    sc."guid" as sensorcapture_guid,
    experiment."guid" as experiment_guid{"," if experiment_properties else ""}
    {experiment_properties}
    FROM ts_representation
    JOIN association a1 ON ts_representation.guid = a1.child
    JOIN channel_capture cc ON a1.parent = cc.guid
    JOIN association a11 ON cc.guid = a11.child
    JOIN sensor_capture sc ON a11.parent = sc.guid
    JOIN association a12 ON sc.guid = a12.child
    JOIN experiment ON a12.parent = experiment.guid
    JOIN channel ON cc.capture_of = channel.guid
    JOIN association a2 ON channel.guid = a2.child
    JOIN sensor ON a2.parent = sensor.guid
    """

    log.debug(sql)
    with Database(ctx) as db:
        db.cur.execute(sql)


@typechecked
def create_cc_view(ctx: Context) -> None:
    """
    Creates a view for all channel captures.

    almost clone of create_cc_repr_view
    See also: create_cc_repr_view(ctx)

    Args:
        ctx: The context object containing the property columns for the experiment, sensor, and channel.
    """
    tmp = []
    for _, items in ctx.channel_properties.items():
        for item in items:  # type: ignore
            tmp.append(item)
    channel_properties = ", ".join(
        f'channel."{item}" as channel_{item}' for item in tmp
    )
    log.info(channel_properties)

    tmp = []
    for _, items in ctx.sensor_properties.items():
        for item in items:  # type: ignore
            tmp.append(item)
    sensor_properties = ", ".join(f'sensor."{item}" as sensor_{item}' for item in tmp)
    log.info(sensor_properties)

    tmp = []
    for _, items in ctx.experiment_properties.items():
        for item in items:  # type: ignore
            tmp.append(item)
    experiment_properties = ", ".join(
        f'experiment."{item}" as experiment_{item}' for item in tmp
    )
    log.info(experiment_properties)

    sql = f"""
    CREATE VIEW cc_view AS
    SELECT
    channel."guid" as channel_guid,
    {channel_properties}{"," if channel_properties else ""}
    cc."guid" as channelcapture_guid,
    sensor."guid" as sensor_guid,
    {sensor_properties}{"," if sensor_properties else ""}
    sc."guid" as sensorcapture_guid,
    experiment."guid" as experiment_guid{"," if experiment_properties else ""} 
    {experiment_properties}
    FROM channel_capture cc
    JOIN association a11 ON cc.guid = a11.child
    JOIN sensor_capture sc ON a11.parent = sc.guid
    JOIN association a12 ON sc.guid = a12.child
    JOIN experiment ON a12.parent = experiment.guid
    JOIN channel ON cc.capture_of = channel.guid
    JOIN association a2 ON channel.guid = a2.child
    JOIN sensor ON a2.parent = sensor.guid
    """

    log.debug(sql)
    with Database(ctx) as db:
        db.cur.execute(sql)


@typechecked
def create_sc_repr_view(ctx: Context) -> None:
    """
    Creates a view for all representations attached to a sensor capture.

    code very similar to create_cc_repr_view
    See also: create_cc_repr_view(ctx)

    Args:
        ctx: The context object containing the property columns for the experiment and sensor.
    """
    tmp = []
    for _, items in ctx.sensor_properties.items():
        for item in items:  # type: ignore
            tmp.append(item)
    sensor_properties = ", ".join(f'sensor."{item}" as sensor_{item}' for item in tmp)

    tmp = []
    for _, items in ctx.experiment_properties.items():
        for item in items:  # type: ignore
            tmp.append(item)
    experiment_properties = ", ".join(
        f'experiment."{item}" as experiment_{item}' for item in tmp
    )

    sql = f"""
    CREATE VIEW sc_repr_view AS
    SELECT
    ts_representation."guid" as ts_representation_guid,
    ts_representation."name" as ts_representation_name,
    ts_representation."type" as ts_representation_type,
    sensor."guid" as sensor_guid, 
    {sensor_properties}{"," if sensor_properties else ""}
    sc."guid" as sensorcapture_guid,
    experiment."guid" as experiment_guid{"," if experiment_properties else ""}
    {experiment_properties}
    FROM ts_representation
    JOIN association a1 ON ts_representation.guid = a1.child
    JOIN sensor_capture sc ON a1.parent = sc.guid
    JOIN association a12 ON sc.guid = a12.child
    JOIN experiment ON a12.parent = experiment.guid
    JOIN sensor ON sc.capture_of = sensor.guid
    """

    log.debug(sql)
    with Database(ctx) as db:
        db.cur.execute(sql)


@typechecked
def add_cols_to_table(
    ctx: Context,
    table: str,
    cols: list[str],
    coltype: str = "TEXT",
) -> None:
    """
    Adds columns to a table in the database.

    Args:
        ctx: The context object containing the paths to the database.
        table: The name of the table to add columns to.
        cols: A list of column names to add to the table.
        coltype: The data type of the columns to add. Defaults to "TEXT". See
            SQLite types for other options.
    """
    with Database(ctx) as db:
        for col in cols:
            sql = f"ALTER TABLE {table} ADD COLUMN {col} {coltype}"
            db.cur.execute(sql)
        db.con.commit()
    log.info(f"Altered table {table} by appending cols {cols}")


@typechecked
def add_property_columns(ctx: Context) -> None:
    """
    Adds property columns to experiment, sensor, and channel tables in DB.

    Args:
        ctx: The context object containing the property columns for the
            experiment, sensor, and channel.
    """
    for coltype, columns in ctx.experiment_properties.items():
        add_cols_to_table(ctx, "experiment", columns, coltype)
    for coltype, columns in ctx.sensor_properties.items():
        add_cols_to_table(ctx, "sensor", columns, coltype)
    for coltype, columns in ctx.channel_properties.items():
        add_cols_to_table(ctx, "channel", columns, coltype)


class MemoryDB:
    """
    A class for working with an in-memory SQLite database.

    The class creates an in-memory database and copies the contents of a
    file-based database into it. The file-based database is then closed, and
    the in-memory database is kept open. The class also provides a method for
    updating the context object with the location of the in-memory database.
    When the in-memory DB is closed, changes are written to the file-based
    origin.


    # Usage example

    ctx = context.attach()
    memory_db = database.use_inmemory(ctx)
    ctx = memory_db.update_ctx(ctx)

    Caveat:
    INSERTs + multiprocessing do not work well together.
    Do INSERTs in main thread.
    """

    @typechecked
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

        # file db
        self.location_file_db = ctx.paths["database"]
        self.file_con = sqlite3.connect(self.location_file_db, uri=True)

        # memory db
        self.location_memory_db = "mem1?mode=memory&cache=shared"
        self.memory_con = sqlite3.connect(f"file:{self.location_memory_db}", uri=True)

        # copy and persist
        self.file_con.backup(self.memory_con)
        self.ctx.paths["database"] = self.location_memory_db

        self.file_con.close()  # close file db but keep memory db open

    @typechecked
    def update_ctx(self, ctx: Context) -> Context:
        """
        replace path to file-based DB with path to in-memory DB
        """
        ctx.paths["database"] = self.location_memory_db
        return ctx

    def close(self) -> None:
        self.file_con = sqlite3.connect(self.location_file_db, uri=True)
        self.memory_con.backup(self.file_con)
        self.memory_con.close()
        self.file_con.close()
        log.info("memory DB copied to file again")


@typechecked
def use_inmemory(ctx: Context) -> MemoryDB:
    """
    Creates an in-memory database and returns a MemoryDB object.

    see usage example in MemoryDB docstring

    Args:
        ctx (storagetools.Context): The context object containing the paths to the database.

    Returns:
        A MemoryDB object.
    """
    db = MemoryDB(ctx)
    log.info(f"using {db.ctx.paths['database']} as DB now")
    return db
