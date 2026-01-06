class Mesh:
    def __init__(self, file):
        import meshio
        self.msh = meshio.read(file)
        self.cells = self.msh.cells[8:12] #Do not include the vortex cells
        self.points = self.msh.points
    
    def visialize(self):
        import matplotlib.pyplot as plt

        points = self.msh.points
        triangles = self.msh.cells_dict["triangle"]

        plt.triplot(points[:, 0], points[:, 1], triangles)
        plt.show()