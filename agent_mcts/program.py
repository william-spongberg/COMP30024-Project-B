# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import copy
import random

# import tensorflow as tf
from cmath import log
from collections import defaultdict
from agent_random.movements import get_valid_coords, get_valid_moves
from agent_random.tetronimos import get_tetronimos
from referee.game import (
    PlayerColor,
    Action,
    PlaceAction,
    Coord,
)
from referee.game.board import Board, CellState

# TODO: redesign Board data structure to be more efficient


class Agent:
    """
    This class is the "entry point" for your self, providing an interface to
    respond to various Tetress game events.
    """

    # attributes
    game_board: Board  # to keep track of game
    game_state: dict[Coord, CellState]  # to try different moves
    tetronimos: list[PlaceAction]  # list of all possible tetronimos
    opponent: PlayerColor  # to keep track of opponent
    sim_logs: list[str]  # to keep track of simulation results
    sim_commentary: list[str]  # to keep track of simulation commentary
    sim_game_num: int  # to keep track of simulation number

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the self.
        Any setup and/or precomputation should be done here.
        """
        self.game_board = Board()
        self.game_state = self.game_board._state
        self.tetronimos = get_tetronimos(Coord(0, 0))
        self._color = color
        self.name = "self_Next " + self._color.name
        self.sim_logs = []
        self.sim_commentary = []
        self.sim_game_num = 0

        # test tetronimos
        with open("tetronimos_test.txt", "w") as f:
            for tetronimo in get_tetronimos(Coord(5, 5)):
                board = Board()
                board.apply_action(tetronimo)
                print(board.render(), file=f)

        # announce self
        print(f"{self.name} *init*: {self._color}")

        # set opponent colour
        match color:
            case PlayerColor.RED:
                self.opponent = PlayerColor.BLUE
            case PlayerColor.BLUE:
                self.opponent = PlayerColor.RED

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the self's turn
        to take an action. It must always return an action object.
        """
        root = MCTSNode(self.game_board)
        action = root.best_action(sim_no=10)

        if action:
            return action
        else:
            return self.get_random_move()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state.
        """

        self.game_board.apply_action(action)
        self.game_state = self.game_board._state

    def get_random_move(self) -> PlaceAction:
        coords = get_valid_coords(self.game_state, self._color)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while get_valid_moves(self.game_state, self.tetronimos, coord) == []:
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if get_valid_moves(self.game_state, self.tetronimos, coord) == []:
            return PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        return random.choice(get_valid_moves(self.game_state, self.tetronimos, coord))

# TODO: fix extreme inefficiency - see board redesign TODO
class MCTSNode:
    def __init__(self, board: Board, parent=None, parent_action=None):
        self.board: Board = board
        self.state: dict[Coord, CellState] = board._state
        self.parent: MCTSNode | None = parent
        self.parent_action: PlaceAction | None = parent_action
        self.children = []

        self._num_visits = 0
        self._actions: list[PlaceAction] = self.get_actions()
        self._results = defaultdict(int)
        self._results[1] = 0  # win
        self._results[-1] = 0  # loss

    def get_actions(self):
        coords: list[Coord] = get_valid_coords(self.state, self.board.turn_color)
        tetronimos: list[PlaceAction] = get_tetronimos(Coord(0, 0))
        actions: list[PlaceAction] = []
        for coord in coords:
            actions.extend(get_valid_moves(self.state, tetronimos, coord))
        #print("valid actions initially: ", actions)
        return actions

    def num_visits(self):
        return self._num_visits

    def expand(self):
        board_node: Board = copy.deepcopy(self.board)
        action = self._actions.pop()
        #print(action)            
        board_node.apply_action(action)
        child_node: MCTSNode = MCTSNode(board_node, self, action)

        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.board.game_over

    def is_fully_expanded(self):
        #print(len(self._actions))
        return len(self._actions) == 0

    def rollout(self):
        current_board: Board = copy.deepcopy(self.board)
        while not current_board.game_over:
            # light playout policy
            # TODO: implement heuristic-driven playout policy
            action = self.get_random_move(current_board)
            # if action available, apply
            if action:
                current_board.apply_action(action)
                #print(current_board.render())
            # if no action available, other player wins
            else:
                print("winner: ", current_board.turn_color.opponent)
                return current_board.turn_color.opponent
        # game over but we still have moves => we win
        print("winner: ", current_board.turn_color)
        return current_board.turn_color

    def backpropagate(self, result):
        self._num_visits += 1
        self._results[result] += 1
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, c_param=1.4):
        best_score: float = -1.0
        best_child = None
        for child in self.children:
            if child._num_visits == 0 or self._num_visits == 0:
                exploit: float = child._results[1]
                explore: float = 0.0
            else:
                exploit: float = child._results[1] / child._num_visits
                # TODO: fix potential error here in abs causing bad results
                explore: float = c_param * abs(2 * log(self._num_visits) / child._num_visits) ** 0.5
            score: float = exploit + explore
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def _tree_policy(self):
        current_node: MCTSNode | None = self
        # select nodes to expand
        while current_node and not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

    def best_action(self, sim_no=100) -> PlaceAction | None:
        # run MCTS
        for _ in range(sim_no):
            # expansion
            v: MCTSNode | None = self._tree_policy()
            if not v:
                print("ERROR: No tree policy node found")
                return None
            # simulation
            print("simulating")
            reward = v.rollout()
            if not reward:
                print("ERROR: No winner found")
                return None
            # backpropagation
            print("backpropagating")
            v.backpropagate(reward)

        # return best action
        best_child = self.best_child(c_param=0.0) # c_param = 0.0
        if best_child:
            return best_child.parent_action

        # if no best child, print error + return None
        print("ERROR: No best child found")
        return None
    
    def get_random_move(self, board) -> PlaceAction | None:
        state = board._state
        tetronimos = get_tetronimos(Coord(0, 0))
        
        coords = get_valid_coords(state, board.turn_color)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while get_valid_moves(state, tetronimos, coord) == []:
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if get_valid_moves(state, tetronimos, coord) == []:
            return None
        # else return random valid move
        return random.choice(get_valid_moves(state, tetronimos, coord))
