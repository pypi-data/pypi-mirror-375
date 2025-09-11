"""Traversal helpers for schema entities and their usages.

This module provides wrapper classes around core schema models (Schema, Cube,
Dimension, Hierarchy, Level, Property) that unify access between shared
entities and their usage-specific overrides. It exposes convenient iterables
and lookup helpers while preserving annotations, captions, and authorization
checks. Internal helpers also reduce repetition when building usage maps and
performing common name-based lookups.
"""

import logging
from collections import OrderedDict
from collections.abc import Iterable, Iterator, Mapping
from functools import lru_cache
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

import immutables as immu

from tesseract_olap.common import T, get_localization
from tesseract_olap.exceptions.query import (
    InvalidEntityName,
)
from tesseract_olap.exceptions.schema import (
    DuplicatedNameError,
    EntityUsageError,
    InvalidNameError,
    MissingPropertyError,
)

from .enums import DataType, DimensionType, TimeScale
from .models import (
    Annotations,
    AnyMeasure,
    CalculatedMeasure,
    CaptionSet,
    Cube,
    Dimension,
    DimensionUsage,
    Entity,
    Hierarchy,
    HierarchyUsage,
    InlineTable,
    Level,
    LevelUsage,
    Measure,
    Property,
    PropertyUsage,
    Schema,
    Table,
    Usage,
)

if TYPE_CHECKING:
    from tesseract_olap.query import RequestWithRoles

logger = logging.getLogger(__name__)

DEFAULT_LOCALE = "xx"
INVALID_NAME_TOKENS = {",", ".", ":"}


class HasName(Protocol):
    @property
    def name(self) -> str: ...


Named = TypeVar("Named", bound=HasName)

EntityType = TypeVar("EntityType", bound=Entity, covariant=True)
UsageType = TypeVar("UsageType", bound=Usage, covariant=True)

Primitive = Union[int, float, bool, str]


class SchemaTraverser(Mapping[str, "CubeTraverser"]):
    """Wrapper class for Schema model.

    Generates the relationships between the shared entities and their usages,
    and allows for quick search and traversing of them.
    """

    schema: "Schema"
    cube_map: OrderedDict[str, "CubeTraverser"]

    def __init__(self, schema: "Schema"):
        self.schema = schema
        self.cube_map = OrderedDict(
            (
                name,
                CubeTraverser(
                    cube,
                    dimension_map=schema.shared_dimension_map,
                    table_map=schema.shared_table_map,
                ),
            )
            for name, cube in schema.cube_map.items()
        )

    def __repr__(self) -> str:
        feat_map = {
            "cubes": len(self.cube_map),
            "dimensions": len(self.schema.shared_dimension_map),
            "tables": len(self.schema.shared_table_map),
        }
        feats = ", ".join(f"{amount} {item}" for item, amount in feat_map.items() if amount > 0)
        return f"Schema({self.schema.name!r}, {feats})"

    def __len__(self) -> int:
        return len(self.cube_map)

    def __getitem__(self, key: str) -> "CubeTraverser":
        return self.get_cube(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self.cube_map)

    @property
    def default_locale(self) -> str:
        """The default locale set for the schema."""
        return self.schema.default_locale

    def get_cube(self, cube_name: str) -> "CubeTraverser":
        """Return a cube by its name. If doesn't exist, raises InvalidEntityName."""
        try:
            return self.cube_map[cube_name]
        except KeyError:
            raise InvalidEntityName("Cube", cube_name) from None

    def get_locale_available(self) -> set[str]:
        """Resolve the locale labels configured in the child entities of this :class:`Schema`."""
        locales = {self.schema.default_locale}
        for cube in self.cube_map.values():
            locales.update(cube.get_locale_available())
        # TODO: add from shared_dimension_map and shared_table_map
        locales.discard(DEFAULT_LOCALE)
        return locales

    def is_authorized(self, request: "RequestWithRoles") -> bool:
        """Validate if a request has enough permissions to be executed."""
        return self.get_cube(request.cube).is_authorized(request.roles)

    def validate(self) -> None:
        """Verify the resulting data structure after parsing the schema file.

        The validation verifies these rules:
        - Each entity name must be unique across its kind in the same cube
        - Level, Property and Measure names must be unique in the same cube
        - Entity names can't contain these tokens: colon (:), period (.), or comma (,).
        """
        for cube in self.cube_map.values():
            cube_name = cube.name
            dimension_set = {}
            hierarchy_set = {}
            column_set = {}

            for measure in cube.measures:
                for item in measure.and_submeasures():
                    _validate_entity_names(cube_name, item, column_set)

            for dimension in cube.dimensions:
                _validate_entity_names(cube_name, dimension, dimension_set)
                for hierarchy in dimension.hierarchies:
                    _validate_entity_names(cube_name, hierarchy, hierarchy_set)
                    for level in hierarchy.levels:
                        _validate_entity_names(cube_name, level, column_set)
                        for prop in level.properties:
                            _validate_entity_names(cube_name, prop, column_set)


