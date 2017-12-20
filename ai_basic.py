import os
import ast
import math
import itertools
import random
import pickle

def selectTerritory(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, playersRestricted, deckRestricted, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)
    
    remainingTerritories = {k for k, v in territories.items() if v.player == ''}
    return random.sample(remainingTerritories,1)[0]

def placeArmies(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, playersRestricted, deckRestricted, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)
    
    ownedTerritories = {k for k, v in territories.items() if v.player == p}
    return random.sample(ownedTerritories,1)[0]

def cardSets(playerCards):
    cardTriples = itertools.combinations(playerCards,3)
    cardSets = []
    for cardTriple in cardTriples:
        if cardTriple[0].type == cardTriple[1].type and cardTriple[0].type == cardTriple[2].type:
            cardSets.append(cardTriple)
        if cardTriple[0].type != cardTriple[1].type and cardTriple[0].type != cardTriple[2].type and cardTriple[1].type != cardTriple[2].type:
            cardSets.append(cardTriple)
    return cardSets

def redeemCards(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, playersRestricted, deckRestricted, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)
        
    if len(players[p].cards) > 4:
        cardSet = random.sample(cardSets(players[p].cards),1)[0]
        return cardSet
    elif len(cardSets(players[p].cards)) > 0:
            if random.getrandbits(1) == 1:
                cardSet = random.sample(cardSets(players[p].cards),1)[0]
                return cardSet
    else:
        return False

def placeReinforcements(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, playersRestricted, deckRestricted, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)
        
    ownedTerritories = {k for k, v in territories.items() if v.player == p}
    return random.sample(ownedTerritories,1)[0]

def attackTerritory(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, playersRestricted, deckRestricted, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)
        
    attackCapableTerritories = {k for k, v in territories.items() if v.player == p and v.armies > 1 and any(territories[e].player != p for e in v.edges)}
    if len(attackCapableTerritories) > 0:
        attackFrom = random.sample(attackCapableTerritories,1)[0]
        possibleTargets = [e for e in territories[attackFrom].edges if territories[e].player != p]
        attackTo = random.sample(possibleTargets,1)[0]
        attackDice = random.randint(1,min(3,territories[attackFrom].armies - 1))
        return [attackFrom, attackTo, attackDice]
    else:
        return False

def defendTerritory(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, playersRestricted, deckRestricted, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)
    with open("attackdata.p", 'rb') as pickle_file:
        attackingTerritory, defendingTerritory, attackDice = pickle.load(pickle_file)
        
    defendDice = random.randint(1,min(2,territories[defendingTerritory].armies))
    return defendDice