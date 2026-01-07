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

    def neigbor_calculate(self, cell):
        for i in range(len(self.cords)):
            for j in range(len(cell.cords)):
                if self.cords[i] in cell.cords and self.cords[j] in cell.cords:
                    if cell in self.ngb:
                        continue
                    else:
                        self.ngb.append(cell)
        
    def neighbor_check(self, msh):
        if len(self.cords) == len(self.ngb):
            return self.ngb
        else:
            for c in msh.cells:
                self.neigbor_calculate(self,c)

    
    def flux(self, a, b, u, v):
        if np.dot(v,u) > 0:
            return a * np.dot(v, u)
        else:
            return b * np.dot(v,u)
    
    def v(self):
        vx = self.center_point[1] - 0.2*self.point[0]
        vy = -1* self.point[0]
        return vx, vy