class CubeTraverser:
    """Wrapper class for the :class:`Cube` model.

    Establishes the relationships between its usages and their source shared entities.
    The relationships are made via the :class:`EntityUsageTraverser` subclasses,
    initialized upon creation.
    """

    _cube: "Cube"
    _dimension_map: Mapping[str, "DimensionTraverser"]
    _table: Union["Table", "InlineTable"]
    annotations: Annotations
    captions: CaptionSet
    measure_map: Mapping[str, "AnyMeasure"]
    name: str
    subset_table: bool
    visible: bool

    def __init__(
        self,
        cube: "Cube",
        *,
        dimension_map: Mapping[str, "Dimension"],
        table_map: Mapping[str, "InlineTable"],
    ) -> None:
        self._cube = cube
        self._dimension_map = OrderedDict(
            (
                name,
                DimensionTraverser(item, table_map=table_map)
                if isinstance(item, Dimension)
                else DimensionTraverser(
                    _get_shared_dimension(dimension_map, item.source),
                    item,
                    table_map=table_map,
                ),
            )
            for name, item in cube.dimension_map.items()
        )
        self.measure_map = immu.Map(
            (item.name, item)
            for measure in self._cube.measure_map.values()
            for item in measure.and_submeasures()
        )
        self._table = table_map[cube.table] if isinstance(cube.table, str) else cube.table

    def __repr__(self) -> str:
        return f"CubeTraverser(name='{self._cube.name}', table={self.table})"

    def __getattr__(self, _name: str) -> Any:
        return getattr(self._cube, _name)

    @property
    def table(self) -> Union["Table", "InlineTable"]:
        """Return the Table entity for this cube."""
        return self._table

    @property
    def measures(self) -> Iterable["AnyMeasure"]:
        """Return a generator which yields all the Measures defined in this Cube."""
        return self._cube.measure_map.values()

    @property
    def calculated_measures(self) -> Iterable["CalculatedMeasure"]:
        """Return a generator which yields only the CalculatedMeasures defined in this Cube."""
        return (
            item for item in self._cube.measure_map.values() if isinstance(item, CalculatedMeasure)
        )

    @property
    def dimensions(self) -> Iterable["DimensionTraverser"]:
        """Return a generator which yields all the Dimensions defined in this Cube."""
        return self._dimension_map.values()

    @property
    def time_dimensions(self) -> Iterable["DimensionTraverser"]:
        """Return a generator which yields only the TIME-type Dimensions defined in this Cube."""
        return (item for item in self.dimensions if item.dim_type == DimensionType.TIME)

    @property
    def hierarchies(self) -> Iterable["HierarchyTraverser"]:
        """Return a generator which yields all the Hierarchies from all Dimensions in this Cube."""
        return chain(*(item.hierarchies for item in self.dimensions))

    @property
    def levels(self) -> Iterable["LevelTraverser"]:
        """Return a generator which yields all the Levels from all Dimensions in this Cube."""
        return chain(*(item.levels for item in self.dimensions))

    @property
    def time_levels(self) -> Iterable["LevelTraverser"]:
        """Return a generator that yields all Levels from a TIME Dimension in this Cube."""
        return chain(*(item.levels for item in self.time_dimensions))

    @property
    def properties(self) -> Iterable["PropertyTraverser"]:
        """Return a generator which yields all the Properties from all Dimensions in this Cube."""
        return chain(*(item.properties for item in self.dimensions))

    def get_annotation(self, name: str) -> Optional[str]:
        """Retrieve an annotation from this Cube. If not defined, returns None."""
        return self._cube.get_annotation(name)

    def get_caption(self, locale: str = DEFAULT_LOCALE) -> str:
        """Retrieve the caption of this Cube, for the provided locale."""
        return self._cube.get_caption(locale)

    @lru_cache(maxsize=1)
    def get_locale_available(self) -> set[str]:
        """Resolve the locale labels configured in the child entities of this :class:`Cube`."""
        locales = set(self.captions.keys())
        for item in self.dimensions:
            locales.update(item.get_locale_available())
        for item in self.measures:
            locales.update(item.get_locale_available())
        return locales

    def get_measure(self, name: str) -> "AnyMeasure":
        """Attempt to retrieve a Measure by its name.

        Raises :class:`InvalidEntityName` if the entity can't be found.
        """
        try:
            return self.measure_map[name]
        except KeyError:
            raise InvalidEntityName("Measure", name) from None

    def get_dimension(self, name: str) -> "DimensionTraverser":
        """Attempt to retrieve a Dimension by its name.

        Raises :class:`InvalidEntityName` if the entity can't be found.
        """
        return _find_by_name(self.dimensions, name, "Dimension")

    def get_hierarchy(self, name: str) -> "HierarchyTraverser":
        """Attempt to retrieve a Hierarchy by its name.

        Raises :class:`InvalidEntityName` if the entity can't be found.
        """
        return _find_by_name(self.hierarchies, name, "Hierarchy")

    def get_level(self, name: str) -> "LevelTraverser":
        """Attempt to retrieve a Level by its name.

        Raises :class:`InvalidEntityName` if the entity can't be found.
        """
        return _find_by_name(self.levels, name, "Level")

    def get_property(self, name: str) -> "PropertyTraverser":
        """Attempt to retrieve a Property by its name.

        Raises :class:`InvalidEntityName` if the entity can't be found.
        """
        return _find_by_name(self.properties, name, "Property")

    def is_authorized(self, roles: Iterable[str]) -> bool:
        """Validate permission to access this Cube by the provided roles."""
        return self._cube.is_authorized(roles)


