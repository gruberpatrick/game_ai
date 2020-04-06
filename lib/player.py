from agents.random_agent import RandomAgent
from agents.mini_max_agent import MiniMaxAgent
from agents.deep_q_agent import DeepQAgent
from agents.q_agent import QAgent


class Player:

    def __init__(self, name, type):

        self._name = name
        self._agent = self.get_agent(type)

    def set_board(self, board):

        if self._agent:
            self._agent.set_board(board)

    def get_agent(self, type):

        if type == "random":
            return RandomAgent()
        elif type == "minimax":
            return MiniMaxAgent()
        elif type == "deepqagent":
            return DeepQAgent()
        elif type == "qagent":
            return QAgent()
        elif type == "human":
            return None

    def get_move(self, board, possible, reward, done, args):

        if self._agent:
            return self._agent.step(board, possible, reward, done, args)
        return self.get_human_move(board, possible, reward, done, args)

    def get_human_move(self, board, possible, reward, done, args):

        print(f"MOVES: {possible}")
        move = int(input('  => '))
        return move

    def end_game(self):

        if self._agent:
            self._agent.end_game()
