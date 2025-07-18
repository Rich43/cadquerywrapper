import json
from pathlib import Path

class ValidationError(Exception):
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
            # skip complex values like max_model_size_mm
            continue
        if model_value < value:
            errors.append(
                f"{key.replace('_', ' ').capitalize()} {model_value} is below minimum {value}"
            )
    return errors

__all__ = ["ValidationError", "load_rules", "validate"]
