
import numpy as np
import time

from Agent import Agent

class MiniMaxAgent(Agent):

    _cache = {}
    _debug = False

    # --------------------------------------------------------------------------
    def evaluate(self, board, moves=[], depth=1, alpha=float("-inf"), 
            beta=float("inf")):

        # if the board is in an end state, we can easily evaluate if the past
        # moves were good choices;

        # by default they are bad;
        res = -(1.0 / depth) - 100.0

        # we'll use the winner to determine the outcome;
        winner = board._winner

        # if the agent is the winner, consider the depth of the graph to
        # distinguish between multiple winning outcomes; this means that the 
        # shortest path is used;
        if winner == self._own_symbol:
            res = (1.0 / depth) + 100
            # keep the probability of the current outcome;
            mask = np.where(board._board == ord(self._own_symbol), 1, 0)
            self._prob_distribution += mask
        # if the board is a draw, we use a lower numbered outcome; to prioritize
        # the winning outcomes;
        elif not winner:
            res = (1.0 / depth) + 50
            # keep the probability of the current outcome;
            mask = np.where(board._board == ord(self._own_symbol), 1, 0)
            self._prob_distribution += mask

        # use the amount of total evaluations for the probabilities;
        self._total_wins += 1

        # pass the data to the recursive calls;
        return res, [moves], alpha, beta

    # --------------------------------------------------------------------------
    def evaluateSeries(self, ID, checks):

        # find the longest consecutive occurences of a given ID in the 
        # previously defined check arrays;

        last_elem = -1
        series = 0.0
        longest_series = 0.0

        for row in checks:
            for elem in row:
                if elem != last_elem:
                    last_elem = elem
                    series = 1.0
                    continue
                if elem == last_elem and elem == ID:
                    series += 1.0
                if series > longest_series: longest_series = series

        return longest_series

    # --------------------------------------------------------------------------
    def estimateRow(self, row):

        """
        GOOD:
        - if opponent can't win
        - if agent can win

        BAD:
        - if opponent can win 
        - if agent can't win

        target cases:

        [ X - X - X - ] => can be converted into a win for X            = +1
        [ O X X X - - ] => can be converted into a win for X            = +1

        [ O - O - O - ] => can be converted into a win for O            = -1
        [ X O O O - - ] => can be converted into a win for O            = -1

        [ X - X O X - ] => can not be converted into a win for X        = 0
        [ X X X O - - ] => can not be converted into a win for X        = 0

        """

        # if row is full, we want to prioritize that outcome over a loss;
        if len(row[row == 0]) == 0: return 0

        series = 0.0
        checks = []
        player = -1
        opponent = -1

        # prepare all the worst and best case scenarios; the idea is that we
        # want to evaluate who would have the upper hand if all the free spots
        # were taken up by only one player;
        for p in self._board._players:
            player = ord(p)
            for o in self._board._players:
                if o == p: continue
                opponent = ord(o)
                check = np.where(row != player, opponent, player)
                checks.append(check)

        # evaluate the worst case scenarios;
        player_series = self.evaluateSeries(player, checks)
        opponent_series = self.evaluateSeries(opponent, checks)

        # return which senario is more dominant;
        if player_series > opponent_series and player_series >= self._board._wins: 
            return player_series / len(checks[0])
        elif opponent_series >= self._board._wins:
            return -(opponent_series / len(checks[0]))

        # if they are evenly distributed, we don't want to consider them, but
        # still prioritize over losses;
        return 0

    # --------------------------------------------------------------------------
    def estimate(self, board, moves=[], depth=1, alpha=float("-inf"), 
            beta=float("inf")):

        # add base board directions;
        to_check = [board._board, board._board.T]

        # add diagonals to check;
        for idx in range(-board._width+1, board._height):
            to_check.append(board._board.diagonal(idx))
            to_check.append(np.flipud(board._board).diagonal(idx))

        res = 0

        # go through boards to check;
        for bb in to_check:

            # if the board is another array;
            if isinstance(bb[0], np.ndarray):

                # go through the rows;
                for row in bb:

                    # and check whether we have a winner;
                    res += self.estimateRow(row)

        return res, [moves], alpha, beta

    # --------------------------------------------------------------------------
    def minimax(self, board, moves=[], depth=1, maxx=True, alpha=float("-inf"), 
            beta=float("inf")):

        # this is pretty much a standard implementation of the minimax
        # algorithm; the only modification is that the shallowest call returns
        # all the results instead of the maximized one; this allows for
        # a final evaluation outside of the call;

        # get all possible and previous moves; 
        possible = board.possibleMoves()
        mm = moves[:]

        # if the board is in an end state, evaluate the result;
        if not board._started:
            res, mov, alpha, beta = self.evaluate(board, mm, depth+1, alpha=alpha, beta=beta)
            if self._debug: print(" "*depth, str(depth)+":", " == RETURN", res)
            return res, mov, alpha, beta

        # if the tree is at a maximum depth, we estimate the outcome with the
        # previously defined function;
        if depth >= 8:
            res, mov, alpha, beta = self.estimate(board, mm, depth+1, alpha=alpha, beta=beta)
            if self._debug: print(" "*depth, str(depth)+":", " == RETURN", res)
            return res, mov, alpha, beta

        # tracker is used both for the min, as well as the max result
        tracker = float("-inf") if maxx else float("inf")

        # results and movements are returned in the shallowest call;
        results = []
        movements = []

        # consider all possible moves;
        for move in possible:

            # if we are at a deep level, consider the time constraint and exit
            # the tree with the current information;
            if depth > 1:
                total_stop = float(time.time()) - self._start_time >= self._cutoff
                branch_stop = float(time.time()) - self._branch_start_time >= self._branch_cutoff
                if total_stop or branch_stop: break

            # copy the board and make the move;
            nb = board.c()
            check = nb.makeMove(move)

            # if the move failed, move on to the next one;
            if not check: continue

            # create the start time for this branch
            if depth == 1: self._branch_start_time = float(time.time())

            # call the recursion;
            res, mov, _, _ = self.minimax(
                nb, 
                moves = mm + [move],
                depth = depth + 1,
                maxx = False if maxx else True,
                alpha = alpha,
                beta = beta
            )

            # only use if it's not working correctly;
            if self._debug: print(" "*depth, str(depth)+":", "MAX" if maxx else "MIN")
            if self._debug: print(" "*depth, str(depth)+":", "res", res, "results", results, "alpha", alpha, "beta", beta)

            # maximize operations, according to the standard implementation;
            if maxx:
                if depth > 1:
                    if res > tracker:
                        tracker = res
                        movements = mov
                    if tracker >= beta:
                        if self._debug: print(" "*depth, str(depth)+":", "BREAK")
                        break
                    if tracker > alpha: 
                        alpha = tracker
                        if self._debug: print(" "*depth, str(depth)+":", "new alpha", alpha)
                else:
                    results.append(res)
                    movements.extend(mov)
            # minimize operations, according to the standard implementation;
            else:
                if res < tracker:
                    tracker = res
                    movements = mov
                if tracker <= alpha: 
                    if self._debug: print(" "*depth, str(depth)+":", "BREAK")
                    break
                if tracker < beta: 
                    beta = tracker
                    if self._debug: print(" "*depth, str(depth)+":", "new beta", beta)
        
        # return 
        if self._debug: print(" "*depth, str(depth)+":", "RETURN", tracker if depth > 1 else results)
        if depth > 1: return tracker, movements, alpha, beta
        return results, movements, alpha, beta

    # --------------------------------------------------------------------------
    def step(self, possible, time_limit=30, use_prob=False):

        # create placeholders for the time constraints;
        self._start_time = float(time.time())
        self._cutoff = time_limit - 2
        self._branch_cutoff = time_limit / len(possible)

        # own symbol to check against in evaluations;
        self._own_symbol = self._board._players[self._board._player_pointer]

        # hashing and probability distribution initialization;
        hhash = self._board._board.tostring()
        self._prob_distribution = np.zeros_like(self._board._board)
        self._total_wins = 0.0

        # check whether the move has already been cached
        if hhash in self._cache:

            # if so return it from cache
            results, movements, alpha, beta = self._cache[hhash]
        
        else:

            results, movements, alpha, beta = self.minimax(self._board, moves=[], depth=1, maxx=True)

            # results containing inf or -inf have not been considered, we have
            # to remove them for the implementation to work; this is usually
            # caused by the time constraint;
            rr = []
            for res in results:
                if res == float("inf") or res == float("-inf"): continue
                rr.append(res)
            results = rr

            if self._debug: print("ORIGINAL", results, movements)

            # try the probability distribution that was calculated;
            if use_prob:
                prob = (self._prob_distribution+.001) / (self._total_wins+.001)
                perc = []
                for it in range(len(movements)):
                    mm = movements[it][0]
                    perc.append( (prob[mm[1]][mm[0]] * results[it]) + results[it] )
                arg = np.argmax(perc)
            # otherwise, just maximize the function results (standard implementation);
            else:
                arg = np.argmax(results)

            print("AGENT DECISIONS", perc if use_prob else results, movements)

            # set the final results and movements;
            results = [results[arg]]
            movements = [movements[arg]]

            # add result to cache;
            self._cache[hhash] = (results, movements, alpha, beta)

        #print("Minimax decision: %4.4f using => " % results[0], movements[0], "alpha:%4.4f, beta:%4.4f" % (alpha, beta))
        return movements[0][0]
