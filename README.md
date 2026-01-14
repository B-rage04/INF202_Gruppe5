



Install modules:

python -m pip install pip-tools

pip-compile requirements.in   
pip install -r requirements.txt

How to commit code destined for dev:


pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
pre-commit install --hook-type commit-msg
pre-commit run --all-files
pre-commit run --all-files


This installs `pre-commit` and enables the `pre-commit` hooks in your local repository. The CI also runs `pre-commit` on every push/PR and branch protection should be enabled to block merges that fail checks.


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
meshName = "Example/Geometry/bay.msh"
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
meshName = "Example/Geometry/bay.msh"
borders = [[0, 0.45], [0, 0.2]]
source = [0.35, 0.45]
```

Runtime toggles:
- Enable/disable ship sink in code: `sim.run_sim(..., use_ship_sink=True/False)`
- Enable/disable sources in code: `sim.run_sim(..., use_sources=True/False)`

## Command Line Usage

The program supports the following command line arguments:

### Run with default config (Defaults/input.toml):
```bash
python main.py
```

### Run a specific config file:
```bash
python main.py -c myconfig.toml
python main.py --config myconfig.toml
```
This reads from `myconfig.toml` in the current project folder

### Run a specific config file from a custom folder:
```bash
python main.py -f Input -c BaseSimConfig.toml
python main.py --folder Input --config BaseSimConfig.toml
```
This reads from `Input/BaseSimConfig.toml`

### Run all config files in a folder:
```bash
python main.py --find_all
python main.py -f Input --find_all
```
- `--find_all` runs all TOML files in the current folder (default)
- `-f Input --find_all` runs all TOML files in the `Input` folder
- Each simulation's results are stored in separate folders under `Output/` named after the config file

### Config File Structure

Each TOML config file must have the following required sections:

```toml
[settings]
nSteps = 500              # Number of simulation steps
tStart = 0.0              # Start time
tEnd = 0.5                # End time

[geometry]
meshName = "Defaults/bay.msh"     # Path to mesh file
borders = [[0, 0.45], [0, 0.2]]   # Boundary constraints
ship = [0.45, 0.4]                # Oil collection ship position

[IO]
writeFrequency = 20       # Write images every N steps (0 = no video)
logName = "log"           # Optional: log file name (defaults to "logfile")

[video]
videoFPS = 5              # Frames per second for video output
```

**Note:** 
- `writeFrequency` determines how often images are captured. Set to 0 to skip video creation.
- `logName` is optional and defaults to "logfile" if not provided.
- The program will return an error if required sections or keys are missing.

