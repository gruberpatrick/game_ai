import math
import numpy as np

from agents.agent import Agent


class QAgent(Agent):

    _epsilon = 1
    _epsilon_decay = .998
    _epsilon_min = .1

    # --------------------------------------------------------------------------
    def __init__(self, engine, params):

        self._engine = engine
        self._params = params
        self._state_size = engine._board._state_size
        self._action_size = engine._board._action_size
        self._q = np.zeros((math.factorial(self._state_size), self._action_size))
        self._encoding = {}
        self._encoding_counter = 0
        self._last_state = None
        self._last_action = None
        self._alpha = 0.1
        self._gamma = 0.6
    
    # --------------------------------------------------------------------------
    def action_to_x_y(self, action):

        x = action % 3
        y = math.floor(action / 3)
        return [x, y]

    # --------------------------------------------------------------------------
    def get_reward(self):

        winner = self._board.check_winning_state()

        if winner is not False:

            if winner == self._own_symbol:
                return 100
            else:
                return -100

        return 1

    # --------------------------------------------------------------------------
    def step(self, orig_state):

        # encode the state values to a single integer value;
        if str(orig_state) not in self._encoding:
            self._encoding[str(orig_state)] = self._encoding_counter
            self._encoding_counter += 1
        state = self._encoding[str(orig_state)]

        # random choice (explore environment);
        if self._epsilon > np.random.rand():
            action = -1
            while self.action_to_x_y(action) not in orig_state:
                action = np.random.randint(self._action_size)

        # use learned actions;
        else:
            action = np.argmax(self._q[state])

        # learn;
        if self._last_action and self._last_state:
            max_value = np.max(self._q[state])
            last_value = self._q[self._last_state, self._last_action]
            new_value = last_value + self._alpha * (self.get_reward() + self._gamma * max_value - last_value)
            self._q[self._last_state, self._last_action] = new_value

        self._last_state = state
        self._last_action = action

        return self.action_to_x_y(action)

    def end_game(self):

        if self._epsilon > self._epsilon_min:
            self._epsilon *= self._epsilon_decay
