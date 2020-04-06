import math
import numpy as np
import json
import neptune

from agents.agent import Agent


class QAgent(Agent):

    _epsilon = 1
    _epsilon_decay = .998
    _epsilon_min = .1

    # --------------------------------------------------------------------------
    def __init__(self):

        self._encoding = {}
        self._encoding_counter = 0
        self._last_state = None
        self._last_action = None
        self._alpha = 0.1
        self._gamma = 0.6

    def set_board(self, board):

        self._board = board
        self._state_size = board._state_size
        self._action_size = board._action_size
        self._q = np.zeros((math.factorial(self._state_size), self._action_size))
        self._q[:] = .5
    
    # --------------------------------------------------------------------------
    def action_to_x_y(self, action):

        x = action % 3
        y = math.floor(action / 3)
        return [x, y]

    # --------------------------------------------------------------------------
    def get_reward(self):

        reward = self._board.get_reward()
        return reward[self._own_symbol]

    # --------------------------------------------------------------------------
    def step(self, board, possible, reward, done, args):

        # own symbol to check against in evaluations;
        self._own_symbol = args["own_symbol"]

        # encode the state values to a single integer value;
        if str(board) not in self._encoding:
            self._encoding[str(board)] = self._encoding_counter
            self._encoding_counter += 1
        state = self._encoding[str(board)]

        neptune.log_metric("Epsilon", self._epsilon)

        # random choice (explore environment);
        if self._epsilon > np.random.rand():
            action = -1
            while action not in possible:
                action = np.random.randint(self._action_size)

        # use learned actions;
        else:
            action = np.argmax(self._q[state])
            while action not in possible:
                self._q[state][action] = -1
                action = np.argmax(self._q[state])

        # learn;
        if self._last_action and self._last_state:
            max_value = np.max(self._q[state])
            last_value = self._q[self._last_state, self._last_action]
            new_value = last_value + self._alpha * (self.get_reward() + self._gamma * max_value - last_value)
            self._q[self._last_state, self._last_action] = new_value

        self._last_state = state
        self._last_action = action

        return action

    def end_game(self):

        if self._epsilon > self._epsilon_min:
            self._epsilon *= self._epsilon_decay
