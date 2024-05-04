# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import copy
import random

from helpers.sim_board import SimBoard
from helpers.movements import valid_moves, valid_coords
from referee.game import PlayerColor, Action, PlaceAction, Coord
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
        self.board = SimBoard(init_color=color)
        self.color = color
        self.name = "Agent_Random " + self.color.name
        self.opponent = self.color.opponent

        print(f"{self.name} *initiated*: {self.color}")

    def get_random_move(self) -> PlaceAction:
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
            return PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        
        # *DEBUGGING* valid moves not working correctly, invalid moves being generated
        print(f"valid moves at coord {coord}:")
        for move in valid_moves(self.board.state, coord): # type: ignore
            print(move)
            temp_board = copy.deepcopy(self.board)
            temp_board.apply_action(move)
            #print(temp_board.render(True))
        print("board colour: ", self.board.turn_color)
        print(f"generated {len(valid_moves(self.board.state, coord))} valid moves at {coord}") # type: ignore
            

        # return random move
        return random.choice(valid_moves(self.board.state, coord)) # type: ignore


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
