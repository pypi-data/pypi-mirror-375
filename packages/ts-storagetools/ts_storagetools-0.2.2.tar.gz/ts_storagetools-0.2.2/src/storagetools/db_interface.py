#
# This file is part of storagetools.
#
# Copyright (c) 2025 Mauritz Mälzer
#
# BSD-3-Clause License
#

"""Manages (de-) serialization

This module provides functions for serializing and deserializing objects to and
from a SQLite database and an LMDB key-value store.

It includes classes for serializing and deserializing objects, as well as
functions for removing objects from the database.
"""

from typing import Any
import lmdb
import pickle
import logging
import sys
import warnings
import uuid

from tqdm import tqdm
from typeguard import typechecked

from storagetools.context import Context
from storagetools.database import Database
from storagetools.model import (
    Channel,
    ChannelCapture,
    Container,
    Experiment,
    HasPropertiesFromCase,
    Identifiable,
    IsCapture,
    Linkable,
    Sensor,
    SensorCapture,
    TSRepresentation,
)

warnings.filterwarnings("ignore", message="metadata on a dtype")

log = logging.getLogger(__name__)

CLASSNAME_TO_TABLE_MAPPING = {
    "Experiment": "experiment",
    "Sensor": "sensor",
    "Channel": "channel",
    "SensorCapture": "sensor_capture",
    "ChannelCapture": "channel_capture",
    "TSRepresentation": "ts_representation",
    "Container": "container",
}

CLASS_TO_TABLE_MAPPING = {
    Experiment: "experiment",
    Sensor: "sensor",
    Channel: "channel",
    SensorCapture: "sensor_capture",
    ChannelCapture: "channel_capture",
    TSRepresentation: "ts_representation",
    Container: "container",
}


class Serializer:
    """
    A class for serializing objects to the metadata database and LMDB key-value store.
    """

    class_to_table_mapping = CLASS_TO_TABLE_MAPPING

    def __init__(self, target: Any) -> None:
        self.target = target
        self.references = []

    def generate_record_and_sql(self) -> tuple[str, dict]:
        """
        Generates a record and SQL statement for inserting the object into the database.

        Returns:
            A tuple containing the SQL statement and the record.
        """
        record = {}
        from_supers = self.gather_record_entries_from_supers()
        from_instance = self.gather_record_entries_from_instance()
        record.update(from_supers)
        record.update(from_instance)
        sql = self.assemble_sql_string(record)
        return sql, record

    def gather_record_entries_from_supers(self) -> dict:
        """
        collect entries from inherited fields (Identifiable, Linkable, ...)

        Returns:
            A dictionary with entries
        """
        record = {}
        if issubclass(self.target.__class__, Identifiable):
            record["guid"] = self.target.guid

        if issubclass(self.target.__class__, Linkable):
            for association in self.target.associations:
                self.references.append((self.target.guid, association))
            for attachment in self.target.attachments:
                self.references.append((attachment, self.target.guid))

        if issubclass(self.target.__class__, HasPropertiesFromCase):
            record.update(self.target.properties)

        if issubclass(self.target.__class__, IsCapture):
            record["capture_of"] = self.target.capture_of
        return record

    def gather_record_entries_from_instance(self) -> dict:
        """
        Collects entries from instance fields (TSRepresentation, Container, ...)

        Returns:
            A dictionary with entries
        """
        record = {}
        if issubclass(self.target.__class__, TSRepresentation):
            record["name"] = self.target.name
            record["type"] = self.target.type
        if issubclass(self.target.__class__, Container):
            record["name"] = self.target.name
            record["info"] = self.target.info
        return record

    def which_table(self) -> str:
        """
        Returns the name of the table in the database that corresponds to the object's class.

        Returns:
            str: name of table
        """
        return self.class_to_table_mapping[self.target.__class__]

    @typechecked
    def assemble_sql_string(self, record: dict) -> str:
        """
        Assembles an SQL statement for inserting the object into the database.

        Args:
            record: The record containing the object's metadata.

        Returns:
            The SQL statement.
        """
        sql = f"""
        INSERT OR REPLACE INTO {self.which_table()}
        {tuple(record.keys())}
        VALUES (?{(len(record.keys()) - 1) * ", ?"})
        """
        return sql

    @typechecked
    def store_blob(self, ctx: Context) -> None:
        """
        Stores the object's payload in the LMDB key-value store.

        Args:
            ctx: The context object containing the paths to the LMDB key-value store.
        """
        kvs = lmdb.open(ctx.paths["storage"], map_size=ctx.max_kvsize)
        payload = pickle.dumps(self.target.payload)
        with kvs.begin(write=True) as txn:
            txn.put(self.target.guid.bytes, payload)
        kvs.close()

    @typechecked
    def serialize_core(self, ctx: Context) -> None:
        """
        Serializes the object's core (metadata) data to the database.

        Should be renamed to serialize_metadata or sth in the future.

        Args:
            ctx: The context object containing the paths to the database.
        """
        sql, record = self.generate_record_and_sql()
        with Database(ctx) as db:
            db.cur.execute(sql, list(record.values()))

    @typechecked
    def serialize_references(self, ctx: Context) -> None:
        """
        Serializes the object's references to other objects to the database.

        References means every association (reference 'up') or attachment (reference 'down').

        Args:
            ctx: The context object containing the paths to the database.
        """
        sql = """
        INSERT OR REPLACE INTO association (child, parent) VALUES (?, ?)
        """
        with Database(ctx) as db:
            db.cur.executemany(sql, self.references)


