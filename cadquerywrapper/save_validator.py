from __future__ import annotations

from pathlib import Path
from typing import Any

import trimesh

import cadquery as cq

from .validator import ValidationError, Validator, validate


class SaveValidator:
    """Wrapper around CadQuery save functions that performs validation."""

    def __init__(self, rules: dict | str | Path | Validator):
        if isinstance(rules, Validator):
            self.validator = rules
        else:
            self.validator = Validator(rules)

    @staticmethod
    def attach_model(obj: Any, model: dict) -> None:
        """Attach printability model data to a CadQuery object."""

        setattr(obj, "_printability_model", model)

    def _validate_obj(self, obj: Any) -> None:
        model = getattr(obj, "_printability_model", None)
        if model is None:
            return

        combined_model = dict(model)
        max_size = self.validator.rules.get("rules", {}).get("max_model_size_mm")
        if max_size is not None:
            try:
                bbox_obj = obj.val().BoundingBox()
            except Exception:  # pragma: no cover - val() may not exist
                bbox_obj = None
                if hasattr(obj, "BoundingBox"):
                    try:
                        bbox_obj = obj.BoundingBox()
                    except Exception:  # pragma: no cover - bounding box failure
                        bbox_obj = None
            if bbox_obj is not None:
                combined_model["max_model_size_mm"] = {
                    "X": bbox_obj.xlen,
                    "Y": bbox_obj.ylen,
                    "Z": bbox_obj.zlen,
                }

        errors = validate(combined_model, self.validator.rules)
        if errors:
            raise ValidationError("; ".join(errors))

    def _check_triangle_count(self, file_name: str | Path) -> None:
        """Validate mesh triangle count against configured limit."""

        limit = self.validator.rules.get("rules", {}).get("maximum_file_triangle_count")
        if limit is None:
            return

        mesh = trimesh.load_mesh(file_name)
        tri_count = int(len(mesh.faces))
        if tri_count > limit:
            raise ValidationError(f"Triangle count {tri_count} exceeds maximum {limit}")

    def export(self, obj: Any, *args: Any, **kwargs: Any) -> Any:
        """Validate ``obj`` and delegate to :func:`cadquery.exporters.export`."""

        self._validate_obj(obj)
        return cq.exporters.export(obj, *args, **kwargs)

    def cq_export(self, obj: Any, *args: Any, **kwargs: Any) -> Any:
        """Validate ``obj`` and delegate to :func:`cadquery.export`."""

        self._validate_obj(obj)
        return cq.export(obj, *args, **kwargs)

    def export_stl(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Validate ``shape`` and call ``exportStl``."""

        self._validate_obj(shape)
        shape.exportStl(*args, **kwargs)
        file_name = None
        if args:
            file_name = args[0]
        file_name = kwargs.get("fileName", file_name)
        if file_name is not None:
            self._check_triangle_count(file_name)

    def export_step(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Validate ``shape`` and call ``exportStep``."""

        self._validate_obj(shape)
        shape.exportStep(*args, **kwargs)

    def export_bin(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Validate ``shape`` and call ``exportBin``."""

        self._validate_obj(shape)
        shape.exportBin(*args, **kwargs)

    def export_brep(self, shape: cq.Shape, *args: Any, **kwargs: Any) -> None:
        """Validate ``shape`` and call ``exportBrep``."""

        self._validate_obj(shape)
        shape.exportBrep(*args, **kwargs)

    def assembly_export(self, assembly: cq.Assembly, *args: Any, **kwargs: Any) -> None:
        """Validate ``assembly`` and call ``Assembly.export``."""

        self._validate_obj(assembly)
        assembly.export(*args, **kwargs)

    def assembly_save(self, assembly: cq.Assembly, *args: Any, **kwargs: Any) -> None:
        """Validate ``assembly`` and call ``Assembly.save``."""

        self._validate_obj(assembly)
        assembly.save(*args, **kwargs)


__all__ = ["SaveValidator"]
