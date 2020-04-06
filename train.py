import argparse
import json
import neptune

from lib.engine import Engine


class Train:

    def __init__(self):
        self._engine = Engine()

    def add_player(self, name, type):
        self._engine.add_player(name, type)

    def pick_board(self, board):
        self._engine.pick_board(board)

    def run(self):

        while True:
            self._engine.episode()


def main(args):

    neptune.init('gruberpatrick/game-ai')
    neptune.create_experiment(name='args.players')

    args.players = json.loads(args.players)

    train = Train()
    for player in args.players:
        train.add_player(player["name"], player["type"])
    train.pick_board(args.board)
    train.run()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Game playing trainer.")

    parser.add_argument(
        "--players",
        action="store",
        type=str,
        required=True,
        help="JSON string to define the players: [{\"name\": \"Player 1\", \"type\": \"random\"}, ...]",
    )

    parser.add_argument(
        "--board",
        action="store",
        type=str,
        required=True,
        help="The board to play on."
    )

    main(parser.parse_args())
