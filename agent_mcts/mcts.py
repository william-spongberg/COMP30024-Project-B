import copy
import random
from cmath import log
from collections import defaultdict

from agent_random.movements import valid_coords, valid_moves
from agent_random.tetronimos import make_tetronimos
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

        self.num_visits = 0
        self.actions: list[PlaceAction] = self.getactions()
        self.results = defaultdict(int)
        self.results[1] = 0  # win
        self.results[-1] = 0  # loss

    def getactions(self):
        coords: list[Coord] = valid_coords(self.state, self.board.turn_color)
        tetronimos: list[PlaceAction] = make_tetronimos(Coord(0, 0))
        actions: list[PlaceAction] = []
        for coord in coords:
            actions.extend(valid_moves(self.state, tetronimos, coord))
        # print("valid actions initially: ", actions)
        return actions

    def expand(self):
        board_node: Board = copy.deepcopy(self.board)
        action = self.actions.pop()
        # print(action)
        board_node.apply_action(action)
        child_node: MCTSNode = MCTSNode(board_node, self, action)

        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.board.game_over

    def is_fully_expanded(self):
        # print(len(self.actions))
        return len(self.actions) == 0

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
                #print("winner: ", current_board.turn_color.opponent)
                return current_board.turn_color.opponent
        # game over but we still have moves => we win
        #print("winner: ", current_board.turn_color)
        return current_board.turn_color

    def backpropagate(self, result):
        self.num_visits += 1
        self.results[result] += 1
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, c_param=1.4):
        best_score: float = -1.0
        best_child = None
        for child in self.children:
            if child.num_visits == 0 or self.num_visits == 0:
                exploit: float = child.results[1]
                explore: float = 0.0
            else:
                exploit: float = child.results[1] / child.num_visits
                # TODO: fix potential error here in abs causing bad results
                explore: float = (
                    c_param * abs(2 * log(self.num_visits) / child.num_visits) ** 0.5
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
            # print("simulating")
            reward = v.rollout()
            if not reward:
                print("ERROR: No winner found")
                return None
            # backpropagation
            # print("backpropagating")
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
        tetronimos = make_tetronimos(Coord(0, 0))

        coords = valid_coords(state, board.turn_color)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while not valid_moves(state, tetronimos, coord):
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if not valid_moves(state, tetronimos, coord):
            return None
        # else return random valid move
        return random.choice(valid_moves(state, tetronimos, coord))
