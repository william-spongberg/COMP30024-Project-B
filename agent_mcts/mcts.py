import copy
import random
from cmath import log
from collections import defaultdict
import warnings

from helpers.movements import check_adjacent_cells, is_valid
from helpers.sim_board import SimBoard, find_actions, update_actions
from referee.game.actions import Action
from referee.game.board import CellState
from referee.game.coord import Coord
from referee.game.player import PlayerColor

# generally want to make more efficient (want at least 100 sims per move)
# TODO: implement asynchronous MCTS to allow searching to continue while waiting for opponent move
# not allowed in specifcation?
# TODO: remove as many checks as possible to increase efficiency
# TODO: debug invalid actions being generated (non-adjacent)
# TODO: implement mcts time limit

MAX_STEPS = 6

class MCTSNode:
    """
    Node class for the Monte Carlo Tree Search algorithm
    """
    state_to_move: dict[dict[Coord, CellState], set[Action]] = {}
    def __init__(
        self,
        board: SimBoard,
        parent: 'MCTSNode | None' = None,
        parent_action: Action | None = None,
    ):
        """
        Initialize the node with the current board state
        """
        self.board: SimBoard = board
        self.parent: MCTSNode | None = parent
        self.parent_action: Action | None = parent_action
        
        self.my_actions: list[Action]

        # parent.parent: parent with same color
        if parent and parent.parent and parent.parent.my_actions:
            self.my_actions = parent.parent.my_actions.copy()
            update_actions(parent.parent.board.state, self.board.state, self.my_actions, board.turn_color)
        else:
            print("no parent")
            self.my_actions = find_actions(board.state, board.turn_color)
            
        self.untried_actions = self.my_actions.copy() # actions not yet tried
        self.__action_to_children: dict[Action, 'MCTSNode'] = {} # my actions to child node
        
        self.color: PlayerColor = board.turn_color
        self.num_visits = 0
        
        self.results = defaultdict(int)
        self.results[1] = 0  # win
        self.results[-1] = 0  # loss
        
        self.danger = False

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
            board_node, parent=self, parent_action=action,
        )

        self.__action_to_children[action] = child_node
        return child_node

    def is_terminal_node(self):
        return self.board.game_over

    def is_fully_expanded(self):
        if not self.untried_actions:
            return True
        return False

    def rollout(self) -> 'MCTSNode | None':
        """
        Simulate a random v random game from the current node
        """
        push_step = 0
        current_node = self
        while not current_node.is_terminal_node():
            # light playout policy
            current_node = current_node._tree_policy()
            push_step += 1
            # print("pushing step: ", push_step)
            if not current_node:
                warnings.warn("ERROR: No tree policy node found in rollout")
                return None
        
        return current_node
    
    def new_rollout(self, max_steps) -> PlayerColor | None:
        """
        Simulate a random v random game from the current node
        not pushing all the way to the end of the game but stopping at max_steps
        """
        # make sure max_steps is even so that both players get equal number of moves
        if max_steps / 2 == 1:
            max_steps += 1
        push_step = 0
        current_node = self
        while not current_node.is_terminal_node() and push_step < max_steps:
            # light playout policy
            current_node = current_node._tree_policy()
            push_step += 1
            # print("pushing step: ", push_step)
            if not current_node:
                warnings.warn("ERROR: No tree policy node found in rollout")
                return None
        if current_node.is_terminal_node():
            self.danger = True
            return current_node.board.winner
        if current_node.heuristics_judge() > current_node.heuristics_judge():
            return current_node.color
        self = current_node # make v the end node for backpropagation
        return current_node.color.opponent
            

    def backpropagate(self, result: PlayerColor | None, root_color: PlayerColor):
        """
        Backpropagate the result of the simulation up the tree
        """
        self.num_visits += 1
        if result == root_color:
            self.results[1] += 1
        elif result == root_color.opponent:
            self.results[-1] += 1
        if self.parent:
            self.parent.danger = self.danger
            self.parent.backpropagate(result, root_color)

    def best_child(self, c_param=1.4) -> 'MCTSNode':
        """
        Select the best child node based on the UCB1 formula
        """
        best_score: float = float("-inf")
        best_child = None
        for child in self.__action_to_children.values():
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
        if not best_child:
            print("ERROR: No best child found")
            print(len(self.__action_to_children))
            exit()
        return best_child

    
    def _tree_policy(self):
        """
        Select a node to expand based on the tree policy
        """
        # select nodes to expand
        if not self.is_terminal_node():
            if not self.is_fully_expanded():
                action = random.choice(self.untried_actions)
                self.untried_actions.remove(action)
                # met bug about expanding invalid action haven't fixed yet but this can be a temporary solution
                if not is_valid(self.board.state, action) or not check_adjacent_cells(action.coords, self.board.state, self.color):
                    self.my_actions.remove(action)
                    return self._tree_policy()
                return self.expand(action)
            else:
                if not self.my_actions:
                    print("ERROR: No actions available")
                    return None
                if (self.__action_to_children):
                    print("finish expanding, looking for best child")
                    return self.best_child()
        return self

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
            print("rolling out: ", i)
            if v.is_terminal_node() and v.board.winner == self.color:
                return v.parent_action
            # rollout with heuristic and max_steps
            winner = v.new_rollout(MAX_STEPS)
            v.backpropagate(winner, self.color)
            
            # rollout to the end of the game
            # end_node = v.rollout()
            # if not end_node:
            #     print("ERROR: No winner found")
            #     return None
            # end_node.backpropagate(end_node.board.winner)

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

    def get_random_move(self) -> Action | None:
        """
        Get a random move for the current state
        """
        return random.choice(list(self.my_actions))

    
    def heuristics_judge(self) -> int:
        """
        heuristic function to predict if this player is winning
        """
        # move_count = len(self.my_actions)
        if self.parent:
            opp_move_count = len(self.parent.my_actions)
        else:
            opp_move_count = len(find_actions(self.board.state, self.color.opponent))
        return (
            - opp_move_count
        )
    
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
