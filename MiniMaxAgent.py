
import numpy as np

from Agent import Agent

class MiniMaxAgent(Agent):

    _cache = {}

    # --------------------------------------------------------------------------
    def evaluate(self, board, moves=[], depth=1, alpha=float("-inf"), 
            beta=float("inf")):

        res = -1.0

        winner = board._winner

        if winner == self._own_symbol:
            res = (1.0 / depth) + 2
            mask = np.where(board._board == ord(self._own_symbol), 1, 0)
            self._prob_distribution += mask
        elif not winner:
            res = 1.0 / depth
            mask = np.where(board._board == ord(self._own_symbol), 1, 0)
            self._prob_distribution += mask

        self._total_wins += 1

        return res, [moves], alpha, beta

    # --------------------------------------------------------------------------
    def minimax(self, board, moves=[], depth=1, maxx=True, alpha=float("-inf"), 
            beta=float("inf")):

        possible = board.possibleMoves()
        mm = moves[:]

        if not board._started or depth == 5:
            res, mov, alpha, beta = self.evaluate(board, mm, depth+1, alpha=alpha, beta=beta)
            #print(" "*depth, " == RETURN", res)
            return res, mov, alpha, beta

        tracker = float("-inf") if maxx else float("inf")
        results = []
        movements = []
        total = len(possible)
        counter = 1.0

        for move in possible:

            nb = board.c()
            check = nb.makeMove(move)

            if not check: continue

            res, mov, _, _ = self.minimax(
                nb, 
                moves = mm + [move],
                depth = depth + 1,
                maxx = False if maxx else True,
                alpha = alpha,
                beta = beta
            )

            #print(" "*depth, "MAX" if maxx else "MIN")
            #print(" "*depth, "res", res, "results", results, "alpha", alpha, "beta", beta)
            # maximize operations
            if maxx:
                if depth > 1:
                    if res > tracker:
                        tracker = res
                        movements = mov
                    if tracker >= beta:
                        #print(" "*depth, "BREAK")
                        break
                    if tracker > alpha: 
                        alpha = tracker
                        #print(" "*depth, "new alpha", alpha)
                else:
                    print("\t\rCalculating", counter / total * 100, "%", end="")
                    results.append(res)
                    movements.extend(mov)
                    counter += 1
                
            # minimize operations
            else:
                if res < tracker:
                    tracker = res
                    movements = mov
                if tracker <= alpha: 
                    #print(" "*depth, "BREAK")
                    break
                if tracker < beta: 
                    beta = tracker
                    #print(" "*depth, "new beta", beta)
            #results.extend(res)
            #movements.extend(moves)
        
        #print(" "*depth, "RETURN", tracker if depth > 1 else results)
        if depth > 1: return tracker, movements, alpha, beta
        print("")
        return results, movements, alpha, beta

    # --------------------------------------------------------------------------
    def step(self, possible):

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
                perc.append( (prob[mm[1]][mm[0]] * results[it]) + results[it] )
            arg = np.argmax(perc)

            print("TRANSFORMED", results, movements)

            results = [results[arg]]
            movements = [movements[arg]]

            #self._cache[hhash] = (results, movements, alpha, beta)

        print("Minimax decision: %4.4f using => " % results[0], movements[0], "alpha:%4.4f, beta:%4.4f" % (alpha, beta))

        print(self._prob_distribution / self._total_wins)

        return movements[0][0]
        
