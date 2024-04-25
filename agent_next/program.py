# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from argparse import Namespace
import asyncio
from os import close
from tkinter import Place
from typing import AsyncGenerator
from agent_random.movements import get_valid_moves, get_valid_coords
from agent_random.tetronimos import get_tetronimos
from referee.agent.client import RemoteProcessClassClient
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
    sim_results: list[str] # to keep track of simulation results
    sim_commentary: list[str] # to keep track of simulation commentary

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self.game_board = Board()
        self.game_state = self.game_board._state
        self.tetronimos = get_tetronimos(Coord(0,0))        
        self._color = color
        self.name = "Agent_Next " + self._color.name
        self.sim_results = []
        self.sim_commentary = []
        
        # test tetronimos
        with open('tetronimos_test.txt', 'w') as f:
            for tetronimo in get_tetronimos(Coord(5,5)):
                board = Board()
                board.apply_action(tetronimo)
                print(board.render(), file=f)
        
        # announce agent
        print(f"{self.name} *init*: {self._color}")
        
        # set opponent colour        
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
        
        # announce simulation
        print("Simulated game: running...")
        
        # pick agents
        pl1 = PlayerLoc("agent_random", "Agent")
        pl2 = PlayerLoc("agent_random", "Agent")
        
        # convert agents to players
        player1 : Player = AgentProxyPlayer("sim_p1", self._color, pl1, None, None)
        player2 : Player = AgentProxyPlayer("sim_p2", self.opponent, pl2, None, None)
        
        # add subprocesses for players
        player1._agent = RemoteProcessClassClient(pl1.pkg, pl1.cls, 100000, 100000, 1.0, 180.0, True, self._color)
        player2._agent = RemoteProcessClassClient(pl2.pkg, pl2.cls, 100000, 100000, 1.0, 180.0, True, self.opponent)
        
        # pick event handlers
        gl: LogStream = LogStream("sim_logger", handlers = [self.file_log_handler], ansi=False)
        rl: LogStream = LogStream("sim___game", handlers = [self.file_commentary_handler], ansi=False)
        event_handlers = [
            game_event_logger(gl) if gl is not None else None, # logs game events
            game_commentator(rl), # commentates game less strictly than logs
            output_board_updates(rl, False, True) # draws board updates
        ]

        # simulate game
        sim_winner: Player | None = asyncio.get_event_loop().run_until_complete(run_game([player1, player2], event_handlers))
        
        # get colour from sim_game
        if sim_winner:
            print(f"Simulated game: {sim_winner.color} wins!")
            
            if sim_winner.color == self._color:
                print(f"[{self.name}] responsible for simulation: wins!")
            else:
                print(f"[{self.name}] responsible for simulation: loses!")
        else:
            print("Simulated game: draw")
        
        # write simulated logs to file
        with open('sim_results.txt', 'w') as f:
            for result in self.sim_results:
                print(result, file=f)
        
        # write commentary + board updates to file
        with open('sim_commentary.txt', 'w') as f:
            for result in self.sim_commentary:
                print(result, file=f)
        
        if action == PlaceAction(Coord(0,0), Coord(0,0), Coord(0,0), Coord(0,0)):
            print(f"No valid moves for {self._color}")
        return action
    
    def file_log_handler(self, message: str):
        self.sim_results.append(message)
    
    def file_commentary_handler(self, message: str):
        self.sim_commentary.append(message)
    
    def none_handler(self, message: str):
        pass

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        
        self.game_board.apply_action(action)
        self.game_state = self.game_board._state