class EntityUsageTraverser(Generic[EntityType, UsageType]):
    """Wrapper class to unify an usage with its entity.

    Its properties are looked on the usage, then on the entity if not found.
    The usage instance is optional, as this wrapper also standardizes the
    properties and traversing methods across entities in the codebase.
    """

    _entity: EntityType
    _usage: Optional[UsageType]

    def __init__(self, entity: EntityType, usage: Optional[UsageType] = None):
        self._entity = entity
        self._usage = usage

    def __contains__(self, item: Union[EntityType, UsageType]) -> bool:
        return item in (self._entity, self._usage)

    def __dir__(self) -> Iterable[str]:
        return sorted(set(dir(self._entity)) | set(dir(self)))

    def __getattr__(self, name: str) -> Any:
        return getattr(self._entity, name)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"

    @property
    def name(self) -> str:
        """Resolve the name of this entity.

        Returns the new name given by the usage reference, or the original
        name of the entity if not defined.
        """
        return self._entity.name if self._usage is None else self._usage.name

    @property
    def annotations(self) -> Annotations:
        """Resolve the combined annotations for the entity and its usage, if defined."""
        if self._usage is None:
            return self._entity.annotations
        return {**self._entity.annotations, **self._usage.annotations}

    @property
    def captions(self) -> CaptionSet:
        """Return the combined captions for the entity and its usage, if defined."""
        if self._usage is None:
            return self._entity.captions
        return {**self._entity.captions, **self._usage.captions}

    def get_annotation(self, name: str) -> Optional[str]:
        """Retrieve an annotation for the entity. If not defined, returns None."""
        return self.annotations.get(name)

    def get_caption(self, locale: str = DEFAULT_LOCALE) -> str:
        """Retrieve the caption of the entity for a certain locale.

        If the a caption hasn't been defined for said locale, will attempt to
        return the fallback caption, and if not defined either, will return the
        entity name.
        """
        caption = get_localization(self.captions, locale)
        return self.name if caption is None else caption

    def get_locale_available(self) -> set[str]:
        """Resolve the locale labels configured in the child entities of this Entity."""
        return set(self.captions.keys())


