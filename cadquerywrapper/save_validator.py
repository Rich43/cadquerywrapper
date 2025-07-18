from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import cadquery as cq

from .validator import validate, load_rules, ValidationError

_rules: dict | None = None
_patched: bool = False
_originals: list[tuple[Any, str, Callable]] = []


def _set_rules(rules: dict | str | Path) -> None:
    global _rules
    if isinstance(rules, (str, Path)):
        _rules = load_rules(rules)
    else:
        _rules = rules


def attach_model(obj: Any, model: dict) -> None:
    """Attach printability model data to a CadQuery object."""
    setattr(obj, "_printability_model", model)


def _validate_obj(obj: Any) -> None:
    if _rules is None:
        return
    model = getattr(obj, "_printability_model", None)
    if model is None:
        return
    errors = validate(model, _rules)
    if errors:
        raise ValidationError("; ".join(errors))


def _wrap_function(func: Callable) -> Callable:
    def wrapper(obj, *args, **kwargs):
        _validate_obj(obj)
        return func(obj, *args, **kwargs)

    return wrapper


def enable_validation(rules: dict | str | Path) -> None:
    """Patch CadQuery saving functions to perform printability validation."""

    global _patched
    if _patched:
        _set_rules(rules)
        return

    _set_rules(rules)

    to_patch = [
        (cq.exporters, "export"),
        (cq.cq, "export"),
        (cq.Shape, "exportStl"),
        (cq.Shape, "exportStep"),
        (cq.Shape, "exportBin"),
        (cq.Shape, "exportBrep"),
        (cq.Assembly, "export"),
        (cq.Assembly, "save"),
    ]

    for target, name in to_patch:
        orig = getattr(target, name)
        _originals.append((target, name, orig))
        setattr(target, name, _wrap_function(orig))

    _patched = True


__all__ = ["enable_validation", "attach_model"]
