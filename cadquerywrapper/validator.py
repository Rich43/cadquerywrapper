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
