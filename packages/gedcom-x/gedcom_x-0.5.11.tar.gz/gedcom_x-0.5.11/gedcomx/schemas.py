
from __future__ import annotations

import inspect
import sys
import types
from typing import Any, Dict, Union, get_args, get_origin, get_type_hints

try:
    # typing.Annotated may not exist in older 3.9 without typing_extensions
    from typing import Annotated  # type: ignore
except Exception:  # pragma: no cover
    Annotated = None  # type: ignore

_UNION_ORIGINS = tuple(
    x for x in (Union, getattr(types, "UnionType", None)) if x is not None
)

"""
======================================================================
 Project: Gedcom-X
 File:    schema.py
 Author:  David J. Cartwright
 Purpose: provide schema for serializatin and extensibility

 Created: 2025-08-25
 Updated:
   - 2025-09-03: _from_json_ refactor
   - 2025-09-09: added schema_class
   
======================================================================
"""





class Schema:
    """
    Central registry of fields for classes.

    - field_type_table: {"ClassName": {"field": <type or type-string>}}
    - URI/Resource preference in unions: URI > Resource > first-declared
    - Optional/None is stripped
    - Containers are preserved; their inner args are normalized recursively
    """

    def __init__(self) -> None:
        self.field_type_table: Dict[str, Dict[str, Any]] = {}
        self._extras: Dict[str, Dict[str, Any]] = {}
        self._toplevel: Dict[str, Dict[str, Any]] = {}

        # Optional binding to concrete classes to avoid name-only matching.
        self._uri_cls: type | None = None
        self._resource_cls: type | None = None

    # ──────────────────────────────
    # Bind concrete classes (optional)
    # ──────────────────────────────
    def set_uri_class(self, cls: type | None) -> None:
        self._uri_cls = cls

    def set_resource_class(self, cls: type | None) -> None:
        self._resource_cls = cls

    # ──────────────────────────────
    # Public API
    # ──────────────────────────────
    def register_class(
        self,
        cls: type,
        *,
        mapping: Dict[str, Any] | None = None,
        include_bases: bool = True,
        use_annotations: bool = True,
        use_init: bool = True,
        overwrite: bool = False,
        ignore: set[str] | None = None,
        toplevel: bool = False,
        toplevel_meta: Dict[str, Any] | None = None,
    ) -> None:
        """
        Introspect and register fields for a class.

        - reads class __annotations__ (preferred) or __init__ annotations
        - merges base classes (MRO) if include_bases=True
        - applies `mapping` overrides last
        - normalizes each type:
            strip Optional → prefer URI/Resource → collapse union to single
        """
        cname = cls.__name__
        ignore = ignore or set()

        def collect(c: type) -> Dict[str, Any]:
            d: Dict[str, Any] = {}
            if use_annotations:
                d.update(self._get_hints_from_class(c))
            if use_init and not d:
                d.update(self._get_hints_from_init(c))
            # filter private / ignored
            for k in list(d.keys()):
                if k in ignore or k.startswith("_"):
                    d.pop(k, None)
            # normalize each
            for k, v in list(d.items()):
                d[k] = self._normalize_field_type(v)
            return d

        fields: Dict[str, Any] = {}
        classes = list(reversed(cls.mro())) if include_bases else [cls]
        for c in classes:
            if c is object:
                continue
            fields.update(collect(c))

        if mapping:
            for k, v in mapping.items():
                fields[k] = self._normalize_field_type(v)

        if not overwrite and cname in self.field_type_table:
            self.field_type_table[cname].update(fields)
        else:
            self.field_type_table[cname] = fields

        if toplevel:
            self._toplevel[cname] = dict(toplevel_meta or {})

    def register_extra(
        self,
        cls: type,
        name: str,
        typ: Any,
        *,
        overwrite: bool = False,
    ) -> None:
        """Register a single extra field (normalized)."""
        cname = cls.__name__
        self.field_type_table.setdefault(cname, {})
        if not overwrite and name in self.field_type_table[cname]:
            return
        nt = self._normalize_field_type(typ)
        self.field_type_table[cname][name] = nt
        self._extras.setdefault(cname, {})[name] = nt

    def normalize_all(self) -> None:
        """Re-run normalization across all registered fields."""
        for _, fields in self.field_type_table.items():
            for k, v in list(fields.items()):
                fields[k] = self._normalize_field_type(v)

    # lookups
    def get_class_fields(self, type_name: str) -> Dict[str, Any] | None:
        return self.field_type_table.get(type_name)

    def set_toplevel(self, cls: type, *, meta: Dict[str, Any] | None = None) -> None:
        self._toplevel[cls.__name__] = dict(meta or {})

    def is_toplevel(self, cls_or_name: type | str) -> bool:
        name = cls_or_name if isinstance(cls_or_name, str) else cls_or_name.__name__
        return name in self._toplevel

    def get_toplevel(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._toplevel)

    def get_extras(self, cls_or_name: type | str) -> Dict[str, Any]:
        name = cls_or_name if isinstance(cls_or_name, str) else cls_or_name.__name__
        return dict(self._extras.get(name, {}))

    @property
    def json(self) -> dict[str, dict[str, str]]:
        return schema_to_jsonable(self)

    # ──────────────────────────────
    # Introspection helpers
    # ──────────────────────────────
    def _get_hints_from_class(self, cls: type) -> Dict[str, Any]:
        """Resolved type hints from class annotations; fallback to raw __annotations__."""
        module = sys.modules.get(cls.__module__)
        gns = module.__dict__ if module else {}
        lns = dict(vars(cls))
        try:
            return get_type_hints(cls, include_extras=True, globalns=gns, localns=lns)
        except Exception:
            return dict(getattr(cls, "__annotations__", {}) or {})

    def _get_hints_from_init(self, cls: type) -> Dict[str, Any]:
        """Parameter annotations from __init__ (excluding self/return/*args/**kwargs)."""
        fn = cls.__dict__.get("__init__", getattr(cls, "__init__", None))
        if not callable(fn):
            return {}
        module = sys.modules.get(cls.__module__)
        gns = module.__dict__ if module else {}
        lns = dict(vars(cls))
        try:
            hints = get_type_hints(fn, include_extras=True, globalns=gns, localns=lns)
        except Exception:
            hints = dict(getattr(fn, "__annotations__", {}) or {})
        hints.pop("return", None)
        hints.pop("self", None)
        # drop *args/**kwargs
        sig = inspect.signature(fn)
        for pname, p in list(sig.parameters.items()):
            if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                hints.pop(pname, None)
        return hints

    # ──────────────────────────────
    # Normalization pipeline
    #   strip Optional -> prefer URI/Resource -> collapse unions
    #   (recurse into containers)
    # ──────────────────────────────
    def _normalize_field_type(self, tp: Any) -> Any:
        tp = self._strip_optional(tp)
        tp = self._prefer_uri_or_resource_or_first(tp)
        tp = self._collapse_unions(tp)
        return tp

    # 1) Remove None from unions and strip Optional[...] wrappers
    def _strip_optional(self, tp: Any) -> Any:
        if isinstance(tp, str):
            return self._strip_optional_str(tp)

        origin = get_origin(tp)
        args = get_args(tp)

        if Annotated is not None and origin is Annotated:
            return self._strip_optional(args[0])

        if origin in _UNION_ORIGINS:
            kept = tuple(a for a in args if a is not type(None))  # noqa: E721
            if not kept:
                return Any
            if len(kept) == 1:
                return self._strip_optional(kept[0])
            # rebuild union (still a union; later steps will collapse)
            return self._rebuild_union_tuple(kept)

        if origin in (list, set, tuple, dict):
            sub = tuple(self._strip_optional(a) for a in args)
            return self._rebuild_param(origin, sub, fallback=tp)

        return tp

    # 2) In any union, prefer URI (if present), else Resource (if present), else first declared
    def _prefer_uri_or_resource_or_first(self, tp: Any) -> Any:
        if isinstance(tp, str):
            return self._prefer_str(tp)

        origin = get_origin(tp)
        args = get_args(tp)

        if Annotated is not None and origin is Annotated:
            return self._prefer_uri_or_resource_or_first(args[0])

        if origin in _UNION_ORIGINS:
            # order is as-declared in typing args
            names = [self._name_of(a) for a in args]
            if "URI" in names:
                i = names.index("URI")
                return args[i] if not isinstance(args[i], str) else "URI"
            if "Resource" in names:
                i = names.index("Resource")
                return args[i] if not isinstance(args[i], str) else "Resource"
            # no preferred present → pick first declared
            return self._prefer_uri_or_resource_or_first(args[0])

        if origin in (list, set, tuple, dict):
            sub = tuple(self._prefer_uri_or_resource_or_first(a) for a in args)
            return self._rebuild_param(origin, sub, fallback=tp)

        return tp

    # 3) If any union still remains (it shouldn't after step 2), collapse to first
    def _collapse_unions(self, tp: Any) -> Any:
        if isinstance(tp, str):
            return self._collapse_unions_str(tp)

        origin = get_origin(tp)
        args = get_args(tp)

        if Annotated is not None and origin is Annotated:
            return self._collapse_unions(args[0])

        if origin in _UNION_ORIGINS:
            return self._collapse_unions(args[0])  # first only

        if origin in (list, set, tuple, dict):
            sub = tuple(self._collapse_unions(a) for a in args)
            return self._rebuild_param(origin, sub, fallback=tp)

        return tp

    # ──────────────────────────────
    # Helpers: typing objects
    # ──────────────────────────────
    def _name_of(self, a: Any) -> str:
        if isinstance(a, str):
            return a.strip()
        if isinstance(a, type):
            return getattr(a, "__name__", str(a))
        # typing objects: str(...) fallback
        return str(a).replace("typing.", "")

    def _rebuild_union_tuple(self, args: tuple[Any, ...]) -> Any:
        # Rebuild a typing-style union from args (for 3.10+ this becomes A|B)
        out = args[0]
        for a in args[1:]:
            try:
                out = out | a  # type: ignore[operator]
            except TypeError:
                out = Union[(out, a)]  # type: ignore[index]
        return out

    def _rebuild_param(self, origin: Any, sub: tuple[Any, ...], *, fallback: Any) -> Any:
        try:
            return origin[sub] if sub else origin
        except TypeError:
            return fallback

    # ──────────────────────────────
    # Helpers: strings
    # ──────────────────────────────
    def _strip_optional_str(self, s: str) -> str:
        s = s.strip().replace("typing.", "")
        # peel Optional[...] wrappers
        while s.startswith("Optional[") and s.endswith("]"):
            s = s[len("Optional["):-1].strip()

        # Union[A, B, None]
        if s.startswith("Union[") and s.endswith("]"):
            inner = s[len("Union["):-1].strip()
            parts = [p for p in self._split_top_level(inner, ",") if p.strip() not in ("None", "NoneType", "")]
            return f"Union[{', '.join(parts)}]" if len(parts) > 1 else (parts[0].strip() if parts else "Any")

        # A | B | None
        if "|" in s:
            parts = [p.strip() for p in self._split_top_level(s, "|")]
            parts = [p for p in parts if p not in ("None", "NoneType", "")]
            return " | ".join(parts) if len(parts) > 1 else (parts[0] if parts else "Any")

        # containers: normalize inside
        for head in ("List", "Set", "Tuple", "Dict", "Annotated"):
            if s.startswith(head + "[") and s.endswith("]"):
                inner = s[len(head) + 1:-1]
                if head == "Annotated":
                    # Annotated[T, ...] -> T
                    items = self._split_top_level(inner, ",")
                    return self._strip_optional_str(items[0].strip()) if items else "Any"
                if head in ("List", "Set"):
                    elem = self._strip_optional_str(inner)
                    return f"{head}[{elem}]"
                if head == "Tuple":
                    elems = [self._strip_optional_str(p.strip()) for p in self._split_top_level(inner, ",")]
                    return f"Tuple[{', '.join(elems)}]"
                if head == "Dict":
                    kv = self._split_top_level(inner, ",")
                    k = self._strip_optional_str(kv[0].strip()) if kv else "Any"
                    v = self._strip_optional_str(kv[1].strip()) if len(kv) > 1 else "Any"
                    return f"Dict[{k}, {v}]"

        return s

    def _prefer_str(self, s: str) -> str:
        s = s.strip().replace("typing.", "")
        # Union[...] form
        if s.startswith("Union[") and s.endswith("]"):
            inner = s[len("Union["):-1]
            parts = [p.strip() for p in self._split_top_level(inner, ",")]
            if "URI" in parts:
                return "URI"
            if "Resource" in parts:
                return "Resource"
            return parts[0] if parts else "Any"

        # PEP 604 bars
        if "|" in s:
            parts = [p.strip() for p in self._split_top_level(s, "|")]
            if "URI" in parts:
                return "URI"
            if "Resource" in parts:
                return "Resource"
            return parts[0] if parts else "Any"

        # containers
        for head in ("List", "Set", "Tuple", "Dict", "Annotated"):
            if s.startswith(head + "[") and s.endswith("]"):
                inner = s[len(head) + 1:-1]
                if head == "Annotated":
                    items = self._split_top_level(inner, ",")
                    return self._prefer_str(items[0].strip()) if items else "Any"
                if head in ("List", "Set"):
                    elem = self._prefer_str(inner)
                    return f"{head}[{elem}]"
                if head == "Tuple":
                    elems = [self._prefer_str(p.strip()) for p in self._split_top_level(inner, ",")]
                    return f"Tuple[{', '.join(elems)}]"
                if head == "Dict":
                    kv = self._split_top_level(inner, ",")
                    k = self._prefer_str(kv[0].strip()) if kv else "Any"
                    v = self._prefer_str(kv[1].strip()) if len(kv) > 1 else "Any"
                    return f"Dict[{k}, {v}]"

        return s

    def _collapse_unions_str(self, s: str) -> str:
        s = s.strip().replace("typing.", "")
        if s.startswith("Union[") and s.endswith("]"):
            inner = s[len("Union["):-1]
            parts = [p.strip() for p in self._split_top_level(inner, ",")]
            return parts[0] if parts else "Any"
        if "|" in s:
            parts = [p.strip() for p in self._split_top_level(s, "|")]
            return parts[0] if parts else "Any"

        # containers
        for head in ("List", "Set", "Tuple", "Dict", "Annotated"):
            if s.startswith(head + "[") and s.endswith("]"):
                inner = s[len(head) + 1:-1]
                if head == "Annotated":
                    items = self._split_top_level(inner, ",")
                    return self._collapse_unions_str(items[0].strip()) if items else "Any"
                if head in ("List", "Set"):
                    elem = self._collapse_unions_str(inner)
                    return f"{head}[{elem}]"
                if head == "Tuple":
                    elems = [self._collapse_unions_str(p.strip()) for p in self._split_top_level(inner, ",")]
                    return f"Tuple[{', '.join(elems)}]"
                if head == "Dict":
                    kv = self._split_top_level(inner, ",")
                    k = self._collapse_unions_str(kv[0].strip()) if kv else "Any"
                    v = self._collapse_unions_str(kv[1].strip()) if len(kv) > 1 else "Any"
                    return f"Dict[{k}, {v}]"
        return s

    def _split_top_level(self, s: str, sep: str) -> list[str]:
        """
        Split `s` by single-char separator (',' or '|') at top level (not inside brackets).
        """
        out: list[str] = []
        buf: list[str] = []
        depth = 0
        for ch in s:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
            if ch == sep and depth == 0:
                out.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
        out.append("".join(buf).strip())
        return [p for p in out if p != ""]

