# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import copy
import random

from helpers.sim_board import SimBoard
from helpers.movements import valid_moves, valid_coords
from referee.game import PlayerColor, Action, Action, Coord
from referee.game.board import Board


class Agent:

    # attributes
    board: SimBoard  # state of game
    color: PlayerColor  # agent colour
    name: str  # agent name
    opponent: PlayerColor  # agent opponent

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)

    def action(self, **referee: dict) -> Action:
        return self.get_random_move()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.board.apply_action(action)

    def init(self, color: PlayerColor):
        self.board = SimBoard()
        self.color = color
        self.name = "Agent_Random " + self.color.name
        self.opponent = self.color.opponent

        print(f"{self.name} *initiated*: {self.color}")

    def get_random_move(self) -> Action:
        coords = valid_coords(self.board.state, self.color)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while not valid_moves(self.board.state, coord):
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if not valid_moves(self.board.state, coord):
            return Action(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))

        # prints to track valid moves generated
        print(
            f"generated {len(valid_moves(self.board.state, coord))} valid moves at {coord}"
        )
        for move in valid_moves(self.board.state, coord):
            print(move)

        # return random move
        return random.choice(valid_moves(self.board.state, coord))


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
    def state(self):
        return self.agent.board.state
