# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import gc
import random

# import tensorflow as tf
from agent_mcts.mcts import MCTSNode
from helpers.bit_board import BitBoard, bit_check_adjacent_cells, bit_generate_random_move, bit_is_valid
from helpers.sim_board import SimBoard
from timeit import default_timer as timer
from referee.game import (
    PlayerColor,
    Action,
    Action,
    Coord,
)
from referee.game.constants import MAX_TURNS

NARROW_SIM_NO = 200
BACKUP_TIME = 5
NARROW_MOVE_NO = 70

class Agent:

    # attributes
    board: BitBoard  # state of game
    root: (
        MCTSNode | None
    )  # root node of MCTS tree NOTE: not to initialise until after first two turns
    color: PlayerColor  # agent colour
    opponent: PlayerColor  # agent opponent

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)

    def action(self, **referee: dict) -> Action:
        if self.board.turn_count < 2:
            return bit_generate_random_move(self.board, self.color, first_turns=True)
        else:
            if not self.root:
                self.root = MCTSNode(self.board.copy())
                
        # branching factor too high, pick random
        if (self.root.estimated_time < 0 or 
            (len(self.root.my_actions) > 200 and self.board.turn_count < 10)):
            return self.random_move()
        
        # time count
        if referee:
            start_time = timer()
            time_remaining:float = referee["time_remaining"] # type: ignore
            estimate_moves = self.root.rollout_turns(10)
            if estimate_moves == 0:
                estimate_moves = MAX_TURNS - self.board.turn_count
            estimation_cost = timer() - start_time
            estimated_time = (time_remaining - estimation_cost - BACKUP_TIME) / estimate_moves
            time_left = time_remaining - estimation_cost
            print("Time left: ", time_left)
            print(f"Estimated time: {estimated_time} for {estimate_moves} moves")
        else:
            estimated_time = 10000
        
        self.root.estimated_time = estimated_time

        if estimate_moves > 6 or len(self.root.my_actions) > 100:
            # not to waste time on too many branches
            print("Greedy explore")
            action = self.root.greedy_explore()
        else:
            # take it serious on intensive situations
            print("Narrow search")
            action = self.root.best_action(
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
        # gc.collect()
        self.root = new_root
        # print(self.root.board.render(True))

    def init(self, color: PlayerColor):
        self.board = BitBoard()
        self.color = color
        self.root = None
        self.name = "Agent_MCTS " + self.color.name
        self.opponent = self.color.opponent

        print(f"{self.name} *initiated*: {self.color}")

    def random_move(self) -> Action:
        action = random.choice(list(self.available_moves))
        if not bit_is_valid(self.board, action) or not bit_check_adjacent_cells(
            self.board, list(action.coords), self.color
        ):
            print("Invalid action: ", action)
            print("state: ", self.board.render())
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
