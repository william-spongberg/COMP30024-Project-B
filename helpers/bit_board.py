from helpers.sim_board import has_action
from referee.game.actions import Action
from referee.game.board import CellState
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.coord import Coord
from referee.game.player import PlayerColor


class BitBoard:
    def __init__(
        self,
        init_state: dict[Coord, CellState] | None = None,
        init_color: PlayerColor = PlayerColor.RED,
    ):
        self.red_state = 0
        self.blue_state = 0
        self._turn_color: PlayerColor = init_color
        self._turn_count: int = 0

    def apply_action(self, action: Action | None = None):
        if not action:
            print("ERROR: No action given")
            return

        for coord in action.coords:
            index = coord.r * BOARD_N + coord.c
            if self._turn_color == PlayerColor.RED:
                self.red_state |= 1 << index  # use bitwise OR to add a piece
            else:
                self.blue_state |= 1 << index  # use bitwise OR to add a piece

        self.clear_lines(action)

        self._turn_color = self._turn_color.opponent
        self._turn_count += 1

    def clear_lines(self, action: Action):
        coords_to_remove = []

        for coord in action.coords:
            row_coords = self._row_occupied(coord)
            col_coords = self._col_occupied(coord)
            if len(row_coords) == BOARD_N:
                coords_to_remove.extend(row_coords)
            if len(col_coords) == BOARD_N:
                coords_to_remove.extend(col_coords)

        for coord in coords_to_remove:
            index = coord.r * BOARD_N + coord.c
            self.red_state &= ~(1 << index)
            self.blue_state &= ~(1 << index)

    def _cell_occupied(self, coord: Coord) -> bool:
        index = coord.r * BOARD_N + coord.c
        return bool((self.red_state >> index) & 1) or bool(
            (self.blue_state >> index) & 1
        )

    def _cell_empty(self, coord: Coord) -> bool:
        return not self._cell_occupied(coord)

    def _get_filled_coords(self, coord: Coord) -> list[Coord]:
        """
        Get all the filled coordinates in the same row and column as the given coordinate
        """
        row_coords = [c for c in self._row_occupied(coord) if self._cell_occupied(c)]
        col_coords = [c for c in self._col_occupied(coord) if self._cell_occupied(c)]
        return row_coords + col_coords

    def render(self, use_color: bool = False) -> str:
        output = ""
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                index = r * BOARD_N + c
                if (self.red_state >> index) & 1:
                    output += "r "
                elif (self.blue_state >> index) & 1:
                    output += "b "
                else:
                    output += ". "
            output += "\n"
        return output

    def __getitem__(self, coord: Coord) -> CellState:
        index = coord.r * BOARD_N + coord.c
        if (self.red_state >> index) & 1:
            return CellState(PlayerColor.RED)
        elif (self.blue_state >> index) & 1:
            return CellState(PlayerColor.BLUE)
        else:
            return CellState()

    def __setitem__(self, coord: Coord, cell: CellState):
        index = coord.r * BOARD_N + coord.c
        if cell == CellState(PlayerColor.RED):
            self.red_state |= 1 << index
            self.blue_state &= ~(1 << index)
        elif cell == CellState(PlayerColor.BLUE):
            self.blue_state |= 1 << index
            self.red_state &= ~(1 << index)
        else:
            self.red_state &= ~(1 << index)
            self.blue_state &= ~(1 << index)

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
        if color == PlayerColor.RED:
            return bin(self.red_state).count("1")
        else:
            return bin(self.blue_state).count("1")

    def _occupied_coords(self) -> list[Coord]:
        return list(filter(self._cell_occupied, self.state.keys()))

    def __eq__(self, other):
        return self.state == other.state

    def __str__(self):
        return self.render()

    def __repr__(self):
        return self.__str__()

    @property
    def turn_count(self) -> int:
        return self._turn_count

    @property
    def state(self) -> dict[Coord, CellState]:
        state = {}
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                index = r * BOARD_N + c
                if (self.red_state >> index) & 1:
                    state[Coord(r, c)] = CellState(PlayerColor.RED)
                elif (self.blue_state >> index) & 1:
                    state[Coord(r, c)] = CellState(PlayerColor.BLUE)
                else:
                    state[Coord(r, c)] = CellState()
        return state

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
            or not has_action(self.state, self._turn_color)
            and self.turn_count > 1
        )

    @property
    def winner(self) -> PlayerColor | None:
        if not self.game_over:
            return None
        if not has_action(self.state, self._turn_color):
            return self._turn_color.opponent
        if not has_action(self.state, self._turn_color.opponent):
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