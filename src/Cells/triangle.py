from src.Cells.cell import Cell
import numpy as np


class Triangle(Cell):
    def __init__(self, msh, cell_points, cell_id):
        super().__init__(msh, cell_points, cell_id)
        self.type = "triangle"
    
    def find_area(self):
        area = 0.5 * abs(
            (self.cords[0][0] - self.cords[2][0])
            * (self.cords[1][1] - self.cords[0][1])
            - (self.cords[0][0] - self.cords[1][0])
            * (self.cords[2][1] - self.cords[0][1])
        )
        return area
    
    def find_scaled_normales(self):
        self.walls = np.array(
            np.array(self.cords[0], self.cords[1]),
            np.array(self.cords[1],self.cords[2]),
            np.array(self.cords[2], self.cords[0])
            )
        
        for wall in self.walls:
            wall[0]

        d = B - A

  
        n = np.array([d[1], -d[0]])
        v = P - A

  
        if np.dot(n, v) < 0:
            n = -n


        if normalize:
            n = n / np.linalg.norm(n)

        return n
        
