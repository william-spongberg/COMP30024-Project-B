from referee.game import PlayerColor, Coord, PlaceAction
from .heuristics import coord_distance_to_goal_line

def get_valid_moves(board: dict[Coord, PlayerColor], tetronimos: list[PlaceAction], coord: Coord) -> list[PlaceAction]:
    """
    Get valid PlaceActions from a given coordinate.
    """
    valid_moves = []
    
    # for each piece, check if valid, if valid, add to list of possible moves
    for move in get_moves(coord, tetronimos):
        if is_valid(board, move):
            valid_moves.append(move)

    #print(valid_moves)
    return valid_moves

def get_valid_adjacents_all_over_the_board(board: dict[Coord, PlayerColor], goal: Coord) -> list[Coord]:
    """
    Get valid adjacent coordinates from all over the board.
    """
    valid_adjacents = []
    for coord in board:
        if (coord is not None) and (board.get(coord, None) == PlayerColor.RED):
            directions = [coord.up(), coord.down(), coord.left(), coord.right()]
            adjacents = [Coord(dir.r, dir.c) for dir in directions]
            for adjacent in adjacents:
                if not board.get(adjacent, None): # if adjacent is empty
                    valid_adjacents.append(adjacent)
    valid_adjacents.sort(key=lambda x: coord_distance_to_goal_line(board, goal, x))
    return valid_adjacents

def is_valid(board: dict[Coord, PlayerColor], piece: PlaceAction) -> bool:
    """
    Check if the piece can be placed on the board.
    """
    for coord in piece.coords:
        if board.get(coord, None):
            return False
    return True

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