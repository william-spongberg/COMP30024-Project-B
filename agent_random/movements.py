from agent_random.tetronimos import make_tetronimos
from referee.game import PlayerColor, Coord, PlaceAction, Direction
from referee.game.board import Board, CellState

# TODO: fix not all possible moves being generated?

tetronimos = make_tetronimos(Coord(0, 0))


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
    Get valid adjacent coordinates from all over the board.
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
    Get all possible tetronimo at a given coordinate.
    """
    return [
        PlaceAction(*[coord + Coord(x, y) for x, y in list(tetronimo.coords)])
        for tetronimo in tetronimos
    ]


def valid_moves(state: dict[Coord, CellState], coord: Coord) -> list[PlaceAction]:
    """
    Get all possible tetronimo at a given coordinate.
    """
    return [
        PlaceAction(*[coord + Coord(x, y) for x, y in list(tetronimo.coords)])
        for tetronimo in tetronimos
        if is_valid(state, tetronimo)
    ]


def has_valid_move(state: dict[Coord, CellState], coord: Coord) -> bool:
    """
    Check if a player has any valid piece.
    """
    for tetronimo in tetronimos:
        if is_valid(
            state,
            PlaceAction(*[coord + Coord(x, y) for x, y in list(tetronimo.coords)]),
        ):
            return True

    return False
