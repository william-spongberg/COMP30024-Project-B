# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import copy
import gc
from hmac import new
import random

# import tensorflow as tf
from agent_mcts.mcts import MCTSNode
from helpers.movements import generate_random_move
from helpers.sim_board import SimBoard
from referee.game import (
    PlayerColor,
    Action,
    Action,
    Coord,
)
from referee.game import board
from referee.game.board import Board

# TODO: redesign Board data structure to be more efficient


class Agent:

    # attributes
    board: SimBoard  # state of game
    root: MCTSNode | None  # root node of MCTS tree NOTE: not to initialise until after first two turns
    color: PlayerColor  # agent colour
    opponent: PlayerColor  # agent opponent

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)

    def action(self, **referee: dict) -> Action:
        if self.board.turn_count < 2:
            return generate_random_move(self.board.state, self.color, first_turns=True)
        else:
            if not self.root:
                self.root = MCTSNode(state=copy.deepcopy(self.board.state), color=self.color)
                
        action = self.root.best_action(sim_no=5)

        if action:
            return action
        return self.random_move()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.board.apply_action(action)
        if not self.root:
            return
        new_root = self.root.get_child(action)
        self.root.chop_nodes_except(new_root)
        gc.collect()
        self.root = new_root
        # print(self.root.board.render(True))

    def init(self, color: PlayerColor):
        self.board = SimBoard()
        self.color = color
        self.root = None
        self.name = "Agent_MCTS " + self.color.name
        self.opponent = self.color.opponent

        print(f"{self.name} *initiated*: {self.color}")

    def random_move(self) -> Action:
        return random.choice(list(self.available_moves))
    
    async def async_thinking(self):
        # TODO: implement async thinking no matter who is taking the turn
        pass
    
    @property
    def available_moves(self) -> set[Action]:
        if self.root:
            return self.root.my_actions
        return set()

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
