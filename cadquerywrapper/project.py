from __future__ import annotations

from pathlib import Path
from typing import Any

from .logger import get_logger

logger = get_logger(__name__)

import cadquery as cq

from .save_validator import SaveValidator
from .validator import ValidationError, Validator


class CadQueryWrapper:
    """Main interface combining :class:`Validator` and :class:`SaveValidator`."""

    def __init__(self, rules: dict | str | Path):
        logger.debug("Initializing CadQueryWrapper with rules %s", rules)
        self.validator = Validator(rules)
        self.saver = SaveValidator(self.validator)

    @staticmethod
    def attach_model(obj: Any, model: dict) -> None:
        """Attach printability model data to ``obj``."""
        logger.debug("Attaching model %s to object %s", model, obj)
        SaveValidator.attach_model(obj, model)

    def validate(self, model: dict) -> None:
        """Validate ``model`` using the underlying :class:`Validator`."""
        logger.debug("Validating model %s", model)
        self.validator.validate(model)

    def export(self, obj: Any, *args: Any, **kwargs: Any) -> Any:
        """Delegate to :meth:`SaveValidator.export`."""
        logger.debug("Exporting %s", obj)
        return self.saver.export(obj, *args, **kwargs)

    def cq_export(self, obj: Any, *args: Any, **kwargs: Any) -> Any:
        """Delegate to :meth:`SaveValidator.cq_export`."""
        logger.debug("cq_export %s", obj)
        return self.saver.cq_export(obj, *args, **kwargs)

    def export_stl(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.export_stl`."""
        logger.debug("export_stl %s", shape)
        self.saver.export_stl(shape, *args, **kwargs)

    def export_step(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.export_step`."""
        logger.debug("export_step %s", shape)
        self.saver.export_step(shape, *args, **kwargs)

    def export_bin(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.export_bin`."""
        logger.debug("export_bin %s", shape)
        self.saver.export_bin(shape, *args, **kwargs)

    def export_brep(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.export_brep`."""
        logger.debug("export_brep %s", shape)
        self.saver.export_brep(shape, *args, **kwargs)

    def assembly_export(self, assembly: cq.Assembly, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.assembly_export`."""

        logger.debug("assembly_export %s", assembly)
        self.saver.assembly_export(assembly, *args, **kwargs)

    def assembly_save(self, assembly: cq.Assembly, *args: Any, **kwargs: Any) -> None:
        """Delegate to :meth:`SaveValidator.assembly_save`."""

        logger.debug("assembly_save %s", assembly)
        self.saver.assembly_save(assembly, *args, **kwargs)


__all__ = ["CadQueryWrapper"]
