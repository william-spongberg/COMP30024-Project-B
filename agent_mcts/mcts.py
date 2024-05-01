from cmath import log
from collections import defaultdict
import copy
import random
from agent_random.movements import get_valid_coords, get_valid_moves
from agent_random.tetronimos import get_tetronimos
from referee.game.actions import PlaceAction
from referee.game.board import Board, CellState
from referee.game.coord import Coord

# TODO: make more efficient
# TODO: implement heuristic-driven playout policy


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
        # print("valid actions initially: ", actions)
        return actions

    def num_visits(self):
        return self._num_visits

    def expand(self):
        board_node: Board = copy.deepcopy(self.board)
        action = self._actions.pop()
        # print(action)
        board_node.apply_action(action)
        child_node: MCTSNode = MCTSNode(board_node, self, action)

        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.board.game_over

    def is_fully_expanded(self):
        # print(len(self._actions))
        return len(self._actions) == 0

    def rollout(self):
        current_board: Board = copy.deepcopy(self.board)
        while not current_board.game_over:
            # light playout policy
            action = self.get_random_move(current_board)
            # if action available, apply
            if action:
                current_board.apply_action(action)
                # print(current_board.render())
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
                explore: float = (
                    c_param * abs(2 * log(self._num_visits) / child._num_visits) ** 0.5
                )
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
            #print("simulating")
            reward = v.rollout()
            if not reward:
                print("ERROR: No winner found")
                return None
            # backpropagation
            #print("backpropagating")
            v.backpropagate(reward)

        # return best action
        best_child = self.best_child(c_param=0.0)
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
