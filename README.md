


insatll modules:

python -m pip install pip-tools

pip-compile requirements.in   
pip install -r requirements.txt

How to comit to code destined for dev:


- run: 
pre-commit run --all-files

- if failed:

pytest -q --maxfail=1  
tox 
isort .  
black .

Oil collection ship:
- Add an optional sink to remove oil near a ship.
- Configure ship position under geometry: `ship = [x, y]` in your sim config TOML.
- The ship removes oil uniformly within a radius of 0.1 around the position.
- Example:

```
[geometry]
meshName = "Exsample/Geometry/bay.msh"
borders = [[0, 0.45], [0, 0.2]]
ship = [0.35, 0.40]
```

Oil sources:
- Add an optional source to inject oil at a position.
- Configure source position under geometry: `source = [x, y]` in your sim config TOML.
- The source injects oil uniformly within a radius of 0.1 around the position.
- Example:

```
[geometry]
meshName = "Exsample/Geometry/bay.msh"
borders = [[0, 0.45], [0, 0.2]]
source = [0.35, 0.45]
```

Runtime toggles:
- Enable/disable ship sink in code: `sim.run_sim(..., use_ship_sink=True/False)`
- Enable/disable sources in code: `sim.run_sim(..., use_sources=True/False)`


