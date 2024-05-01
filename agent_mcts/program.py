# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing self

import copy
import random

# import tensorflow as tf
from cmath import log
from collections import defaultdict
from agent_mcts.mcts import MCTSNode
from agent_random.movements import get_valid_coords, get_valid_moves
from agent_random.tetronimos import get_tetronimos
from referee.game import (
    PlayerColor,
    Action,
    PlaceAction,
    Coord,
)
from referee.game.board import Board, CellState

# TODO: redesign Board data structure to be more efficient


class Agent:
    """
    This class is the "entry point" for your self, providing an interface to
    respond to various Tetress game events.
    """

    # attributes
    game_board: Board  # to keep track of game
    game_state: dict[Coord, CellState]  # to try different moves
    tetronimos: list[PlaceAction]  # list of all possible tetronimos
    opponent: PlayerColor  # to keep track of opponent
    sim_logs: list[str]  # to keep track of simulation results
    sim_commentary: list[str]  # to keep track of simulation commentary
    sim_game_num: int  # to keep track of simulation number

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the self.
        Any setup and/or precomputation should be done here.
        """
        self.game_board = Board()
        self.game_state = self.game_board._state
        self.tetronimos = get_tetronimos(Coord(0, 0))
        self._color = color
        self.name = "self_Next " + self._color.name
        self.sim_logs = []
        self.sim_commentary = []
        self.sim_game_num = 0

        # test tetronimos
        with open("tetronimos_test.txt", "w") as f:
            for tetronimo in get_tetronimos(Coord(5, 5)):
                board = Board()
                board.apply_action(tetronimo)
                print(board.render(), file=f)

        # announce self
        print(f"{self.name} *init*: {self._color}")

        # set opponent colour
        match color:
            case PlayerColor.RED:
                self.opponent = PlayerColor.BLUE
            case PlayerColor.BLUE:
                self.opponent = PlayerColor.RED

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the self's turn
        to take an action. It must always return an action object.
        """
        root = MCTSNode(self.game_board)
        action = root.best_action(sim_no=10)

        if action:
            return action
        else:
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
