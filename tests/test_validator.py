import importlib
import sys
import types
from pathlib import Path

import pytest

# Provide stub cadquery module before importing package modules
_dummy_cq = types.ModuleType("cadquery")

_dummy_cq.export_calls = []


def _export(obj, *args, **kwargs):
    _dummy_cq.export_calls.append((obj, args, kwargs))


_dummy_cq.export = _export
_dummy_cq.exporters = types.SimpleNamespace()
_dummy_cq.exporters.calls = []


def _exporter(obj, *args, **kwargs):
    _dummy_cq.exporters.calls.append((obj, args, kwargs))


_dummy_cq.exporters.export = _exporter


class DummyShape:
    def __init__(self):
        self.called = []

    def exportStl(self, *args, **kwargs):
        self.called.append(("exportStl", args, kwargs))

    def exportStep(self, *args, **kwargs):
        self.called.append(("exportStep", args, kwargs))

    def exportBin(self, *args, **kwargs):
        self.called.append(("exportBin", args, kwargs))

    def exportBrep(self, *args, **kwargs):
        self.called.append(("exportBrep", args, kwargs))


class DummyAssembly:
    def __init__(self):
        self.called = []

    def export(self, *args, **kwargs):
        self.called.append(("export", args, kwargs))

    def save(self, *args, **kwargs):
        self.called.append(("save", args, kwargs))


_dummy_cq.Shape = DummyShape
_dummy_cq.Assembly = DummyAssembly

sys.modules.setdefault("cadquery", _dummy_cq)

from cadquerywrapper.validator import Validator, load_rules, validate
from cadquerywrapper.save_validator import SaveValidator, ValidationError


RULES_PATH = Path("cadquerywrapper/rules/bambu_printability_rules.json")


def test_load_rules():
    rules = load_rules(RULES_PATH)
    assert rules["printer"] == "Bambu Labs"


def test_validate_errors():
    rules = {"rules": {"minimum_wall_thickness_mm": 0.8}}
    model = {"minimum_wall_thickness_mm": 0.5}
    errors = validate(model, rules)
    assert errors == ["Minimum wall thickness mm 0.5 is below minimum 0.8"]


def test_validator_from_file():
    validator = Validator(RULES_PATH)
    assert "minimum_wall_thickness_mm" in validator.rules["rules"]


def test_validator_validate_raises():
    validator = Validator({"rules": {"minimum_wall_thickness_mm": 0.8}})
    with pytest.raises(ValidationError):
        validator.validate({"minimum_wall_thickness_mm": 0.5})


def test_save_validator_delegates_and_validates():
    sv = SaveValidator({"rules": {"minimum_wall_thickness_mm": 0.8}})
    obj = DummyShape()
    SaveValidator.attach_model(obj, {"minimum_wall_thickness_mm": 0.9})
    sv.export(obj)
    assert _dummy_cq.exporters.calls[-1][0] is obj


def test_save_validator_invalid_raises():
    sv = SaveValidator({"rules": {"minimum_wall_thickness_mm": 0.8}})
    obj = DummyShape()
    SaveValidator.attach_model(obj, {"minimum_wall_thickness_mm": 0.1})
    with pytest.raises(ValidationError):
        sv.export_stl(obj, "out.stl")
