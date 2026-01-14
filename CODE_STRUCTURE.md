## How to read scores



---

OIL SPILL SIMULATION – MASTER CHECKLIST (FULL GRADE)

================================================
SECTION 1 – CORE PROBLEM UNDERSTANDING

[x] I understand that the task is to simulate oil transport on a 2D surface
[x] I understand that the oil follows a velocity field (advection problem)
[x] I understand the simulation is cell-based (finite volume style)
[x] I understand the physical problem is fictional but the algorithm is real
[x] I understand that accuracy + software quality are both graded

Domain & Initial Conditions

[x] Coordinate system is 2D (x, y)
[x] Origin (0, 0) is bottom-left of the map
[x] Mesh file used is bay.msh
[x] Oil initially centered at (0.35, 0.45)
[x] Initial oil distribution uses exponential formula
[x] Oil exists only in triangle cells
[x] Boundary (line) cells always contain zero oil

Fishing Grounds

[ ] Fishing grounds defined as:
x in [0.0, 0.45]
y in [0.0, 0.2]

[ ] I compute oil inside fishing grounds correctly
[ ] I log oil in fishing grounds over time

================================================
SECTION 2 – NUMERICAL SIMULATION DETAILS
Spatial Discretization

[x] I do NOT store u(x) continuously
[x] I store oil values per cell
[x] I evaluate oil at cell midpoints
[x] Each triangle cell has:
- 3 points
- 3 edges
- 3 neighbors

Cell Geometry (Triangle Cells)

[x] I compute cell midpoint correctly
[x] I compute triangle area correctly
[x] I compute outward-pointing normals
[x] Normals are unit length
[x] Normals point outward (angle < 90° rule)
[x] I compute scaled normals (nu = n * edge length)
[x] I do NOT recompute geometry every timestep

Cell Types

[x] Triangle cells:
- oil evolves over time

[x] Line cells:
- only represent boundaries
- oil is always zero
- never updated

Time Discretization

[x] I define total simulation time
[x] I define time step Δt
[x] I split time into N steps
[x] Oil only moves to neighbor cells per timestep

================================================
SECTION 3 – FLUX COMPUTATION (CRITICAL)
Velocity Field

[x] Velocity field is implemented exactly as given
[x] v(x, y) = (y - 0.2x, -x)
[x] Velocity evaluated at cell midpoints

Flux Function g(a, b, nu, v)

[ ] If dot(v, nu) > 0:
g = a * dot(v, nu)

[ ] Else:
g = b * dot(v, nu)

[] I do NOT swap signs incorrectly
[x] I use averaged velocity:
(v_i + v_ngh) / 2

Flux per Edge

[x] I compute flux per neighbor
[x] Flux formula includes:
- Δt
- cell area
- scaled normal
- correct oil values

Cell Update

[x] I sum fluxes from all 3 neighbors
[x] Update rule is applied exactly as given
[x] Only triangle cells are updated

================================================
SECTION 4 – SOURCES AND SINKS (SHIP)
Oil Collection Ship

[ ] Ship is optional
[ ] Ship defined in config file
[ ] geometry.ship = [x, y]
[ ] Ship radius = 0.1

Oil Removal Logic

[ ] Only cells whose midpoint is inside radius are affected
[ ] Oil removal uses uniform distribution
[ ] Standard deviation = 1
[ ] Oil is removed (sink)
[ ] No ship = no oil removal

Analysis Requirement

[ ] I tested multiple ship positions
[ ] I found a good ship location
[ ] I discussed this in the report

================================================
SECTION 5 – CONFIG FILE (TOML)
Reading Config Files

[x] Program reads .toml files
[ ] Program errors if file does not exist
[ ] Program errors if entries are missing
[ ] Program errors if entries are inconsistent

Required Structure

[ ] Structure EXACTLY matches provided figure
[ ] All names are spelled correctly
[ ] All sections exist

Optional Parameters

[ ] writeFrequency implemented
[ ] If writeFrequency missing → no video
[ ] logName default = "logfile"

================================================
SECTION 6 – COMMAND LINE INTERFACE
Config Selection

[ ] Default config = input.toml
[ ] -c file.toml works
[ ] --config file.toml works

Multiple Configs

[x] --find all works
[x] Program searches folder for configs
[x] Each config runs separately
[x] Results saved per config

Folder Selection

[ ] -f folder works
[ ] --folder folder works
[ ] --folder test --find all works

Safety

[x] Program does NOT overwrite src
[x] Program does NOT overwrite non-result folders

================================================
SECTION 7 – OUTPUT & VISUALIZATION

[x] Plot of final oil distribution
[x] Video of oil evolution over time
[ ] writeFrequency respected
[x] Images saved correctly

================================================
SECTION 8 – LOGGING

[Lasse] Logger used (not print)
[ ] All config parameters logged
[ ] Oil in fishing grounds logged over time
[ ] Log saved to file

================================================
SECTION 9 – SOFTWARE QUALITY (30%)
Code Design

[ ] Object-oriented design
[ ] Clear class responsibilities
[ ] Easy to extend (e.g. new cell type)
[ ] Geometry separated from logic
[ ] Simulation separated from IO

Efficiency

[x] No repeated geometry computation
[ ] No unnecessary loops
[ ] No unnecessary memory usage

Error Handling

[ ] Errors are caught
[ ] Error messages are meaningful

================================================
SECTION 10 – TESTING (VERY IMPORTANT)

[ ] ≥ 85% function coverage
[ ] Unit tests implemented
[ ] Integration tests implemented
[x] Edge-case tests implemented
[ ] Tests follow course design rules
[ ] Tests are meaningful

================================================
SECTION 11 – PROJECT STRUCTURE

[ ] Proper package layout
[x] requirements.txt exists
[ ] Only used packages listed
[ ] No virtual environments
[ ] No git folder included

================================================
SECTION 12 – DOCUMENTATION
Code Documentation

[ ] Docstrings for all classes
[ ] Docstrings for all methods
[ ] Docstrings for all modules

Report (LaTeX)

[ ] Written in LaTeX
[ ] Includes formulas
[ ] Includes images
[ ] Includes tables

Report Content

[ ] Problem description
[ ] Simulation explanation
[ ] User guide
[ ] Code structure
[ ] Agile development
[ ] Results and discussion

[ ] ~3 pages of text (excluding figures)

================================================
SECTION 13 – PRESENTATION (5 MIN)

[ ] Explain problem & motivation
[ ] Explain simulation approach
[ ] Explain code structure
[ ] Explain quality assurance
[ ] Show results
[ ] Convince examiners code is:
- correct
- maintainable
- extendable
- usable

================================================
SECTION 14 – DISCUSSION PREPARATION

[ ] I can explain any file in the code
[ ] I know where key logic lives
[ ] I understand numerical method
[ ] I can spot weaknesses
[ ] I can suggest improvements

================================================
SECTION 15 – FINAL SUBMISSION

[ ] ZIP file only
[ ] Correct folder name
[ ] Code included
[ ] Report PDF included
[ ] Git log included
[ ] bay.msh included

[ ] Code submitted by Jan 21, 14:00
[ ] Slides submitted by Jan 23, 23:59

================================================
