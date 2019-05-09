
import numpy as np
import copy

class Board:

    _board = []
    _players = []
    _started = False
    _player_pointer = 0
    _verbose = True

    # --------------------------------------------------------------------------
    def __init__(self, width, height, wins):

        # initialize game parameters;
        self._width = width
        self._height = height
        self._wins = wins

        # initialize the board;
        self._board = np.zeros((self._width, self._height), dtype=np.int64)

    # --------------------------------------------------------------------------
    def reset(self):

        self._winner = None
        self._board = np.zeros((self._width, self._height), dtype=np.int64)
        self._player_pointer = np.random.randint(0, len(self._players))

    # --------------------------------------------------------------------------
    def c(self):

        return copy.deepcopy(self)

    # --------------------------------------------------------------------------
    def getCurrentPlayer(self):

        return self._player_pointer, self._players[self._player_pointer]

    # --------------------------------------------------------------------------
    def addPlayer(self, symbol):

        # do not allow new players after game has started;
        if self._started:
            if self._verbose: print("[ERROR] Game already started.")
            return
        
        # add a new player to the game;
        self._players.append(symbol)
        if self._verbose: print("Added player '%s'." % symbol)

    # --------------------------------------------------------------------------
    def possibleMoves(self):

        moves = []

        for it in range(self._board.shape[0]):
            for jt in range(self._board.shape[1]):

                if self._board[it][jt] == 0: moves.append([jt, it])

        return moves

    # --------------------------------------------------------------------------
    def makeMove(self, x, y, change_player=True):

        # check if game started;
        if not self._started:
            if self._verbose: print("[ERROR] Game hasn't started yet.")
            return False

        # check if move out of bounds;
        if x >= self._board.shape[1] or y >= self._board.shape[0] or x < 0 or y < 0:
            if self._verbose: print("[ERROR] Illegal move (%d, %d)." % (x, y))
            return False

        # check if field already occupied;
        if self._board[y][x] != 0:
            if self._verbose: print("[ERROR] Field already occupied.")
            return False

        # get the symbol;
        symbol = self._players[self._player_pointer]

        # add symbol to board;
        self._board[y][x] = ord(symbol)

        # let the next player make the next move;
        if change_player: self._player_pointer += 1
        if self._player_pointer >= len(self._players): self._player_pointer = 0
        
        # check if the game is over;
        winner = self.checkWinningState()
        if winner:
            self._winner = winner
            if self._verbose: print("Player '%s' won the game."% (winner))
            self._started = False

        return True

    # --------------------------------------------------------------------------
    def checkRow(self, row):

        series = 0
        last_elem = -1

        # go through columns in row and find sequences that determine the
        # winning streak; streaks of 0s do not count;
        for elem in row:

            # a new element other than 0 found, begins the series;
            if elem != last_elem and elem != 0:
                last_elem = elem
                series = 1
            # the element is the same as the last, series continues;
            elif elem == last_elem and elem != 0:
                series += 1
            # reset the series otherwise;
            else:
                series = 0

            # if the series is the amount required to win, we found a winner;
            if series >= self._wins:
                return chr(last_elem), series

        # no winner on current board;
        return False, series

    # --------------------------------------------------------------------------
    def checkWinningState(self):

        if len(self._board[self._board == 0]) == 0:
            self._winner = None
            self._started = False
            return

        # add base board directions;
        to_check = [self._board, self._board.T]

        # add diagonals to check;
        for idx in range(-self._width+1, self._height):
            to_check.append(self._board.diagonal(idx))
            to_check.append(np.flipud(self._board).diagonal(idx))

        # go through boards to check;
        for bb in to_check:

            # if the board is another array;
            if isinstance(bb[0], np.ndarray):

                # go through the rows;
                for row in bb:

                    # and check whether we have a winner;
                    winner, series = self.checkRow(row)
                    if winner: return winner

            # otherwise we are checking a diagonal (which is returned by numpy as
            # a 1D array);
            else:

                # else the board is a row;
                row = bb
                # find the winner from there;
                winner, series = self.checkRow(row)
                if winner: return winner

        return False

    # --------------------------------------------------------------------------
    def startGame(self):

        # check the amount of players;
        if len(self._players) < 2:
            if self._verbose: print("[ERROR] Not enough players in the game.")
            return False

        # reset the board;
        self.reset()
        self._started = True

        return True

    # --------------------------------------------------------------------------
    def printBoard(self):

        for it in range(self._board.shape[0]):
            for jt in range(self._board.shape[1]):
                print("-" if self._board[it][jt] == 0 else chr(self._board[it][jt]), end="\t")
            print("")

if __name__ == "__main__":
    b = Board(3, 3, 3)
    #b.addPlayer("O")
    #b.addPlayer("X")
    #b.printBoard()
    #b.startGame()
    #b.makeMove(1, 1)
    #b.makeMove(0, 2)
    #b.makeMove(1, 2)
    #b.makeMove(0, 1)
    #b.makeMove(1, 0)
    test_board = [[50,50,0],[50,51,51],[50,51,51]]
    b._board = np.array(test_board)
    b.printBoard()
    print(b.checkWinningState())
