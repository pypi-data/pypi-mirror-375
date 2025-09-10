import sys
import typing
import inspect
from functools import lru_cache
import types
from typing import (
    Optional,
    TypeVar,
    Callable,
    Union,
    Any,
)
from collections.abc import Sequence
from enum import Enum
from .exceptions import AutoTUIException

# namedtuple type - can't really bind this to anything, since tuple
# is too generic, and NamedTuple isn't a type
NT = TypeVar("NT")

# Generic type -- used elsewhere for function bindings
T = TypeVar("T")

# something with no arguments which when called
# prompts the user -- returns some value
PromptFunction = Callable[[], T]
OptionalPromptFunction = Callable[[], Optional[T]]
PromptFunctionorValue = Union[PromptFunction, T]

# A lot of these are helpers from:
# https://github.com/karlicoss/cachew/blob/f4db4a6c6609170642c6cd09d50b52ac4c0edec9/src/cachew/__init__.py#L144

# items that can serialized directly into JSON by json.dumps
PRIMITIVES = {
    str: type[str],
    int: type[int],
    float: type[float],
    bool: type[bool],
}

PrimitiveType = Union[str, int, float, bool, dict]


CONTAINERS = {
    list: type[list],
    set: type[set],
}


def cache(user_function):
    'Simple lightweight unbounded cache. Sometimes called "memoize".'
    return lru_cache(maxsize=None)(user_function)


# needed to check if we can type hint generics
# https://www.python.org/dev/peps/pep-0585/
# or have unions like X | Y
# https://www.python.org/dev/peps/pep-0604/
above_310 = sys.version_info.major >= 3 and sys.version_info.minor >= 10

AllowedContainers = Union[list[T], set[T]]


def add_to_container(container: AllowedContainers, item: T) -> AllowedContainers:
    if isinstance(container, list):
        container.append(item)
    elif isinstance(container, set):
        container.add(item)
    else:
        raise RuntimeError(
            f"{type(container)} is not a list/set, not sure how to add to"
        )
    return container


from typing import Type


@cache
def get_union_args(cls: Type) -> Optional[tuple[list[type[Any]], bool]]:
    """
    >>> get_union_args(Union[str, int])
    ([<class 'str'>, <class 'int'>], False)
    >>> get_union_args(Optional[str])
    ([<class 'str'>], True)
    >>> get_union_args(str)
    """
    is_union_type = False
    if above_310 and typing.get_origin(cls) == types.UnionType:  # type: ignore[attr-defined]
        is_union_type = True
    if not is_union_type:
        origin_attr = getattr(cls, "__origin__", None)
        if origin_attr == Union:
            is_union_type = True

    if not is_union_type:
        return None

    args: Type = cls.__args__
    arg_list: list[type] = [e for e in args if e != type(None)]  # noqa: E721
    is_opt = type(None) in args
    assert len(arg_list) > 0
    return arg_list, is_opt


def resolve_annotation_single(cls: type) -> tuple[type, bool]:
    """
    Given the annotation type from a namedtuple, extract the type
    Doesn't allow Unions other than Optional/None Unions
    """
    is_optional = False
    res = get_union_args(cls)
    if res is not None:
        attr_types, is_optional = res
        if len(attr_types) == 1:
            cls = attr_types[0]
    return cls, is_optional


# an estimation, someone could always trick
# this if they really wanted to...
# this should be passed the NamedTuple object,
# not a class type
def is_namedtuple_obj(thing: Any) -> bool:
    _asdict = getattr(thing, "_asdict", None)
    return _asdict is not None and callable(_asdict)


# this should be passed a NamedTuple type (typically
# created with class(NamedTuple), not an instance
def is_namedtuple_type(thing: type) -> bool:
    return hasattr(thing, "_fields") and issubclass(thing, tuple) and callable(thing)


@cache
def enum_getval(enum: type[Enum], value: Any) -> Enum:
    """
    Given some value and an enum, get the corresponding Enum value

    Prefer the enum value to the enum attribute name
    since its more likely the value is dumped to JSON
    """
    try:
        return enum[value]
    except KeyError:
        pass
    try:
        return enum(value)
    except ValueError:
        pass
    raise AutoTUIException(
        f"Could not find {value} on Enumeration {enum} {enum.__members__.items()}"
    )


def is_union(cls: type) -> bool:
    return get_union_args(cls) is not None


def is_optional(cls: type) -> bool:
    res = get_union_args(cls)
    if res is None:
        return False
    _, is_opt = res
    assert isinstance(is_opt, bool)
    return is_opt


@cache
def get_collection_types(cls: type) -> tuple[type, type]:
    """
    >>> from typing import List, Set
    >>> get_collection_types(List[int])
    (<class 'list'>, <class 'int'>)
    >>> get_collection_types(Set[bool])
    (<class 'set'>, <class 'bool'>)
    """
    container_type: type = strip_generic(cls)
    # e.g. if List[int], internal[0] == int
    internal: Sequence[type] = typing.get_args(cls)  # requires 3.8
    assert (
        len(internal) == 1
    ), f"Expected 1 argument for {container_type}, got {len(internal)}"
    return container_type, internal[0]


@cache
def strip_generic(tp):
    """
    >>> from typing import List
    >>> strip_generic(List[int])
    <class 'list'>
    >>> strip_generic(str)
    <class 'str'>
    """
    GA = getattr(typing, "_GenericAlias")
    if isinstance(tp, GA):
        return tp.__origin__
    origin = typing.get_origin(tp)
    if origin is not None:
        return origin
    return tp


def is_primitive(cls: type) -> bool:
    """
    Whether or not this is a supported, serializable primitive

    >>> from typing import Dict
    >>> is_primitive(int)
    True
    >>> is_primitive(str)
    True
    >>> is_primitive(float)
    True
    >>> is_primitive(bool)
    True
    >>> is_primitive(set)
    False
    """
    return cls in PRIMITIVES


def is_supported_container(cls: type) -> bool:
    """
    >>> from typing import Dict, List, Set, Tuple
    >>> is_supported_container(List[int])
    True
    >>> is_supported_container(Set[str])
    True
    >>> is_supported_container(Tuple[int])
    False
    >>> is_supported_container(Dict[int, str])
    False
    """
    return strip_generic(cls) in CONTAINERS


@cache
def inspect_signature_dict(nt: Callable[..., Any]) -> dict[str, type]:
    return {
        name: param.annotation
        for name, param in inspect.signature(nt).parameters.items()
    }


@cache
def enum_attribute_dict(enum_cls: type[Enum]) -> dict[str, Enum]:
    if not hasattr(enum_cls, "__members__"):
        raise TypeError(
            f"Could not find __members__ attribute on Enumeration {enum_cls}. May have passed a value instead of a type?"
        )
    return dict(enum_cls.__members__.items())
