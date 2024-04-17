from tkinter import Place
from referee.game import PlaceAction, Coord
from referee.game.pieces import create_piece, piece_fingerprint, PieceType, Piece

BOARD_N = 11

def get_tetronimos(coord: Coord) -> list[PlaceAction]:
    """
    Get all possible tetronimos as PlaceActions.
    """
    
    pieces: list[Piece] = []
    tetronimos = []
    for piece_type in PieceType:
        # all possible orientations of a piece
        tetronimos.append(create_piece(piece_type, coord))
            
    # remove duplicates
    tetronimos = list(set(tetronimos))
    
    # convert all elements to PlaceAction
    for i in range(len(tetronimos)):
        tetronimos[i] = PlaceAction(*tetronimos[i].coords)
    
    return tetronimos