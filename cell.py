class Cell:
    def __init__(self, i, cell):
        self.oc = 0 #oil-count
        self.ngb = [] #neigbours
        self.id = i
        self.cords = cell[n].data

    def neigbor_calculate(self, cell):
        if self.cords[0] in cell.cords and self.cords[1] in cell.cords:
            self.ngb.append(cell)
        elif self.cords[1] in cell.cords and self.cords[2] in cell.cords:
            self.ngb.append(cell)
        elif self.cords[0] in cell.cords and self.cords[2] in cell.cords:
            self.ngb.append(cell)

    def neighbor_chech(self):
        if len(self.cords) == len(self.ngb):
            return self.ngb
        else:
            for c in cells
                self.neigbor_calculate(self,c)
        
