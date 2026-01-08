from .Cells.cell import Cell


class Mesh:
    def __init__(self, file: str):
        mesh = self.read_mesh(file)
        self.cells = self.cell_factory(mesh)

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


class Cell_factory:
    def cell_factory(mesh):
        """
        Creates cells
        """
        print(mesh)


maa = Mesh("bay.msh")
