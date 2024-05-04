
from helpers.heuristics import BOARD_N
from helpers.movements import has_valid_move, valid_coords, valid_moves
from referee.game.actions import PlaceAction
from referee.game.board import CellState
from referee.game.constants import MAX_TURNS
from referee.game.coord import Coord
from referee.game.player import PlayerColor

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


def empty_state() -> dict[Coord, CellState]:
    return {Coord(r, c): CellState() for r in range(BOARD_N) for c in range(BOARD_N)}

class SimBoard:
    """
    Light weight adaptation of the Board class
    """

    def __init__(
        self,
        init_state: dict[Coord, CellState] = empty_state(),
        init_color: PlayerColor = PlayerColor.RED,
    ):
        """
        Initialize the board state
        """
        self._state: dict[Coord, CellState] = init_state
        self._turn_color: PlayerColor = init_color
        self._turn_count: int = 0
        self._actions: list[PlaceAction]

        # self._history: list[BoardMutation] = []
        # possible way to store previously used states - may be too memory expensive however

    def apply_action(self, action: PlaceAction | None):
        """
        Apply the action to the current state
        """
        if not action:
            print("ERROR: No action given")
            return
        for coord in action.coords:
            self._state[coord] = CellState(self._turn_color)
        self._turn_color = self._turn_color.opponent
        self._turn_count += 1

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
                        output += self.apply_ansi(str=text, bold=False, color=color)
                    else:
                        output += text
                else:
                    output += "."
                output += " "
            output += "\n"
        return output

    def __getitem__(self, coord: Coord) -> CellState:
        return self._state[coord]

    def __setitem__(self, coord: Coord, cell: CellState):
        self._state[coord] = cell

    def _cell_occupied(self, coord: Coord) -> bool:
        return self._state[coord].player != None

    def _cell_empty(self, coord: Coord) -> bool:
        return self._state[coord].player == None

    def _player_token_count(self, color: PlayerColor) -> int:
        return sum(1 for cell in self._state.values() if cell.player == color)

    def _occupied_coords(self) -> set[Coord]:
        return set(filter(self._cell_occupied, self._state.keys()))

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
        The game is over if turn limit reached or no player can place any more pieces.
        """
        return self.turn_limit_reached or (
            not has_action(self._state, PlayerColor.RED)
            and not has_action(self._state, PlayerColor.BLUE)
        )

    # TODO: what happens on turn_limit_reached?