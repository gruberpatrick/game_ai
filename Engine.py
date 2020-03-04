import time

from games.connect_four import Board
from agents.random_agent import RandomAgent
from agents.mini_max_agent import MiniMaxAgent
from agents.deep_q_agent import DeepQAgent


class Engine:

    _infinite = True
    _run_loop = True
    _players = {}

    # --------------------------------------------------------------------------
    def __init__(self, width, height, wins, connect_four=False):

        self._board = Board(width, height, wins, connect_four=connect_four)

    # --------------------------------------------------------------------------
    def add_player(self, name, player_type, params={}):

        if name in self._players:
            print(f"Player '{name}' already exists.")

        player = [player_type]

        if player_type == "minimax":
            player.append(MiniMaxAgent(self, params))
        elif player_type == "deep-q":
            player.append(DeepQAgent(self, params))
        elif player_type == "random":
            player.append(RandomAgent(self, params))

        self._players[name] = player
        self._board.add_player(name)

    # --------------------------------------------------------------------------
    def game_handler(self):

        while self._board._started:

            _, player_name = self._board.get_current_player()
            possible = self._board.possible_moves()
            success = False

            while not success:

                start = time.time()

                if self._players[player_name][0] == "H" or self._players[player_name][0] == "":

                    op = "1 2"
                    op = op.split(" ")
                    for it in range(len(op)):
                        op[it] = int(op[it])
                    print("Player move", op)

                    try:
                        check = self._board.make_move(op)
                    except Exception:
                        print("Invalid input.")
                        check = False

                    if check:
                        success = True

                else:

                    self._players[player_name][1].set_board(self._board.c())
                    move = self._players[player_name][1].step(possible)
                    # print("Agent move", move)
                    check = self._board.make_move(move)

                    if check:
                        success = True

                # print("[NOTIFICATION] Took", time.time() - start, "seconds")

            # self._board.printBoard()

    # --------------------------------------------------------------------------
    def train(self):

        while True:

            if self._board.start_game():
                self.game_handler()

            for player in self._players:
                self._players[player][1].set_board(self._board.c())
                self._players[player][1].end_game()

            # call the end of game trigger;
            if not self._infinite:
                break


# --------------------------------------------------------------------------
if __name__ == "__main__":

    e = Engine(3, 3, 3, connect_four=False)
    e.add_player("X", "deep-q", {"model_name": "1583284745.688666"})
    e.add_player("O", "deep-q")
    e.train()
