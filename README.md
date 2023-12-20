WUMPUS
======
The goal is to develop an AI capable of solving the Wumpus problem.

The agent is blindless, he only perceive its environment with smell.

The Wumpus and pits are detected from an Euclidian distance of 1, gold from 0.

The agent must avoid pits and the Wumpus, grab the gold and get out of the cave.

Bonus points for him if he manage to kill the Wumpus before escaping.


The agent explore the map carefully and takes risks only if it's his only option, privileging smaller risks.

# Exercice: Rational Agent

    python3 wumpus.py -a RationalAgent -w 12 -g 1
    # (_with a 12x12 world with random seed 1)
