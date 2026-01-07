import math as math


class Flow:
    def __init__(self):
        self.x_star = 0.35
        self.y_star = 0.45
        self.x_vector = (self.x_star, self.y_star)

    def u0(self, x, y):
        r2 = (x - self.x_star) ** 2 + (y - self.y_star) ** 2  # ||x - x*||^2
        return math.exp(-r2 / 0.01)

    def v(self, x, y):
        vx = y - 0.2 * x
        vy = -x
        return vx, vy
