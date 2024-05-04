from referee.game import PlaceAction, Coord
from referee.game.board import Board
from referee.game.pieces import create_piece, PieceType

BOARD_N = 11


def make_tetrominos(coord: Coord) -> list[PlaceAction]:
    """
    Get all possible tetrominos as PlaceActions.
    """

    tetrominos = []

    # get all possible orientations of a piece
    for piece_type in PieceType:
        tetrominos.append(create_piece(piece_type, coord))

    # remove duplicates
    tetrominos = list(set(tetrominos))

    # convert all elements to PlaceAction
    for i, tetronimo in enumerate(tetrominos):
        tetrominos[i] = PlaceAction(*tetronimo.coords)
    return tetrominos

def test_tetronimos():
    with open("tetronimos_test.txt", "w") as f:
        for tetronimo in make_tetrominos(Coord(5, 5)):
            board = Board()
            board.apply_action(tetronimo)
            print(board.render(), file=f)