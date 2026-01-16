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

**Parameters for all sources/sinks:**
- **Radius**: 0.1 (cells within this distance are affected)
- **σ (sigma)**: 1.0 (standard deviation of Gaussian distribution)
- **Strength**: 100.0 for sinks (oil removal), 50.0 for sources (oil injection)

#### Oil Collection Ship (Sink)
The ship is a single oil removal device positioned at one location.
- Configure ship position: `ship = [x, y]` in the geometry section
- Set to empty `[]` to disable the ship
- The ship removes oil from cells near its position using a Gaussian distribution
- Example:

```toml
[geometry]
ship = [0.45, 0.4]    # Position: x=0.45, y=0.4
```

#### Multiple Oil Sources
Multiple oil injection points that add oil to the system.
- Configure sources: `source = [[x1, y1], [x2, y2], ...]`
- Each source injects oil near its position using a Gaussian distribution
- Set to empty `[]` for no sources
- Example with 2 sources:

```toml
[geometry]
source = [[0.35, 0.45], [0.25, 0.35]]
```

#### Multiple Oil Sinks
Multiple oil removal devices in addition to the ship.
- Configure additional sinks: `sink = [[x1, y1], [x2, y2], ...]`
- Each sink removes oil from cells near its position using a Gaussian distribution
- Set to empty `[]` for no additional sinks
- Example with 1 sink:

```toml
[geometry]
sink = [[0.2, 0.3]]
```

#### Complete Example with All Features
```toml
[geometry]
meshName = "Defaults/bay.msh"
borders = [[0, 0.45], [0, 0.2]]
ship = [0.45, 0.4]              # Oil collection ship
source = [[0.35, 0.45], [0.2, 0.2]]    # Oil sources
sink = [[0.1, 0.3], [0.6, 0.4]]        # Additional oil sinks
```

The simulation will log which sources and sinks are active:
```
Ship at [0.45, 0.4]: 186 cells affected
Oil source 0 at [0.35, 0.45]: 182 cells affected
Oil source 1 at [0.2, 0.2]: 178 cells affected
Sink 0 at [0.1, 0.3]: 156 cells affected
Sink 1 at [0.6, 0.4]: 165 cells affected
Configuration summary: 1 ship, 2 sources, 2 sinks
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
meshName = "Defaults/bay.msh"           # Path to mesh file
borders = [[0, 0.45], [0, 0.2]]         # Boundary constraints
ship = [0.45, 0.4]                      # Optional: Single ship position [x, y] or [] to disable
source = [[0.35, 0.45], [0.25, 0.35]]   # Optional: Array of source positions [[x1, y1], [x2, y2], ...] or []
sink = [[0.2, 0.3]]                     # Optional: Array of sink positions [[x1, y1], [x2, y2], ...] or []

[IO]
writeFrequency = 20       # Write images every N steps (0 = no video)
logName = "log"           # Optional: log file name (defaults to "logfile")

[video]
videoFPS = 5              # Frames per second for video output
totalOilFlag = false      # Optional: Show total oil amount in visualization
```

**Notes:**
- All sources/sinks are optional. Set to `[]` to disable or omit the line entirely.
- The `ship` parameter expects a single `[x, y]` position.
- The `source` and `sink` parameters expect arrays of positions: `[[x1, y1], [x2, y2], ...]`.
- Visualization includes markers for all active sources (green ▲), sinks (orange ▼), and ship (red ■).
- Configuration is logged when the simulation starts, showing which sources and sinks are active.

**Note:** 
- `writeFrequency` determines how often images are captured. Set to 0 to skip video creation.
- `logName` is optional and defaults to "logfile" if not provided.
- `totalOilFlag` is optional and defaults to false.
- The program will return an error if required sections or keys are missing.

## Project Structure

```
INF202_Gruppe5/
├── Defaults/             
│   ├── bay.msh           
│   └── input.toml        
├── Input/                
│   ├── mesh/
│   ├── toml/
├── Output/               
│   ├── [Name_toml_file]
│   │   └── videos/       
│   │   └── images/             
│   └── log/              
├── src/                  
│   ├── Geometry/         
│   │   └──       
│   ├── IO/        
│   │   └──         
│   ├── Simulation/               
│   │   └──         
├── test/        
├── rapport/             
├── main.py      
├── image.png #BATMELON 
└── README.md            
```

