
import numpy as np

from agents.agent import Agent


class RandomAgent(Agent):

    # --------------------------------------------------------------------------
    def step(self, possible):

        # pick a random move from all possible ones;
        move = possible[np.random.randint(0, len(possible))]
        return move
