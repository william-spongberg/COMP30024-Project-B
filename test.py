import cProfile
import pstats
import sys

from agent_mcts.program import AgentMCTS
from agent_random.program import AgentRandom
from helpers.sim_board import SimBoard
from helpers.tetrominoes import test_tetronimoes
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


def check_agent_state(agent_blue, game_state):
    if agent_blue.state != game_state._state:
        print(f"{agent_blue.name} state != game_state._state")
        state: SimBoard = SimBoard(init_state=agent_blue.state)
        print(state.render(True))
        for coord in game_state._state:
            if game_state._state[coord] != agent_blue.state[coord]:
                print(
                    "diff at", coord, game_state._state[coord], agent_blue.state[coord]
                )
        sys.exit(1)


def play_game():
    # test_tetronimoes()
    agent_red, agent_blue = get_agents()
    game_state: SimBoard = SimBoard()

    # play game until over
    while not game_state.game_over:
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

        # *debug*
        # check_agent_state(agent_red, game_state)
        # check_agent_state(agent_blue, game_state)

    # print final game state
    print("final game state:")
    print(game_state.render(True))
    print(game_state.turn_color.opponent, " wins")


def play_game_multiple_times():
    for _ in range(10):
        play_game()


#play_game()

cProfile.run("play_game()", "test.prof")
# cProfile.run("play_game_multiple_times()", "test.prof")

p = pstats.Stats("test.prof")
p.strip_dirs().sort_stats("cumulative").print_stats(10)
p.strip_dirs().sort_stats("time").print_stats(10)