@typechecked
def serialize(ctx: Context, target: Any, blob_also: bool = True) -> None:
    """
    Serializes an object.

    Serializes an object to the metadata database and optionally its payload to the LMDB key-value store.

    Args:
        ctx: The context object containing the paths to the database and LMDB key-value store.
        target: The object to serialize.
        blob_also: Whether to serialize the object payload to the LMDB key-value store. Defaults to True.
    """
    serializer = Serializer(target)
    serializer.serialize_core(ctx)
    if issubclass(target.__class__, Linkable):
        serializer.serialize_references(ctx)
    if blob_also:  # can be skipped if for example only association is updated
        if issubclass(target.__class__, TSRepresentation):
            serializer.store_blob(ctx)


@typechecked
def serialize_list(ctx: Context, target_list: list[Any]) -> None:
    """
    Convenience function that serializes a list of objects to database key-value store.

    Args:
        ctx: The context object containing the paths to the database and LMDB key-value store.
        target_list: The list of objects to serialize.
    """
    kvs = lmdb.open(ctx.paths["storage"], map_size=ctx.max_kvsize)
    with kvs.begin(write=True) as txn:
        for target in tqdm(target_list):
            serialize(ctx, target, blob_also=False)
            if issubclass(target.__class__, TSRepresentation):
                payload = pickle.dumps(target.payload)
                txn.put(target.guid.bytes, payload)
    kvs.close()


