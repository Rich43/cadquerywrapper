from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import cadquery as cq

from .validator import ValidationError, Validator


class SaveValidator:
    """Patch CadQuery save functions to apply printability validation."""

    def __init__(self, rules: dict | str | Path | Validator):
        if isinstance(rules, Validator):
            self.validator = rules
        else:
            self.validator = Validator(rules)
        self._patched: bool = False
        self._originals: list[tuple[Any, str, Callable]] = []

    @staticmethod
    def attach_model(obj: Any, model: dict) -> None:
        """Attach printability model data to a CadQuery object."""

        setattr(obj, "_printability_model", model)

    def _validate_obj(self, obj: Any) -> None:
        model = getattr(obj, "_printability_model", None)
        if model is None:
            return
        errors = self.validator.validate(model)
        if errors:
            raise ValidationError("; ".join(errors))

    def _wrap_function(self, func: Callable) -> Callable:
        def wrapper(obj, *args, **kwargs):
            self._validate_obj(obj)
            return func(obj, *args, **kwargs)

        return wrapper

    def enable(self) -> None:
        """Patch CadQuery saving functions to perform validation."""

        if self._patched:
            return

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
            self._originals.append((target, name, orig))
            setattr(target, name, self._wrap_function(orig))

        self._patched = True

    def disable(self) -> None:
        """Restore original CadQuery saving functions."""

        if not self._patched:
            return

        for target, name, orig in self._originals:
            setattr(target, name, orig)

        self._originals.clear()
        self._patched = False

__all__ = ["SaveValidator"]
