class Cell:
    def __init__(self, msh):
        self.oc = 0 #oil-count
        self.ngb = [] #neigbours
        self.id = "Oskar"
        self.cords = msh.cells[n].data

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
