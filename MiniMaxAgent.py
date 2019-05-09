
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
            res = 1.0
            mask = np.where(board._board == ord(self._own_symbol), 1, 0)
            self._prob_distribution += mask
        elif not winner:
            res = 0.0
            mask = np.where(board._board == ord(self._own_symbol), 1, 0)
            self._prob_distribution += mask

        self._total_wins += 1

        return [1/depth*res], [moves], alpha, beta

    # --------------------------------------------------------------------------
    def minimax(self, board, moves=[], depth=1, maxx=True, alpha=float("-inf"), 
            beta=float("inf")):

        possible = board.possibleMoves()
        mm = moves[:]

        #results = []
        #movements = []

        results = [float("-inf") if maxx else float("inf")]
        movements = []

        for move in possible:

            nb = board.c()
            check = nb.makeMove(move[0], move[1])

            if not check: continue

            action = "nothing"

            if not nb._started:
                res, moves, alpha, beta = self.evaluate(nb, mm + [move], depth+1, alpha=alpha, beta=beta)
                action = "evaluate"
            else:
                res, moves, alpha, beta = self.minimax(
                    nb, 
                    moves = mm + [move],
                    depth = depth + 1,
                    maxx = False if maxx else True,
                    alpha = alpha,
                    beta = beta
                )
                action = "recursion"

            #print(mm, depth, max)
            print(" "*depth, "MAX" if maxx else "MIN")
            print(" "*depth, action)
            print(" "*depth, "res", res, "alpha", alpha, "beta", beta)
            # maximize operations
            if maxx:
                if res[0] > results[0]:
                    results = res
                    movements = moves
                if results[0] > alpha: alpha = results[0]
                if results[0] >= beta: break
            # minimize operations
            else:
                if res[0] < results[0]:
                    results = res
                    movements = moves
                if results[0] < beta: beta = results[0]
                if results[0] <= alpha: break
            
            #results.extend(res)
            #movements.extend(moves)

        """if depth > 1:
            if maxx: arg = np.argmax(results)
            else: arg = np.argmin(results)
            results = [results[arg]]
            movements = [movements[arg]]
        else:
            prob = self._prob_distribution / self._total_wins
            perc = []
            for move in movements:
                mm = move[0]
                perc.append(prob[mm[1]][mm[0]])
            print(perc, movements)
            arg = np.argmax(perc)
            results = [results[arg]]
            movements = [movements[arg]]"""
        
        print(" "*depth, "RETURN", results)
        return results, movements, alpha, beta

    # --------------------------------------------------------------------------
    def step(self, possible):

        self._own_symbol = self._board._players[self._board._player_pointer]

        #hhash = self._board._board.tostring()
        self._prob_distribution = np.zeros_like(self._board._board)
        self._total_wins = 0.0

        #if hhash in self._cache:

        #    results, movements, alpha, beta = self._cache[hhash]
        
        #else:

        results, movements, alpha, beta = self.minimax(self._board, moves=[], depth=1, maxx=True)
        #self._cache[hhash] = (results, movements, alpha, beta)

        print(results, movements)
        print("Minimax decision: %4.4f using => " % results[0], movements[0], "alpha:%4.4f, beta:%4.4f" % (alpha, beta))

        print(self._prob_distribution / self._total_wins)

        return movements[0][0]
        
