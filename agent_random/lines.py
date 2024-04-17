from referee.game import PlayerColor, Coord

BOARD_N = 11

def construct_horizontal_line(coord: Coord, board: dict[Coord, PlayerColor]) -> list[Coord]:
    """
    Construct a horizontal line for a coord, only including empty spaces
    """
    line = []
    for i in range(BOARD_N):
        if not board.get(Coord(coord.r, i), None):
            line.append(Coord(coord.r, i))
    return line

def construct_vertical_line(coord: Coord, board: dict[Coord, PlayerColor]) -> list[Coord]:
    """
    Construct a vertical line for a coord, only including empty spaces
    """
    line = []
    for i in range(BOARD_N):
        if not board.get(Coord(i, coord.c), None):
            line.append(Coord(i, coord.c))
    return line

def delete_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord]) -> dict[Coord, PlayerColor]:
    """
    Delete the coordinates on the goal line from the board.
    """
    if goal_line[0].r == goal_line[1].r:  # check if goal line is horizontal
        goal_line_rows = {coord.r for coord in goal_line}
        for coord in list(board.keys()):  # create a copy of keys to iterate over
            if coord.r in goal_line_rows:
                del board[coord]
    else:  # goal line is vertical
        goal_line_cols = {coord.c for coord in goal_line}
        for coord in list(board.keys()):  # create a copy of keys to iterate over
            if coord.c in goal_line_cols:
                del board[coord]
    return board

def delete_filled_lines(board: dict[Coord, PlayerColor]):
    """
    Delete filled rows and columns from the board.
    """
    coords_to_remove = []
    for r in range(BOARD_N):
        row_coords = [Coord(r, c) for c in range(BOARD_N)]
        if all(coord in board for coord in row_coords):
            # If all coordinates in the row are filled, delete them
            coords_to_remove.extend(row_coords)
    for c in range(BOARD_N):
        col_coords = [Coord(r, c) for r in range(BOARD_N)]
        if all(coord in board for coord in col_coords):
            # If all coordinates in the column are filled, delete them
            coords_to_remove.extend(col_coords)
    for coord in coords_to_remove:
        board.pop(coord, None)
    return board