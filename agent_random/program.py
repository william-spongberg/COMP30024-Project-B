# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from agent_random.movements import get_valid_moves, get_valid_coords
from agent_random.tetronimos import get_tetronimos
from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.board import Board, CellState
import random


class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """

    # attributes
    game_board: Board  # to keep track of game
    game_state: dict[Coord, CellState]  # to try different moves
    tetronimos: list[PlaceAction]  # list of all possible tetronimos

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self.game_board = Board()
        self.game_state = self.game_board._state
        self.tetronimos = get_tetronimos(Coord(0, 0))
        self._color = color
        self.name = "Agent_Random " + self._color.name

        print(f"{self.name} *init*: {self._color}")

        match color:
            case PlayerColor.RED:
                self.opponent = PlayerColor.BLUE
            case PlayerColor.BLUE:
                self.opponent = PlayerColor.RED

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object.
        """
        return self.get_random_move()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state.
        """

        self.game_board.apply_action(action)
        self.game_state = self.game_board._state
    
    def get_random_move(self) -> PlaceAction:
        coords = get_valid_coords(self.game_state, self._color)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while get_valid_moves(self.game_state, self.tetronimos, coord) == []:
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if get_valid_moves(self.game_state, self.tetronimos, coord) == []:
            return PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        return random.choice(get_valid_moves(self.game_state, self.tetronimos, coord))
