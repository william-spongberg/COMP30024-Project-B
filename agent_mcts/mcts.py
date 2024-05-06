import copy
import random
from cmath import log
from collections import defaultdict
import warnings

from helpers.movements import valid_coords, valid_moves
from helpers.sim_board import SimBoard, find_actions
from referee.game.actions import Action
from referee.game.board import CellState
from referee.game.coord import Coord
from referee.game.player import PlayerColor

# generally want to make more efficient (want at least 100 sims per move)
# TODO: save possible moves for each board state
# TODO: implement asynchronous MCTS to allow searching to continue while waiting for opponent move
# TODO: remove as many checks as possible to increase efficiency
# TODO: add transposition table to store board states and results, avoids re-searching same states


class MCTSNode:
    """
    Node class for the Monte Carlo Tree Search algorithm
    """

    def __init__(
        self,
        state: dict[Coord, CellState],
        color: PlayerColor = PlayerColor.RED,
        parent=None,
        parent_action=None,
    ):
        """
        Initialize the node with the current board state
        """
        self.board: SimBoard = SimBoard(state, color)
        self.parent: MCTSNode | None = parent
        self.parent_action: Action | None = parent_action
        self.action_to_children : dict[Action, MCTSNode] = {}
        self.children: list[MCTSNode] = []
        self.color: PlayerColor = color
        self.num_visits = 0
        self.actions: list[Action] = find_actions(
            self.board._state, self.board._turn_color
        )
        self.results = defaultdict(int)
        self.results[1] = 0  # win
        self.results[-1] = 0  # loss

    def expand(self):
        """
        Expand the current node by adding a new child node
        """
        board_node: SimBoard = copy.deepcopy(self.board)
        action = self.actions.pop()
        # print(action)
        board_node.apply_action(action)
        # print(board_node)
        child_node: MCTSNode = MCTSNode(
            board_node._state, self.color, parent=self, parent_action=action
        )

        self.children.append(child_node)
        return child_node
    
    def add_action(self, action: Action):
        """
        Add action to children
        """
        self.board.apply_action(action)
        self.board._turn_color = self.board._turn_color.opponent
        
        self.action_to_children[action] = MCTSNode(
            copy.deepcopy(self.board._state), self.color, parent=self, parent_action=action
        )

    def is_terminal_node(self):
        return self.board.game_over

    def is_fully_expanded(self):
        # print(len(self.actions))
        return len(self.actions) == 0

    def rollout(self) -> PlayerColor | None:
        """
        Simulate a random v random game from the current node
        """
        current_board: SimBoard = copy.deepcopy(self.board)
        while not current_board.game_over:
            # light playout policy
            """ 
            # TODO: wrong logic here, the num of actions change over the rollout, but fixing this causes really bad efficiency
            # But better to develop consist tree first, heuristics are bad in efficiency generally
            # if len(self.actions) > 50:
            #     action = self.get_random_move(current_board)
            # else:
            #     action = self.get_heuristic_based_move(current_board)
            """
            action = self.get_random_move(current_board)
            # if action available, apply
            if action:
                current_board.apply_action(action)
                # print(current_board.render())
            # if no action available, should not be in this loop (but anyway return opponent as winner)
            else:
                warnings.warn("ERROR: No action available in rollout but not game over yet")
                return current_board._turn_color.opponent
        
        return current_board.winner

    def backpropagate(self, result):
        """
        Backpropagate the result of the simulation up the tree
        """
        self.num_visits += 1
        self.results[result] += 1
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, c_param=1.4):
        """
        Select the best child node based on the UCB1 formula
        """
        best_score: float = float("-inf")
        best_child = None
        for child in self.children:
            if child.num_visits == 0 or self.num_visits == 0:
                exploit: float = child.results[1]
                explore: float = 0.0
            else:
                exploit: float = child.results[1] / child.num_visits
                # TODO: fix potential error here in abs causing bad results
                if (self.num_visits) < 1 or (child.num_visits) < 1:
                    print("ERROR: abnormal num_visits")
                    print("num_visits: ", self.num_visits)
                    print("child.num_visits: ", child.num_visits)
                    exit()
                explore: float = (
                    c_param * abs(2 * log(self.num_visits) / child.num_visits) ** 0.5
                )
            score: float = exploit + explore
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    # TODO: implement iterative deepening to allow for more efficient search
    # return winner as whoever has more pieces on board (for now - in future, use heuristic)
    def _tree_policy(self):
        """
        Select a node to expand based on the tree policy
        """
        current_node: MCTSNode | None = self
        # select nodes to expand
        while current_node and not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

    def best_action(self, sim_no=100) -> Action | None:
        """
        Perform MCTS search for the best action
        """
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
            print("best action: ", best_child.parent_action)
            # temp_board = SimBoard(best_child.board.state, best_child.board.turn_color)
            # temp_board.apply_action(best_child.parent_action)
            # temp_board.turn_color = temp_board.turn_color.opponent
            # print(temp_board.render(True))
            return best_child.parent_action

        # if no best child, print error + return None
        print("ERROR: No best child found")
        return None

    def get_random_move(self, board) -> Action | None:
        """
        Get a random move for the current state
        """
        state: dict[Coord, CellState] = board.state

        coords = valid_coords(state, board.turn_color)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while not valid_moves(state, coord):
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if not valid_moves(state, coord):
            return None
        # else return random valid move
        return random.choice(valid_moves(state, coord))

    def heuristic(self, move: Action, board: SimBoard):
        # TODO: copy state instead of whole board for better efficiency
        current_board = copy.deepcopy(board)
        coords = valid_coords(current_board._state, current_board._turn_color)
        move_count = 0
        for coord in coords:
            move_count += len(valid_moves(current_board._state, coord))
        current_board.apply_action(move)
        opp_coords = valid_coords(current_board._state, current_board._turn_color)
        opp_move_count = 0
        for coord in opp_coords:
            opp_move_count += len(valid_moves(current_board._state, coord))
        return (
            move_count - opp_move_count + len(coords) - len(opp_coords)
        )  # bigger is better

    def get_heuristic_based_move(self, board: SimBoard) -> Action | None:
        best_move = None
        best_heuristic = float("-inf")
        state = board._state

        coords = valid_coords(state, board._turn_color)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        for coord in coords:
            moves = valid_moves(state, coord)
            for move in moves:
                heuristic = self.heuristic(move, board)
                if heuristic > best_heuristic:
                    best_heuristic = heuristic
                    best_move = move
        return best_move
