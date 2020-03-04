
import numpy as np
import copy


class Board:

    _board = []
    _players = []
    _started = False
    _player_pointer = 0
    _verbose = True
    _winner = None

    # --------------------------------------------------------------------------
    def __init__(self, width, height, wins, connect_four=False):

        # initialize game parameters;
        self._width = width
        self._height = height
        self._wins = wins
        self._connect_four = connect_four
        self._state_size = width * height
        self._action_size = self._state_size

        # initialize the board;
        self._board = np.zeros((self._width, self._height), dtype=np.int64)

    # --------------------------------------------------------------------------
    def reset(self):

        self._winner = None
        self._started = False
        self._board = np.zeros((self._width, self._height), dtype=np.int64)

        # TODO: randomize starting player
        self._player_pointer = np.random.randint(0, len(self._players))
        #self._player_pointer = 0

    # --------------------------------------------------------------------------
    def c(self):

        # only copy elements that are neccessary;
        b = Board(self._width, self._height, self._wins, connect_four=self._connect_four)
        b._board = copy.deepcopy(self._board)
        b._players = self._players[:]
        b._started = self._started
        b._player_pointer = self._player_pointer
        b._verbose = self._verbose

        return b

    # --------------------------------------------------------------------------
    def get_current_player(self):

        # return the current player;
        return self._player_pointer, self._players[self._player_pointer]

    # --------------------------------------------------------------------------
    def add_player(self, symbol):

        # do not allow new players after game has started;
        if self._started:
            if self._verbose:
                print("[ERROR] Game already started.")
            return

        # add a new player to the game;
        self._players.append(symbol)
        if self._verbose:
            print("Added player '%s'." % symbol)

    # --------------------------------------------------------------------------
    def possible_moves(self):

        moves = []

        # return the current moves that are possible; 2D for tic tac toe
        if not self._connect_four:
            for it in range(self._board.shape[0]):
                for jt in range(self._board.shape[1]):
                    if self._board[it][jt] == 0:
                        moves.append([jt, it])
        # and 1D for connect four;
        else:
            board_t = self._board.T
            for it in range(len(board_t)):
                if board_t[it][0] == 0: moves.append([it, 0])

        return moves

    # --------------------------------------------------------------------------
    def make_move(self, move, change_player=True):

        if self._connect_four:
            x = move[0]
        else:
            x, y = move

        # check if game started;
        if not self._started:
            if self._verbose:
                print("[ERROR] Game hasn't started yet.")
            return False

        # TODO: check and set y accoding to connect 4 rules
        if self._connect_four:
            y = -1
            board_t = self._board.T[x]
            for it in range(len(board_t)+1):
                #print(board_t)
                if it == len(board_t):
                    y = len(board_t) - 1
                    break
                elif board_t[it] != 0:
                    y = it - 1
                    break

        #print(x, y)

        # check if move out of bounds;
        if x >= self._board.shape[1] or y >= self._board.shape[0] or x < 0 or y < 0:
            if self._verbose:
                print("[ERROR] Illegal move (%d, %d)." % (x, y))
            return False

        # check if field already occupied;
        if self._board[y][x] != 0:
            if self._verbose:
                print("[ERROR] Field already occupied.")
            return False

        # get the symbol;
        symbol = self._players[self._player_pointer]

        # add symbol to board;
        self._board[y][x] = ord(symbol)

        # let the next player make the next move;
        if change_player:
            self._player_pointer += 1
        if self._player_pointer >= len(self._players):
            self._player_pointer = 0
        
        # check if the game is over;
        winner = self.check_winning_state()
        if winner:
            self._winner = winner
            if self._verbose:
                print("Player '%s' won the game." % (winner))
            self._started = False
        if not winner and not self._started:
            self._winner = False
            if self._verbose:
                print("Draw")

        return True

    # --------------------------------------------------------------------------
    def check_row(self, row):

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
    def check_winning_state(self):

        if len(self._board[self._board == 0]) == 0:
            self._started = False

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
                    winner, _ = self.check_row(row)
                    if winner:
                        return winner

            # otherwise we are checking a diagonal (which is returned by numpy as
            # a 1D array);
            else:

                # else the board is a row;
                row = bb
                # find the winner from there;
                winner, series = self.check_row(row)
                if winner:
                    return winner

        return False

    # --------------------------------------------------------------------------
    def start_game(self):

        # check the amount of players;
        if len(self._players) < 2:
            if self._verbose:
                print("[ERROR] Not enough players in the game.")
            return False

        # reset the board;
        self.reset()
        self._started = True

        return True

    # --------------------------------------------------------------------------
    def print_board(self):

        # print the board to the console;
        for it in range(self._board.shape[0]):
            for jt in range(self._board.shape[1]):
                print("-" if self._board[it][jt] == 0 else chr(self._board[it][jt]), end="\t")
            print("")

    # --------------------------------------------------------------------------
    def __str__(self):

        result = ""

        # return the board as a string representation;
        for it in range(self._board.shape[0]):
            for jt in range(self._board.shape[1]):
                result += ("-" if self._board[it][jt] == 0 else chr(self._board[it][jt])) + "\t"
            result += "\n"

        return result


if __name__ == "__main__":

    b = Board(3, 3, 3, connect_four=True)
    b.add_player("O")
    b.add_player("X")
    b.print_board()
    b.start_game()
    #b.makeMove(0, 2)
    #b.makeMove(1, 2)
    #b.makeMove(0, 1)
    #b.makeMove(1, 0)
    test_board = [[0, 0, 0],[0, 0, 0],[0, 50, 0]]
    b._board = np.array(test_board)
    b.make_move([1])
    b.print_board()
    print(b.check_winning_state())
