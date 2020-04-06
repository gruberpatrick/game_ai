import numpy as np
import time
import copy

from agents.agent import Agent


class MiniMaxAgent(Agent):

    _cache = {}
    _debug = False

    # --------------------------------------------------------------------------
    def evaluate(
        self, board, moves=[], depth=1, alpha=float("-inf"), beta=float("inf")
    ):

        # print(res, board.get_reward()[self._own_symbol])
        res = board.get_reward()[self._own_symbol]

        # pass the data to the recursive calls;
        return res, [moves], alpha, beta, copy.deepcopy(board._board).tolist()

    # --------------------------------------------------------------------------
    def minimax(
        self,
        board,
        moves=[],
        depth=1,
        maxx=True,
        alpha=float("-inf"),
        beta=float("inf"),
    ):

        # this is pretty much a standard implementation of the minimax
        # algorithm; the only modification is that the shallowest call returns
        # all the results instead of the maximized one; this allows for
        # a final evaluation outside of the call;

        # get all possible and previous moves;
        possible = board.get_possible_moves()
        mm = moves[:]

        # if the board is in an end state, evaluate the result;
        done, _ = board.get_done()
        if done:
            return self.evaluate(
                board, mm, depth + 1, alpha=alpha, beta=beta
            )

        # tracker is used both for the min, as well as the max result
        tracker = float("-inf") if maxx else float("inf")

        # results and movements are returned in the shallowest call;
        results = []
        movements = []
        winners = []

        # consider all possible moves;
        for move in possible:

            # copy the board and make the move;
            nb = copy.deepcopy(board)
            reward = nb.step(move)

            # call the recursion;
            res, mov, _, _, winner = self.minimax(
                nb,
                moves=mm + [move],
                depth=depth + 1,
                maxx=False if maxx else True,
                alpha=alpha,
                beta=beta,
            )

            # maximize operations, according to the standard implementation;
            if maxx:
                if depth > 1:
                    if res > tracker:
                        tracker = res
                        movements = mov
                    if tracker >= beta:
                        break
                    if tracker > alpha:
                        alpha = tracker
                else:
                    results.append(res)
                    movements.extend(mov)
                    winners.append(winner)

            # minimize operations, according to the standard implementation;
            else:
                if res < tracker:
                    tracker = res
                    movements = mov
                if tracker <= alpha:
                    break
                if tracker < beta:
                    beta = tracker

        if depth > 1:
            return tracker, movements, alpha, beta, winner
        return results, movements, alpha, beta, winners

    # --------------------------------------------------------------------------
    def step(self, board, possible, reward, done, args, time_limit=30, use_prob=False):

        # own symbol to check against in evaluations;
        self._own_symbol = args["own_symbol"]

        # hashing and probability distribution initialization;
        hhash = self._board._board.tostring()
        self._prob_distribution = np.zeros_like(self._board._board)
        self._total_wins = 0.0

        # check whether the move has already been cached
        if hhash in self._cache:

            # if so return it from cache
            results, movements, alpha, beta = self._cache[hhash]

        else:

            results, movements, alpha, beta, winners = self.minimax(
                self._board, moves=[], depth=1, maxx=True
            )

            # try the probability distribution that was calculated;
            arg = np.argmax(results)

            # print("AGENT DECISIONS", perc if use_prob else results, movements)
            # print(winners)
            # print(f"  Picked {results[arg]} - {movements[arg]}")

            # set the final results and movements;
            results = [results[arg]]
            movements = [movements[arg]]

            # add result to cache;
            self._cache[hhash] = (results, movements, alpha, beta)

        # print("Minimax decision: %4.4f using => " % results[0], movements[0], "alpha:%4.4f, beta:%4.4f" % (alpha, beta))
        return movements[0][0]

    # --------------------------------------------------------------------------
    def end_game(self):

        pass
