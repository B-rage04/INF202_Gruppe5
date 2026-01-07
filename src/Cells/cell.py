from src.mesh import Mesh
import numpy as np


class Cell:
    def __init__(self, msh, n):
        self.oc = 0 #oil-count
        self.ngb = [] #neigbours
        self.id = str(n)
        self.cords = msh.cells[3].data[n]
        self.on = np.array()
        self.center_point = Mesh.triangle_mid(self.cords)

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
