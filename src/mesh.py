from .Cells.cell import cell_factory

class Mesh:
    def __init__(self, file : str):
        self.msh = self.read_mesh(file)
        self.cells = self.cell_factory(self.msh)

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

#maa = Mesh("bay.msh")
#print(maa.cells)