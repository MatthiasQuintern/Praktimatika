import numpy as np
import functions as fun

# Todo: eps0, u0, c, h, h_, ...

class Pi(fun.Param):
    def __init__(self):
        super().__init__("pi", np.pi)

