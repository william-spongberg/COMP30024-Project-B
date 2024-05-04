from referee.game import PlaceAction, Coord
from referee.game.board import Board
from referee.game.pieces import Piece, create_piece, PieceType

BOARD_N = 11


def make_tetrominoes(coord: Coord) -> list[PlaceAction]:
    """
    Get all possible tetrominoes as PlaceActions.
    """

    tetrominoes = []
    moved_tetrominoes = []

    # get all possible orientations of a piece
    for piece_type in PieceType:
        tetrominoes.append(create_piece(piece_type, Coord(0, 0)))

    # remove duplicates
    tetrominoes = list(set(tetrominoes))
    
    for tetromino in tetrominoes:
        # choose different starting origins
        for origin in tetromino.coords:
            moved_tetrominoes.append(Piece([coord + Coord(x, y) - origin for x, y in tetromino.coords]))
    

    # convert all elements to PlaceAction
    for i, moved_tetromino in enumerate(moved_tetrominoes):
        moved_tetrominoes[i] = PlaceAction(*moved_tetromino.coords)
    
    return moved_tetrominoes


def test_tetronimoes():
    with open("tetronimoes_test.txt", "w") as f:
        print("testing tetrominoes", file=f)
        for tetromino in make_tetrominoes(Coord(5, 5)):
            board = Board()
            board.apply_action(tetromino)
            print(board.render(), file=f)
        print("num tetrominoes:", len(make_tetrominoes(Coord(5, 5))), file=f)
