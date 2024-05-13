from referee.game import Action, Coord
from referee.game.pieces import Piece, create_piece, PieceType

BOARD_N = 11


def make_tetrominoes(coord: Coord) -> list[Action]:
    """
    Get all possible tetrominoes as Actions.
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
    

    # convert all elements to Action
    for i, moved_tetromino in enumerate(moved_tetrominoes):
        moved_tetrominoes[i] = Action(*moved_tetromino.coords)
    
    moved_tetrominoes = list(set(moved_tetrominoes))
    
    return moved_tetrominoes
