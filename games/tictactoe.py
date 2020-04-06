import cv2
import numpy as np
import math
import random

from games.board import Board
from lib.rendering import Rendering


class TicTacToe(Board):

    _state_size = 9
    _action_size = 9

    def reset_board(self):

        self._board = np.zeros((3, 3), dtype=np.int32)
        self._board[:, :] = -1
        self._current_player = random.randint(0, len(self._players) - 1)
        self._rendering = Rendering()

    def get_current_player(self):

        return self._current_player

    def get_board(self):

        return self._board.flatten()

    def get_possible_moves(self):
        """
        Get all the possible moves for the current board layout.
        :return: List of possible moves.
        """

        moves = self.get_board()
        possible = []

        for idx in range(moves.shape[0]):
            if moves[idx] == -1:
                possible.append(idx)

        return possible

    def get_reward(self):
        """
        Get the reward of the current board layout. Normal playing will add 1 to the reward
        of each player. Loosing will add -100, while winning will add 100.
        :return: int, determining the reward of the current moves.
        """

        reward = {0: 1, 1: 1}

        done, player_won = self.get_done()
        if done and player_won >= 0:
            reward = {0: -100, 1: -100}
            reward[player_won] = 100

        return reward

    def get_done(self):
        """
        Determine if the game is done, and who won.
        :return: Tuple of bool and int, determining if the game is done and who won.
        """

        # check all rows and columns;
        for it in range(self._board.shape[0]):
            x, y, z = self._board[it, :]
            xi, yi, zi = self._board.T[it, :]
            if x == y == z and x != -1:
                return True, x
            if xi == yi == zi and xi != -1:
                return True, xi

        # check the diagonal;
        x, y, z = self._board.diagonal()
        xi, yi, zi = np.flipud(self._board).diagonal()
        if x == y == z and x != -1:
            return True, x
        if xi == yi == zi and xi != -1:
            return True, xi

        possible = self.get_possible_moves()
        if len(possible) == 0:
            return True, -1

        return False, -1

    def switch_player(self):

        self._current_player += 1
        if self._current_player >= len(self._players):
            self._current_player = 0

    def step(self, move):

        if move not in self.get_possible_moves():
            raise Exception("Move not possible")

        y = math.floor(move / 3)
        x = move % 3
        self._board[y, x] = self._current_player

        self.switch_player()

        return self.get_reward()

    def render(self, img):

        self._rendering.reset_image(img)

        img_width = img.shape[0]
        img_height = img.shape[1]

        per_width = int(img_width / 3)
        per_height = int(img_height / 3)

        # add vertical lines;
        for idx in range(3):
            img = cv2.line(img, ((idx + 1) * per_width, 0), ((idx + 1) * per_width, img_height), (0, 0, 0), 2)

        # add horizontal lines;
        for idx in range(3):
            img = cv2.line(img, (0, (idx + 1) * per_height), (img_width, (idx + 1) * per_height), (0, 0, 0), 2)

        # show symbols;
        for idx in range(9):
            x, y = int(idx / 3), idx % 3
            value = int(self._board[x, y])
            if value < 0:
                continue
            img = cv2.putText(img, str(value), (y * per_width, (x + 1) * per_height), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 0), 2, cv2.LINE_AA)

        return img


if __name__ == "__main__":
    board = TicTacToe(players=[10, 50])
    print(board.get_possible_moves())
    board.step(6)
    print(board.get_board())
    print(board.get_done())
