import copy
import random
from cmath import log
from collections import defaultdict
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

    def __init__(
        self,
        state: dict[Coord, CellState],
        color: PlayerColor = PlayerColor.RED,
        parent: 'MCTSNode|None'=None,
        parent_action=None,
    ):
        """
        Initialize the node with the current board state
        """
        self.board: SimBoard = SimBoard(state, color)
        self.parent: MCTSNode | None = parent
        self.parent_action: Action | None = parent_action
        
        if parent and parent.actions:
            self.actions: list[Action] = parent.actions.copy()
            update_actions(parent.board.state, self.board.state, self.actions, color)
        else:
            self.actions = find_actions(state, color)
            
        if parent and parent.opp_actions:
            self.opp_actions: list[Action] = parent.opp_actions.copy()
            update_actions(parent.board.state, self.board.state, self.opp_actions, color.opponent)
        else:
            self.opp_actions = find_actions(state, color.opponent)
            
        self.untried_actions: list[Action] = self.actions
            
        self.action_to_children : dict[Action, MCTSNode] = {}
        
        self.color: PlayerColor = color
        self.num_visits = 0
        
        self.results = defaultdict(int)
        self.results[1] = 0  # win

    def expand(self, action: Action):
        """
        Expand the current node by adding a new child node
        """
        board_node: SimBoard = copy.deepcopy(self.board)
        board_node.apply_action(action)
        # print(board_node)
        child_node: MCTSNode = MCTSNode(
            board_node._state, self.color, parent=self, parent_action=action
        )

        self.action_to_children[action] = child_node
        return child_node
    

    def is_terminal_node(self):
        return self.board.game_over

    def is_fully_expanded(self):
        # print(len(self.actions))
        return len(self.actions) == 0

    # def rollout(self) -> PlayerColor | None:
    #     """
    #     Simulate a random v random game from the current node
    #     """
    #     current_board: SimBoard = copy.deepcopy(self.board)
    #     while not current_board.game_over:
    #         # light playout policy
    #         action = self.get_random_move(current_board)
    #         # if action available, apply
    #         if action:
    #             current_board.apply_action(action)
    #             # print(current_board.render())
    #         # if no action available, should not be in this loop (but anyway return opponent as winner)
    #         else:
    #             warnings.warn("ERROR: No action available in rollout but not game over yet")
    #             return current_board._turn_color.opponent
        
    #     return current_board.winner
    
    def new_rollout(self, max_steps) -> PlayerColor | None:
        """
        Simulate a random v random game from the current node
        not pushing all the way to the end of the game but stopping at max_steps
        """
        current_board: SimBoard = copy.deepcopy(self.board)
        steps = 0
        color = current_board._turn_color
        updating_actions = self.actions.copy()
        opp_actions = self.opp_actions.copy()
        while steps < max_steps and not current_board.game_over:
            print("step: ", steps)
            # light playout policy
            if current_board._turn_color == color:
                action = self.get_random_move(updating_actions)
            else:
                action = self.get_random_move(opp_actions)
            if action:
                prev_state = current_board._state.copy()
                current_board.apply_action(action)
                update_actions(prev_state, current_board._state, updating_actions, color)
                update_actions(prev_state, current_board._state, opp_actions, color.opponent)
                steps += 1
            else:
                warnings.warn("ERROR: No action available in rollout but not game over yet")
                return current_board._turn_color.opponent
        if (current_board.winner):
            return current_board.winner
        else:
            return color if (len(updating_actions) - len(opp_actions) > 
                    len(self.actions) - len(find_actions(self.board._state, self.color.opponent))) else color.opponent
            

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
        for child in self.action_to_children.values():
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
                action = random.choice(current_node.untried_actions)
                current_node.untried_actions.remove(action)
                return current_node.expand(action)
            else:
                current_node = current_node.best_child()
        return current_node

    def best_action(self, sim_no=100) -> Action | None:
        """
        Perform MCTS search for the best action
        """
        for i in range(sim_no):
            # expansion
            v: MCTSNode | None = self._tree_policy()
            if not v:
                print("ERROR: No tree policy node found")
                return None
            # simulation
            # print("simulating")
            # reward = v.rollout()
            print("rolling out", i)
            reward = v.new_rollout(10)
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

    def get_random_move(self, actions: list[Action]) -> Action | None:
        """
        Get a random move for the current state
        """
        if self.board.turn_count < 2:
            return random.choice(find_actions(self.board._state, self.color))
        return random.choice(actions)
    
    def update(self, action: Action):
        """
        Update the MCTS tree with the opponent's move
        """
        if action in self.action_to_children:
            self = self.action_to_children[action]
        else:
            self.expand(action)
            self.update(action)

    # def heuristic(self, move: Action, board: SimBoard):
    #     # TODO: copy state instead of whole board for better efficiency
    #     current_board = copy.deepcopy(board)
    #     coords = valid_coords(current_board._state, current_board._turn_color)
    #     move_count = 0
    #     for coord in coords:
    #         move_count += len(valid_moves(current_board._state, coord))
    #     current_board.apply_action(move)
    #     opp_coords = valid_coords(current_board._state, current_board._turn_color)
    #     opp_move_count = 0
    #     for coord in opp_coords:
    #         opp_move_count += len(valid_moves(current_board._state, coord))
    #     return (
    #         move_count - opp_move_count + len(coords) - len(opp_coords)
    #     )  # bigger is better
        
    # def board_heuristic(self, state: dict[Coord, CellState], color: PlayerColor):
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
    #         moves = valid_moves(state, coord)
    #         for move in moves:
    #             heuristic = self.heuristic(move, board)
    #             if heuristic > best_heuristic:
    #                 best_heuristic = heuristic
    #                 best_move = move
    #     return best_move
