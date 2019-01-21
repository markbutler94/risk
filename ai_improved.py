import itertools
import random
import operator

# This version selects an adjacent terrotiry to one already selected, if it can.
def selectTerritory(p, state):
    territories = state.territories
    remainingTerritories = state.remainingTerritories

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
def placeArmies(p, state):
    territories = state.territories

    ownedTerritories = {k: v for k, v in territories.items() if v.player == p}
    threatenedTerritories = {k: v for k, v in ownedTerritories.items() if not all(territories[e].player == p for e in v.edges)}

    if len(threatenedTerritories) != 0:
        return random.sample(list(threatenedTerritories),1)[0]
    else:
        return random.sample(list(ownedTerritories),1)[0]

# Not changed yet
def cardSets(playerCards):
    cardTriples = itertools.combinations(playerCards,3)
    cardSets = []
    for cardTriple in cardTriples:
        if cardTriple[0].type == cardTriple[1].type and cardTriple[0].type == cardTriple[2].type:
            cardSets.append(cardTriple)
        if cardTriple[0].type != cardTriple[1].type and cardTriple[0].type != cardTriple[2].type and cardTriple[1].type != cardTriple[2].type:
            cardSets.append(cardTriple)
    return cardSets

# Not changed yet
def redeemCards(p, state):
    players = state.players

    if len(players[p].cards) > 4:
        cardSet = random.sample(cardSets(players[p].cards),1)[0]
        return cardSet
    elif len(cardSets(players[p].cards)) > 0:
            if random.getrandbits(1) == 1:
                cardSet = random.sample(cardSets(players[p].cards),1)[0]
                return cardSet
    else:
        return False

# This version prioritises reinforcing threatened territories.
def placeReinforcements(p, state):
    territories = state.territories
    
    ownedTerritories = {k: v for k, v in territories.items() if v.player == p}
    threatenedTerritories = {k: v for k, v in ownedTerritories.items() if not all(territories[e].player == p for e in v.edges)}

    if len(threatenedTerritories) != 0:
        return random.sample(list(threatenedTerritories),1)[0]
    else:
        return random.sample(list(ownedTerritories),1)[0]

# Prioritises the continent with highest (but not complete) ownership. Doesn't always attack.
def attackTerritory(p, state):
    territories = state.territories
    continents = state.continents

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

# This version always defends with 2 armies if it can.
def defendTerritory(p, state):
    territories = state.territories
    attackData = state.attackData

    attackingTerritory, defendingTerritory, attackDice = attackData
    defendDice = max(1,min(2,territories[defendingTerritory].armies))
    return defendDice