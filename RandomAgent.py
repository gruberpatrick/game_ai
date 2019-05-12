
import numpy as np

from Agent import Agent

class RandomAgent(Agent):

    # --------------------------------------------------------------------------
    def step(self, possible):

        # pick a random move from all possible ones;
        move = possible[np.random.randint(0, len(possible))]
        return move
