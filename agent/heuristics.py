from referee.game import PlayerColor, Coord, PlaceAction
from .lines import construct_horizontal_line, construct_vertical_line

BOARD_N = 11

def goal_line_completion(board: dict[Coord, PlayerColor], goal_line: list[Coord]):
    """
    Calculate the completion of the goal line.
    """
    return sum(1 for coord in goal_line if board.get(coord, None) is None)

# used in movement.py
def coord_distance_to_goal_line(board: dict[Coord, PlayerColor], goal: Coord, coord: Coord):
    """
    Calculate the distance from a coord to the closest goal line coord.
    """
    row_line = construct_horizontal_line(goal, board)
    col_line = construct_vertical_line(goal, board)

    return min(
        min(
            abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
            for goal_coord in row_line
        ),
        min(
            abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
            for goal_coord in col_line
        ),
    )

def distance_to_furthest_goal(
    board: dict[Coord, PlayerColor], goal_line: list[Coord]
):
    """
    Calculate the max distance from a red piece to the furthest goal line coord.
    """
    return max(
        abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
        for coord in board
        if board[coord] == PlayerColor.RED
        for goal_coord in goal_line
    )

MAGIC_NUMBER =  1.1428571428571428 #8/7
# We tested out the magic number by running the heuristic on test cases and adjusting it to get the best results.

def calculate_heuristic(
    board: dict[Coord, PlayerColor], goal: Coord, path: list[PlaceAction]
):
    """
    Calculate the heuristic of a given move. Calculate both possible goal lines and return the minimum.
    """
    row_line = construct_horizontal_line(goal, board)
    col_line = construct_vertical_line(goal, board)
    row_heuristic = (
        goal_line_completion(board, row_line)
        + distance_to_goal_line(board, row_line)
        + empty_around_by(board, row_line)
    )* MAGIC_NUMBER
    col_heuristic = (
        goal_line_completion(board, col_line)
        + distance_to_goal_line(board, col_line)
        + empty_around_by(board, col_line)
    ) * MAGIC_NUMBER
    return min(row_heuristic, col_heuristic) + path_continuity(path)*MAGIC_NUMBER


def no_horizontal_obstacles_in_the_way(
    board: dict[Coord, PlayerColor], move_coord: Coord, goal_coord: Coord
):
    """
    Check if there are any obstacles in the way of a horizontal move.
    """
    for c in range(
        min(move_coord.c, goal_coord.c) + 1, max(move_coord.c, goal_coord.c)
    ):
        if board.get(Coord(move_coord.r, c), None) is PlayerColor.BLUE:
            return False
    return True


def no_vertical_obstacles_in_the_way(
    board: dict[Coord, PlayerColor], move_coord: Coord, goal_coord: Coord
):
    """
    Check if there are any obstacles in the way of a vertical move.
    """
    for r in range(
        min(move_coord.r, goal_coord.r) + 1, max(move_coord.r, goal_coord.r)
    ):
        if board.get(Coord(r, move_coord.c), None) is not PlayerColor.BLUE:
            return False
    return True


def distance_to_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord]):
    """
    Calculate the distance from a path to the closest exposed goal line coord.
    """
    
    # minimal row/column distance from all reds to exposed coords in goal line
    min_r = min(
        (
            abs(red.r - goal_coord.r)
            for red in board
            if board[red] == PlayerColor.RED
            for goal_coord in goal_line
            if no_horizontal_obstacles_in_the_way(board, red, goal_coord)
        ),
        default=distance_to_furthest_goal(board, goal_line),
    )

    min_c = min(
        (
            abs(red.c - goal_coord.c)
            for red in board
            if board[red] == PlayerColor.RED
            for goal_coord in goal_line
            if no_vertical_obstacles_in_the_way(board, red, goal_coord)
        ),
        default=distance_to_furthest_goal(board, goal_line)
    )
    return min(min_r, min_c)


def empty_around_by(board: dict[Coord, PlayerColor], goal_line: list[Coord]):
    """
    Return empty coords in goal line surrounded by Blue pieces.
    """
    n = 0
    for coord in goal_line:
        if all(
            board.get(Coord(*coord_d), None) == PlayerColor.BLUE
            for coord_d in [coord.up(), coord.down(), coord.left(), coord.right()]
        ):
            n += 4
    return n

def path_continuity(path: list[PlaceAction]):
    """
    Calculate the number of consecutive pieces in the path.
    """
    consecutive_pieces = 0
    for i in range(1, len(path)):
        # Convert sets to lists before accessing by index
        current_coords = list(path[i].coords)
        previous_coords = list(path[i - 1].coords)
        if (
            abs(current_coords[0].r - previous_coords[-1].r)
            + abs(current_coords[0].c - previous_coords[-1].c)
            == 1
        ):
            consecutive_pieces += 1
    return consecutive_pieces
