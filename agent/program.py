# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import random

from agent.mcts import MCTSNode
from .helpers.movements import check_adjacent_cells, generate_random_move, is_valid
from .helpers.sim_board import SimBoard
from timeit import default_timer as timer
from referee.game import PlayerColor, Action, Action
from referee.game.constants import MAX_TURNS

WIDE_DEPTH = 4
NARROW_DEPTH = 8
NARROW_SIM_NO = 200
NARROW_MOVE_NO = 100
BACKUP_TIME = 5
NUM_TURN_ESTIMATION_ROLLOUTS = 3


class Agent:

    # attributes
    board: SimBoard  # state of game
    root: MCTSNode | None  # root node of MCTS tree
    color: PlayerColor  # agent colour
    opponent: PlayerColor  # agent opponent
    estimated_time: float  # estimated time for each move
    estimated_turns: int  # estimated turns for each move

    def __init__(self, color: PlayerColor, **referee: dict):
        self.init(color)

    def init(self, color: PlayerColor):
        # agent info
        self.color = color
        self.name = "Agent_MCTS " + self.color.name
        self.opponent = self.color.opponent

        # game state
        self.board = SimBoard()
        self.root = None

        # announce agent
        print(f"{self.name} *initiated*: {self.color}")

    def action(self, **referee: dict) -> Action:
        # first two turns, do random moves
        if self.board.turn_count < 2:
            return generate_random_move(self.board.state, self.color, first_turns=True)

        # then can start MCTS
        if not self.root:
            self.root = MCTSNode(self.board.copy())

        # branching factor too high, pick random since not worth MCTS
        if self.root.estimated_time < 0 or (
            len(self.root.my_actions) > 200 and self.board.turn_count < 6
        ):
            return self.random_move()

        # be aware of timer
        if referee:
            self.set_timer(referee)
        else:
            # if no referee, just set a large default time
            self.estimated_time = 10000
        self.root.estimated_time = self.estimated_time

        # casual search if not too many moves
        if len(self.root.my_actions) > NARROW_MOVE_NO:
            print("Wide search")
            action = self.root.best_action(
                WIDE_DEPTH, min((int)(len(self.root.my_actions)), NARROW_SIM_NO)
            )
        else:
            # take it serious on intensive situations
            print("Narrow search")
            action = self.root.best_action(
                NARROW_DEPTH,
                max((int)(len(self.root.my_actions) * 2), NARROW_SIM_NO),
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

    def set_timer(self, referee):
        start_time = timer()
        time_remaining: float = referee["time_remaining"]  # type: ignore
        
        self.estimated_turns = self.root.rollout_turns(NUM_TURN_ESTIMATION_ROLLOUTS)  # type: ignore
        if self.estimated_turns == 0:
            self.estimated_turns = MAX_TURNS - self.board.turn_count
            
        estimation_cost = timer() - start_time
        self.estimated_time = (
            time_remaining - estimation_cost - BACKUP_TIME
        ) / self.estimated_turns
        time_left = time_remaining - estimation_cost

        print("Time left: ", time_left)
        print(f"Estimated time: {self.estimated_time} for {self.estimated_turns} moves")

    def random_move(self) -> Action:
        """
        Generate a random move for the agent
        """
        return random.choice(list(self.available_moves))

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
