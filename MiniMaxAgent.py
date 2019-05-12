
import numpy as np
import time

from Agent import Agent

class MiniMaxAgent(Agent):

    _cache = {}
    _debug = False

    # --------------------------------------------------------------------------
    def evaluate(self, board, moves=[], depth=1, alpha=float("-inf"), 
            beta=float("inf")):

        # TODO: normalize the occurences per branch when adding to the
        # prob_distribution

        res = -(1.0 / depth) - 200.0

        winner = board._winner

        if winner == self._own_symbol:
            res = (1.0 / depth) + 100
            mask = np.where(board._board == ord(self._own_symbol), 1, 0)
            self._prob_distribution += mask
        elif not winner:
            res = (1.0 / depth) + 50
            mask = np.where(board._board == ord(self._own_symbol), 1, 0)
            self._prob_distribution += mask

        self._total_wins += 1

        return res, [moves], alpha, beta

    # --------------------------------------------------------------------------
    def estimateRow(self, row):

        row = np.flip(row)

        series = 0.0
        last_elem = -1

        longest_series = 0.0

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

        # if row is full, nothing
        if len(row[row == 0]) == 0: return 0

        checks = []
        player = -1
        opponent = -1

        for p in self._board._players:
            player = ord(p)
            for o in self._board._players:
                if o == p: continue
                opponent = ord(o)
                check = np.where(row != player, opponent, player)
                checks.append(check)

        last_elem = -1
        series = 0.0
        player_series = 0.0

        for row in checks:
            for elem in row:
                if elem != last_elem:
                    last_elem = elem
                    series = 1.0
                    continue
                if elem == last_elem and elem == player:
                    series += 1.0
                if series > player_series: player_series = series

        last_elem = -1
        series = 0.0
        opponent_series = 0.0

        for row in checks:
            for elem in row:
                if elem != last_elem:
                    last_elem = elem
                    series = 1.0
                    continue
                if elem == last_elem and elem == player:
                    series += 1.0
                if series > opponent_series: opponent_series = series

        if player_series > opponent_series and player_series >= self._board._wins: 
            return player_series / len(checks[0])
        elif opponent_series >= self._board._wins:
            return -(opponent_series / len(checks[0]))

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

        possible = board.possibleMoves()
        mm = moves[:]

        if not board._started:
            res, mov, alpha, beta = self.evaluate(board, mm, depth+1, alpha=alpha, beta=beta)
            if self._debug: print(" "*depth, str(depth)+":", " == RETURN", res)
            return res, mov, alpha, beta

        if depth >= 6:
            res, mov, alpha, beta = self.estimate(board, mm, depth+1, alpha=alpha, beta=beta)
            if self._debug: print(" "*depth, str(depth)+":", " == RETURN", res)
            return res, mov, alpha, beta

        tracker = float("-inf") if maxx else float("inf")
        results = []
        movements = []
        total = len(possible)
        counter = 1.0

        for move in possible:

            if depth > 1:
                total_stop = float(time.time()) - self._start_time >= self._cutoff
                branch_stop = float(time.time()) - self._branch_start_time >= self._branch_cutoff
                if total_stop or branch_stop: break

            nb = board.c()
            check = nb.makeMove(move)

            if not check: continue

            if depth == 1:
                self._branch_start_time = float(time.time())

            res, mov, _, _ = self.minimax(
                nb, 
                moves = mm + [move],
                depth = depth + 1,
                maxx = False if maxx else True,
                alpha = alpha,
                beta = beta
            )

            if self._debug: print(" "*depth, str(depth)+":", "MAX" if maxx else "MIN")
            if self._debug: print(" "*depth, str(depth)+":", "res", res, "results", results, "alpha", alpha, "beta", beta)
            # maximize operations
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
                    if self._debug: print("\t\rCalculating", counter / total * 100, "%", end="")
                    results.append(res)
                    movements.extend(mov)
                    counter += 1
                
            # minimize operations
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
            #results.extend(res)
            #movements.extend(moves)
        
        if self._debug: print(" "*depth, str(depth)+":", "RETURN", tracker if depth > 1 else results)
        if depth > 1: return tracker, movements, alpha, beta
        print("")
        return results, movements, alpha, beta

    # --------------------------------------------------------------------------
    def step(self, possible, time_limit=30):

        self._start_time = float(time.time())
        self._cutoff = time_limit - 2
        self._branch_cutoff = time_limit / len(possible)

        self._own_symbol = self._board._players[self._board._player_pointer]

        hhash = self._board._board.tostring()
        self._prob_distribution = np.zeros_like(self._board._board)
        self._total_wins = 0.0

        if hhash in self._cache:

            results, movements, alpha, beta = self._cache[hhash]
        
        else:

            results, movements, alpha, beta = self.minimax(self._board, moves=[], depth=1, maxx=True)

            print("ORIGINAL", results, movements)

            prob = (self._prob_distribution+.001) / (self._total_wins+.001)
            perc = []
            for it in range(len(movements)):
                mm = movements[it][0]
                #print(prob)
                #print(results)
                perc.append( (prob[mm[1]][mm[0]] * results[it]) + results[it] )
            #arg = np.argmax(perc)
            arg = np.argmax(results)

            #print("PERC", perc)
            print("AGENT DECISIONS", perc, movements)

            results = [results[arg]]
            movements = [movements[arg]]

            #self._cache[hhash] = (results, movements, alpha, beta)

        print("Minimax decision: %4.4f using => " % results[0], movements[0], "alpha:%4.4f, beta:%4.4f" % (alpha, beta))

        return movements[0][0]
        
