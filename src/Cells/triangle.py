from src.mesh import Mesh
import numpy as np

class Cell:
    def __init__(self, msh, n):
        self.oc = 0 #oil-count
        self.ngb = [] #neigbours
        self.id = str(n)
        self.cords = msh.cells[3].data[n]
        self.on = np.array()
        *self.center_point = Mesh.triangle_mid(self.cords)

    def neigbor_calculate(self, cell):
        if self.cords[0] in cell.cords and self.cords[1] in cell.cords:
            self.ngb.append(cell)
        elif self.cords[1] in cell.cords and self.cords[2] in cell.cords:
            self.ngb.append(cell)
        elif self.cords[0] in cell.cords and self.cords[2] in cell.cords:
            self.ngb.append(cell)

    def neighbor_chech(self, msh):
        if len(self.cords) == len(self.ngb):
            return self.ngb
        else:
            for c in msh.cells:
                self.neigbor_calculate(self,c)

    def area(self):
        return 0.5 * abs((self.cords[0][0] - self.cords[2][0])(self.cords[1][1] - self.cords[0][1]) - (self.cords[0][0] - self.cords[1][0])(self.cords[2][1] - self.cords[0][1]))
    
    def flux(self, a, b, u, v):
        if np.dot(v,u) > 0:
            return a * np.dot(v, u)
        else:
            return b * np.dot(v,u)
    
    def v(self):
        vx = self.center_point[1] - 0.2*self.point[0]
        vy = -1* self.point[0]
        return vx, vy
