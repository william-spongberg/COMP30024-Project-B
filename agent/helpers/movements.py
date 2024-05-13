import random
from .tetrominoes import make_tetrominoes
from referee.game import PlayerColor, Coord, Action, Direction
from referee.game.board import CellState


tetrominoes = make_tetrominoes(Coord(0, 0))


def is_valid(state: dict[Coord, CellState], piece: Action) -> bool:
    """
    Check if the piece can be placed on the board.
    """
    for coord in piece.coords:
        if state[coord].player is not None:
            return False
    return True


def check_adjacent_cells(
    action: Action, state: dict[Coord, CellState], color: PlayerColor
) -> bool:
    """
    Check if the given coordinates have any adjacent cells of the same color
    """
    for coord in action.coords:
        for dir in Direction:
            if state[coord + dir].player == color:
                return True
    return False


def generate_random_move(
    state: dict[Coord, CellState], color: PlayerColor, first_turns: bool = False
) -> Action:
    """
    Generate a random move for a given state and player colour.
    """
    coords = valid_coords(state, color, first_turns)
    coord = random.choice(coords)
    coords.remove(coord)

    # try all available coords
    while True:
        moves = valid_moves(state, coord)
        if moves or not coords:
            break
        coord = random.choice(coords)
        coords.remove(coord)

    # if no valid moves available
    if not moves:
        print("no valid moves available")
        exit(1)
        # return None

    # return random move
    return random.choice(moves)


def valid_coords(
    state: dict[Coord, CellState], player_colour: PlayerColor, first_turns: bool = False
) -> list[Coord]:
    """
    Get all valid adjacent coordinates for a player's state.
    """

    # if dict does not contain any player colour coords, return all coords
    if first_turns:
        return list(state.keys())

    # else if dict contains a player colour coord, return all adjacent coords
    return [
        adjacent
        for coord in state.keys()
        if state[coord].player == player_colour
        for adjacent in [coord + dir for dir in Direction]
        if state[adjacent].player is None
    ]


def valid_moves(state: dict[Coord, CellState], coord: Coord) -> list[Action]:
    """
    Get all possible valid tetrominoes at a given coordinate for a given state.
    """
    valid_moves = []
    for tetromino in tetrominoes:
        action = Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        if is_valid(state, action):
            valid_moves.append(action)
    return valid_moves


def valid_moves_of_any_empty(
    state: dict[Coord, CellState], coord: Coord, color: PlayerColor
) -> list[Action]:
    if state[coord].player is not None:
        print("invalid coord")
        exit(1)
    return [
        move
        for move in valid_moves(state, coord)
        if check_adjacent_cells(move, state, color)
    ]


def has_valid_move(state: dict[Coord, CellState], coord: Coord) -> bool:
    """
    Check there is at least one valid move available.
    """
    for tetromino in tetrominoes:
        action = Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        if is_valid(state, action):
            return True
    return False
