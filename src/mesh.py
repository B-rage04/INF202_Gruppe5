from .Cells.triangle import Triangle
from .Cells.line import Line

class Mesh:
    def __init__(self, file : str):
        self.mesh = self.read_mesh(file)
        self.cells = self.cell_factory(self.mesh)

    def read_mesh(self, file: str):
        """
        Reads Mesh file
        """
        import meshio
        return meshio.read(file)

    def cell_factory(self, mesh):
        """
        Uses the Cell Factory class to make new cells
        then assigns all static variables
        """

        cells = cell_factory(mesh)

        return cells


def cell_factory(mesh):
    """
    Creates cells with data from the mesh and returns as a list
    """

    cell_list = []
    
    for cell in mesh.cells:
        match cell.type:
            case "triangle":
                triangles = mesh.cells_dict["triangle"]
                for n in range(len(triangles)):
                    cell_list.append(Triangle(mesh, triangles[n]))
            case "line":
                lines = mesh.cells_dict["line"]
                for n in range(len(lines)):
                    cell_list.append(Line(mesh, lines[n]))


maa = Mesh("bay.msh")
print(maa.cells)