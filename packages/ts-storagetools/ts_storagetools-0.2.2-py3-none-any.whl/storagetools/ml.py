#
# This file is part of storagetools.
#
# Copyright (c) 2025 Mauritz Mälzer
#
# BSD-3-Clause License
#

"""Machine learning related classes for data analysis."""

import logging
from typing import Any

from storagetools import helpers
from storagetools.context import Context
from storagetools import model
from storagetools.model import Identifiable, Linkable
from typeguard import typechecked

log = logging.getLogger(__name__)


class Datapoint(Linkable):
    """
    A class for an Input-Output mapping, intended for complex Inputs.

    has no serialization possibility at the moment
    """

    @typechecked
    def __init__(self, X: Identifiable, y: Any) -> None:
        """
        Args:
            X: an identifiable (TSRepresentation or Container or ...)
            y: label information (str or int or ...)
        """

        Linkable.__init__(self)
        self.X = X
        self.y = y


class Dataset(Linkable, dict):
    """
    A convenience class for organizations of multiple complex datapoint.

    Is supposed to store X and y, as well as others, for example:
        X_featurized
        X_transformed
        y_pred
        y_encoded

    Has no serialization possibility at the moment.
    """

    @classmethod
    @typechecked
    def from_datapoints_container(
        cls, ctx: Context, container: model.Container
    ) -> "Dataset":
        """
        creates Dataset from container (container may contain ONLY datapoints)

        so far no check function implemented
        """
        if container.lading == []:
            helpers.deserialize_lading(ctx, container)

        X = [datapoint.X for datapoint in container.lading]
        y = [datapoint.y for datapoint in container.lading]
        return cls(X, y)

    @typechecked
    def __init__(self, X: list, y: list = [], *args, **kwargs) -> None:
        """
        Args:
            X: a list of datapoints
            y: a list of label information (same order as X)
            args, kwargs: allows for enrichment with other information
        """

        Linkable.__init__(self)
        dict.__init__(self, *args, **kwargs)
        self["X"] = X
        self["y"] = y

    def as_dict(self) -> dict:
        """
        An export function, to share for use without storagetools.

        Returns:
            dict representation of the dataset
        """
        result = {}
        for k, v in self.items():
            result[k] = v
        return result
