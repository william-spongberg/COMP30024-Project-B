# Project Part B

## Agents

- `agent_random` - random agent
- `agent_next` - (experimental) game-within-a-game agent
- `agent_mcts` - MCTS agent

## Running the project

python -m referee -c [agent] [agent]

e.g python -m referee -c agent_random agent_mcts

## Testing the project

python -m test [agent] [agent]

e.g python -m test agent_random agent_mcts