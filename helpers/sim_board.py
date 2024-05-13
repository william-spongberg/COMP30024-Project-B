from .heuristics import BOARD_N
from .movements import has_valid_move, valid_coords, valid_moves, is_valid, check_adjacent_cells, valid_moves_of_any_empty
from referee.game.actions import Action
from referee.game.board import CellState
from referee.game.constants import MAX_TURNS
from referee.game.coord import Coord, Direction
from referee.game.player import PlayerColor


def find_actions(state: dict[Coord, CellState], color: PlayerColor) -> list[Action]:
    """
    Find all possible valid actions for the current state
    """
    coords: list[Coord] = valid_coords(state, color)
    actions: list[Action] = []
    for coord in coords:
        actions.extend(valid_moves(state, coord))
    actions = list(set(actions))
    return actions

def update_actions(prev_state: dict[Coord, CellState], 
                   new_state: dict[Coord, CellState], my_actions: list[Action], color: PlayerColor):
    """
    Get a new list of actions that are valid for the current state
    """
    my_actions_set = my_actions.copy()
    for action in my_actions_set.copy():
        if not is_valid(new_state, action) or not check_adjacent_cells(action, new_state, color):
            my_actions_set.remove(action)
    for coord in changed_coords(prev_state, new_state):
        # two situations: new empty/new needed color
        if new_state[coord].player is None:
            my_actions_set.extend(valid_moves_of_any_empty(new_state, coord, color))
        elif new_state[coord].player == color:
            # looking for empty adjacent cells
            for adjacent in [coord + dir for dir in Direction]:
                if new_state[adjacent].player is None:
                    my_actions_set.extend(valid_moves(new_state, adjacent))
    return list(set(my_actions_set))
        
def changed_coords(state: dict[Coord, CellState], new_state: dict[Coord, CellState]) -> list[Coord]:
    """
    Get all coordinates that have changed
    """
    return [coord for coord in state.keys() if state[coord].player != new_state[coord].player]        

def has_action(state: dict[Coord, CellState], color: PlayerColor) -> bool:
    """
    Check if there is any valid action for the current state
    """
    coords: list[Coord] = valid_coords(state, color)

    for coord in coords:
        if has_valid_move(state, coord):
            return True
    return False


def empty_state() -> dict[Coord, CellState]:
    return {Coord(r, c): CellState() for r in range(BOARD_N) for c in range(BOARD_N)}


class SimBoard:
    """
    Light weight adaptation of the Board class
    """

    def __init__(
        self,
        init_state: dict[Coord, CellState] | None = None,
        init_color: PlayerColor = PlayerColor.RED,
    ):
        """
        Initialize the board state
        """
        if init_state is None:
            init_state = empty_state()
        self._state: dict[Coord, CellState] = init_state
        self._turn_color: PlayerColor = init_color
        self._turn_count: int = 0

    def apply_action(self, action: Action | None = None):
        """
        Apply the action to the current state
        """
        if not action:
            print("ERROR: No action given")
            return

        for coord in action.coords:
            self._state[coord] = CellState(self._turn_color)

        self.clear_lines(action)

        self._turn_color = self._turn_color.opponent
        self._turn_count += 1

        # print(self.render(True))

    def clear_lines(self, action: Action):
        """
        Clear all filled lines
        """
        coords_to_remove = []

        for coord in action.coords:
            if self._cell_empty(coord):
                continue
            if self._cell_occupied(coord):
                coords_to_remove.extend(self._get_filled_coords(coord))

        for coord in coords_to_remove:
            self._state[coord] = CellState()

    def _get_filled_coords(self, coord: Coord) -> list[Coord]:
        """
        Get all the filled coordinates in the same row and column as the given coordinate
        """
        row_coords = [c for c in self._row_occupied(coord) if self._cell_occupied(c)]
        col_coords = [c for c in self._col_occupied(coord) if self._cell_occupied(c)]
        return row_coords + col_coords

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
                    color = self._state[Coord(r, c)].player
                    color = "r" if color == PlayerColor.RED else "b"
                    text = f"{color}"
                    if use_color:
                        output += self.apply_ansi(str=text, bold=True, color=color)
                    else:
                        output += text
                else:
                    output += "."
                output += " "
            output += "\n"
        return output
    
    def copy(self):
        new_board = SimBoard(self._state.copy(), self._turn_color)
        new_board._turn_count = self._turn_count
        return new_board

    def __getitem__(self, coord: Coord) -> CellState:
        return self._state[coord]

    def __setitem__(self, coord: Coord, cell: CellState):
        self._state[coord] = cell

    def _cell_occupied(self, coord: Coord) -> bool:
        return self._state[coord].player != None

    def _cell_empty(self, coord: Coord) -> bool:
        return self._state[coord].player == None

    def _row_occupied(self, coord: Coord) -> list[Coord]:
        if all(self._cell_occupied(Coord(coord.r, c)) for c in range(BOARD_N)):
            return [Coord(coord.r, c) for c in range(BOARD_N)]
        else:
            return []

    def _col_occupied(self, coord: Coord) -> list[Coord]:
        if all(self._cell_occupied(Coord(r, coord.c)) for r in range(BOARD_N)):
            return [Coord(r, coord.c) for r in range(BOARD_N)]
        else:
            return []

    def _player_token_count(self, color: PlayerColor) -> int:
        return sum(1 for cell in self._state.values() if cell.player == color)

    def _occupied_coords(self) -> list[Coord]:
        return list(filter(self._cell_occupied, self._state.keys()))

    def __eq__(self, other):
        return self._state == other.state

    def __str__(self):
        return self.render()

    def __repr__(self):
        return self.__str__()

    @property
    def turn_count(self) -> int:
        return self._turn_count

    @property
    def state(self) -> dict[Coord, CellState]:
        return self._state

    @property
    def turn_color(self) -> PlayerColor:
        return self._turn_color

    @property
    def turn_limit_reached(self) -> bool:
        return self._turn_count >= MAX_TURNS

    @property
    def game_over(self) -> bool:
        """
        The game is over if turn limit reached or one of the player cannot place any more pieces.
        """
        return (
            self.turn_limit_reached
            or not has_action(self._state, self._turn_color) and self.turn_count > 1
        )

    @property
    def winner_color(self) -> PlayerColor | None:
        if not self.game_over:
            return None
        if not has_action(self._state, self._turn_color):
            return self._turn_color.opponent
        if not has_action(self._state, self._turn_color.opponent):
            return self._turn_color
        if self.turn_limit_reached:
            # print("turn limit reached")
            if self._player_token_count(PlayerColor.RED) == self._player_token_count(
                PlayerColor.BLUE
            ):
                return None
            return (
                PlayerColor.RED
                if self._player_token_count(PlayerColor.RED)
                > self._player_token_count(PlayerColor.BLUE)
                else PlayerColor.BLUE
            )

