# CadQueryWrapper

CadQueryWrapper is a lightweight wrapper around [CadQuery/cadquery](https://github.com/CadQuery/cadquery). It provides a small validator for checking model parameters against 3D printer rules.

## Usage

```python
from cadquerywrapper.validator import load_rules, validate

rules = load_rules("cadquerywrapper/rules/bambu_printability_rules.json")
model = {"minimum_wall_thickness_mm": 0.6}
errors = validate(model, rules)
```
