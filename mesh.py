class Mesh:
    def __init__(self):
        import meshio
        self.msh = meshio.read("bay.msh")
        self.cells = self.msh.cells[8:12] #Do not include the vortex cells
        self.points = self.msh.points