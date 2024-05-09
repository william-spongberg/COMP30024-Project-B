# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import gc
import random

# import tensorflow as tf
from agent_mcts.mcts import MCTSNode
from helpers.movements import check_adjacent_cells, generate_random_move, is_valid
from helpers.sim_board import SimBoard
from referee.game import (
    PlayerColor,
    Action,
    Action,
    Coord,
)

NARROW_SIM_NO = 80
WIDE_SIM_NO = 40
# MAX_STEPS = 10 # not used, should modify MCTS class to use this

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
                self.root = MCTSNode(self.board)
        
        if len(self.root.my_actions) > 200:
            return self.random_move()
        if len(self.root.my_actions) > 100 and not self.root.danger:
            # not to waste time on too many branches
            action = self.root.best_action(max((int)(len(self.root.my_actions)/2), WIDE_SIM_NO))
        else:
            # take it serious on intensive situations
            action = self.root.best_action(max((int)(len(self.root.my_actions)), NARROW_SIM_NO))
        
        if action:
            # temp fix for invalid actions
            if not check_adjacent_cells(action.coords, self.board.state, self.color):
                print("Invalid action: ", action)
                print("state: ", self.board.state)
                exit(1)
                # self.root.untried_actions.remove(action)
                # self.root.my_actions.remove(action)
                # return self.action()
            self.root.my_actions.remove(action)
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
        action = random.choice(list(self.available_moves))
        if not is_valid(self.board.state, action) or not check_adjacent_cells(action.coords, self.board.state, self.color):
            print("Invalid action: ", action)
            print("state: ", self.board.state)
            exit(1)
            # self.available_moves.remove(action)
            # return self.random_move()
        return action
    
    async def async_thinking(self):
        # TODO: implement async thinking no matter who is taking the turn
        pass
    
    @property
    def available_moves(self) -> list[Action]:
        if self.root:
            return self.root.my_actions
        return []

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
