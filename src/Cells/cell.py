import numpy as np
from abc import ABC, abstractmethod

import numpy as np

from ..mesh import Mesh


class Cell(ABC):
    def __init__(self, msh, cell_points, cell_id):
        self.type = None
        self.id = cell_id
        self.cords = [msh.points[i] for i in cell_points]
        self.midpoint = self.find_midpoint()
        self.area = self.find_area()
        self.scaled_normal = []
        self.ngb = []
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

    def find_ngb(self, all_cells):
        for other in all_cells:
            if other.id == self.id:
                continue
            # Check for shared points
            shared = set(tuple(p) for p in self.cords) & set(tuple(p) for p in other.cords)
            if len(shared) >= 2: 
                if other not in self.ngb:
                    self.ngb.append(other)
                if self not in other.ngb:
                    other.ngb.append(self)
                                
    def find_flow(self):
        return np.array([self.midpoint[1] - self.midpoint[0] * 0.2, -self.midpoint[0]])

    def find_oil(self):
        return np.exp(-(np.linalg.norm(self.midpoint - np.array([0.35, 0.45, 0]))** 2)/ 0.01)

    def update_oil(self, ngb):
        
        for ngb in self.ngb:
            self.new_oil = self.oil - delta_time / self.area * flux(ngb)
            

    def flux(self, ngb):
        flow_avg = (self.flow + ngb.flow) / 2
        if np.dot(flow_avg, self.scaled_normal) > 0:
            return self.oil * np.dot(flow_avg, self.scaled_normal)
        else:
            return ngb.oil * np.dot(flow_avg, self.scaled_normal)

def cell_factory(msh):
    """
    Creates cells with data from the mesh and returns as a list
    """
    
    from .line import Line
    from .triangle import Triangle
    cell_list = []
    
    # msh.cells is a list of CellBlock objects
    for cell_block in msh.cells:
        cell_type = cell_block.type
        cells_array = cell_block.data
        if cell_type == "triangle":
            for idx, cell_points in enumerate(cells_array):
                cell_list.append(Triangle(msh, cell_points, idx))
        elif cell_type == "line":
            for idx, cell_points in enumerate(cells_array):
                cell_list.append(Line(msh, cell_points, idx))
    
    # find neighbors
    for cell in cell_list:
        cell.find_ngb(cell_list)
    
    return cell_list
