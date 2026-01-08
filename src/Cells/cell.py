import numpy as np
from ..mesh import Mesh

from abc import ABC, abstractmethod

class Cell(ABC):
    def __init__(self, msh: Mesh, n):
        self.type = None
        self.id = n
        self.cords = [msh.msh.points[msh.msh.cells[n][i]] for i in range(len[msh.msh.points])]
        self.midpoint = self.find_midpoint()
        self.area = self.find_area()
        self.scaled_normal = []
        self.ngb = self.find_ngb()
        self.flow = self.find_flow()
        self.oil = self.find_oil()
        self.new_oil = None

    @abstractmethod
    def find_area(self):
        pass

    def find_midpoint(self):
        return np.array(
            [
                (self.cords[0][0] + self.cords[1][0] + self.cords[2][0]) / 3,
                (self.cords[0][1] + self.cords[1][1] + self.cords[2][1]) / 3,
                (self.cords[0][2] + self.cords[1][2] + self.cords[2][2]) / 3
            ]
        )

        self.oil = np.exp(
            -(
                np.linalg.norm(
                    np.array(
                        [
                            self.center_point[0],
                            self.center_point[1],
                            self.center_point[2],
                        ]
                    )
                    - np.array([0.35, 0.45, 0])
                )
                ** 2
            )
            / 0.01
        )

    def find_ngb(self, msh: Mesh):
        if len(self.cords) == len(self.ngb):
            return self.ngb
        else:
            for c in msh.cells:
                if c in self.ngb:
                    continue
                for i in range(len(self.cords)):
                    for j in range(len(c.cords)):
                        if self.cords[i] in c.cords and self.cords[j] in c.cords:
                            if c in self.ngb:
                                print(c + " was already in list of NGB")
                                continue
                            else:
                                self.ngb.append(c)
                                if self in c.ngb:
                                    continue
                                else:
                                    c.ngb.append(self)
                                
    def find_scaled_normales(self):
        pass

    def find_ngb(self):
        pass

    def find_flow(self):
        return np.array([self.midpoint[1]-self.midpoint[0]*0.2, -self.midpoint[0]])
    
    def find_oil(self):
        return np.exp(-(np.linalg.norm(np.array([self.center_point[0],self.center_point[1],self.center_point[2],]) - np.array([0.35, 0.45, 0]))** 2)/ 0.01)
    
