# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import copy
import random

from helpers.bit_board import BitBoard, bit_generate_random_move
from helpers.sim_board import SimBoard
from helpers.movements import generate_random_move
from referee.game import PlayerColor, Action, Action


class Agent:

    # attributes
    board: BitBoard  # state of game
    color: PlayerColor  # agent colour
    name: str  # agent name
    opponent: PlayerColor  # agent opponent

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)

    def action(self, **referee: dict) -> Action:
        if self.board.turn_count < 2:
            return bit_generate_random_move(self.board, self.color, first_turns=True)
        return bit_generate_random_move(self.board, self.color)

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.board.apply_action(action)

    def init(self, color: PlayerColor):
        self.board = BitBoard()
        self.color = color
        self.name = "Agent_Random " + self.color.name
        self.opponent = self.color.opponent

        print(f"{self.name} *initiated*: {self.color}")

class AgentRandom:
    # wrap Agent class
    def __init__(self, color: PlayerColor):
        self.agent = Agent(color)

    def action(self) -> Action:
        return self.agent.action()

    def update(self, color: PlayerColor, action: Action):
        self.agent.update(color, action)

    @property
    def color(self):
        return self.agent.color

    @property
    def name(self):
        return self.agent.name

    @property
    def state(self):
        return self.agent.board.state
