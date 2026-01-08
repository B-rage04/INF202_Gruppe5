from src.Cells.cell import Cell


class Triangle(Cell):
    def __init__(
        self,
    ):
        super.__init__()

    def area(self):
        return 0.5 * abs(
            (self.cords[0][0] - self.cords[2][0])(self.cords[1][1] - self.cords[0][1])
            - (self.cords[0][0] - self.cords[1][0])(self.cords[2][1] - self.cords[0][1])
        )
