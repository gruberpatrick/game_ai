
import numpy as np

from Agent import Agent

class RandomAgent(Agent):

    # --------------------------------------------------------------------------
    def step(self, possible):

        move = possible[np.random.randint(0, len(possible))]
        return move
