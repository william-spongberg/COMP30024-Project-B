# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import random

from agent_mcts.mcts import MCTSNode
from .helpers.movements import check_adjacent_cells, generate_random_move, is_valid
from .helpers.sim_board import SimBoard
from timeit import default_timer as timer
from referee.game import (
    PlayerColor,
    Action,
    Action
)
from referee.game.constants import MAX_TURNS

WIDE_DEPTH = 4
NARROW_DEPTH = 8
NARROW_SIM_NO = 200
NARROW_MOVE_NO = 100
BACKUP_TIME = 5

class Agent:

    # attributes
    board: SimBoard  # state of game
    # NOTE: not to initialise until after first two turns
    root: (MCTSNode | None)  # root node of MCTS tree 
    color: PlayerColor  # agent colour
    opponent: PlayerColor  # agent opponent

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)

    def action(self, **referee: dict) -> Action:
        # first two turns, run hard-coded moves
        if self.board.turn_count < 2:
            return generate_random_move(self.board.state, self.color, first_turns=True)
        # then we can start MCTS
        else:
            if not self.root:
                self.root = MCTSNode(self.board.copy())
                
        # branching factor too high, pick random
        if (self.root.estimated_time < 0 or 
            (len(self.root.my_actions) > 200 and self.board.turn_count < 6)):
            return self.random_move()
        
        # time count
        if referee:
            start_time = timer()
            time_remaining:float = referee["time_remaining"] # type: ignore
            estimate_turns = self.root.rollout_turns(1)
            if estimate_turns == 0:
                estimate_turns = MAX_TURNS - self.board.turn_count
            estimation_cost = timer() - start_time
            estimated_time = (time_remaining - estimation_cost - BACKUP_TIME) / estimate_turns
            time_left = time_remaining - estimation_cost
            print("Time left: ", time_left)
            print(f"Estimated time: {estimated_time} for {estimate_turns} moves")
        else:
            estimated_time = 10000
        
        self.root.estimated_time = estimated_time

        # casual search
        if len(self.root.my_actions) > NARROW_MOVE_NO:
            print("Wide search")
            action = self.root.best_action(WIDE_DEPTH,
                min((int)(len(self.root.my_actions)), NARROW_SIM_NO))
        else:
            # take it serious on intensive situations
            print("Narrow search")
            action = self.root.best_action(NARROW_DEPTH,
                max((int)(len(self.root.my_actions)*2), NARROW_SIM_NO),
            )

        if action:
            self.root.my_actions.remove(action)
            return action
        return self.random_move()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        self.board.apply_action(action)
        if not self.root:
            return
        new_root = self.root.get_child(action)
        self.root.chop_nodes_except(new_root)
        self.root = new_root

    def init(self, color: PlayerColor):
        self.board = SimBoard()
        self.color = color
        self.root = None
        self.name = "Agent_MCTS " + self.color.name
        self.opponent = self.color.opponent

        print(f"{self.name} *initiated*: {self.color}")

    def random_move(self) -> Action:
        """
        Generate a random move for the agent, useless if the node is not initialised
        """
        action = random.choice(list(self.available_moves))
        if not is_valid(self.board.state, action) or not check_adjacent_cells(
            action, self.board.state, self.color
        ):
            print("Invalid action: ", action)
            print("state: ", self.board.render())
            exit(1)
        return action

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
