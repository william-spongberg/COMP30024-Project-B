from referee.game import PlaceAction, Coord
from referee.game.pieces import create_piece, PieceType

BOARD_N = 11


def make_tetronimos(coord: Coord) -> list[PlaceAction]:
    """
    Get all possible tetronimos as PlaceActions.
    """

    tetronimos = []

    # get all possible orientations of a piece
    for piece_type in PieceType:
        tetronimos.append(create_piece(piece_type, coord))

    # remove duplicates
    tetronimos = list(set(tetronimos))

    # convert all elements to PlaceAction
    for i, tetronimo in enumerate(tetronimos):
        tetronimos[i] = PlaceAction(*tetronimo.coords)
    return tetronimos
