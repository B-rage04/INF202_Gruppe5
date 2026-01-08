import numpy as np


class Cell:
    def __init__(self, msh, n):

        self.ngb = []  # neigbours
        self.cords = [msh.points[msh.triangles[n][i]] for i in range(3)]

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
