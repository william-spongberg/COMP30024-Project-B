# Project Part B

## Agents

- `agent_random` - random agent
- `agent_next` - (experimental) game-within-a-game agent
- `agent_mcts` - MCTS agent

## Running the project

python -m referee -c [agent] [agent]
(e.g python -m referee -c agent_random agent_mcts)

## Testing the project

1. python -m pip install snakeviz

2. python -m cProfile -o test.prof test.py [agent] [agent]
(e.g python -m cProfile -o test.prof test.py agent_random agent_mcts)

3. snakeviz test.prof