import os
import ast
import math
import itertools
import random
import pickle
import operator

import ai_basic

# This version selects an adjacent terrotiry to one already selected, if it can.
def selectTerritory(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, players, deck, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)

    remainingTerritories = {k for k, v in territories.items() if v.player == ''}
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

# This version prioritises reinforcing threatened territories.
def placeArmies(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, players, deck, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)

    ownedTerritories = {k: v for k, v in territories.items() if v.player == p}
    threatenedTerritories = {k: v for k, v in ownedTerritories.items() if not all(territories[e].player == p for e in v.edges)}

    if len(threatenedTerritories) != 0:
        return random.sample(list(threatenedTerritories),1)[0]
    else:
        return random.sample(list(ownedTerritories),1)[0]

def cardSets(playerCards):
    return ai_basic.cardSets(playerCards)

# Not changed yet
def redeemCards(p):
    return ai_basic.redeemCards(p)

# This version prioritises reinforcing threatened territories.
def placeReinforcements(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, players, deck, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)
    
    ownedTerritories = {k: v for k, v in territories.items() if v.player == p}
    threatenedTerritories = {k: v for k, v in ownedTerritories.items() if not all(territories[e].player == p for e in v.edges)}

    if len(threatenedTerritories) != 0:
        return random.sample(list(threatenedTerritories),1)[0]
    else:
        return random.sample(list(ownedTerritories),1)[0]

# Prioritises the continent with highest (but not complete) ownership. Doesn't always attack.
def attackTerritory(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, players, deck, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)

    continentOwnership = {}
    continentTarget = False
    for c in continents:
        continentTerritoriesOwned = len([t for t in territories if territories[t].continent == c and territories[t].player == p])
        continentTerritoriesTotal = len([t for t in territories if territories[t].continent == c])
        continentOwnership[c] = continentTerritoriesOwned / continentTerritoriesTotal
    sortedContinentOwnership = sorted(continentOwnership.items(), key=operator.itemgetter(1), reverse = True)
    for (k,v) in sortedContinentOwnership:
        if v < 1:
            continentTarget = k
            break

    attackCapableTerritories = {k for k, v in territories.items() if v.player == p and v.armies > 1 and any(territories[e].player != p for e in v.edges)}
    if len(attackCapableTerritories) > 0:
        attackFrom = random.sample(attackCapableTerritories,1)[0]
        possibleTargets = [e for e in territories[attackFrom].edges if territories[e].player != p]
        attackTo = random.sample(possibleTargets,1)[0]
        attackDice = random.randint(1,min(3,territories[attackFrom].armies - 1))
        return [attackFrom, attackTo, attackDice]
    else:
        return False

# This version always defends with two armies if it can.
def defendTerritory(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, players, deck, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)
    with open("attackdata.p", 'rb') as pickle_file:
        attackingTerritory, defendingTerritory, attackDice = pickle.load(pickle_file)
        
    defendDice = max(1,min(2,territories[defendingTerritory].armies))
    return defendDice