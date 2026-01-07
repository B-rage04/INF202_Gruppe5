class Mesh:
    def __init__(self, file):
        import meshio
        self.mesh = meshio.read(file)
        self.triangles = self.mesh.cells_dict["triangle"]
        self.points = self.mesh.points
    
    def triangle_mid(self):
        pts = self.points[self.cells]
        return pts.mean(axis=1)

    def triangle_area(self):
        point = self.points[self.triangles]
        x1, y1 = point[:, 0, 0], point[:, 0, 1]
        x2, y2 = point[: 1, 0], point[:, 1, 1]
        x3, y3 = point[: 2, 0], point[:, 2, 1]
        return 0.5*abs((x1 - x3)*(y2 - y1) - (x1 - x2)*(y3 - y1))
    
    def common_data(self):
        print(self.triangles[0])
        print(self.points[0])

maa = Mesh("bay.msh")
maa.common_data()