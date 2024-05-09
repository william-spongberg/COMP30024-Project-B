# Project Part B

## Agents

- `agent_random` - random agent
- `agent_next` - (experimental) game-within-a-game agent
- `agent_mcts` - MCTS agent

## Running the project

python -m referee -c [agent] [agent]
(e.g python -m referee -c agent_random agent_mcts)

## Running with limits
python -m referee -s 250 -t 180.0 -c agent_random agent_mcts

## Testing the project

1. python -m pip install snakeviz

2. python test.py [agent] [agent]
(e.g python test.py agent_random agent_mcts)

3. snakeviz test.prof