class Deserializer:
    """
    A class for deserializing objects from the metadata database and LMDB key-value store.
    """

    class_to_table_mapping = CLASS_TO_TABLE_MAPPING

    def __init__(self, target_guid: uuid.UUID) -> None:
        self.target_guid = target_guid
        self.record = {}

    @typechecked
    def get_class(self, ctx: Context) -> None:
        """
        Gets the class of the object the deserializer was initialized with.

        The GUID could resolve to anything, thus its class has to be determined
        in order to find the table in the database from which to deserialize
        metadata from.

        Args:
            ctx: The context object containing the paths to the database and
                LMDB key-value store.
        """
        sql = "SELECT tablename FROM guid_lookup WHERE guid = ?"
        with Database(ctx) as db:
            tablename = db.cur.execute(sql, (self.target_guid,)).fetchone()[0]
        self.class_ = [
            key
            for key, value in self.class_to_table_mapping.items()
            if value == tablename
        ][0]

    @typechecked
    def get_record_entries_from_supers(self, ctx: Context) -> dict:
        """
        Collects entries from inherited fields (Linkable, HasPropertiesFromCase, IsCapture)

        Args:
            ctx: The context object containing the paths to the database and
                LMDB key-value store.

        Returns:
            A dict with metadata
        """
        record = {}
        table = self.class_to_table_mapping[self.class_]

        if issubclass(self.class_, Linkable):
            record["associations"] = []
            record["attachments"] = []
            # fetch guid from associations where guid = parent or = child
            sql = "SELECT parent FROM association WHERE child = ?"
            with Database(ctx) as db:
                results = db.cur.execute(sql, (self.target_guid,)).fetchall()
            for result in results:
                record["associations"].append(result[0])

            sql = "SELECT child FROM association WHERE parent = ?"
            with Database(ctx) as db:
                results = db.cur.execute(sql, (self.target_guid,)).fetchall()
            for result in results:
                record["attachments"].append(result[0])

        if issubclass(self.class_, HasPropertiesFromCase):
            record["properties"] = {}
            if self.class_ == Experiment:
                property_set = ctx.experiment_properties
            elif self.class_ == Sensor:
                property_set = ctx.sensor_properties
            elif self.class_ == Channel:
                property_set = ctx.channel_properties
            else:
                log.warning("property set not defined for deserialization!")
                property_set = {}

            # iterate over types (_) in properties (integer, text, etc)
            for _, cols in property_set.items():
                sql = f"""
                SELECT {", ".join(cols)} FROM {table} WHERE guid = ?
                """
                with Database(ctx) as db:
                    vals = db.cur.execute(sql, (self.target_guid,)).fetchone()
                result = {}
                for i, col in enumerate(cols):
                    result[col] = vals[i]
                record["properties"].update(result)

        if issubclass(self.class_, IsCapture):
            sql = f"SELECT capture_of FROM {table} WHERE guid = ?"
            with Database(ctx) as db:
                record["capture_of"] = db.cur.execute(
                    sql, (self.target_guid,)
                ).fetchone()[0]
        return record

    @typechecked
    def get_record_entries_from_instance(self, ctx: Context) -> dict:
        """
        Collects entries specific to distinct classes (TSRepresentation, Container)

        May be merged with get_record_entries_from_supers in the future, works similarly.

        Args:
            ctx: The context object containing the paths to the database and
                LMDB key-value store.

        Returns:
            A dict with metadata
        """

        record = {}
        table = self.class_to_table_mapping[self.class_]

        if issubclass(self.class_, TSRepresentation):
            sql = f"SELECT name, type FROM {table} WHERE guid = ? "
            with Database(ctx) as db:
                result = db.cur.execute(sql, (self.target_guid,)).fetchone()
            record["name"] = result[0]
            record["type"] = result[1]

        if issubclass(self.class_, Container):
            sql = f"SELECT name, info FROM {table} WHERE guid = ? "
            with Database(ctx) as db:
                result = db.cur.execute(sql, (self.target_guid,)).fetchone()
            record["name"] = result[0]
            record["info"] = result[1]
        return record

    @typechecked
    def restore_blob(self, ctx: Context) -> Any:
        """
        Retrieves payload data from key value store.

        Args:
            ctx: The context object containing the paths to the database and
                LMDB key-value store.

        Returns:
            Whatever payload is related to GUID
        """
        kvs = lmdb.open(ctx.paths["storage"], map_size=ctx.max_kvsize)
        with kvs.begin() as txn:
            payload = pickle.loads(txn.get(self.target_guid.bytes))
        kvs.close()
        return payload

    @typechecked
    def delete_blob(self, ctx: Context) -> None:
        """
        deletes payload data related to deserializer guid from key value store.

        args:
            ctx: the context object containing the paths to the database and
                lmdb key-value store.
        """
        kvs = lmdb.open(ctx.paths["storage"], map_size=ctx.max_kvsize)
        with kvs.begin(write=True) as txn:
            txn.delete(self.target_guid.bytes)
        kvs.close()

    @typechecked
    def create_from_record(self, ctx: Context, record: dict) -> Any:
        """
        Recreates an object from the collected metadata.

        Requires class of the target object to be determined and metadata collected.

        args:
            ctx: the context object containing the paths to the database and
                lmdb key-value store.
            record: dict with metadata

        Returns:
            desieralized object
        """

        if self.class_ == Experiment:
            x = Experiment(
                properties=record["properties"],
            )
            x.guid = self.target_guid
        elif self.class_ == Sensor:
            x = Sensor(
                properties=record["properties"],
            )
            x.guid = self.target_guid
        elif self.class_ == Channel:
            x = Channel(
                properties=record["properties"],
            )
            x.guid = self.target_guid
            x.properties = record["properties"]
        elif self.class_ == SensorCapture:
            x = SensorCapture(capture_of=record["capture_of"])
            x.guid = self.target_guid
        elif self.class_ == ChannelCapture:
            x = ChannelCapture(capture_of=record["capture_of"])
            x.guid = self.target_guid
        elif self.class_ == Container:
            x = Container()
            x.guid = self.target_guid
            x.name = record["name"]
            x.info = record["info"]
        elif self.class_ == TSRepresentation:
            payload = self.restore_blob(ctx)
            x = TSRepresentation(
                payload=payload,
                name=record["name"],
                type_=record["type"],
            )
            x.guid = self.target_guid
        else:
            log.error(f"no matching class for {self.class_}")
            sys.exit()

        if issubclass(self.class_, Linkable):
            x.attachments = record["attachments"]  # type: ignore
            x.associations = record["associations"]  # type: ignore
        return x

    @typechecked
    def core_remove_from_db(self, ctx: Context) -> None:
        """
        Removes an objects metadata.

        Think twice, maybe use db_interface.remove().
        Does not touch the key value store.
        May be renamed in the future and merged with delete_blob.

        Args:
            ctx: the context object containing the paths to the database and
                lmdb key-value store.
        """

        self.get_class(ctx)
        table = self.class_to_table_mapping[self.class_]

        # remove row from table
        sql = f"DELETE FROM {table} WHERE guid = ?"
        with Database(ctx) as db:
            db.cur.execute(sql, (self.target_guid,))

        # remove links
        sql = """
        DELETE FROM association 
        WHERE parent = ? 
        OR child = ? 
        """
        with Database(ctx) as db:
            db.cur.execute(sql, (self.target_guid, self.target_guid))


