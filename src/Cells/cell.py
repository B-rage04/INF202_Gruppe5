import numpy as np
from abc import ABC, abstractmethod

class Cell(ABC):
    def __init__(self, msh, n):
        self.type = None
        self.id = n
        self.cords = [msh.points[msh.triangles[n][i]] for i in range(3)]
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

    def find_scaled_normales(self):
        pass

    def find_ngb(self):
        pass

    def find_flow(self):
        return np.array([self.midpoint[1]-self.midpoint[0]*0.2, -self.midpoint[0]])
    
    def find_oil(self):
        return np.exp(-(np.linalg.norm(np.array([self.center_point[0],self.center_point[1],self.center_point[2],]) - np.array([0.35, 0.45, 0]))** 2)/ 0.01)
    