# ──────────────────────────────
# Stringification helpers (JSON dump)
# ──────────────────────────────
def type_repr(tp: Any) -> str:
    if isinstance(tp, str):
        return tp

    origin = get_origin(tp)
    args = get_args(tp)

    if origin is None:
        if isinstance(tp, type):
            return tp.__name__
        return str(tp).replace("typing.", "")

    if origin in _UNION_ORIGINS:
        return " | ".join(type_repr(a) for a in args)

    if origin is list:
        return f"List[{type_repr(args[0])}]" if args else "List[Any]"
    if origin is set:
        return f"Set[{type_repr(args[0])}]" if args else "Set[Any]"
    if origin is tuple:
        return "Tuple[" + ", ".join(type_repr(a) for a in args) + "]" if args else "Tuple"
    if origin is dict:
        k, v = args or (Any, Any)
        return f"Dict[{type_repr(k)}, {type_repr(v)}]"

    return str(tp).replace("typing.", "")


def schema_to_jsonable(schema: Schema) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for cls_name, fields in schema.field_type_table.items():
        out[cls_name] = {fname: type_repr(ftype) for fname, ftype in fields.items()}
    return out





def schema_class(
    mapping: Dict[str, Any] | None = None,
    *,
    include_bases: bool = True,
    use_annotations: bool = True,
    use_init: bool = True,
    overwrite: bool = False,
    ignore: set[str] | None = None,
    toplevel: bool = False,
    toplevel_meta: Dict[str, Any] | None = None,
):
    """Decorator to register a class with SCHEMA at import time."""
    def deco(cls: type):
        SCHEMA.register_class(
            cls,
            mapping=mapping,
            include_bases=include_bases,
            use_annotations=use_annotations,
            use_init=use_init,
            overwrite=overwrite,
            ignore=ignore,
            toplevel=toplevel,
            toplevel_meta=toplevel_meta,
        )
        return cls
    return deco


# Singleton instance
SCHEMA = Schema()





