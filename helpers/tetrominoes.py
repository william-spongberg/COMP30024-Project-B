from referee.game import PlaceAction, Coord
from referee.game.board import Board
from referee.game.pieces import create_piece, PieceType

BOARD_N = 11


def make_tetrominoes(coord: Coord) -> list[PlaceAction]:
    """
    Get all possible tetrominoes as PlaceActions.
    """

    tetrominoes = []
    moved_tetrominoes = []

    # get all possible orientations of a piece
    for piece_type in PieceType:
        tetrominoes.append(create_piece(piece_type, coord))

    # remove duplicates
    tetrominoes = list(set(tetrominoes))

    # convert all elements to PlaceAction
    for i, tetromino in enumerate(tetrominoes):
        tetrominoes[i] = PlaceAction(*tetromino.coords)
    
    # # get all possible moves of a piece
    # for tetromino in tetrominoes:
    #     for coord in list(tetromino.coords):
    # TODO: copy tetronimo to have all 4 coords be the start coord
            
        
    
    return tetrominoes


def test_tetronimoes():
    with open("tetronimoes_test.txt", "w") as f:
        print("testing tetrominoes", file=f)
        for tetromino in make_tetrominoes(Coord(5, 5)):
            board = Board()
            board.apply_action(tetromino)
            print(board.render(), file=f)
        print("num tetrominoes:", len(make_tetrominoes(Coord(5, 5))), file=f)
