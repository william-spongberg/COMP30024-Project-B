from referee.game import PlayerColor, Coord, PlaceAction, Direction
from referee.game.board import Board, CellState

def get_valid_moves(state: dict[Coord, CellState], tetronimos: list[PlaceAction], coord: Coord) -> list[PlaceAction]:
    """
    Get valid PlaceActions from a given coordinate.
    """
    valid_moves = []
    
    # for each piece, check if valid, if valid, add to list of possible moves
    for move in get_moves(coord, tetronimos):
        if is_valid(state, move):
            valid_moves.append(move)
        # else:
        #     print(f"invalid move: {move}")

    #print(valid_moves)
    return valid_moves

def get_valid_coords(state: dict[Coord, CellState], player_colour: PlayerColor) -> list[Coord]:
    """
    Get valid adjacent coordinates from all over the board.
    """
    valid_adjacents = []
    for coord in state.keys():
        if state[coord].player == player_colour:
            adjacents = [coord + dir for dir in Direction]
            for adjacent in adjacents:
                if state[adjacent].player is None: # if adjacent is empty
                    valid_adjacents.append(adjacent)
    if not valid_adjacents:
        print("no valid adjacents found, returning all coords")
        for coord in state.keys():
            valid_adjacents.append(coord)
    return valid_adjacents

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
    get all possible tetronimo moves from a given coordinate
    """
    list_of_moves = []
    for tetronimo in tetronimos:
        move = [coord + Coord(x, y) for x, y in list(tetronimo.coords)]
        move = PlaceAction(*move)
        list_of_moves.append(move)
    return list_of_moves