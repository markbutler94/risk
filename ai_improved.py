import os
import ast
import math
import itertools
import random
import pickle

# This version selects an adjacent terrotiry to one already selected, if it can.
def selectTerritory(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories,remainingTerritories,players = pickle.load(pickle_file)

    ownedTerritories = set()
    adjTerritories = set()
    for t in territories:
        if territories[t].player == p:
            ownedTerritories.add(t)
            for t2 in territories:
                if t2 in territories[t].edges:
                    adjTerritories.add(t2)
    remainingAdjTerritories = set.intersection(adjTerritories,remainingTerritories)

    if len(remainingAdjTerritories) != 0:
        return random.sample(remainingAdjTerritories,1)[0]
    else:
        return random.sample(remainingTerritories,1)[0]

# Not yet improved.
def placeArmies(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories,remainingTerritories,players = pickle.load(pickle_file)

    ownedTerritories = {k: v for k, v in territories.items() if v.player == p}
    threatenedTerritories = {k: v for k, v in ownedTerritories.items() if not all(territories[e].player == p for e in v.edges)}

    if len(threatenedTerritories) != 0:
        return random.sample(list(threatenedTerritories),1)[0]
    else:
        return random.sample(list(ownedTerritories),1)[0]