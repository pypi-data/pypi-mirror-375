from __future__ import annotations

from dataclasses import fields as _fields
from typing import cast, TYPE_CHECKING

from ..protocols import CorbelDataclass

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Type

    from ..types import TCorbelDataclass


def fields(
    cls: Type[TCorbelDataclass],
) -> tuple[Field, ...]:
    """
    Retrieve the dataclass fields for a Corbel dataclass type.

    Returns the ``corbel_fields`` attribute if present, otherwise falls back
    to standard :func:`dataclasses.fields`.

    :param cls:
        The dataclass type to inspect.
    :return:
        A tuple of :class:`dataclasses.Field` objects representing the fields
        of the class.
    :rtype: tuple[Field, ...]
    """
    return (
        getattr(cast(CorbelDataclass, cls), "corbel_fields")
        if hasattr(cls, "corbel_fields")
        else _fields(cls)
    )


__all__ = ("fields",)
