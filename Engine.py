
import numpy as np
import os

from Board import Board
from RandomAgent import RandomAgent
from MiniMaxAgent import MiniMaxAgent

cls = lambda: os.system('clear')

class Engine:

    _run_loop = True
    _players = {}

    # --------------------------------------------------------------------------
    def __init__(self, width, height, wins):

        self._board = Board(width, height, wins)
        #self.eventLoop()

    # --------------------------------------------------------------------------
    def eventLoop(self):

        while self._run_loop:

            op = input("> ")
            self.operationSwitch(op.split(" "))

    # --------------------------------------------------------------------------
    def printHelp(self):

        print(
            "    ap SYMBOL [H|R]: Add a new player with given symbol and type (defaults to HUMAN).\n"
            "    sp : Show players that are currently in the game.\n"
            "    r : Reset the current board.\n"
            "    p : Print the current board.\n"
            "    s : Start the game."
        )

    # --------------------------------------------------------------------------
    def addPlayer(self, op):

        if op[1] in self._players: print("Player '%s' already exists." % op[1])

        player = ["H" if len(op) <= 2 else op[2]]
        if len(op) > 2 and op[2] == "R": player.append(RandomAgent(self))
        if len(op) > 2 and op[2] == "MM": player.append(MiniMaxAgent(self))

        self._players[op[1]] = player
        self._board.addPlayer(op[1])

    # --------------------------------------------------------------------------
    def gameHandler(self):

        while self._board._started:

            cls()
            _, player_name = self._board.getCurrentPlayer()
            possible = self._board.possibleMoves()
            print("Current: %s" % player_name)
            self._board.printBoard()
            success = False

            while not success:

                if self._players[player_name][0] == "H" or self._players[player_name][0] == "":

                    op = input("Enter x y: ").split(" ")
                    try:
                        check = self._board.makeMove(int(op[0]), int(op[1]))
                    except:
                        print("Invalid input.")
                        check = False
                    if check: success = True

                else:

                    self._players[player_name][1].setBoard(self._board.c())
                    move = self._players[player_name][1].step(possible)
                    check = self._board.makeMove(move[0], move[1])
                    if check: success = True

            self._board.printBoard()

    # --------------------------------------------------------------------------
    def operationSwitch(self, op):

        if op[0] == "h": self.printHelp()
        elif op[0] == "e": self._run_loop = False
        elif op[0] == "ap": self.addPlayer(op)
        elif op[0] == "sp": print(self._players)
        elif op[0] == "r": self._board.reset()
        elif op[0] == "p": self._board.printBoard()
        elif op[0] == "s":
            if self._board.startGame(): self.gameHandler()
        else: print("Invalid command. Type 'h' for help.")

if __name__ == "__main__":
    e = Engine(3, 3, 3)
    e.operationSwitch(["ap", "X"])
    e.operationSwitch(["ap", "O", "MM"])
    e.operationSwitch(["sp"])
    e.operationSwitch(["s"])

