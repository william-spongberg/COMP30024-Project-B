import random
from helpers.sim_board import has_action
from helpers.tetrominoes import make_tetrominoes
from referee.game.actions import Action
from referee.game.board import CellState
from referee.game.constants import BOARD_N, MAX_TURNS
from referee.game.coord import Coord, Direction
from referee.game.player import PlayerColor

# bit methods
tetrominoes = make_tetrominoes(Coord(0, 0))


def bit_check_adjacent_cells(board: "BitBoard", coords: list[Coord], color: PlayerColor) -> bool:
    for coord in coords:
        for dir in Direction:
            adjacent = coord + dir
            if board[adjacent] == color:
                return True
    return False

def bit_valid_moves_of_any_empty(board: "BitBoard", coord: Coord, color: PlayerColor) -> list[Action]:
    if board._cell_occupied(coord):
        print("invalid coord")
        exit(1)
    moves = []
    for move in bit_valid_moves(board, coord):
        if bit_check_adjacent_cells(board, move.coords, color):
            moves.append(move)
            break
    return moves

def bit_generate_random_move(board: "BitBoard", color: PlayerColor, first_turns: bool = False) -> Action:
    if first_turns and color == PlayerColor.RED:
        return Action(Coord(5, 5), Coord(5, 6), Coord(5, 7), Coord(5, 8))
    coords = bit_valid_coords(board, color, first_turns)
    while coords:
        coord = random.choice(coords)
        coords.remove(coord)
        moves = bit_valid_moves(board, coord)
        if moves:
            print(f"generated {len(moves)} valid moves at {coord}")
            return random.choice(moves)
    print("no valid moves available")
    exit(1)

def bit_has_valid_move(board: "BitBoard", coord: Coord) -> bool:
    for tetromino in tetrominoes:
        action = Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        if bit_is_valid(board, action):
            return True
    return False

def bit_valid_moves(board: "BitBoard", coord: Coord) -> list[Action]:
    valid_moves = []
    for tetromino in tetrominoes:
        action = Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        if bit_is_valid(board, action):
            valid_moves.append(action)
    return valid_moves

def bit_valid_coords(board: "BitBoard", player_color: PlayerColor, first_turns: bool = False) -> list[Coord]:
    if first_turns and board._red_state == 0 and board._blue_state == 0:
        return [Coord(r, c) for r in range(BOARD_N) for c in range(BOARD_N)]
    state = board.red_state if player_color == PlayerColor.RED else board.blue_state
    valid_coords = []
    for coord in state.keys():
        for dir in Direction:
            adjacent = coord + dir
            if board._cell_empty(adjacent):
                valid_coords.append(adjacent)
    return valid_coords

def bit_is_valid(board: "BitBoard", piece: Action) -> bool:
    for coord in piece.coords:
        if not board._cell_empty(coord):
            return False
    return True

def bit_find_actions(board: "BitBoard", color: PlayerColor) -> list[Action]:
    coords: list[Coord] = bit_valid_coords(board, color)
    actions: list[Action] = []
    for coord in coords:
        actions.extend(bit_valid_moves(board, coord))
    return list(set(actions))

def bit_update_actions(prev_board: "BitBoard", new_board: "BitBoard", my_actions: list[Action], color: PlayerColor):
    my_actions_set = set(my_actions)
    for action in my_actions_set.copy():
        if not bit_is_valid(new_board, action) or not bit_check_adjacent_cells(new_board, action.coords, color):
            my_actions_set.remove(action)
    for coord in bit_changed_coords(prev_board, new_board):
        if new_board[coord] is None:
            my_actions_set.update(bit_valid_moves_of_any_empty(new_board, coord, color))
        elif new_board[coord] == color:
            for adjacent in [coord + dir for dir in Direction]:
                if new_board[adjacent] is None:
                    my_actions_set.update(bit_valid_moves(new_board, adjacent))
    return list(my_actions_set)

