# CadQueryWrapper

CadQueryWrapper is a lightweight wrapper around [CadQuery/cadquery](https://github.com/CadQuery/cadquery). It provides a small validator for checking model parameters against 3D printer rules.

## Usage

```python
from cadquerywrapper import Validator, SaveValidator

# load rules and create a validator
validator = Validator("cadquerywrapper/rules/bambu_printability_rules.json")

model = {"minimum_wall_thickness_mm": 0.6}
errors = validator.validate(model)

# enable validation for CadQuery save functions
save_validator = SaveValidator(validator)
save_validator.enable()

# attach printability parameters to an object
wp = cadquery.Workplane().box(1, 1, 1)
SaveValidator.attach_model(wp, model)
# exporting will raise ValidationError if parameters fail
wp.export("out.stl")
```

## Code Style
See [CODE_STYLE.md](CODE_STYLE.md) for contribution guidelines. Monkey patching is prohibited.
