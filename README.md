# CadQueryWrapper

CadQueryWrapper is a lightweight wrapper around [CadQuery/cadquery](https://github.com/CadQuery/cadquery). It provides a small validator for checking model parameters against 3D printer rules.

## Usage

```python
from cadquerywrapper.validator import load_rules, validate
from cadquerywrapper import enable_validation, attach_model

rules = load_rules("cadquerywrapper/rules/bambu_printability_rules.json")
model = {"minimum_wall_thickness_mm": 0.6}
errors = validate(model, rules)

# enable validation for CadQuery save functions
enable_validation(rules)

# attach printability parameters to an object
wp = cadquery.Workplane().box(1, 1, 1)
attach_model(wp, model)
# exporting will raise ValidationError if parameters fail
wp.export("out.stl")
```
