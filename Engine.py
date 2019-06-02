
import numpy as np
import os
import websockets
import asyncio
import json
import time

from Board import Board
from RandomAgent import RandomAgent
from MiniMaxAgent import MiniMaxAgent
from DeepQAgent import DeepQAgent


class Engine:

    _infinite = True
    _run_loop = True
    _players = {}

    # --------------------------------------------------------------------------
    def __init__(self, width, height, wins, connect_four=False):

        self._board = Board(width, height, wins, connect_four=connect_four)
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

        if op[1] in self._players:
            print("Player '%s' already exists." % op[1])

        player = ["H" if len(op) <= 2 else op[2]]
        if len(op) > 2 and op[2] == "R":
            player.append(RandomAgent(self))
        elif len(op) > 2 and op[2] == "MM":
            player.append(MiniMaxAgent(self))
        elif len(op) > 2 and op[2] == "DQ":
            player.append(DeepQAgent(self))

        self._players[op[1]] = player
        self._board.addPlayer(op[1])

    # --------------------------------------------------------------------------
    async def gameHandler(self):

        while self._board._started:

            #print("====================================================")
            _, player_name = self._board.getCurrentPlayer()
            possible = self._board.possibleMoves()
            #await sendMessage("current_player", str(player_name))
            #await sendMessage("board", str(self._board))
            success = False

            while not success:

                start = time.time()

                if self._players[player_name][0] == "H" or self._players[player_name][0] == "":

                    #op = input("Enter x y: ").split(" ")
                    #op = await sendMessageAndAwaitResponse("action", "Enter x y: ")
                    op = "1 2"
                    op = op.split(" ")
                    for it in range(len(op)):
                        op[it] = int(op[it])
                    print("Player move", op)

                    try:
                        check = self._board.makeMove(op)
                    except Exception:
                        print("Invalid input.")
                        check = False

                    if check:
                        success = True

                else:

                    self._players[player_name][1].setBoard(self._board.c())
                    move = self._players[player_name][1].step(possible)
                    #print("Agent move", move)
                    check = self._board.makeMove(move)

                    if check:
                        success = True

                #print("[NOTIFICATION] Took", time.time() - start, "seconds")
            
            #self._board.printBoard()
            #await sendMessage("board", str(self._board))

    # --------------------------------------------------------------------------
    async def operationSwitch(self, op):

        if op[0] == "h":
            self.printHelp()
        #elif op[0] == "e": self._run_loop = False
        elif op[0] == "ap":
            self.addPlayer(op)
        elif op[0] == "sp":
            await sendMessage("players", str(self._players))
        elif op[0] == "r":
            self._board.reset()
        elif op[0] == "p":
            pass #await sendMessage("board", str(self._board))
        elif op[0] == "s":

            while True:

                if self._board.startGame():
                    await self.gameHandler()
                
                for player in self._players:
                    self._players[player][1].setBoard(self._board.c())
                    self._players[player][1].endGame()

                # call the end of game trigger;
                if not self._infinite:
                    break

                #test = input("Continue?")

        elif op[0] == "mm":
            move = []
            for it in range(1, len(op)):
                move.append(int(op[it]))
            self._board.makeMove(move)
        
        else:
            print("Invalid command. Type 'h' for help.")


################################################################################
_websocket = None


# --------------------------------------------------------------------------
async def socketHook(websocket, path):

    global _websocket, e
    _websocket = websocket

    while True:

        op = await _websocket.recv()
        await e.operationSwitch(op.split(" "))

        message = json.dumps({"message": "10-4"})
        await _websocket.send(message)


# --------------------------------------------------------------------------
async def sendMessage(ttype, message):

    global _websocket

    message = json.dumps({"type": ttype, "message": message})
    await _websocket.send(message)


# --------------------------------------------------------------------------
async def sendMessageAndAwaitResponse(ttype, message):

    global _websocket

    message = json.dumps({"type":ttype, "message": message})
    await _websocket.send(message)

    return await _websocket.recv()


# --------------------------------------------------------------------------
if __name__ == "__main__":
    #e = Engine(7, 6, 3)
    e = Engine(3, 3, 3, connect_four=False)
    start_server = websockets.serve(socketHook, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
