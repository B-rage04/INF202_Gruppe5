import numpy as np


class Flow:
    def __init__(self, x_star: float = 0.35, y_star: float = 0.45):
        self.x_star = x_star
        self.y_star = y_star

    def u0(self, x: float, y: float) -> float:
        return np.exp(-((x - self.x_star) ** 2 + (y - self.y_star) ** 2) / 0.01)

    def v(self, x: float, y: float):
        vx = y - 0.2 * x
        vy = -x
        return vx, vy
