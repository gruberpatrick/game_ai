from agents.agent import Agent


class QAgent(Agent):

    def __init__(self, engine, params):

        self._engine = engine
        self._params = params
