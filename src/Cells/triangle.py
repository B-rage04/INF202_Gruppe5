from src.Cells.cell import Cell


class Triangle(Cell):
    def __init__(self, msh, n):
        super().__init__(msh, n)
    
    def find_area(self):
        area = 0.5 * abs(
            (self.cords[0][0] - self.cords[2][0])
            * (self.cords[1][1] - self.cords[0][1])
            - (self.cords[0][0] - self.cords[1][0])
            * (self.cords[2][1] - self.cords[0][1])
        )
        return area