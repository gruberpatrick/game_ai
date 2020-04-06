
class Agent:

    # --------------------------------------------------------------------------
    def set_board(self, board):

        self._board = board
        self._board._verbose = False

    # --------------------------------------------------------------------------
    def step(self, board, possible, reward, done, args):

        raise Exception("Not implemented.")

    # --------------------------------------------------------------------------
    def end_game(self):

        raise Exception("Not implemented.")
