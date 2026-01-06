from mesh import Mesh

class Cell:
    def __init__(self, msh, n):
        self.oc = 0 #oil-count
        self.ngb = [] #neigbours
        self.id = str(n)
        self.cords = msh.cells[3].data[n]

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

    def area(self):
        return 0.5 * abs((self.cords[0][0] - self.cords[2][0])(self.cords[1][1] - self.cords[0][1]) - (self.cords[0][0] - self.cords[1][0])(self.cords[2][1] - self.cords[0][1]))
    
jeff = Cell(Mesh)