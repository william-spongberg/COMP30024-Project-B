# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from tkinter import Place
from agent_random.movements import get_valid_moves, get_valid_coords
from agent_random.tetronimos import get_tetronimos
from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.board import Board, CellState
from referee.run import run_game
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
        # if no valid moves, pick a new coord
        if (get_valid_moves(self.game_state, self.tetronimos, coord) == []):
            for coord in get_valid_coords(self.game_state, self._color):
                if (get_valid_moves(self.game_state, self.tetronimos, coord) != []):
                    break
        action = random.choice(get_valid_moves(self.game_state, self.tetronimos, coord))
        
        # in future will then play game out to end, but not update actual board
        
        # use run_game() to simulate the game to the end
        #run_game()
        
        print(f"{self.name} *action*: {self._color} to play: {PlaceAction(*action.coords)}")
        return action

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        
        self.game_board.apply_action(action)
        self.game_state = self.game_board._state
        
        #print(self.game_board.render())

        # print the action that was played
        print(f"{self.name} *update*: {color} played: {PlaceAction(*action.coords)}")
