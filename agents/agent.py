
class Agent:

    # --------------------------------------------------------------------------
    def __init__(self, engine, params):

        self._engine = engine

    # --------------------------------------------------------------------------
    def set_board(self, board):

        self._board = board
        self._board._verbose = False

    # --------------------------------------------------------------------------
    def step(self):

        raise Exception("Not implemented.")

    # --------------------------------------------------------------------------
    def end_game(self):

        raise Exception("Not implemented.")
