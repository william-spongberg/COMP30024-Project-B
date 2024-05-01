from referee.game import PlayerColor, Coord, PlaceAction, Direction
from referee.game.board import Board, CellState


def valid_moves(
    state: dict[Coord, CellState], tetronimos: list[PlaceAction], coord: Coord
) -> list[PlaceAction]:
    """
    Get valid PlaceActions from a given coordinate.
    """
    return [move for move in get_moves(coord, tetronimos) if is_valid(state, move)]


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


def is_valid(state: dict[Coord, CellState], piece: PlaceAction) -> bool:
    """
    Check if the piece can be placed on the board.
    """
    for coord in piece.coords:
        if state[coord].player is not None:
            return False
    return True


def get_moves(coord: Coord, tetronimos: list[PlaceAction]) -> list[PlaceAction]:
    """
    Get all possible tetronimo moves from a given coordinate
    """
    return [
        PlaceAction(*[coord + Coord(x, y) for x, y in list(tetronimo.coords)])
        for tetronimo in tetronimos
    ]
