import copy
import random
from cmath import log
from collections import defaultdict
from socket import send_fds
import warnings

from helpers.movements import valid_coords, valid_moves
from helpers.sim_board import SimBoard, find_actions, update_actions
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
    state_to_move: dict[dict[Coord, CellState], set[Action]] = {}
    def __init__(
        self,
        state: dict[Coord, CellState],
        color: PlayerColor,
        parent: 'MCTSNode | None' = None,
        parent_action: Action | None = None,
    ):
        """
        Initialize the node with the current board state
        """
        self.board: SimBoard = SimBoard(state, color)
        self.parent: MCTSNode | None = parent
        self.parent_action: Action | None = parent_action
        
        self.my_actions: set[Action]
        if parent and parent.parent and parent.parent.my_actions:
            self.my_actions = copy.deepcopy(parent.parent.my_actions)
            update_actions(parent.board.state, self.board.state, self.my_actions, color)
        else:
            print("no parent")
            self.my_actions = set(find_actions(state, color))
        # self.my_actions = set(find_actions(state, color))
            
        self.__action_to_children: dict[Action, 'MCTSNode'] = {} # my actions to child node
        
        self.color: PlayerColor = color
        self.num_visits = 0
        
        self.results = defaultdict(int)
        self.results[1] = 0  # win
        self.results[-1] = 0  # loss

    def expand(self, action: Action):
        """
        Expand the current node by adding a new child node
        Using opponent move as action
        """
        board_node: SimBoard = copy.deepcopy(self.board)

        # print(action)
        board_node.apply_action(action)
        # print(board_node)
        child_node: MCTSNode = MCTSNode(
            board_node._state, board_node.turn_color, parent=self, parent_action=action
        )

        self.__action_to_children[action] = child_node
        return child_node
    
    # def add_action(self, action: Action):
    #     """
    #     Add action to children
    #     """
    #     self.board.apply_action(action)
        
    #     # TODO: in future keep track of all previous actions, useful for ML?
        
    #     # TODO: check if action already exists in children
    #     self.children = []

    def is_terminal_node(self):
        return self.board.game_over

    def is_fully_expanded(self):
        for action in self.my_actions:
            if action not in self.__action_to_children:
                return False
        return True

    def rollout(self) -> 'MCTSNode | None':
        """
        Simulate a random v random game from the current node
        """
        current_node = self
        while not current_node.board.game_over:
            # light playout policy
            current_node = current_node._tree_policy()
            if not current_node:
                warnings.warn("ERROR: No tree policy node found in rollout")
                return None
        
        return current_node
    
    # def new_rollout(self, max_steps) -> PlayerColor | None:
    #     """
    #     Simulate a random v random game from the current node
    #     not pushing all the way to the end of the game but stopping at max_steps
    #     """
    #     current_board: SimBoard = copy.deepcopy(self.board)
    #     steps = 0
    #     color = current_board._turn_color
    #     if not self.heuristic_value:
    #         self.heuristic_value = self.board_heuristic_move_count(current_board.state, self.color)
    #     while steps < max_steps and not current_board.game_over:
    #         # light playout policy
    #         action = self.get_random_move(current_board)
    #         if action:
    #             current_board.apply_action(action)
    #             steps += 1
    #         else:
    #             warnings.warn("ERROR: No action available in rollout but not game over yet")
    #             return current_board._turn_color.opponent
    #     if (current_board.winner):
    #         return current_board.winner
    #     else:
    #         return color if self.board_heuristic_move_count(current_board.state, self.color) > self.heuristic_value else color.opponent
            

    def backpropagate(self, result: PlayerColor | None):
        """
        Backpropagate the result of the simulation up the tree
        """
        self.num_visits += 1
        if result == self.color:
            self.results[1] += 1
        elif result == self.color.opponent:
            self.results[-1] += 1
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, c_param=1.4) -> 'MCTSNode':
        """
        Select the best child node based on the UCB1 formula
        """
        best_score: float = float("-inf")
        best_child = None
        for child in self.__action_to_children.values():
            if child.num_visits == 0 or self.num_visits == 0:
                exploit: float = child.results[-1] # children are opponent, so looking for their loss
                explore: float = 0.0
            else:
                exploit: float = child.results[-1] / child.num_visits
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
        if not best_child:
            print("ERROR: No best child found")
            print(len(self.__action_to_children))
            exit()
        return best_child

    # TODO: implement iterative deepening to allow for more efficient search
    # return winner as whoever has more pieces on board (for now - in future, use heuristic)
    def _tree_policy(self):
        """
        Select a node to expand based on the tree policy
        """
        current_node: MCTSNode = self
        # select nodes to expand
        while current_node and not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                action = random.choice(
                    [action for action in current_node.my_actions 
                     if action not in current_node.__action_to_children])
                return current_node.expand(action)
            else:
                if not current_node.my_actions:
                    print("ERROR: No actions available")
                    return None
                if (current_node.__action_to_children):
                    return current_node.best_child()
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
            end_node = v.rollout()
            # reward = v.new_rollout(4)
            if not end_node:
                print("ERROR: No winner found")
                return None
            # backpropagation
            # print("backpropagating")
            end_node.backpropagate(end_node.board.winner)

        print("children: ", self.__action_to_children)
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
        return random.choice(list(self.my_actions))

    # def heuristic(self, move: Action, board: SimBoard):
    #     # TODO: copy state instead of whole board for better efficiency
    #     current_board = copy.deepcopy(board)
    #     coords = valid_coords(current_board._state, current_board._turn_color)
    #     move_count = 0
    #     for coord in coords:
    #         move_count += len(valid_moves(current_board._state, coord, current_board._turn_color))
    #     current_board.apply_action(move)
    #     opp_coords = valid_coords(current_board._state, current_board._turn_color)
    #     opp_move_count = 0
    #     for coord in opp_coords:
    #         opp_move_count += len(valid_moves(current_board._state, coord, current_board._turn_color.opponent))
    #     return (
    #         move_count - opp_move_count + len(coords) - len(opp_coords)
    #     )  # bigger is better
        
    # def board_heuristic_move_count(self, state: dict[Coord, CellState], color: PlayerColor):
    #     """
    #     heuristic function to predict if this player is winning
    #     """
    #     move_count = len(find_actions(state, color))
    #     opp_move_count = len(find_actions(state, color.opponent))
    #     return (
    #         move_count - opp_move_count
    #     )  # bigger is better

    # def get_heuristic_based_move(self, board: SimBoard) -> Action | None:
    #     best_move = None
    #     best_heuristic = float("-inf")
    #     state = board._state

    #     coords = valid_coords(state, board._turn_color)
    #     coord: Coord = random.choice(coords)
    #     coords.remove(coord)

    #     for coord in coords:
    #         moves = valid_moves(state, coord, board._turn_color)
    #         for move in moves:
    #             heuristic = self.heuristic(move, board)
    #             if heuristic > best_heuristic:
    #                 best_heuristic = heuristic
    #                 best_move = move
    #     return best_move
    
    def chop_nodes_except(self, node: 'MCTSNode | None' = None):
        """
        To free up memory, delele all useless nodes
        need to call gc.collect() after this function
        params: node: node to keep as it will be the new root
        """
        if (node):
            for child in self.__action_to_children.values():
                if node and child == node:
                    continue
                else:
                    child.chop_nodes_except()
        else:
            del self.__action_to_children
            del self.board
            del self.parent
            del self.parent_action
            del self.my_actions
            del self.results
            del self.color
       
    
    def get_child(self, action: Action):
        """
        Function to wrap the action_to_children dictionary in case of KeyError
        """
        if action in self.__action_to_children:
            return self.__action_to_children[action]
        else:
            self.expand(action)
            return self.__action_to_children[action]
