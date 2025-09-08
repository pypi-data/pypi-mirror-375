# -*- coding: utf-8 -*-
# mypy: disable-error-code="index"

"""
Datastructure wrappers
"""

from copy import deepcopy
from typing import Iterator, TypeAlias, Union

from .commons import (
    DOT,
    IndexType,
    SegmentsTuple,
    ValueType,
    assured_collection,
    full_traverse,
    iter_paths,
    partial_traverse,
)
from .cache import CacheOfCaches, ParsingCache


SINGLETON_CACHES = CacheOfCaches()

StructureDataType: TypeAlias = Union[ValueType, "Structure"]


class Structure:
    """A data structure, immutable by default, ..."""

    def __init__(
        self,
        original_data_structure: StructureDataType,
        separator: str = DOT,
    ) -> None:
        """Always store a deep copy of data"""
        if isinstance(original_data_structure, Structure):
            self.__data = deepcopy(original_data_structure.data)
        else:
            self.__data = deepcopy(original_data_structure)
        #
        self.__cache: ParsingCache = SINGLETON_CACHES[separator]

    @property
    def data(self) -> ValueType:
        """access to data"""
        return self.get(())

    @property
    def is_mutable(self) -> bool:
        """Return True only from on mutable subclasses"""
        return False

    @property
    def parsing_cache(self) -> ParsingCache:
        """access to the internal cache"""
        return self.__cache

    def __getitem__(self, full_path: IndexType) -> ValueType:
        """Return the substructure determined by full_path"""
        return self.get(full_path)

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"{self.__class__.__name__}({self.data!r},"
            f" separator={self.parsing_cache.separator!r})"
        )

    def __eq__(self, other) -> bool:
        """Equality test"""
        return all(
            (
                self.data == other.data,
                self.is_mutable == other.is_mutable,
                self.parsing_cache.separator == other.parsing_cache.separator,
            )
        )

    def __get_substructure(self, segments: SegmentsTuple) -> ValueType:
        """Return the substructure determined by full_path"""
        if segments:
            substructure = full_traverse(self.__data, segments)
        else:
            substructure = self.__data
        #
        if self.is_mutable:
            return substructure
        #
        return deepcopy(substructure)

    def get(self, full_path: IndexType) -> ValueType:
        """Return the substructure determined by full_path"""
        return self.__get_substructure(self.__cache[full_path])

    def get_with_default(self, full_path: IndexType, default: ValueType) -> ValueType:
        """Return the substructure determined by full_path"""
        try:
            return self.__get_substructure(self.__cache[full_path])
        except (KeyError, IndexError):
            return default
        #

    def iter_canonical_endpoints(self) -> Iterator[str]:
        """Iterate over the canonical endpoints of the data structure"""
        for segments in iter_paths(self.data):
            yield self.parsing_cache.canonical(segments)
        #


class MutableStructure(Structure):
    """A mutable data structure, immutable by default, ..."""

    def __init__(
        self,
        original_data_structure: StructureDataType,
        separator: str = DOT,
    ) -> None:
        """Store the data as-is"""
        super().__init__(original_data_structure, separator=separator)
        self.__mutable = True

    @property
    def is_mutable(self) -> bool:
        """Return True on mutable instances"""
        return self.__mutable

    def freeze(self) -> list[str]:
        """Make the instance immutable and return a list of strings
        describing the effects for debugging purposes
        """
        class_name = self.__class__.__name__
        if self.is_mutable:
            self.__mutable = False
            return [
                f"{class_name} instance changed to immutable",
                "the .get() method will from now on"
                " return a deep copy of the found substructure",
            ]
        #
        return [f"No change, {class_name} instance had already been immutable"]

    def __setitem__(self, full_path: IndexType, new_value: ValueType) -> None:
        """Store a new value. Build the intermediate structure if required."""
        self.update(full_path, new_value, fail_on_missing_keys=False)

    def __delitem__(self, full_path: IndexType) -> None:
        """Delete the specified substructure"""
        self.delete(full_path)

    def __collection_and_key(
        self,
        full_path: IndexType,
    ) -> tuple[ValueType, ValueType]:
        """Return the collection at the last but one path segment,
        and the key determined by the last segment
        """
        segments = self.parsing_cache[full_path]
        if len(segments) < 1:
            raise IndexError(
                f"Minimum one path component is required, but got only {segments!r}"
            )
        #
        partial_traversal_path = segments[:-1]
        return assured_collection(
            full_traverse(self.data, partial_traversal_path)
        ), segments[-1]

    def delete(self, full_path: IndexType) -> None:
        """Delete the substructure at full_path"""
        subcollection, key = self.__collection_and_key(full_path)
        del assured_collection(subcollection)[key]  # type: ignore[arg-type]

    def update(
        self,
        full_path: IndexType,
        new_value: ValueType,
        fail_on_missing_keys: bool = False,
    ) -> None:
        """Modify the data structure in place setting self[full_path] to new_value"""
        if fail_on_missing_keys:
            # shortcut: regard the full path only
            subcollection, key = self.__collection_and_key(full_path)
        else:
            # slow traversal - search the existing path part,
            # and build a new substructure
            # so in the resulting structure there will be the full path available
            segments = self.parsing_cache[full_path]
            if not segments:
                raise ValueError("Cannot modify with an empty path")
            #
            subcollection, remaining_segments = partial_traverse(
                self.data,
                segments,
                min_remaining_segments=1,
                fail_on_missing_keys=False,
            )
            if len(remaining_segments) > 1:
                # build intermediate path
                still_remaining_segments = list(remaining_segments)
                while len(still_remaining_segments) > 1:
                    key = still_remaining_segments.pop(0)
                    subcollection[key] = {}
                    subcollection = subcollection[key]
                #
                key = still_remaining_segments.pop(0)
            else:
                key = remaining_segments[0]
            #
        #
        assured_collection(subcollection)[key] = new_value  # type: ignore[index]


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
