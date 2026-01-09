from src.Cells.cell_factory import Cell_factory

 
class Mesh:
    def __init__(self, file: str):
        self.msh = self.read_mesh(file)
        self.points = self.msh.points
        self.triangles = self.msh.cells_dict["triangle"]
        self.cells = Cell_factory(self.msh)

    def read_mesh(self, file: str):
        """
        Reads Mesh file
        """
        import meshio

        return meshio.read(file)
