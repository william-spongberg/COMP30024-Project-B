import cProfile
import sys

from agent_mcts.program import AgentMCTS
from agent_random.program import AgentRandom
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
    else :
        print("agent not found")
        sys.exit(1)
    
    if sys.argv[2] == "agent_random":
        agent_b = AgentRandom(PlayerColor.BLUE)
    elif sys.argv[2] == "agent_mcts":
        agent_b = AgentMCTS(PlayerColor.BLUE)
    else :
        print("agent not found")
        sys.exit(1)
        
    return agent_a, agent_b

def play_game():
    agent_a, agent_b = get_agents()
    game_state: Board = Board()

    # play game until over
    while not game_state.game_over:        
        if game_state.turn_color == agent_a.color:
            # agent A turn
            move = agent_a.action()
            print(f"agent {agent_a.color} placed ", move)
        else:
            # agent B turn
            move = agent_b.action()
            print(f"agent {agent_b.color} placed ", move)

        # apply move to game state
        game_state.apply_action(move)
        
        # update agents
        agent_a.update(game_state.turn_color, move)
        agent_b.update(game_state.turn_color, move)

    # print final game state
    print("final game state:")
    print(game_state.render(True))
    print(game_state.winner_color, " wins")

# profile the game
play_game()