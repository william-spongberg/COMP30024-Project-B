import random
from unittest import result
from .tetrominoes import make_tetrominoes
from referee.game import PlayerColor, Coord, Action, Direction, actions
from referee.game.board import Board, CellState

# TODO: fix not all possible moves being generated?

tetrominoes = make_tetrominoes(Coord(0, 0))


def is_valid(state: dict[Coord, CellState], piece: Action) -> bool:
    """
    Check if the piece can be placed on the board.
    """
    for coord in piece.coords:
        if state[coord].player is not None:
            return False
    return True

def check_adjacent_cells(coords: list[Coord], state: dict[Coord, CellState], color: PlayerColor) -> bool:
    """
    Check if the given coordinates have any adjacent cells of the same color
    """
    for coord in coords:
        for dir in Direction:
            if state[coord + dir].player == color:
                return True
    return False

def generate_random_move(state: dict[Coord, CellState], color: PlayerColor, first_turns: bool=False) -> Action:
    """
    Generate a random move for a given state and player colour.
    """
    if first_turns and color == PlayerColor.RED:
            return Action(Coord(5, 5), Coord(5, 6), Coord(5, 7), Coord(5, 8))
    coords = valid_coords(state, color, first_turns)
    coord = random.choice(coords)
    coords.remove(coord)

    # try all available coords
    while not valid_moves(state, coord):
        if coords:
            coord = random.choice(coords)
            coords.remove(coord)
        else:
            break
    moves = valid_moves(state, coord)
    # if no valid moves available
    if not moves:
        return Action(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))

    # prints to track valid moves generated
    print(
        f"generated {len(moves)} valid moves at {coord}"
    )
    # for move in valid_moves(state, coord):
    #     print(move)

    # return random move
    return random.choice(moves)

def valid_coords(
    state: dict[Coord, CellState], player_colour: PlayerColor, first_turns: bool=False
) -> list[Coord]:
    """
    Get all valid adjacent coordinates for a player's state.
    """

    # if dict does not contain any player colour coords, return all coords
    if first_turns:
        return list(state.keys())

    # else if dict contains a player colour coord, return all adjacent coords
    return [
        adjacent
        for coord in state.keys()
        if state[coord].player == player_colour
        for adjacent in [coord + dir for dir in Direction]
        if state[adjacent].player is None
    ]
    # TODO: check if valid coords are surrounded (can't have pieces placed)
    # avoids needing to check all 19 pieces


def moves_at_coord(coord: Coord) -> list[Action]:
    """
    Get all possible tetrominoes at a given coordinate.
    """
    return [
        Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        for tetromino in tetrominoes
    ]


def valid_moves(state: dict[Coord, CellState], coord: Coord) -> list[Action]:
    """
    Get all possible valid tetrominoes at a given coordinate for a given state.
    """
    return [
        Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        for tetromino in tetrominoes
        if is_valid(
            state, Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        )
    ]
    
def valid_moves_of_any_empty(state: dict[Coord, CellState], coord:Coord, color: PlayerColor) -> list[Action]:
    if (state[coord].player is not None):
        print("invalid coord")
        exit()
    result = []
    for tetromino in tetrominoes:
        action = Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        if is_valid(state, action) and check_adjacent_cells(action.coords, state, color):
            result.append(action)
    return result

def has_valid_move(state: dict[Coord, CellState], coord: Coord, color: PlayerColor) -> bool:
    """
    Check there is at least one valid move available.
    """
    for tetromino in tetrominoes:
        if is_valid(
            state,
            Action(*[coord + Coord(x, y) for x, y in tetromino.coords])
        ):
            return True
    return False
