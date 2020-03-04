
import numpy as np
import torch
import math
import time

from agents.agent import Agent
from tensorboardX import SummaryWriter


class NN(torch.nn.Module):

    _epsilon = 1
    _epsilon_decay = .998
    _epsilon_min = .1

    # --------------------------------------------------------------------------
    def __init__(self, state_size, action_size, epsilon=1):

        super(NN, self).__init__()

        self._epsilon = epsilon

        self._state_size = state_size
        self._action_size = action_size

        self._fc1 = torch.nn.Linear(self._state_size, 15)
        self._fc2 = torch.nn.Linear(15, 15)
        self._fc3 = torch.nn.Linear(15, self._action_size)
        self._relu = torch.nn.ReLU()
        self._dropout = torch.nn.Dropout(.4)
        self._softmax = torch.nn.Softmax()

        self._opt = torch.optim.Adam(lr=.001, params=self.parameters())
        self._loss = torch.nn.NLLLoss()

        torch.nn.init.xavier_normal_(self._fc1.weight)
        torch.nn.init.xavier_normal_(self._fc2.weight)

    # --------------------------------------------------------------------------
    def forward(self, x):

        X = self._fc1(x)
        X = self._relu(X)
        X = self._fc2(X)
        X = self._relu(X)
        X = self._fc3(X)

        return self._softmax(X)

    # --------------------------------------------------------------------------
    def x_y_to_action(self, x, y):

        return (y*3) + x

    # --------------------------------------------------------------------------
    def action_to_x_y(self, action):

        x = action % 3
        y = math.floor(action / 3)
        return x, y

    # --------------------------------------------------------------------------
    def step(self, state, possible):

        if self._epsilon > np.random.rand():

            x, y = [-1, -1]

            while [x, y] not in possible:

                action = np.random.randint(self._action_size)
                x, y = self.action_to_x_y(action)

        else:

            state = torch.Tensor([state]).float()
            linear = self.forward(state)
            prob = self._softmax(linear)[0].detach().numpy()

            for it in range(len(prob)):

                x, y = self.action_to_x_y(it)
                if [x, y] not in possible:
                    prob[it] = 0

            prob /= np.sum(prob)
            action = np.random.choice(len(prob), p=prob)

        x, y = self.action_to_x_y(action)

        return x, y, action


class DeepQAgent(Agent):

    _trigger_amount = 250
    _batch_size = 64

    _states = []
    _actions = []
    _reward = 0
    _steps = 0

    _final_states = []
    _final_actions = []
    _final_rewards = []

    _translation = {79: -1, 88: 1}

    # --------------------------------------------------------------------------
    def __init__(self, engine, params):

        if "model_name" not in params:
            self._name = str(time.time())
            self._nn = NN(engine._board._state_size, engine._board._action_size)
        else:
            self._name = params["model_name"]
            self._nn = NN(engine._board._state_size, engine._board._action_size, epsilon=.001)
            state_dict = torch.load("./output/" + self._name + ".model")
            self._nn.load_state_dict(state_dict)
            self._name += "_continue"
        self._training_count = 0
        self._writer = SummaryWriter(logdir="./output/DeepQAgent/" + self._name + "_tb/")

    # --------------------------------------------------------------------------
    def preprocess_board(self, board):

        res = []
        for item in board:

            if item in self._translation:
                res.append(self._translation[item])
            else:
                res.append(0)

        return res

    # --------------------------------------------------------------------------
    def step(self, possible):

        # own symbol to check against in evaluations;
        self._own_symbol = self._board._players[self._board._player_pointer]

        # reformat the board;
        board = self.preprocess_board(self._board._board.flatten().tolist())

        # run through the reinforcement agent;
        x, y, action = self._nn.step(board, possible)

        self._states.append(board)
        self._actions.append(action)
        self._reward += self.get_reward()

        return x, y

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
    def get_best_batches(self, percentile=.8):

        states = []
        actions = []
        rewards = []

        threshold = np.percentile(self._final_rewards, percentile)

        for it in range(len(self._final_rewards)):

            if self._final_rewards[it] < threshold:
                continue
            rewards.append(self._final_rewards[it])

            for jt in range(len(self._final_states[it])):

                states.append(self._final_states[it][jt])
                actions.append(self._final_actions[it][jt])

        return states, actions, rewards, threshold

    # --------------------------------------------------------------------------
    def end_game(self):

        self._reward += self.get_reward()

        self._final_states.append(self._states)
        self._final_actions.append(self._actions)
        self._final_rewards.append(self._reward)
        self._states = []
        self._actions = []
        self._reward = 0
        self._steps = 0

        if len(self._final_rewards) >= self._trigger_amount:

            if self._nn._epsilon > self._nn._epsilon_min:
                self._nn._epsilon *= self._nn._epsilon_decay

            states, actions, rewards, threshold = self.get_best_batches(percentile=80)

            total = math.ceil(len(states) / self._batch_size)
            losses = []

            for it in range(total):

                x = torch.Tensor(states[it*self._batch_size:(it+1)*self._batch_size]).float()
                y = torch.Tensor(actions[it*self._batch_size:(it+1)*self._batch_size]).long()

                self._nn._opt.zero_grad()

                y_hat = self._nn(x)
                loss = self._nn._loss(y_hat, y)

                loss.backward()
                self._nn._opt.step()

                losses.append(loss.item())

            self._training_count += 1
            # print("[%d] loss:%3.8f \t threshold:%3.8f" % (self._training_count, loss, threshold))

            self._writer.add_scalar("DeepQAgent/loss", np.array(losses).mean(), self._training_count)
            self._writer.add_scalar("DeepQAgent/threshold", threshold, self._training_count)
            self._writer.add_scalar("DeepQAgent/reward", np.array(self._final_rewards).mean(), self._training_count)
            self._writer.add_scalar("DeepQAgent/epsilon", self._nn._epsilon, self._training_count)

            torch.save(self._nn.state_dict(), "./output/" + self._name + ".model")

            self._final_states = []
            self._final_actions = []
            self._final_rewards = []
