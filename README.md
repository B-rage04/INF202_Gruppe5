# Oil Spill Simulation

A Python-based oil spill simulation tool using finite volume methods to model oil dispersion on water surfaces.

## Installation

Install modules:

```bash
python -m pip install pip-tools
pip-compile requirements.in   
pip install -r requirements.txt
```

## Development Setup

How to commit code destined for dev:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
pre-commit install --hook-type commit-msg
pre-commit run --all-files
```

This installs `pre-commit` and enables the `pre-commit` hooks in your local repository. The CI also runs `pre-commit` on every push/PR and branch protection should be enabled to block merges that fail checks.

If pre-commit fails:

```bash
pytest -q --maxfail=1  
tox 
isort .  
black .
```

## Features

### Oil Sources and Sinks

The simulation supports sources (oil injection) and sinks (oil removal) using a Gaussian distribution formula:

$$S_i = \frac{1}{2\pi\sigma^2} \exp\left(-\frac{\|x_S - x_{mid}\|^2}{2\sigma^2}\right)$$

The update formula with sources and sinks:
- $u_i^{n+1/2} = u_i^n + F_i^{(ngh_1,n)} + F_i^{(ngh_2,n)} + F_i^{(ngh_3,n)}$
- $u_i^{n+1} = u_i^{n+1/2} / (1 + \Delta t S_i^- - \Delta t S_i^+)$

where $S_i^-$ is the sink coefficient and $S_i^+$ is the source coefficient.

#### Oil Collection Ship (Sink)
- Configure ship position: `ship = [x, y]` in the geometry section
- The ship removes oil within radius 0.1 using Gaussian distribution (σ = 1.0)
- Example:

```toml
[geometry]
meshName = "Defaults/bay.msh"
borders = [[0, 0.45], [0, 0.2]]
ship = [0.45, 0.4]
```

#### Multiple Sources
- Add oil injection points: `source = [[x1, y1], [x2, y2], ...]`
- Each source injects oil within radius 0.1 using Gaussian distribution (σ = 1.0)
- Example:

```toml
[geometry]
meshName = "Defaults/bay.msh"
borders = [[0, 0.45], [0, 0.2]]
source = [[0.35, 0.45], [0.25, 0.35]]
```

#### Multiple Sinks
- Add additional oil removal points: `sink = [[x1, y1], [x2, y2], ...]`
- Each sink removes oil within radius 0.1 using Gaussian distribution (σ = 1.0)
- Example:

```toml
[geometry]
meshName = "Defaults/bay.msh"
borders = [[0, 0.45], [0, 0.2]]
ship = [0.45, 0.4]
sink = [[0.2, 0.3]]
```

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
ship = [0.45, 0.4]                # Optional: Oil collection ship position (sink)
source = [[0.35, 0.45]]           # Optional: Oil source positions (injection)
sink = [[0.2, 0.3]]               # Optional: Additional sink positions (removal)

[IO]
writeFrequency = 20       # Write images every N steps (0 = no video)
logName = "log"           # Optional: log file name (defaults to "logfile")

[video]
videoFPS = 5              # Frames per second for video output
totalOilFlag = false      # Optional: Show total oil amount in visualization
```

**Note:** 
- `writeFrequency` determines how often images are captured. Set to 0 to skip video creation.
- `logName` is optional and defaults to "logfile" if not provided.
- `totalOilFlag` is optional and defaults to false.
- The program will return an error if required sections or keys are missing.

## Project Structure

```
INF202_Gruppe5/
├── Defaults/              # Default configuration and mesh files
│   ├── bay.msh           # Default mesh geometry
│   └── input.toml        # Default simulation configuration
├── Input/                 # Example simulation configurations
│   ├── BaseSimConfig.toml
│   ├── HighRESSimConfig.toml
│   └── NoVidSimConfig.toml
├── Output/                # Simulation output (auto-generated)
│   ├── images/           # Generated visualization images
│   ├── videos/           # Generated simulation videos
│   └── log/              # Simulation logs
├── src/                   # Source code
│   ├── Cells/            # Cell classes for mesh elements
│   ├── mesh.py           # Mesh handling
│   ├── simulation.py     # Main simulation logic
│   ├── visualize.py      # Visualization functions
│   ├── video.py          # Video creation
│   └── SimManager.py     # Command-line interface
├── test/                  # Unit tests
├── main.py               # Entry point
└── README.md             # This file
```

