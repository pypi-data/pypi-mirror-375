# openearth

Python client for the OpenEarth API

## Install (local)
```bash
pip install -e .
```

## Usage
```python
from openearth import OpenEarth

oe = OpenEarth(base_url="http://localhost:8000")
print(oe.health())
print(oe.rain("Did it rain in rural Iowa yesterday?"))
print(oe.wildfire("Wildfire near Santa Rosa today?"))
oe.close()
```
