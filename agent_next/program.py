# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import asyncio
from tkinter import Place
from typing import AsyncGenerator
from agent_random.movements import get_valid_moves, get_valid_coords
from agent_random.tetronimos import get_tetronimos
from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.board import Board, CellState
import random
from referee.log import LogStream
from referee.run import game_commentator, game_delay, game_event_logger, output_board_updates, run_game, game
from referee.agent import Player, AgentProxyPlayer
from referee.options import PlayerLoc

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
    opponent: PlayerColor # to keep track of opponent

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
                self.opponent = PlayerColor.BLUE
            case PlayerColor.BLUE:
                print(f"Testing: my name is {self.name} and I am playing as BLUE")
                self.opponent = PlayerColor.RED

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        
        coord = random.choice(get_valid_coords(self.game_state, self._color))
        action = PlaceAction(Coord(0,0), Coord(0,0), Coord(0,0), Coord(0,0)) # default
        
        # if no valid moves, pick a new coord
        if (get_valid_moves(self.game_state, self.tetronimos, coord) == []):
            # try all available coords
            for coord in get_valid_coords(self.game_state, self._color):
                if (get_valid_moves(self.game_state, self.tetronimos, coord) != []):
                    action = random.choice(get_valid_moves(self.game_state, self.tetronimos, coord))
                    break
        else:
            action = random.choice(get_valid_moves(self.game_state, self.tetronimos, coord))
        
        # pick agents
        pl1 = PlayerLoc("agent_random", "Agent")
        pl2 = PlayerLoc("agent_random", "Agent")
        
        # convert agents to players
        player1 : Player = AgentProxyPlayer("sim_p1", self._color, pl1, None, None)
        player2 : Player = AgentProxyPlayer("sim_p2", self.opponent, pl2, None, None)
        
        # pick event handlers
        gl: LogStream = LogStream("name1")
        rl: LogStream = LogStream("name2")
        #event_handler: AsyncGenerator = []
        event_handlers = [
            game_event_logger(gl) if gl is not None else None,
            game_commentator(rl),
            output_board_updates(rl, True, True)
        ]

        # simulate game
        #event_handlers = []  # TODO: create and add event handlers
        sim_winner: Player | None = asyncio.get_event_loop().run_until_complete(run_game([player1, player2], event_handlers))
        
        # get colour from sim_game
        if sim_winner:
            if sim_winner.color == self._color:
                print(f"Simulated game: {self._color} wins!")
            else:
                print(f"Simulated game: {self._color} loses!")
        else:
            print("Simulated game: draw")
        
        print(event_handlers)
            
        # TODO: fix sim_winner returning as RED every time due to BLUE likely making an error move
        # (BLUE plays first due to this agent being blue and player1 set to this agent's colour)
        
        
        if action == PlaceAction(Coord(0,0), Coord(0,0), Coord(0,0), Coord(0,0)):
            print(f"No valid moves for {self._color}")
        else:
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
