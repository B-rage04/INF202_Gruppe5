import numpy as np

from ..mesh import Mesh


class Cell:
    def __init__(self, msh, n):
        # self.oil = np.exp(-(( - self.x_star)**2 + (y - self.y_star)**2)/0.01)
        self.ngb = []  # neigbours
        self.cords = []
        for i in range(3):
            self.cords.append(msh.points[msh.triangles[n][i]])

        self.center_point = np.array(
            [
                (self.cords[0][0] + self.cords[1][0] + self.cords[2][0]) / 3,
                (self.cords[0][1] + self.cords[1][1] + self.cords[2][1]) / 3,
                (self.cords[0][2] + self.cords[1][2] + self.cords[2][2]) / 3,
            ]
        )
        self.area = 0.5 * abs(
            (self.cords[0][0] - self.cords[2][0])
            * (self.cords[1][1] - self.cords[0][1])
            - (self.cords[0][0] - self.cords[1][0])
            * (self.cords[2][1] - self.cords[0][1])
        )
        self.flow = np.array(
            [self.center_point[1] - self.center_point[0] * 0.2, -self.center_point[0]]
        )

        self.oil = np.exp(
            -(
                np.linalg.norm(
                    np.array(
                        [
                            self.center_point[0],
                            self.center_point[1],
                            self.center_point[2],
                        ]
                    )
                    - np.array([0.35, 0.45, 0])
                )
                ** 2
            )
            / 0.01
        )


"""        
msh = Mesh("bay.msh")

cell = Cell(msh, 1)

print(cell.cords)
print(cell.center_point)
print(cell.area)
print(cell.oil)

"""
