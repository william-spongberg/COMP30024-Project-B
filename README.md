# COMP30024 Artificial Intelligence, Semester 1 2024

## Project Part B: Game Playing Agent

### Agents

- `agent_random` - random agent
- `agent_experimental` - experimental game-within-a-game agent
- `agent` - MCTS agent

### Running the project

python -m referee -c [agent] [agent]

- (e.g python -m referee -c agent_random agent)

#### Running with limits

python -m referee -s 250 -t 180.0 -c [agent] [agent]

- (e.g python -m referee -s 250 -t 180.0 -c agent_random agent)

### Testing the project

1. python -m pip install snakeviz

2. python test.py [agent] [agent]
   - (e.g python test.py agent_random agent)

3. snakeviz test.prof
