
class Agent:

    # --------------------------------------------------------------------------
    def __init__(self, engine):

        self._engine = engine

    # --------------------------------------------------------------------------
    def setBoard(self, board):
        
        self._board = board
        self._board._verbose = False

    # --------------------------------------------------------------------------
    def step(self):

        pass
