from src.Cells.cell import Cell


class Triangle(Cell):
    def __init__(self, msh, n):
        super().__init__(msh, n)


# TODO burde vi slitte ut cell til å bli polygon får nå er både linje og trekant bruker 3 cord
