from __future__ import annotations

from pathlib import Path
from typing import Any

import cadquery as cq

from .save_validator import SaveValidator
from .validator import ValidationError, Validator


class CadQueryWrapper:
    """Main interface combining :class:`Validator` and :class:`SaveValidator`."""

    def __init__(self, rules: dict | str | Path):
        self.validator = Validator(rules)
        self.saver = SaveValidator(self.validator)

    @staticmethod
    def attach_model(obj: Any, model: dict) -> None:
        """Attach printability model data to ``obj``."""

        SaveValidator.attach_model(obj, model)

    def validate(self, model: dict) -> None:
        """Validate ``model`` using the underlying :class:`Validator`."""

        self.validator.validate(model)

    def export(self, obj: Any, *args: Any, **kwargs: Any) -> Any:
        """Delegate to :meth:`SaveValidator.export`."""

        return self.saver.export(obj, *args, **kwargs)

    def cq_export(self, obj: Any, *args: Any, **kwargs: Any) -> Any:
        """Delegate to :meth:`SaveValidator.cq_export`."""

        return self.saver.cq_export(obj, *args, **kwargs)

    def export_stl(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.export_stl`."""

        self.saver.export_stl(shape, *args, **kwargs)

    def export_step(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.export_step`."""

        self.saver.export_step(shape, *args, **kwargs)

    def export_bin(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.export_bin`."""

        self.saver.export_bin(shape, *args, **kwargs)

    def export_brep(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.export_brep`."""

        self.saver.export_brep(shape, *args, **kwargs)

    def assembly_export(self, assembly: cq.Assembly, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.assembly_export`."""

        self.saver.assembly_export(assembly, *args, **kwargs)

    def assembly_save(self, assembly: cq.Assembly, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.assembly_save`."""

        self.saver.assembly_save(assembly, *args, **kwargs)


__all__ = ["CadQueryWrapper"]