class DimensionTraverser(EntityUsageTraverser[Dimension, DimensionUsage]):
    """Allows seamless aliasing of values between a Dimension and a DimensionUsage."""

    dim_type: DimensionType
    hierarchy_map: Mapping[str, "HierarchyTraverser"]

    def __init__(
        self,
        entity: "Dimension",
        usage: Optional["DimensionUsage"] = None,
        *,
        table_map: Mapping[str, "InlineTable"] = {},
    ) -> None:
        super().__init__(entity, usage)

        dim_type = self.dim_type

        self.hierarchy_map = _build_usage_map(
            entity.hierarchy_map,
            usage.hierarchy_map if usage else {},
            lambda e, u=None: HierarchyTraverser(e, u, table_map=table_map, dim_type=dim_type),
            resolve_source=lambda src: entity.hierarchy_map[src],
        )

    @property
    def foreign_key(self) -> str:
        """Returns the foreign key for this Dimension."""
        # A DimensionTraverser represents PrivateDimension or DimensionUsage,
        # and the foreign_key property must be present in both, final value
        # depends solely on self._usage presence.
        if self._usage is not None:
            return self._usage.foreign_key
        if self._entity.foreign_key is None:
            # should be unreachable, but checks types
            raise MissingPropertyError("Dimension", self.name, "foreign_key")
        return self._entity.foreign_key

    @property
    def fkey_time_format(self) -> Optional[str]:
        """Returns the declared format of the foreign key for a Time Dimension."""
        if self.dim_type is not DimensionType.TIME:
            return None
        time_format = self._usage.fkey_time_format if self._usage else None
        return time_format or self._entity.fkey_time_format or "YYYY"

    @property
    def default_hierarchy(self) -> "HierarchyTraverser":
        """Return the default Hierarchy entity as defined by the parent Dimension.

        If the Dimension doesn't define one, returns the first Hierarchy declared.
        """
        hie = self._entity.get_default_hierarchy()
        if self._usage is None:
            return self.hierarchy_map[hie.name]
        try:
            # find the HierarchyTraverser that references the default Hierarchy
            return next(item for item in self.hierarchies if hie in item)
        except StopIteration:
            return next(iter(self.hierarchies))

    @property
    def hierarchies(self) -> Iterable["HierarchyTraverser"]:
        """Returns a generator that yields all Hierarchies under this Dimension."""
        return self.hierarchy_map.values()

    @property
    def levels(self) -> Iterable["LevelTraverser"]:
        """Returns a generator that yields all Levels under this Dimension."""
        return chain(*(item.levels for item in self.hierarchies))

    @property
    def properties(self) -> Iterable["PropertyTraverser"]:
        """Returns a generator that yields all Properties under this Dimension."""
        return chain(*(item.properties for item in self.hierarchies))

    def get_hierarchy(self, name: str) -> "HierarchyTraverser":
        """Retrieve a Hierarchy from this Dimension by its name.

        Raises :class:`InvalidEntityName` if the Hierarchy can't be found.
        """
        return _find_by_name(self.hierarchies, name, "Hierarchy")

    def get_level(self, name: str) -> "LevelTraverser":
        """Retrieve a Level from this Dimension by its name.

        Raises :class:`InvalidEntityName` if the Level can't be found.
        """
        return _find_by_name(self.levels, name, "Level")

    def get_property(self, name: str) -> "PropertyTraverser":
        """Retrieve a Property from this Dimension by its name.

        Raises :class:`InvalidEntityName` if the Property can't be found.
        """
        return _find_by_name(self.properties, name, "Property")


class HierarchyTraverser(EntityUsageTraverser[Hierarchy, HierarchyUsage]):
    """Allows seamless aliasing of values between a Hierarchy and a HierarchyUsage."""

    level_map: Mapping[str, "LevelTraverser"]
    primary_key: str
    # `table` might be `None` if intended to use foreign key as value, like "Year"
    table: Union["Table", "InlineTable", None]
    dim_type: DimensionType

    def __init__(
        self,
        entity: "Hierarchy",
        usage: Optional["HierarchyUsage"] = None,
        *,
        table_map: Mapping[str, "InlineTable"],
        dim_type: DimensionType,
    ) -> None:
        super().__init__(entity, usage)

        self.dim_type = dim_type
        self.table = table_map[entity.table] if isinstance(entity.table, str) else entity.table
        self.level_map = _build_usage_map(
            entity.level_map,
            usage.level_map if usage else {},
            lambda e, u=None: LevelTraverser(e, u, dim_type=dim_type),
            resolve_source=lambda src: entity.level_map[src],
        )

    @property
    def levels(self) -> Iterable["LevelTraverser"]:
        """Returns a generator that yields all Levels under this Hierarchy."""
        return self.level_map.values()

    @property
    def properties(self) -> Iterable["PropertyTraverser"]:
        """Returns a generator that yields all Properties under this Hierarchy."""
        return chain(*(item.properties for item in self.levels))

    @property
    def default_member(self) -> Optional[tuple["LevelTraverser", Primitive]]:
        """If defined, returns a tuple containing a Level and a default member ID.

        These are used in queries to apply a restriction when the parent Dimension
        is not part of the request.
        """
        if self._entity.default_member is None:
            return None

        level_name, member = self._entity.default_member
        level = self.get_level(level_name)
        caster = level.key_type.get_caster()
        return level, caster(member)

    def get_level(self, name: str) -> "LevelTraverser":
        """Retrieve a Level from this Cube by its name."""
        return _find_by_name(self.levels, name, "Level")

    def get_property(self, name: str) -> "PropertyTraverser":
        """Retrieve a Property from this Cube by its name."""
        return _find_by_name(self.properties, name, "Property")


