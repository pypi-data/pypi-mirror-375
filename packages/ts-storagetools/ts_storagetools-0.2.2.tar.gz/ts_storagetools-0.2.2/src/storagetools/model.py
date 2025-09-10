#
# This file is part of storagetools.
#
# Copyright (c) 2025 Mauritz Mälzer
#
# BSD-3-Clause License
#

"""Main class model of storagetools."""

import logging
import uuid
from typing import Any

from storagetools.context import Context
import storagetools.database
from typeguard import typechecked

log = logging.getLogger(__name__)


class Identifiable:
    """
    A base class that makes things identifiable with a GUID.
    """

    def __init__(self) -> None:
        self.guid = uuid.uuid4()

    def __repr__(self) -> str:
        base_repr = super().__repr__()
        guid = f"self.guid = {self.guid.__repr__()}"
        extended_info = f"{base_repr}\n{guid}"
        return extended_info

    def supers(self) -> list[str]:
        """
        Retrieves the inheritence hierarchy of the class

        Returns:
            list of names in the method resolution order
        """
        supers = [x.__name__ for x in self.__class__.__mro__]
        return supers


class Linkable(Identifiable):
    """
    A base class that makes things linkable via attachments and associations.
    """

    def __init__(self) -> None:
        Identifiable.__init__(self)
        self.associations = []
        self.attachments = []

    def __repr__(self) -> str:
        base_repr = super().__repr__()
        assoc_str = self.associations.__repr__()
        attac_str = self.attachments.__repr__()
        associations = f"\nself.associations = {assoc_str}"
        attachments = f"\nself.attachments = {attac_str}"
        extended_info = f"{base_repr}{associations}{attachments}"
        return extended_info

    @typechecked
    def attach_to(self, target: "Linkable") -> None:
        """
        attaches object to another object (target is root, self is leaf)
        """
        target.attachments.append(self.guid)
        self.associations.append(target.guid)

    @typechecked
    def associate(self, target: "Linkable") -> None:
        """
        associates object to with another object (target is leaf, self is root)
        """
        target.associations.append(self.guid)
        self.attachments.append(target.guid)


class HasPropertiesFromCase:
    """
    A base class that makes things have properties.
    """

    @typechecked
    def __init__(self, properties={}) -> None:
        self.properties = properties

    def __repr__(self) -> str:
        base_repr = super().__repr__()
        extended_info = f"{base_repr}"
        for k, v in self.properties.items():
            extended_info += f"\nself.properties['{k}'] = {v}"
        return extended_info


class IsCapture:
    """
    A base class that makes things a capture of sth else.

    Intended mainly for channel and sensor captures.
    """

    @typechecked
    def __init__(self, capture_of: uuid.UUID | Identifiable) -> None:
        if isinstance(capture_of, uuid.UUID):
            self.capture_of = capture_of
        else:
            self.capture_of = capture_of.guid

    def __repr__(self) -> str:
        base_repr = super().__repr__()
        extended_info = f"{base_repr}\nself.capture_of = {self.capture_of}"
        return extended_info


class Experiment(Linkable, HasPropertiesFromCase):
    """
    A class that represents an experiment.

    An experiment is a concept, it is atomic and defined by location, time and
    participating entities. Some practical examples: an experiment can be a
    process, a group of processes or a measurement. Basically anything that
    would get a label in a datamining context.
    """

    @typechecked
    def __init__(self, properties: dict = {}) -> None:
        Linkable.__init__(self)
        HasPropertiesFromCase.__init__(self, properties)


class Sensor(Linkable, HasPropertiesFromCase):
    """
    A class that represents a sensor.
    """

    @typechecked
    def __init__(
        self,
        properties: dict = {},
    ) -> None:
        Linkable.__init__(self)
        HasPropertiesFromCase.__init__(self, properties)


class Channel(Linkable, HasPropertiesFromCase):
    """
    A class that represents a sensor channel.
    """

    @typechecked
    def __init__(
        self,
        properties: dict = {},
    ) -> None:
        Linkable.__init__(self)
        HasPropertiesFromCase.__init__(self, properties)


class SensorCapture(Linkable, IsCapture):
    """
    A class that represents a capture of a sensor.
    """

    def __init__(self, capture_of: Identifiable) -> None:
        Linkable.__init__(self)
        IsCapture.__init__(self, capture_of)


class ChannelCapture(Linkable, IsCapture):
    """
    A class that represents a capture of a sensor channel.
    """

    def __init__(self, capture_of: Identifiable) -> None:
        Linkable.__init__(self)
        IsCapture.__init__(self, capture_of)


class TSRepresentation(Linkable):
    """
    A class that represents a time series representation.

    Time series can be representated in many ways:
    * as an array of measurement values
    * as a feature set
    * as a spectrum
    * as a series of symbols
    etc.

    In addition, time series representations can be stored in different formats:
    * numpy.Array
    * pandas.Series
    * pandas.DataFrame
    * CSV-files
    * proprietary
    etc.

    In this context, a TSRepresentation always has
    * a name, e.g., "filtered_signal"
    * a type, e.g., "pd.Series"
    * a payload that contains any object
    """

    @typechecked
    def __init__(
        self,
        payload: Any,
        name: str = "original",
        type_: str = "pd.Series",
    ) -> None:
        Linkable.__init__(self)
        self.payload = payload
        self.name = name
        self.type = type_

    def __repr__(self) -> str:
        base_repr = super().__repr__()
        name = f"\nself.name = '{self.name}'"
        type_ = f"\nself.type= '{self.type}'"
        payload = f"\nself.payload = {self.payload.__repr__()}"
        extended_info = f"{base_repr}{name}{type_}{payload}"
        return extended_info


class Container(Linkable):
    """
    A Grouping element.

    Can hold GUIDs and optionally the deserialized objects identified by the GUIDs.

    Attributes:
        name: short_name
        info: description of what it contains or sql_statement
        lading: list that may store the deserialized attachments
    """

    @typechecked
    def __init__(self, name: str = "", info: str = "") -> None:
        super().__init__()
        if " " in name:
            # mkview will not work then...
            raise ValueError("container names may not have spaces, use _ or -")
        self.name = name
        self.info = info
        self.lading = []

    def __repr__(self) -> str:
        base_repr = super().__repr__()
        name = f"\nself.name = '{self.name}'"
        info = f"\nself.info = '{self.info}'"
        lading = f"\nself.lading = {self.lading.__repr__()}"
        extended_info = f"{base_repr}{name}{info}{lading}"
        return extended_info

    @typechecked
    def mkview(self, ctx: Context) -> None:
        """
        Creates a view in the metadata DB containing the related objects.

        Can be handy for more complex sql filterings.
        """
        sql = f"""
        CREATE VIEW IF NOT EXISTS '{self.name}' AS
            SELECT a.child AS guid
            FROM association a
            JOIN container c ON a.parent = c.guid
            WHERE c.name = '{self.name}'
        """
        with storagetools.database.Database(ctx) as db:
            db.cur.execute(sql)

    @typechecked
    def rmview(self, ctx: Context) -> None:
        """
        Removes a related view in the metadata DB if exists.
        """
        sql = f"DROP VIEW IF EXISTS {self.name}"
        with storagetools.database.Database(ctx) as db:
            db.cur.execute(sql)
