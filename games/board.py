class Board:

    def __init__(self, players):

        self._players = players
        self.reset_board()

    def reset_board(self):

        raise NotImplementedError('Not implemented.')

    def get_board(self):

        raise NotImplementedError('Not implemented.')

    def get_possible_moves(self):

        raise NotImplementedError('Not implemented.')

    def get_reward(self):

        raise NotImplementedError('Not implemented.')

    def get_done(self):

        raise NotImplementedError('Not implemented.')

    def step(self, move, value):

        raise NotImplementedError('Not implemented.')

    def render(self, img):

        return img
