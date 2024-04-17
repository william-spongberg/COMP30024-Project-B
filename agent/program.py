# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from tkinter import Place
from agent.movements import get_valid_moves, get_valid_coords
from agent.tetronimos import get_tetronimos
from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.board import Board, CellState
import random

#import tensorflow as tf


class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """
    
    # attributes
    game_board: Board # to keep track of game
    game_state: dict[Coord, CellState] # to try different moves
    tetronimos: list[PlaceAction] # list of all possible tetronimos

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self.game_board = Board()
        self.game_state = self.game_board._state
        self.tetronimos = get_tetronimos(Coord(0,0))
        
        # for tetronimo in get_tetronimos(Coord(5,5)):
        #     board = Board()
        #     board.apply_action(tetronimo)
        #     print(board.render())
        
        self._color = color
        self.name = "Agent " + self._color.name
        
        match color:
            case PlayerColor.RED:
                print(f"Testing: my name is {self.name} and I am playing as RED")
            case PlayerColor.BLUE:
                print(f"Testing: my name is {self.name} and I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        
        coord = random.choice(get_valid_coords(self.game_state, self._color))
        while (get_valid_moves(self.game_state, self.tetronimos, coord) == []):
            coord = random.choice(get_valid_coords(self.game_state, self._color))
        action = random.choice(get_valid_moves(self.game_state, self.tetronimos, coord))
        
        # in future will then play game out to end, but not update actual board
        
        return action

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        
        # NOTE: called once per agent
        
        self.game_board.apply_action(action)
        self.game_state = self.game_board._state
        
        #print(self.game_board.render())

        # print the action that was played
        place_action: PlaceAction = action
        c1, c2, c3, c4 = action.coords
        print(f"{self.name} update: {color} played: {c1}, {c2}, {c3}, {c4}")
