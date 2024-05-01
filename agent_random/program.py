# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import random

from agent_random.movements import valid_moves, valid_coords
from agent_random.tetronimos import make_tetronimos
from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.board import Board


class Agent:

    # attributes
    board: Board  # state of game
    colour: PlayerColor  # agent colour
    name: str  # agent name
    opponent: PlayerColor  # agent opponent
    tetronimos: list[PlaceAction]  # list of all possible tetronimos

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)

    def action(self, **referee: dict) -> Action:
        return self.get_random_move()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.board.apply_action(action)

    def init(self, color: PlayerColor):
        self.board = Board()
        self.colour = color
        self.name = "Agent_Random " + self.colour.name
        self.tetronimos = make_tetronimos(Coord(0, 0))

        match color:
            case PlayerColor.RED:
                self.opponent = PlayerColor.BLUE
            case PlayerColor.BLUE:
                self.opponent = PlayerColor.RED

        print(f"{self.name} *initiated*: {self.colour}")

    def get_random_move(self) -> PlaceAction:
        coords = valid_coords(self.board._state, self.colour)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while valid_moves(self.board._state, self.tetronimos, coord) == []:
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if valid_moves(self.board._state, self.tetronimos, coord) == []:
            return PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))

        # return random move
        return random.choice(valid_moves(self.board._state, self.tetronimos, coord))

class AgentRandom:
    # wrap Agent class
    def __init__(self, color: PlayerColor, **referee: dict):
        self.agent = Agent(color)
    
    def action(self, **referee: dict) -> Action:
        return self.agent.action()
    
    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.agent.update(color, action)
        
    @property
    def colour(self):
        return self.agent.colour