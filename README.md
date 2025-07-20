# CadQueryWrapper

CadQueryWrapper is a lightweight wrapper around [CadQuery/cadquery](https://github.com/CadQuery/cadquery). It provides a small validator for checking model parameters against 3D printer rules.

## Installation

If Python is not available on your system, run the helper script. Use the
Bash version on Linux and macOS or the batch version on Windows:

```bash
./install_python.sh
```

```cmd
install_python.bat
```
Both scripts are self-contained and do not require Python to run.

Then install the runtime dependencies with:

```bash
pip install -r requirements.txt
```

For running the test suite use the development requirements instead:

```bash
pip install -r requirements-dev.txt
```

## Usage

```python
from cadquerywrapper import CadQueryWrapper, ValidationError

# load rules and create a wrapper
wrapper = CadQueryWrapper("cadquerywrapper/rules/bambu_printability_rules.json")

model = {"minimum_wall_thickness_mm": 0.6}
try:
    wrapper.validate(model)
except ValidationError as exc:
    print("Model invalid:", exc)

wp = cadquery.Workplane().box(1, 1, 1)
wrapper.attach_model(wp, model)
# exporting will raise ValidationError if parameters fail
wrapper.export_stl(wp, "out.stl")
```

## Code Style
See [CODE_STYLE.md](CODE_STYLE.md) for contribution guidelines. Monkey patching is prohibited.
