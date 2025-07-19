"""Printability rules validation helpers."""

import json
from pathlib import Path


class ValidationError(Exception):
    """Raised when an object fails printability validation."""

    pass


def load_rules(rules_path: str | Path) -> dict:
    path = Path(rules_path)
    with path.open() as f:
        return json.load(f)


def validate(model: dict, rules: dict) -> list[str]:
    """Validate model parameters against printability rules.

    Parameters
    ----------
    model: dict
        A dictionary containing model parameters to validate. Keys should
        correspond to the rules names in the JSON file.
    rules: dict
        Dictionary loaded from a rules JSON file.

    Returns
    -------
    list[str]
        List of human readable error messages. Empty if model is valid.
    """
    errors = []
    rule_values = rules.get("rules", {})

    for key, value in rule_values.items():
        model_value = model.get(key)
        if model_value is None:
            continue
        if isinstance(value, dict):
            if isinstance(model_value, dict) and key == "max_model_size_mm":
                for axis, limit in value.items():
                    axis_value = model_value.get(axis)
                    if axis_value is None:
                        continue
                    if axis_value > limit:
                        msg = f"Model size {axis} {axis_value} exceeds maximum {limit}"
                        errors.append(msg)
            continue
        if model_value < value:
            msg = (
                f"{key.replace('_', ' ').capitalize()} {model_value} "
                f"is below minimum {value}"
            )
            errors.append(msg)
    return errors


class Validator:
    """Object oriented wrapper around :func:`validate`.

    The ``validate`` method will raise :class:`ValidationError` if the provided
    model data does not satisfy the stored rules.
    """

    def __init__(self, rules: dict | str | Path):
        if isinstance(rules, (str, Path)):
            self.rules = load_rules(rules)
        else:
            self.rules = rules

    @classmethod
    def from_file(cls, path: str | Path) -> "Validator":
        """Create a :class:`Validator` from a rules JSON file."""

        return cls(load_rules(path))

    def validate(self, model: dict) -> None:
        """Validate ``model`` against the stored ``rules``.

        Raises
        ------
        ValidationError
            If any of the model values are below the configured limits.
        """

        errors = validate(model, self.rules)
        if errors:
            raise ValidationError("; ".join(errors))


__all__ = ["ValidationError", "load_rules", "validate", "Validator"]


def is_manifold(shape: object) -> bool:
    """Return ``True`` if ``shape`` appears to be manifold."""
    try:
        if hasattr(shape, "isValid") and not shape.isValid():
            return False
    except Exception:
        return False
    try:
        if hasattr(shape, "isClosed") and not shape.isClosed():
            return False
    except Exception:
        return False
    return True


def shape_has_open_edges(shape: object) -> bool:
    """Return ``True`` if ``shape`` seems to have open edges."""
    if hasattr(shape, "hasOpenEdges"):
        try:
            return bool(shape.hasOpenEdges())
        except Exception:
            return True
    if hasattr(shape, "open_edges"):
        return bool(getattr(shape, "open_edges"))
    return False


def assembly_has_intersections(assembly: object) -> bool:
    """Return ``True`` if any solids in ``assembly`` intersect."""
    solids = []
    if hasattr(assembly, "solids"):
        try:
            solids = list(assembly.solids())
        except Exception:
            solids = []
    if not solids and hasattr(assembly, "children"):
        solids = [c for c in assembly.children if hasattr(c, "intersect")]
    for i, shape1 in enumerate(solids):
        for shape2 in solids[i + 1 :]:
            try:
                result = shape1.intersect(shape2)
            except Exception:
                continue
            if result is None:
                continue
            is_null = False
            if hasattr(result, "isNull"):
                try:
                    is_null = result.isNull()
                except Exception:
                    is_null = False
            elif hasattr(result, "Volume"):
                try:
                    is_null = result.Volume() == 0
                except Exception:
                    is_null = False
            if not is_null:
                return True
    return False


def assembly_minimum_clearance(assembly: object) -> float | None:
    """Return the minimum distance between solids in ``assembly``."""

    solids = []
    if hasattr(assembly, "solids"):
        try:
            solids = list(assembly.solids())
        except Exception:  # pragma: no cover - solids retrieval failure
            solids = []
    if not solids and hasattr(assembly, "children"):
        solids = [c for c in assembly.children if hasattr(c, "distTo")]

    min_dist: float | None = None
    for i, shape1 in enumerate(solids):
        for shape2 in solids[i + 1 :]:
            dists = []
            for shape_a, shape_b in ((shape1, shape2), (shape2, shape1)):
                method = (
                    getattr(shape_a, "distTo", None)
                    or getattr(shape_a, "distance", None)
                    or getattr(shape_a, "Distance", None)
                )
                if callable(method):
                    try:
                        d = float(method(shape_b))
                    except Exception:  # pragma: no cover - distance failure
                        continue
                    dists.append(d)
            if not dists:
                continue
            pair_dist = min(dists)
            if min_dist is None or pair_dist < min_dist:
                min_dist = pair_dist
    return min_dist


def shape_max_overhang_angle(
    shape: object, z_dir: tuple[float, float, float] = (0.0, 0.0, 1.0)
) -> float | None:
    """Return the maximum overhang angle of ``shape`` in degrees."""

    faces = []
    for attr in ("faces", "Faces", "all_faces"):
        getter = getattr(shape, attr, None)
        if callable(getter):
            try:
                faces = list(getter())
            except Exception:  # pragma: no cover - faces failure
                faces = []
            if faces:
                break
        elif isinstance(getter, (list, tuple)):
            faces = list(getter)
            break
    if not faces:
        return None

    import math

    z_len = math.sqrt(sum(c * c for c in z_dir)) or 1.0
    z_axis = tuple(c / z_len for c in z_dir)
    max_angle = 0.0

    for face in faces:
        normal = None
        if hasattr(face, "normalAt"):
            try:
                normal = face.normalAt()
            except Exception:  # pragma: no cover - normal failure
                normal = None
        if normal is None and hasattr(face, "normal"):
            normal = face.normal
        if normal is None:
            continue
        if hasattr(normal, "toTuple"):
            normal = normal.toTuple()
        if not isinstance(normal, (list, tuple)) or len(normal) != 3:
            continue
        n_len = math.sqrt(sum(c * c for c in normal)) or 1.0
        norm = tuple(c / n_len for c in normal)
        dot = abs(sum(a * b for a, b in zip(norm, z_axis)))
        dot = max(-1.0, min(1.0, dot))
        angle = math.degrees(math.acos(dot))
        if angle > max_angle:
            max_angle = angle

    return max_angle


__all__ += [
    "is_manifold",
    "shape_has_open_edges",
    "assembly_has_intersections",
    "assembly_minimum_clearance",
    "shape_max_overhang_angle",
]