class LevelTraverser(EntityUsageTraverser[Level, LevelUsage]):
    """Allow seamless aliasing of values between a Level and a LevelUsage."""

    count: int
    depth: int
    key_column: str
    key_type: DataType
    name_column_map: Mapping[str, str]
    property_map: Mapping[str, "PropertyTraverser"]
    dim_type: DimensionType

    def __init__(
        self,
        entity: "Level",
        usage: Optional["LevelUsage"] = None,
        *,
        dim_type: DimensionType,
    ):
        super().__init__(entity, usage)

        self.dim_type = dim_type
        self.property_map = _build_usage_map(
            entity.property_map,
            usage.property_map if usage else {},
            lambda e, u=None: PropertyTraverser(e, u),
            resolve_source=lambda src: entity.property_map[src],
        )

    @property
    def time_scale(self) -> Optional[TimeScale]:
        """If from a Time dimension, return the time scale this Level represents."""
        if self.dim_type is not DimensionType.TIME:
            return None
        return TimeScale.from_str(self._entity.time_scale or self.name)

    @property
    def type_caster(self) -> Callable[[str], Primitive]:
        """Return the function that converts values of the same key_type into its type."""
        return self.key_type.get_caster()

    @property
    def properties(self) -> Iterable["PropertyTraverser"]:
        """Return a generator that yields all Properties under this Level."""
        return self.property_map.values()

    def get_name_column(self, locale: str = DEFAULT_LOCALE) -> Optional[str]:
        """Return the matching `name_column` of this Level for a certain locale."""
        return self._entity.get_name_column(locale)


class PropertyTraverser(EntityUsageTraverser[Property, PropertyUsage]):
    """Allows seamless aliasing of values between a Property and a PropertyUsage."""

    key_column_map: Mapping[str, str]
    key_type: DataType

    def get_key_column(self, locale: str = DEFAULT_LOCALE) -> str:
        """Return the matching `key_column` of this Property for a certain locale."""
        return self._entity.get_key_column(locale)


def _build_usage_map(
    entity_map: Mapping[str, EntityType],
    usage_map: Mapping[str, UsageType],
    ctor: Callable[[EntityType, Optional[UsageType]], T],
    *,
    resolve_source: Callable[[str], EntityType],
) -> OrderedDict[str, T]:
    """Construct an OrderedDict of traversers from an entity map and optional usage map.

    When a usage map is provided, it remaps each usage to its source entity
    using `resolve_source` and constructs the traverser with both entity and
    usage. When no usage map is provided (or it's empty), traversers are built
    from the original entities alone.

    - entity_map: base objects keyed by their canonical names
    - usage_map: usage overrides keyed by usage name
    - ctor: factory that accepts (entity, usage|None) and returns a traverser
    - resolve_source: function mapping a usage.source string to the base entity
    """
    if not usage_map:
        return OrderedDict((name, ctor(item, None)) for name, item in entity_map.items())
    return OrderedDict(
        (name, ctor(resolve_source(item.source), item)) for name, item in usage_map.items()
    )


def _find_by_name(iterable: Iterable[Named], name: str, kind: str) -> Named:
    """Return the first item in `iterable` whose `.name` matches.

    Raises InvalidEntityName(kind, name) when no match is found.
    """
    try:
        return next(item for item in iterable if item.name == name)
    except StopIteration:
        raise InvalidEntityName(kind, name) from None


def _get_shared_dimension(shared_map: Mapping[str, T], name: str) -> T:
    """Retrieve a shared Dimension by name or raise a usage error.

    This is used to resolve a `DimensionUsage` that references a shared
    Dimension by its `source` name.
    """
    try:
        return shared_map[name]
    except KeyError:
        raise EntityUsageError(name, "SharedDimension") from None


def _validate_entity_names(
    cube: str,
    item: Union["AnyMeasure", "EntityUsageTraverser[Entity, Usage]"],
    record: dict[str, str],
) -> None:
    """Verify the name of an entity is valid and unique within a cube.

    - Rejects names containing any token in INVALID_NAME_TOKENS.
    - Enforces uniqueness across Measures, Levels, and Properties per cube.
    Records the entity type in `record` keyed by the entity name.
    """
    if isinstance(item, (Measure, CalculatedMeasure)):
        origin = item
    else:
        origin = item._entity if item._usage is None else item._usage
    name = origin.name
    entity_type = type(origin).__name__

    if set(name) & INVALID_NAME_TOKENS:
        raise InvalidNameError(cube, entity_type, name)

    if name in record:
        raise DuplicatedNameError(cube, record[name], entity_type, name)

    record[name] = entity_type
