import random
from math import log
from collections import defaultdict
from statistics import mean

from .helpers.movements import generate_random_move
from .helpers.sim_board import SimBoard, find_actions, update_actions
from referee.game.actions import Action
from referee.game.constants import MAX_TURNS
from referee.game.player import PlayerColor
from timeit import default_timer as timer


CLOSE_TO_END = 100


class MCTSNode:
    """
    Node class for the Monte Carlo Tree Search algorithm
    """

    def __init__(
        self,
        board: SimBoard,
        parent: "MCTSNode | None" = None,
        parent_action: Action | None = None,
    ):
        """
        Initialize the node with the current board state
        """
        self.board: SimBoard = board
        self.parent: MCTSNode | None = parent
        self.parent_action: Action | None = parent_action

        self.my_actions: list[Action] = []
        self.opp_actions: list[Action] = []

        # parent.parent: parent with same color
        if parent:
            self.opp_actions = update_actions(
                parent.board.state, self.board.state, parent.my_actions, parent.color
            )
            if parent.parent:
                self.my_actions = update_actions(
                    parent.parent.board.state,
                    self.board.state,
                    parent.parent.my_actions,
                    board.turn_color,
                )
        else:
            self.my_actions = find_actions(board.state, board.turn_color)
            self.opp_actions = find_actions(board.state, board.turn_color.opponent)
            if len(self.my_actions) == 0:
                print("ERROR: bit_find_actions returned no actions")

        # actions not yet tried
        self.untried_actions = self.my_actions.copy()

        # my actions to child node
        self.__action_to_children: dict[Action, "MCTSNode"] = {}

        self.color: PlayerColor = board.turn_color
        self.num_visits = 0

        self.results = defaultdict(int)
        self.results[1] = 0  # win
        self.results[-1] = 0  # lose

        self.estimated_time: float = 0

    def expand(self, action: Action | None = None):
        """
        Expand the current node by adding a new child node
        Using opponent move as action
        """
        board_node: SimBoard = self.board.copy()
        if action is None:
            if self.untried_actions:
                action = random.choice(self.untried_actions)
            else:
                return random.choice(list(self.__action_to_children.values()))

        board_node.apply_action(action)

        child_node: MCTSNode = MCTSNode(board_node, parent=self, parent_action=action)
        child_node.estimated_time = self.estimated_time
        if action in self.untried_actions:
            self.untried_actions.remove(action)
        self.__action_to_children[action] = child_node
        return child_node

    def is_terminal_node(self):
        return self.board.game_over

    def is_fully_expanded(self):
        if not self.untried_actions:
            return True
        return False

    def rollout_turns(self, times: int) -> int:
        """
        Simulate a random v random game from the current node
        """
        print("rolling out for turns")
        push_steps = []
        tried_times = 0
        while tried_times != times:
            current_node = self.tree_policy()
            if not current_node:
                break
            current_board = current_node.board.copy()
            this_push_step = 0
            while not current_board.game_over:
                current_board.apply_action(
                    generate_random_move(current_board.state, current_board.turn_color)
                )
                this_push_step += 1
            if current_board.winner_color == current_node.color:
                current_node.results[1] += 1
            else:
                current_node.results[-1] += 1
            tried_times += 1
            push_steps.append(this_push_step + 1)
        avg = mean(push_steps)
        result = round(avg / 2)  # half of the turns are ours
        return result

    def new_rollout(self, max_steps) -> None:
        """
        Simulate a random v random game from the current node
        not pushing all the way to the end of the game but stopping at max_steps
        """
        push_step = 0
        current_board = self.board.copy()
        while not current_board.game_over and push_step < max_steps:
            current_board.apply_action(
                generate_random_move(current_board.state, current_board.turn_color)
            )
            push_step += 1
        if current_board.winner_color == self.color:
            # backpropagate the result
            self.results[1] += 1
            return
        elif current_board.winner_color == self.color.opponent:
            self.results[-1] += 1
            return
        end_node = MCTSNode(current_board)
        if end_node.heuristics_judge() > 0 and self.color == end_node.color:
            self.results[1] += 1
        elif end_node.heuristics_judge() < 0 and self.color != end_node.color:
            self.results[1] += 1

    def best_child(self, c_param=1.4) -> "MCTSNode":
        """
        Select the best child node based on the UCB1 formula
        """
        best_score: float = float("-inf")
        best_child = None
        for child in self.__action_to_children.values():
            if child.num_visits <= 0 or self.num_visits <= 0:
                exploit: float = child.results[-1]
                explore: float = 0.0
            else:
                exploit: float = child.results[-1] / child.num_visits
                explore: float = (
                    c_param * (log(self.num_visits) / child.num_visits) ** 0.5
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

    def tree_policy(self) -> "MCTSNode | None":
        """
        Select a node to expand based on the tree policy
        """
        # select nodes to expand
        if not self.is_terminal_node():
            if not self.is_fully_expanded():
                return self.expand()
            else:
                if not self.my_actions:
                    print("ERROR: No actions available")
                    return None
                if self.__action_to_children:
                    print("finish expanding, looking for best child")
                    return self.best_child()
        return self

    def best_action(self, steps=MAX_TURNS, sim_no=100) -> Action | None:
        """
        Perform MCTS search for the best action
        """
        sim_count = 0
        start_time = timer()
        for _ in range(sim_no):
            if timer() - start_time > self.estimated_time:
                break
            # expansion
            v: MCTSNode | None = self.tree_policy()
            if not v:
                print("ERROR: No tree policy node found")
                return None
            # simulation
            if v.is_terminal_node() and v.board.winner_color == self.color:
                return v.parent_action
            # rollout with heuristic and max_steps
            v.new_rollout(steps - 1)
            sim_count += 1
        
        print("sim_count: ", sim_count)
        if (sim_count > 0):
            print("average time per simulation: ", (timer() - start_time) / sim_count)

        # return best action
        best_child = self.best_child(c_param=0.0)
        if best_child:
            print("best action: ", best_child.parent_action)
            return best_child.parent_action

        # if no best child, print error + return None
        print("ERROR: No best child found")
        return None

    def heuristics_judge(self) -> float:
        """
        heuristic function to predict if this player is winning
        """
        result = len(self.my_actions) - len(self.opp_actions)
        # let the number of tokens be the tie breaker if the turn_count is close to the max
        if self.board.turn_count > CLOSE_TO_END:
            result += (
                self.board._player_token_count(self.color)
                - self.board._player_token_count(self.color.opponent)
            ) / (MAX_TURNS - self.board.turn_count + 1)
        return result

    def chop_nodes_except(self, node: "MCTSNode | None" = None):
        """
        To free up memory, delele all useless nodes
        need to call gc.collect() after this function
        params: node: node to keep as it will be the new root
        """
        if node:
            # main branch
            for child in self.__action_to_children.values():
                # child node to keep, all children of this node will be saved
                if node and child == node:
                    continue
                else:
                    # recursively delete all other children
                    child.chop_nodes_except()
        else:
            del self.__action_to_children
            del self.board
            del self.parent
            del self.parent_action
            del self.my_actions
            del self.results
            del self.color
            del self.num_visits
            del self.untried_actions

    def get_child(self, action: Action):
        """
        Function to wrap the action_to_children dictionary in case of KeyError
        """
        if action in self.__action_to_children:
            return self.__action_to_children[action]
        else:
            # did not expand it
            self.expand(action)
            return self.__action_to_children[action]
