from .tetrominoes import make_tetrominoes
from referee.game import PlayerColor, Coord, Action, Direction
from referee.game.board import Board, CellState

# TODO: fix not all possible moves being generated?

tetrominoes = make_tetrominoes(Coord(0, 0))


def is_valid(state: dict[Coord, CellState], piece: Action, color: PlayerColor) -> bool:
    """
    Check if the piece can be placed on the board.
    """
    for coord in piece.coords:
        if state[coord].player is not PlayerColor:
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


def moves_at_coord(coord: Coord) -> list[Action]:
    """
    Get all possible tetrominoes at a given coordinate.
    """
    return [
        Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        for tetromino in tetrominoes
    ]


def valid_moves(state: dict[Coord, CellState], coord: Coord, color: PlayerColor) -> list[Action]:
    """
    Get all possible valid tetrominoes at a given coordinate for a given state.
    """
    return [
        Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        for tetromino in tetrominoes
        if is_valid(
            state, Action(*[coord + Coord(x, y) for x, y in tetromino.coords]), color
        )
    ]


def has_valid_move(state: dict[Coord, CellState], coord: Coord, color: PlayerColor) -> bool:
    """
    Check there is at least one valid move available.
    """
    for tetromino in tetrominoes:
        if is_valid(
            state,
            Action(*[coord + Coord(x, y) for x, y in tetromino.coords]), color
        ):
            return True
    return False
