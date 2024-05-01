# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import random

# import tensorflow as tf
from agent_mcts.mcts import MCTSNode
from agent_random.movements import get_valid_coords, get_valid_moves
from agent_random.tetronimos import get_tetronimos
from referee.game import (
    PlayerColor,
    Action,
    PlaceAction,
    Coord,
)
from referee.game.board import Board

# TODO: redesign Board data structure to be more efficient


class Agent:

    # attributes
    board: Board  # state of game
    colour: PlayerColor  # agent colour
    opponent: PlayerColor  # agent opponent
    tetronimos: list[PlaceAction]  # list of all possible tetronimos

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)
        self.test_tetronimos()

    def action(self, **referee: dict) -> Action:
        root = MCTSNode(self.board)
        action = root.best_action(sim_no=5)

        if action:
            return action
        else:
            return self.get_random_move()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.board.apply_action(action)

    def init(self, color: PlayerColor):
        self.board = Board()
        self.colour = color
        self.name = "Agent_MCTS " + self.colour.name
        self.tetronimos = get_tetronimos(Coord(0, 0))

        match color:
            case PlayerColor.RED:
                self.opponent = PlayerColor.BLUE
            case PlayerColor.BLUE:
                self.opponent = PlayerColor.RED

        print(f"{self.name} *initiated*: {self.colour}")

    def test_tetronimos(self):
        with open("tetronimos_test.txt", "w") as f:
            for tetronimo in get_tetronimos(Coord(5, 5)):
                board = Board()
                board.apply_action(tetronimo)
                print(board.render(), file=f)

    def get_random_move(self) -> PlaceAction:
        coords = get_valid_coords(self.board._state, self.colour)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while get_valid_moves(self.board._state, self.tetronimos, coord) == []:
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if get_valid_moves(self.board._state, self.tetronimos, coord) == []:
            return PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))

        # return random move
        return random.choice(get_valid_moves(self.board._state, self.tetronimos, coord))


class AgentMCTS:
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