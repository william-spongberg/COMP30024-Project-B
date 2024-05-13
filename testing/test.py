import cProfile
import pstats
import sys
from timeit import default_timer as timer

from agent_mcts.program import AgentMCTS
from agent_random.program import AgentRandom
from agent_mcts.helpers.bit_board import BitBoard
from agent_mcts.helpers.sim_board import SimBoard
from agent_mcts.helpers.tetrominoes import test_tetronimoes
from referee.game.board import Board
from referee.game.player import PlayerColor


def get_agents():
    if len(sys.argv) < 3:
        print("Usage: python -m test <agent> <agent>")
        sys.exit(1)

    if sys.argv[1] == "agent_random":
        agent_a = AgentRandom(PlayerColor.RED)
    elif sys.argv[1] == "agent_mcts":
        agent_a = AgentMCTS(PlayerColor.RED)
    else:
        print("agent not found")
        sys.exit(1)

    if sys.argv[2] == "agent_random":
        agent_b = AgentRandom(PlayerColor.BLUE)
    elif sys.argv[2] == "agent_mcts":
        agent_b = AgentMCTS(PlayerColor.BLUE)
    else:
        print("agent not found")
        sys.exit(1)

    return agent_a, agent_b


def check_agent_state(agent, game_state):
    if agent.state != game_state._state:
        print(f"{agent.name} state != game_state._state")
        state: Board = Board(initial_state=agent.state)
        print(state.render(True))
        for coord in game_state._state:
            if game_state._state[coord] != agent.state[coord]:
                print(
                    "diff at", coord, game_state._state[coord], agent.state[coord]
                )
        sys.exit(1)


def play_game(depth=1000) -> float:
    # test_tetronimoes()
    agent_red, agent_blue = get_agents()
    game_state: Board = Board()
    start_time = timer()
    steps = 0

    # play game until over
    while not game_state.game_over and steps < depth:
        if game_state.turn_color == agent_red.color:
            # agent A turn
            move = agent_red.action()
            # print(f"{agent_red.name} placed", move)
            # print(game_state.render(True))
        else:
            # agent B turn
            move = agent_blue.action()
            # print(f"{agent_blue.name} placed", move)
            # print(game_state.render(True))

        # apply move to game state
        game_state.apply_action(move)
        # print(game_state.render(True))

        # update agents
        agent_red.update(game_state.turn_color, move)
        agent_blue.update(game_state.turn_color, move)
        
        # update step count
        steps += 1

        # *debug*
        # check_agent_state(agent_red, game_state)
        # check_agent_state(agent_blue, game_state)
    
    if game_state.game_over:
        # print final game state
        print("final game state:")
        print(game_state.render(True))
        print(game_state.winner_color, " wins")
    elif steps >= depth:
        print("final game state:")
        print(game_state.render(True))
        if game_state._player_token_count(PlayerColor.RED) > game_state._player_token_count(PlayerColor.BLUE):
            winner = PlayerColor.RED
        elif game_state._player_token_count(PlayerColor.RED) == game_state._player_token_count(PlayerColor.BLUE):
            winner = None
        else:
            winner = PlayerColor.BLUE
        print("blue tokens: ", game_state._player_token_count(PlayerColor.BLUE))
        print("red tokens: ", game_state._player_token_count(PlayerColor.RED))
        print(winner, " wins")
    
    return timer() - start_time


def play_game_multiple_times(num_games=1000, depth=1000):
    total_time = 0
    for _ in range(num_games):
        total_time += play_game(depth=depth)
    print("\n\ntotal time:", total_time)
    print("num games:", num_games)
    if (depth != 1000):
        print("to depth:", depth)
    else:
        print("to depth: unlimited")
    print("average time:", total_time / num_games)
    print("games per second:", num_games / total_time)


#play_game()
play_game_multiple_times(num_games=1000, depth=8)

# cProfile.run("play_game()", "test.prof")
# cProfile.run("play_game_multiple_times(num_games=1000, depth=8)", "test.prof")

# p = pstats.Stats("test.prof")
# p.strip_dirs().sort_stats("cumulative").print_stats(10)
# p.strip_dirs().sort_stats("time").print_stats(10)
