from src.mesh import Mesh
from src.Cells.cell import Cell
from src.visualize import Visualizer

msh = Mesh("bay.msh")

cells = []
for i in range( len(msh.triangles)):
    cells.append(Cell(msh, i))


oil_val = []

for cel in cells:
    oil_val.append(cel.oil)

vs = Visualizer(msh)
vs.plotting(oil_val)