# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import asyncio
from collections import defaultdict
import copy
import random
from typing import AsyncGenerator
from helpers.movements import valid_moves, valid_coords
from helpers.tetrominos import make_tetrominos
from referee.agent.client import RemoteProcessClassClient
from referee.game import (
    BoardUpdate,
    GameBegin,
    GameEnd,
    GameUpdate,
    PlayerColor,
    Action,
    PlaceAction,
    Coord,
    PlayerError,
    PlayerInitialising,
    TurnBegin,
    TurnEnd,
    UnhandledError,
)
from referee.game.board import Board, CellState
from referee.game.exceptions import IllegalActionException, PlayerException
from referee.log import LogStream
from referee.run import (
    game_commentator,
    game_event_logger,
    output_board_updates,
)
from referee.agent import Player, AgentProxyPlayer
from referee.options import PlayerLoc

# import tensorflow as tf

# TODO: redesign Board data structure to be more efficient


class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """

    # attributes
    game_board: Board  # to keep track of game
    game_state: dict[Coord, CellState]  # to try different moves
    tetrominos: list[PlaceAction]  # list of all possible tetrominos
    opponent: PlayerColor  # to keep track of opponent
    sim_logs: list[str]  # to keep track of simulation results
    sim_commentary: list[str]  # to keep track of simulation commentary
    sim_game_num: int  # to keep track of simulation number

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self.game_board = Board()
        self.game_state = self.game_board._state
        self.tetrominos = make_tetrominos(Coord(0, 0))
        self._color = color
        self.name = "Agent_Next " + self._color.name
        self.sim_logs = []
        self.sim_commentary = []
        self.sim_game_num = 0

        # test tetrominos
        with open("tetronimos_test.txt", "w") as f:
            for tetronimo in make_tetrominos(Coord(5, 5)):
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

        ## pick random move ##

        action = self.get_random_move()

        ## simulate game within game ##

        # pick agents
        pl1 = PlayerLoc("agent_random", "Agent")
        pl2 = PlayerLoc("agent_random", "Agent")

        # convert agents to players
        player1: Player = AgentProxyPlayer("sim_p1", self._color, pl1, None, None)
        player2: Player = AgentProxyPlayer("sim_p2", self.opponent, pl2, None, None)

        # add subprocesses for players
        player1._agent = RemoteProcessClassClient(
            pl1.pkg, pl1.cls, 100000, 100000, 1.0, 180.0, True, self._color
        )
        player2._agent = RemoteProcessClassClient(
            pl2.pkg, pl2.cls, 100000, 100000, 1.0, 180.0, True, self.opponent
        )

        # pick event handlers
        gl: LogStream = LogStream(
            "sim_log", handlers=[self.file_log_handler], ansi=False, unicode=False
        )
        rl: LogStream = LogStream(
            "sim_game",
            handlers=[self.file_commentary_handler],
            ansi=False,
            unicode=False,
        )
        event_handlers = [
            game_event_logger(gl) if gl is not None else None,  # logs game events
            game_commentator(rl),  # commentates game less strictly than logs
            output_board_updates(rl, False, True),  # draws board updates
        ]

        # run simulation
        print("Simulated game: running...")
        sim_winner: Player | None = asyncio.get_event_loop().run_until_complete(
            self.run_game([player1, player2], event_handlers)
        )

        # get colour from sim_game, print result to terminal
        if sim_winner:
            print(f"Simulated game: {sim_winner.color} wins!")

            if sim_winner.color == self._color:
                print(f"Agent [{self.name}] responsible for simulation wins!")
            else:
                print(f"Agent [{self.name}] responsible for simulation loses!")
        else:
            print("Simulated game: draw")

        # TODO:
        # if sim_winner != self._color:
        #     # update heuristics + choose new move

        # write simulated logs to file
        with open(f"sim_logs/sim_log_{self.sim_game_num}.txt", "w") as f:
            for result in self.sim_logs:
                print(result, file=f)

        # write commentary + board updates to file
        with open(f"sim_commentaries/sim_commentary_{self.sim_game_num}.txt", "w") as f:
            for result in self.sim_commentary:
                print(result, file=f)

        # update logs for end of simulation
        self.sim_logs = []
        self.sim_commentary = []
        self.sim_game_num += 1

        # TODO: read and analyse logs to improve agent
        # log files are in sim_logs and sim_commentary
        # log format: * sim_log/t: [time]/t[level]/tmessage
        # (/t = tab)

        # if no valid moves, print message
        if action == PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0)):
            print(f"ERROR: No valid moves for {self._color}")
        return action

    def get_random_move(self) -> PlaceAction:
        coords = valid_coords(self.game_state, self._color)
        coord: Coord = random.choice(coords)
        coords.remove(coord)

        # try all available coords
        while valid_moves(self.game_state, coord) == []:
            if coords:
                coord = random.choice(coords)
                coords.remove(coord)
            else:
                break
        # if no valid moves available
        if valid_moves(self.game_state,  coord) == []:
            return PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        return random.choice(valid_moves(self.game_state, coord))

    def file_log_handler(self, message: str):
        self.sim_logs.append(message)

    def file_commentary_handler(self, message: str):
        self.sim_commentary.append(message)

    def null_event_handler(self, message: str):
        pass

    ## sketchy but working - copied and altered game code ##

    # TODO: rewrite sim game logic to be far simpler + efficient
    # try rewriting without using asyncio

    async def game(
        self,
        p1: Player,
        p2: Player,
    ) -> AsyncGenerator[GameUpdate, None]:
        """
        Run an asynchronous game sequence, yielding updates to the consumer as the
        game progresses. The consumer is responsible for handling these updates
        appropriately (e.g. logging them).
        """
        players: dict[PlayerColor, Player] = {
            player.color: player for player in [p1, p2]
        }
        assert PlayerColor.RED in players
        assert PlayerColor.BLUE in players

        board: Board = copy.deepcopy(self.game_board)
        board._turn_color = self._color

        winner_color: PlayerColor | None = None

        yield GameBegin(board)
        try:
            # Initialise the players
            yield PlayerInitialising(p1)
            async with p1:

                yield PlayerInitialising(p2)
                async with p2:

                    # TODO: might not work if calling agent is RED instead of BLUE
                    # update players to current board state
                    for board_mutation in board._history:
                        for player in players.values():
                            await player.update(player.color, board_mutation.action)

                    # Each loop iteration is a turn.
                    while True:
                        # Get the current player.
                        turn_color: PlayerColor = board._turn_color
                        player: Player = players[board._turn_color]

                        # Get the current player's requested action.
                        turn_id = board.turn_count + 1
                        yield TurnBegin(turn_id, player)
                        action: Action = await player.action()
                        yield TurnEnd(turn_id, player, action)

                        # Update the board state accordingly.
                        board.apply_action(action)
                        yield BoardUpdate(board)

                        # Check if game is over.
                        if board.game_over:
                            winner_color = board.winner_color
                            break

                        # Update both players.
                        await p1.update(turn_color, action)
                        await p2.update(turn_color, action)

        except PlayerException as e:
            error_msg: str = e.args[0]
            if isinstance(e, IllegalActionException):
                error_msg = f"ILLEGAL ACTION: {e.args[0]}"
            else:
                error_msg = f"ERROR: {e.args[0]}"
            error_player: PlayerColor = e.args[1]
            winner_color = error_player.opponent
            yield PlayerError(error_msg)

        except Exception as e:
            # Unhandled error (possibly a referee bug), allow it through
            # while also notifying the consumer.
            yield UnhandledError(str(e))
            raise e

        yield GameEnd(players[winner_color] if winner_color is not None else None)

    async def run_game(
        self, players: list[Player], event_handlers: list[AsyncGenerator | None] = []
    ) -> Player | None:
        """
        Run a game, yielding event handler generators over the game updates.
        Return the winning player (interface) or 'None' if draw.
        """

        async def _update_handlers(
            handlers: list[AsyncGenerator | None], update: GameUpdate | None
        ):
            for handler in handlers:
                try:
                    if handler is not None:
                        await handler.asend(update)
                except StopAsyncIteration:
                    handlers.remove(handler)

        await _update_handlers(event_handlers, None)
        async for update in self.game(*players):  # using altered game()
            await _update_handlers(event_handlers, update)
            match update:
                case GameEnd(winner):
                    return winner

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state.
        """

        self.game_board.apply_action(action)
        self.game_state = self.game_board._state
