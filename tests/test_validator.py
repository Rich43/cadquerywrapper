import importlib
import sys
import types
from pathlib import Path

import trimesh

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


class DummyBBoxShape(DummyShape):
    def __init__(self, x: float, y: float, z: float):
        super().__init__()
        self._bbox = types.SimpleNamespace(xlen=x, ylen=y, zlen=z)

    def val(self):
        return self

    def BoundingBox(self):
        return self._bbox


class SphereShape(DummyShape):
    def __init__(self, subdivisions: int):
        super().__init__()
        self.subdivisions = subdivisions

    def exportStl(self, file_name: str, *args, **kwargs):
        super().exportStl(file_name, *args, **kwargs)
        mesh = trimesh.creation.icosphere(subdivisions=self.subdivisions)
        mesh.export(file_name)


sys.modules.setdefault("cadquery", _dummy_cq)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cadquerywrapper.validator import Validator, load_rules, validate
from cadquerywrapper.save_validator import SaveValidator, ValidationError
from cadquerywrapper.project import CadQueryWrapper


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


def test_wrapper_delegates_and_validates():
    wrapper = CadQueryWrapper({"rules": {"minimum_wall_thickness_mm": 0.8}})
    obj = DummyShape()
    CadQueryWrapper.attach_model(obj, {"minimum_wall_thickness_mm": 0.9})
    wrapper.export_stl(obj)
    assert obj.called[-1][0] == "exportStl"


def test_wrapper_invalid_raises():
    wrapper = CadQueryWrapper({"rules": {"minimum_wall_thickness_mm": 0.8}})
    obj = DummyShape()
    CadQueryWrapper.attach_model(obj, {"minimum_wall_thickness_mm": 0.1})
    with pytest.raises(ValidationError):
        wrapper.export_stl(obj)


def test_validate_max_model_size_dict():
    rules = {"rules": {"max_model_size_mm": {"X": 1, "Y": 1, "Z": 1}}}
    model = {"max_model_size_mm": {"X": 2, "Y": 0.5, "Z": 0.5}}
    errors = validate(model, rules)
    assert errors == ["Model size X 2 exceeds maximum 1"]


def test_save_validator_model_too_large():
    rules = {"rules": {"max_model_size_mm": {"X": 1, "Y": 1, "Z": 1}}}
    sv = SaveValidator(rules)
    obj = DummyBBoxShape(2, 0.5, 0.5)
    SaveValidator.attach_model(obj, {})
    with pytest.raises(ValidationError):
        sv.export_stl(obj, "out.stl")


def test_save_validator_triangle_count(tmp_path):
    rules = {"rules": {"maximum_file_triangle_count": 100}}
    sv = SaveValidator(rules)
    shape = SphereShape(subdivisions=3)
    SaveValidator.attach_model(shape, {})
    file_name = tmp_path / "sphere.stl"
    with pytest.raises(ValidationError):
        sv.export_stl(shape, file_name)
