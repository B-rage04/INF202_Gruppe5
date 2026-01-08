import numpy as np
#from src.mesh import Mesh
from abc import ABC, abstractmethod

class Cell(ABC):
    def __init__(self, msh, n):
        self.type = None
        self.id = n
        self.cords = [msh.points[i] for i in n]
        self.midpoint = self.find_midpoint()
        self.area = self.find_area()
        self.scaled_normal = []
        self.ngb = []
        self.ngb = self.find_ngb(msh)
        self.flow = self.find_flow()
        self.oil = self.find_oil()
        self.new_oil = None

    @abstractmethod
    def find_area(self):
        pass

    def find_midpoint(self):
        if len(self.cords) == 0:
            return np.array([0, 0, 0])
        return np.mean(self.cords, axis=0)

    def find_scaled_normales(self):
        pass

    def find_ngb(self, msh):
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
                                
    def find_flow(self):
        return np.array([self.midpoint[1]-self.midpoint[0]*0.2, -self.midpoint[0]])
    
    def find_oil(self):
        return np.exp(-(np.linalg.norm(np.array([self.center_point[0],self.center_point[1],self.center_point[2],]) - np.array([0.35, 0.45, 0]))** 2)/ 0.01)


def cell_factory(msh):
    """
    Creates cells with data from the mesh and returns as a list
    """
    
    from .line import Line
    from .triangle import Triangle
    cell_list = []
    
    for cell in msh.cells:
        match cell.type:
            case "triangle":
                triangles = msh.cells_dict["triangle"]
                for n in range(len(triangles)):
                    cell_list.append(Triangle(msh, triangles[n]))
            case "line":
                lines = msh.cells_dict["line"]
                for n in range(len(lines)):
                    cell_list.append(Line(msh, lines[n]))