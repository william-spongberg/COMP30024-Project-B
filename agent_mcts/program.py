# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import copy
import random

# import tensorflow as tf
from agent_mcts.mcts import MCTSNode
from helpers.movements import valid_coords, valid_moves
from helpers.sim_board import SimBoard
from helpers.tetrominoes import make_tetrominoes
from referee.game import (
    PlayerColor,
    Action,
    Action,
    Coord,
)
from referee.game.board import Board

# TODO: redesign Board data structure to be more efficient


class Agent:

    # attributes
    board: SimBoard  # state of game
    root: MCTSNode  # root node of MCTS tree
    color: PlayerColor  # agent colour
    opponent: PlayerColor  # agent opponent

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)

    def action(self, **referee: dict) -> Action:
        #self.root = MCTSNode(state=self.board.state, color=self.color)
        action = self.root.best_action(sim_no=10)

        if action:
            return action
        return self.random_move()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.board.apply_action(action)
        # TODO: update MCTS tree every turn
        self.root.add_action(action)
        print(self.root.board.render(True))
        # print(self.board.render(True))

    def init(self, color: PlayerColor):
        self.board = SimBoard()
        self.root = MCTSNode(state=copy.deepcopy(self.board.state))
        self.color = color
        self.name = "Agent_MCTS " + self.color.name
        self.opponent = self.color.opponent

        print(f"{self.name} *initiated*: {self.color}")

    def random_move(self) -> Action:
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

        # return random move
        return random.choice(valid_moves(self.board.state, coord))


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

    @property
    def name(self):
        return self.agent.name

    @property
    def state(self):
        return self.agent.board.state
