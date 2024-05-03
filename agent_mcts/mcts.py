import copy
import random
from cmath import log
from collections import defaultdict

from agent_random.movements import has_valid_move, valid_coords, valid_moves
from agent_random.tetronimos import BOARD_N
from referee.game.actions import PlaceAction
from referee.game.board import CellState
from referee.game.constants import MAX_TURNS
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
        self.parent_action: PlaceAction | None = parent_action
        self.children: list[MCTSNode] = []

        self.num_visits = 0
        self.actions: list[PlaceAction] = find_actions(
            self.board.state, self.board.turn_color
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
            board_node.state, parent=self, parent_action=action
        )

        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.board.game_over

    def is_fully_expanded(self):
        # print(len(self.actions))
        return len(self.actions) == 0

    def rollout(self):
        """
        Simulate a random v random game from the current node
        """
        current_board: SimBoard = copy.deepcopy(self.board)
        while not current_board.game_over:
            # light playout policy
            # TODO: wrong logic here, the num of actions change over the rollout, but fixing this causes really bad efficiency
            if len(self.actions) > 50:
                action = self.get_random_move(current_board)
            else:
                action = self.get_heuristic_based_move(current_board)
            # if action available, apply
            if action:
                current_board.apply_action(action)
                # print(current_board.render())
            # if no action available, other player wins
            else:
                # print("winner: ", current_board.turn_color.opponent)
                return current_board.turn_color.opponent
        # game over but we still have moves => we win
        # print("winner: ", current_board.turn_color)
        return current_board.turn_color

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
    
    # TODO: fix tree policy returning None - related to not finding all possible moves?

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

    def best_action(self, sim_no=100) -> PlaceAction | None:
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
            #temp_board = SimBoard(best_child.board.state, best_child.board.turn_color)
            #temp_board.apply_action(best_child.parent_action)
            # temp_board.turn_color = temp_board.turn_color.opponent
            # print(temp_board.render(True))
            return best_child.parent_action

        # if no best child, print error + return None
        print("ERROR: No best child found")
        return None

    def get_random_move(self, board) -> PlaceAction | None:
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

    def heuristic(self, move: PlaceAction, board: 'SimBoard'):
        current_board = copy.deepcopy(board)
        coords = valid_coords(current_board.state, current_board.turn_color)
        move_count = 0
        for coord in coords:
            move_count += len(valid_moves(current_board.state, coord))
        current_board.apply_action(move)
        opp_coords = valid_coords(current_board.state, current_board.turn_color)
        opp_move_count = 0
        for coord in opp_coords:
            opp_move_count += len(valid_moves(current_board.state, coord))
        return move_count - opp_move_count + len(coords) - len(opp_coords) # bigger is better
    
    def get_heuristic_based_move(self, board: 'SimBoard') -> PlaceAction | None:
        best_move = None
        best_heuristic = float('-inf')
        state = board.state

        coords = valid_coords(state, board.turn_color)
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


def find_actions(
    state: dict[Coord, CellState], color: PlayerColor
) -> list[PlaceAction]:
    """
    Find all possible valid actions for the current state
    """
    coords: list[Coord] = valid_coords(state, color)
    actions: list[PlaceAction] = []
    for coord in coords:
        actions.extend(valid_moves(state, coord))
    return actions


def has_action(state: dict[Coord, CellState], color: PlayerColor) -> bool:
    """
    Check if there is any valid action for the current state
    """
    coords: list[Coord] = valid_coords(state, color)

    for coord in coords:
        if has_valid_move(state, coord):
            return True
    return False

class SimBoard:
    """
    Light weight adaptation of the Board class
    """

    def __init__(
        self,
        state: dict[Coord, CellState] | None = None,
        color: PlayerColor = PlayerColor.RED,
    ):
        """
        Initialize the board state
        """
        if state:
            self.state: dict[Coord, CellState] = state
        else:
            self.state: dict[Coord, CellState] = self.empty_state()
        self.possible_actions: list[PlaceAction]
        self.turn_color: PlayerColor = color
        self.turn_count = 0

    def __getitem__(self, coord: Coord) -> CellState:
        return self.state[coord]

    def __setitem__(self, coord: Coord, cell: CellState):
        self.state[coord] = cell

    def empty_state(self) -> dict[Coord, CellState]:
        return {
            Coord(r, c): CellState() for r in range(BOARD_N) for c in range(BOARD_N)
        }

    def apply_action(self, action: PlaceAction | None):
        """
        Apply the action to the current state
        """
        if not action:
            print("ERROR: No action given")
            return
        for coord in action.coords:
            self.state[coord] = CellState(self.turn_color)
        self.turn_color = self.turn_color.opponent
        self.turn_count += 1

    def apply_ansi(self, str, bold=True, color=None):
        bold_code = "\033[1m" if bold else ""
        color_code = ""
        if color == "r":
            color_code = "\033[31m"
        if color == "b":
            color_code = "\033[34m"
        return f"{bold_code}{color_code}{str}\033[0m"

    def render(self, use_color: bool = False) -> str:
        """
        Returns a visualisation of the game board as a multiline string, with
        optional ANSI color codes and Unicode characters (if applicable).
        """

        output = ""
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                if self._cell_occupied(Coord(r, c)):
                    color = self.state[Coord(r, c)].player
                    color = "r" if color == PlayerColor.RED else "b"
                    text = f"{color}"
                    if use_color:
                        output += self.apply_ansi(str=text, bold=False, color=color)
                    else:
                        output += text
                else:
                    output += "."
                output += " "
            output += "\n"
        return output

    def _cell_occupied(self, coord: Coord) -> bool:
        return self.state[coord].player != None

    def _cell_empty(self, coord: Coord) -> bool:
        return self.state[coord].player == None

    def _player_token_count(self, color: PlayerColor) -> int:
        return sum(1 for cell in self.state.values() if cell.player == color)

    def _occupied_coords(self) -> set[Coord]:
        return set(filter(self._cell_occupied, self.state.keys()))

    def __eq__(self, other):
        return self.state == other.state

    def __str__(self):
        return self.render()

    def __repr__(self):
        return self.__str__()

    @property
    def turn_limit_reached(self) -> bool:
        return self.turn_count >= MAX_TURNS

    @property
    def game_over(self) -> bool:
        """
        The game is over if turn limit reached or no player can place any more pieces.
        """
        return self.turn_limit_reached or (
            not has_action(self.state, PlayerColor.RED)
            and not has_action(self.state, PlayerColor.BLUE)
        )

    # TODO: what happens on turn_limit_reached?