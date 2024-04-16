from referee.game import Coord, PlaceAction
from referee.game.pieces import create_piece, piece_fingerprint, PieceType

BOARD_N = 11

def get_tetronimos() -> list[PlaceAction]:
    """
    Get all possible tetronimos.
    """
    
    tetronimos = []
    for piece_type in PieceType:
        tetronimos.append(create_piece(piece_type))
    
    # rotate each tetronimo
    rotated_tetronimos = []
    for tetronimo in tetronimos:
        for i in range(4):
            rotated_tetronimos.append(rotate(tetronimo, i))
    
    # remove duplicates
    return list(set(rotated_tetronimos))

def rotate(tetronimo: PlaceAction, times: int) -> PlaceAction:
    """
    Rotate a tetronimo a certain number of times.
    """
    rotated = list(tetronimo.coords)
    for _ in range(times):
        # rotated = [Coord(-y, x) for x, y in rotated] # rotate 90 degrees clockwise (x, y) -> (-y, x)
        rotated = [(Coord(y, x) - Coord((2 * y) % BOARD_N, 0)) for x, y in rotated]
    rotated = PlaceAction(*rotated)
    return rotated