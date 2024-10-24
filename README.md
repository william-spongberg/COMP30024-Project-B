# Project Part B: Game Playing Agent

*Created for COMP30024 Artificial Intelligence in Semester 1 of 2024 for the University of Melbourne.*

*Authored by William Spongberg and Gaoyongle Zhang*

---

Python program that plays two agents against each other in **Tetress**.

Find details of the assignment [here](/AI_2024_Project_PartB.pdf).

Find rules of the game [here](/AI_2024_Game_Rules.pdf).

Find our report [here](/AI%20-%20Project%202%20Report.pdf).

## Agents

- `agent_random` - random agent
- `agent_experimental` - experimental game-within-a-game agent
- `agent` - MCTS agent

## Running the project

python -m referee -c [agent] [agent]

*e.g. python -m referee -c agent_random agent*

### Running with limits

python -m referee -s 250 -t 180.0 -c [agent] [agent]

*e.g. python -m referee -s 250 -t 180.0 -c agent_random agent*

## Testing the project

1. python -m pip install snakeviz

2. python test.py [agent] [agent]
   - (e.g python test.py agent_random agent)

3. snakeviz test.prof
