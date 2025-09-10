#
# This file is part of storagetools.
#
# Copyright (c) 2025 Mauritz Mälzer
#
# BSD-3-Clause License
#

"""Convenience functions for working with storagetools."""

import logging
import os
import pickle
from typing import Any
from uuid import UUID, uuid4
import copy

from storagetools import database
from storagetools import db_interface as dbi
from storagetools import model
from storagetools.context import Context
from typeguard import typechecked

log = logging.getLogger(__name__)


@typechecked
def pickl(ctx: Context, target: Any, subdir: str, name: str) -> None:
    """
    Convenience function to pickle away objects in the worktree.

    Args:
        ctx: The context object containing the paths to the LMDB key-value store.
        target: thing to be pickled
        subdir: directory below "workdir" in wich to store pickle
        name: filename
    """
    os.makedirs(os.path.join(ctx.paths["work"], subdir), exist_ok=True)
    with open(os.path.join(ctx.paths["work"], subdir, name), "wb") as f:
        pickle.dump(target, f, protocol=pickle.HIGHEST_PROTOCOL)


@typechecked
def unpickl(ctx: Context, subdir: str, name: str) -> Any:
    """
    Convenience function to unpickle objects in the worktree.

    Args:
        ctx: The context object containing the paths to the LMDB key-value store.
        subdir: directory below "workdir" in wich to store pickle
        name: filename

    Returns:
        unpickled object
    """
    with open(os.path.join(ctx.paths["work"], subdir, name), "rb") as f:
        result = pickle.load(f)
    return result


@typechecked
def fetch_container_by_name(ctx: Context, name: str) -> model.Container:
    """
    Fetches container by name.

    Args:
        ctx: context
        name: container name

    Returns:
        Container
    """
    sql = f"SELECT guid FROM container WHERE name = '{name}'"
    with database.Database(ctx) as db:
        id_ = db.con.execute(sql).fetchone()[0]

    container = dbi.deserialize(ctx, id_)
    return container


@typechecked
def fetch_single_by_sql(ctx: Context, sql: str) -> Any:
    """
    Fetches first result from an SQL query.

    Note: query for GUIDs

    Args:
        ctx: context
        sql: query string for the metadata DB

    Returns:
        deserialized object that corresponds to the first sql result.
    """
    with database.Database(ctx) as db:
        id_ = db.con.execute(sql).fetchone()[0]

    x = dbi.deserialize(ctx, id_)
    return x


@typechecked
def create_container_from_guid_list(
    ctx: Context,
    guid_list: list[UUID],
    name: str = "",
    info: str = "",
) -> model.Container:
    """
    Creates a container with lading from a list of guids.

    How it works:
    in order to properly attach stuff, guids need to be deserialized first
    * deserialize all
    * attach lading to container

    Args:
        ctx: context
        guid_list: list of single-item-tuples containing guids
            (or list of guids)
        name: container name
        info: container info

    Returns:
        container instance with lading
    """
    lading = dbi.deserialize_guid_list(ctx, guid_list)

    container = model.Container(name=name, info=info)
    for thing in lading:
        thing.attach_to(container)  # type: ignore
    container.lading = lading
    return container


@typechecked
def create_container_from_sql(
    ctx: Context,
    sql: str,
    name: str = "",
    info: str = "",
) -> model.Container:
    """
    Convenience function to avoid 'with db' statement.

    Args:
        ctx: context
        sql: sql-query string that selects only guids
        name: container name
        info: container info

    Returns:
        container instance with lading
    """
    with database.Database(ctx) as db:
        guids = db.con.execute(sql).fetchall()

    guid_list = [x[0] for x in guids]
    container = create_container_from_guid_list(ctx, guid_list, name=name, info=info)
    return container


@typechecked
def deserialize_lading(ctx: Context, container: model.Container) -> None:
    """
    Deserializes attachments and stores objects into lading.
    """
    # guid_list = [(x,) for x in container.attachments]
    guid_list = container.attachments
    container.lading = dbi.deserialize_guid_list(ctx, guid_list)


@typechecked
def serialize_lading(ctx: Context, container: model.Container) -> None:
    """
    Serializes lading into DB.
    """
    dbi.serialize_list(ctx, container.lading)


@typechecked
def clone(target: model.Identifiable) -> model.Identifiable:
    """
    Creates a object with identical properties and new guid.

    Args:
        target: object to clone

    Returns:
        An Identifiable with identical properties and new guid
    """
    new = copy.deepcopy(target)
    new.guid = uuid4()
    return new