@typechecked
def deserialize(ctx: Context, target_guid: uuid.UUID) -> Any:
    """
    Deserializes an object from the database and LMDB key-value store.

    Args:
        ctx: The context object containing the paths to the database and LMDB
            key-value store.
        target_guid: The GUID of the object to deserialize
    Returns:
        The deserialized object.
    """
    deserializer = Deserializer(target_guid)
    deserializer.get_class(ctx)
    record = {}
    record.update(deserializer.get_record_entries_from_supers(ctx))  # type: ignore
    record.update(deserializer.get_record_entries_from_instance(ctx))
    x = deserializer.create_from_record(ctx, record)
    return x


@typechecked
def deserialize_guid_list(
    ctx: Context,
    guid_list: list[uuid.UUID],
    disable_progressbar: bool = True,
) -> list[Any]:
    """
    convenience function, does what it says

    Args:
        ctx: The context object containing the paths to the database and LMDB
            key-value store.
        guid_list: list of guids to deserialize
        progressbar: tqdm progressbar
    Returns:
        list of deserialized objects
    """
    x = []
    for guid in tqdm(guid_list, disable=disable_progressbar):
        x.append(deserialize(ctx, guid))
    return x


@typechecked
def remove(
    ctx: Context,
    target_guid: uuid.UUID,
    blob_also: bool = True,
) -> None:
    """
    Removes object from metadata database, also from key-value store.

    Args:
        ctx: The context object containing the paths to the database and LMDB
            key-value store.
        target_guid: GUID of object to be removed
        blob_also (optional): Whether to remove the blob also (otherwise metadata only)
    """
    deserializer = Deserializer(target_guid)
    deserializer.core_remove_from_db(ctx)
    if blob_also:
        if issubclass(deserializer.class_, TSRepresentation):
            deserializer.delete_blob(ctx)


@typechecked
def remove_blob_only(ctx: Context, target_guid: uuid.UUID) -> None:
    """
    Removes object from key-value store only.

    Args:
        ctx: The context object containing the paths to the database and LMDB
            key-value store.
        target_guid: GUID of object to be removed
    """
    deserializer = Deserializer(target_guid)
    deserializer.delete_blob(ctx)
