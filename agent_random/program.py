# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import random

from agent_random.movements import valid_moves, valid_coords
from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.board import Board


class Agent:

    # attributes
    board: Board  # state of game
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
        self.board = Board()
        self.color = color
        self.name = "Agent_Random " + self.color.name

        match color:
            case PlayerColor.RED:
                self.opponent = PlayerColor.BLUE
            case PlayerColor.BLUE:
                self.opponent = PlayerColor.RED

        print(f"{self.name} *initiated*: {self.color}")

    def get_random_move(self) -> PlaceAction:
        coords = valid_coords(self.board._state, self.color)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while not valid_moves(self.board._state, coord):
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if not valid_moves(self.board._state, coord):
            return PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))

        # return random move
        return random.choice(valid_moves(self.board._state, coord))


class AgentRandom:
    # wrap Agent class
    def __init__(self, color: PlayerColor, **referee: dict):
        self.agent = Agent(color)

    def action(self, **referee: dict) -> Action:
        return self.agent.action()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.agent.update(color, action)

    @property
    def color(self):
        return self.agent.color
