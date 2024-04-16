from referee.game import Coord, PlaceAction

BOARD_N = 11

def get_tetronimos() -> list[PlaceAction]:
    """
    Get all possible tetronimos.
    """
    
    tetronimos = [
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(1, BOARD_N-1), Coord(2, BOARD_N-1)),  # S (S-shape)
        PlaceAction(Coord(BOARD_N-1, 0), Coord(0, 0), Coord(0, BOARD_N-1), Coord(1, BOARD_N-1)),
        # rest repeated in rotation
        
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(2, 1)), # Z (Z-shape)
        PlaceAction(Coord(BOARD_N-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 1)),
        # rest repeated in rotation
        
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(3, 0)),  # I (straight)
        PlaceAction(Coord(BOARD_N-1, 0), Coord(0, 0), Coord(1, 0), Coord(2, 0)),
        # rest repeated in rotation
        
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(1, 1)),  # T (T-shape)
        PlaceAction(Coord(BOARD_N-1, 0), Coord(0, 0), Coord(1, 0), Coord(0, 1)),
        PlaceAction(Coord(BOARD_N-2, 0), Coord(BOARD_N-1, 0), Coord(0, 0), Coord(BOARD_N-1, 1)),
        PlaceAction(Coord(BOARD_N-1, BOARD_N-1), Coord(0, BOARD_N-1), Coord(1, BOARD_N-1), Coord(0, 0)),
        
        PlaceAction(Coord(0, 0), Coord(0, 1), Coord(0, 2), Coord(1, 2)),  # L (L-shape)
        PlaceAction(Coord(0, BOARD_N-1), Coord(0, 0), Coord(0, 1), Coord(1, 1)),
        PlaceAction(Coord(0, BOARD_N-2), Coord(0, BOARD_N-1), Coord(0, 0), Coord(1, 0)),
        PlaceAction(Coord(BOARD_N-1, BOARD_N-2), Coord(BOARD_N-1, BOARD_N-1), Coord(BOARD_N-1, 0), Coord(0, 0)),
        
        PlaceAction(Coord(0, 0), Coord(0, 1), Coord(0, 2), Coord(BOARD_N-1, 2)),  # J (J-shape)
        PlaceAction(Coord(0, BOARD_N-1), Coord(0, 0), Coord(0, 1), Coord(BOARD_N-1, 1)),
        PlaceAction(Coord(0, BOARD_N-2), Coord(0, BOARD_N-1), Coord(0, 0), Coord(BOARD_N-1, 0)),
        PlaceAction(Coord(1, 2), Coord(1, 1), Coord(1, 0), Coord(0, 0)),
    ]
    
    # rotate each tetronimo
    rotated_tetronimos = []
    for tetronimo in tetronimos:
        for i in range(4):
            rotated_tetronimos.append(rotate(tetronimo, i))
    
    rotated_tetronimos.append(PlaceAction(Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1)))  # O (square)
    rotated_tetronimos.append(PlaceAction(Coord(BOARD_N-1, 0), Coord(0, 0), Coord(BOARD_N-1, 1), Coord(0, 1)))
    rotated_tetronimos.append(PlaceAction(Coord(0, BOARD_N-1), Coord(1, BOARD_N-1), Coord(0, 0), Coord(1, 0)))
    rotated_tetronimos.append(PlaceAction(Coord(BOARD_N-1, BOARD_N-1), Coord(0, BOARD_N-1), Coord(BOARD_N-1, 0), Coord(0, 0)))
    
    return rotated_tetronimos

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

def get_moves(coord: Coord, tetronimos: list[PlaceAction]) -> list[PlaceAction]:
    """
    get all possible tetronimo moves from a given coordinate
    """
    list_of_moves = []
    for tetronimo in tetronimos:
        move = [coord + Coord(x, y) for x, y in list(tetronimo.coords)]
        move = PlaceAction(*move)
        list_of_moves.append(move)
    return list_of_moves