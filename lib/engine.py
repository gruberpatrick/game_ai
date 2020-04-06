import neptune

from lib.player import Player
from lib.rendering import Rendering
from games.tictactoe import TicTacToe


class Engine:

    _current_player = 0
    _players = []

    def __init__(self, render=False):

        self._render = render
        if render:
            self._rendering = Rendering()
            self._img = self._rendering.initialize_canvas()
            self._rendering.show_image(self._img)

    def add_player(self, name, type):

        self._players.append(Player(name, type))

    def pick_board(self, board):

        if board == "tictactoe":
            self._board = TicTacToe(list(range(len(self._players))))
        else:
            raise Exception(f"The board '{board}' does not exist.")

        for player in self._players:
            player.set_board(self._board)

    def episode(self, debug=False):

        self._board.reset_board()
        done, winner = self._board.get_done()
        reward = 0

        while not done:

            possible = self._board.get_possible_moves()
            board = self._board.get_board()
            current_player = self._board.get_current_player()

            # print(f"  Current player - {self._players[current_player]._name}")

            move = self._players[current_player].get_move(
                board,
                possible,
                reward,
                done,
                {"own_symbol": current_player},
            )

            reward = self._board.step(move)
            done, winner = self._board.get_done()

            # print(f"  Move {move}")

            if self._render:
                img = self._board.render(self._img)
                self._rendering.show_image(img)

        print(f"Result {done} - {winner}")
        idx = 0
        for player in self._players:
            neptune.log_metric(player._name, 1 if winner == idx else 0)
            player.end_game()
            idx += 1
