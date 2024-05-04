from .tetrominos import make_tetrominos
from referee.game import PlayerColor, Coord, PlaceAction, Direction
from referee.game.board import Board, CellState

# TODO: fix not all possible moves being generated?

tetrominos = make_tetrominos(Coord(0, 0))


def is_valid(state: dict[Coord, CellState], piece: PlaceAction) -> bool:
    """
    Check if the piece can be placed on the board.
    """
    for coord in piece.coords:
        if state[coord].player is not None:
            return False
    return True


def valid_coords(
    state: dict[Coord, CellState], player_colour: PlayerColor
) -> list[Coord]:
    """
    Get all valid adjacent coordinates for a player's state.
    """

    # if dict does not contain any player colour coords, return all coords
    if not any([cell.player == player_colour for cell in state.values()]):
        return list(state.keys())

    # else if dict contains a player colour coord, return all adjacent coords
    return [
        adjacent
        for coord in state.keys()
        if state[coord].player == player_colour
        for adjacent in [coord + dir for dir in Direction]
        if state[adjacent].player is None
    ]
    # TODO: check if valid coords are surrounded (can't have pieces placed)
    # avoids needing to check all 19 pieces


def moves_at_coord(coord: Coord) -> list[PlaceAction]:
    """
    Get all possible tetrominos at a given coordinate.
    """
    return [
        PlaceAction(*[coord + Coord(x, y) for x, y in list(tetronimo.coords)])
        for tetronimo in tetrominos
    ]


def valid_moves(state: dict[Coord, CellState], coord: Coord) -> list[PlaceAction]:
    """
    Get all possible valid tetrominos at a given coordinate for a given state.
    """
    moves: list[PlaceAction] = []
    for tetronimo in tetrominos:
        move = PlaceAction(*[coord + Coord(x, y) for x, y in list(tetronimo.coords)])
        if is_valid(state, move):
            moves.append(move)
    return moves


def has_valid_move(state: dict[Coord, CellState], coord: Coord) -> bool:
    """
    Check there is at least one valid move available.
    """
    for tetronimo in tetrominos:
        if is_valid(
            state,
            PlaceAction(*[coord + Coord(x, y) for x, y in list(tetronimo.coords)]),
        ):
            return True

    return False