def bit_changed_coords(prev_board: "BitBoard", new_board: "BitBoard") -> list[Coord]:
    return [Coord(i // BOARD_N, i % BOARD_N) for i in range(BOARD_N * BOARD_N) if (prev_board[Coord(i // BOARD_N, i % BOARD_N)] != new_board[Coord(i // BOARD_N, i % BOARD_N)])]

def bit_has_action(board: "BitBoard", color: PlayerColor) -> bool:
    coords: list[Coord] = bit_valid_coords(board, color)
    for coord in coords:
        if bit_has_valid_move(board, coord):
            return True
    return False


class BitBoard:
    # TODO: allow init_state
    def __init__(
        self,
        init_state: dict[Coord, CellState] | None = None,
        init_color: PlayerColor = PlayerColor.RED,
    ):
        self._red_state = 0
        self._blue_state = 0
        self._turn_color: PlayerColor = init_color
        self._turn_count: int = 0

    def apply_action(self, action: Action | None = None):
        if not action:
            print("ERROR: No action given")
            return

        for coord in action.coords:
            index = coord.r * BOARD_N + coord.c
            if self._turn_color == PlayerColor.RED:
                # use bitwise OR to add piece
                self._red_state |= 1 << index
            else:
                self._blue_state |= 1 << index

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
            # remove piece from red and blue bit representations
            self._red_state &= ~(1 << index)
            self._blue_state &= ~(1 << index)

    def _cell_occupied(self, coord: Coord) -> bool:
        index = coord.r * BOARD_N + coord.c
        # return true if red or blue has piece at cell
        return bool((self._red_state >> index) & 1) or bool(
            (self._blue_state >> index) & 1
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

    def apply_ansi(self, str, bold=True, color=None):
        bold_code = "\033[1m" if bold else ""
        color_code = ""
        if color == "r":
            color_code = "\033[31m"
        if color == "b":
            color_code = "\033[34m"
        return f"{bold_code}{color_code}{str}\033[0m"

    def render(self, use_color: bool = False) -> str:
        output = ""
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                index = r * BOARD_N + c
                color = None
                if self._cell_occupied(Coord(r, c)):
                    if (self._red_state >> index) & 1:
                        color = "r"
                    elif (self._blue_state >> index) & 1:
                        color = "b"
                    text = f"{color} "
                    if use_color:
                        output += self.apply_ansi(str=text, bold=True, color=color)
                    else:
                        output += text
                else:
                    output += ". "
            output += "\n"
        return output

    def copy(self):
        new_board = BitBoard()
        new_board._red_state = self._red_state
        new_board._blue_state = self._blue_state
        new_board._turn_color = self._turn_color
        new_board._turn_count = self._turn_count
        return new_board

    def __getitem__(self, coord: Coord) -> CellState:
        index = coord.r * BOARD_N + coord.c
        # if red has piece at cell, return red CellState
        if (self._red_state >> index) & 1:
            return CellState(PlayerColor.RED)
        # if blue has piece at cell, return blue CellState
        elif (self._blue_state >> index) & 1:
            return CellState(PlayerColor.BLUE)
        else:
            return CellState()

    def __setitem__(self, coord: Coord, cell: CellState):
        index = coord.r * BOARD_N + coord.c
        # if the new state is red, add red piece and remove blue piece
        if cell == CellState(PlayerColor.RED):
            self._red_state |= 1 << index
            self._blue_state &= ~(1 << index)
        # if the new state is blue, add blue piece and remove red piece
        elif cell == CellState(PlayerColor.BLUE):
            self._blue_state |= 1 << index
            self._red_state &= ~(1 << index)
        else:
            # if new state is empty, remove both red and blue pieces
            self._red_state &= ~(1 << index)
            self._blue_state &= ~(1 << index)

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
            # if player is red, count the number of 1s in red_state
            return bin(self._red_state).count("1")
        else:
            # if player is blue, count the number of 1s in red_state
            return bin(self._blue_state).count("1")

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
        # for each cell in the board
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                index = r * BOARD_N + c  # calculate the index in bit representation
                # if red has piece at cell, add red CellState
                if (self._red_state >> index) & 1:
                    state[Coord(r, c)] = CellState(PlayerColor.RED)
                # if blue has piece at cell, add blue CellState
                elif (self._blue_state >> index) & 1:
                    state[Coord(r, c)] = CellState(PlayerColor.BLUE)
                else:  # if cell empty, add empty CellState
                    state[Coord(r, c)] = CellState()
        return state

    @property
    def blue_state(self) -> dict[Coord, CellState]:
        state = {}
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                index = r * BOARD_N + c
                if (self._blue_state >> index) & 1:
                    state[Coord(r, c)] = CellState(PlayerColor.BLUE)
                else:
                    state[Coord(r, c)] = CellState()
        return state

    @property
    def red_state(self) -> dict[Coord, CellState]:
        state = {}
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                index = r * BOARD_N + c
                if (self._red_state >> index) & 1:
                    state[Coord(r, c)] = CellState(PlayerColor.RED)
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
