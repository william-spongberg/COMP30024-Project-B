# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import random

# import tensorflow as tf
from agent_mcts.mcts import MCTSNode
from helpers.movements import valid_coords, valid_moves
from helpers.tetrominos import make_tetrominos
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
    color: PlayerColor  # agent colour
    opponent: PlayerColor  # agent opponent

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)
        self.test_tetronimos()

    def action(self, **referee: dict) -> Action:
        root = MCTSNode(state=self.board._state, color=self.color)
        action = root.best_action(sim_no=50)

        if action:
            return action
        return self.random_move()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.board.apply_action(action)
        #print(self.board.render(True))

    def init(self, color: PlayerColor):
        self.board = Board()
        self.color = color
        self.name = "Agent_MCTS " + self.color.name
        self.opponent = self.color.opponent

        print(f"{self.name} *initiated*: {self.color}")

    def test_tetronimos(self):
        with open("tetronimos_test.txt", "w", encoding="utf-8") as f:
            for tetromino in make_tetrominos(Coord(5, 5)):
                board = Board()
                board.apply_action(tetromino)
                print(board.render(), file=f)

    def random_move(self) -> PlaceAction:
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


class AgentMCTS:
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
