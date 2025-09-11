# extensible.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable

from .schemas import SCHEMA
# If you're using the earlier schema registry:
#from .serialization_schema import SCHEMA



class Extensible:
    # class-level registry of declared extras
    _declared_extras: Dict[str, Any] = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        # each subclass gets its own dict (copy, not shared)
        cls._declared_extras = dict(getattr(cls, "_declared_extras", {}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # cooperative
        self.extras: Dict[str, Any] = {}
        # seed declared defaults
        for k, default in type(self)._declared_extras.items():
            self.extras[k] = _copy_default(default)

    @classmethod
    def define_ext(
        cls,
        name: str,
        *,
        typ: type | None = None,
        default: Any = None,
        overwrite: bool = False,
    ) -> None:
        """
        Declare an extra field on the CLASS.

        Args:
            name: field name
            typ: Python type (used to update schema registry)
            default: default value for new instances
            overwrite: if True, replaces existing definition
        """
        if name in getattr(cls, "__dataclass_fields__", {}):
            raise AttributeError(f"{name!r} already exists on {cls.__name__}")

        already = hasattr(cls, name)
        if already and not overwrite:
            return

        # Attach descriptor
        setattr(cls, name, _ExtraField(name, default))
        cls._declared_extras[name] = default

        # Register with schema
        if typ is None and default is not None:
            typ = type(default)
        SCHEMA.register_extra(cls, name, typ or type(None))

    @classmethod
    def declared_extras(cls) -> Dict[str, Any]:
        return dict(getattr(cls, "_declared_extras", {}))


class _ExtraField:
    def __init__(self, name: str, default: Any):
        self.name = name
        self.default = default
    def __get__(self, obj, owner):
        if obj is None:
            return self
        return obj.extras.get(self.name, self.default)
    def __set__(self, obj, value):
        obj.extras[self.name] = value


def _copy_default(v: Any) -> Any:
    if isinstance(v, (list, dict, set)):
        return v.copy()
    return v
    # avoid shared mutable defaults
    if isinstance(v, (list, dict, set)):
        return v.copy()
    return v