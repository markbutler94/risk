import itertools
import random

def selectTerritory(p, state):
    remainingTerritories = state.remainingTerritories
    return random.sample(remainingTerritories,1)[0]

def placeArmies(p, state):
    territories = state.territories
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

def placeReinforcements(p, state):
    territories = state.territories
    ownedTerritories = {k for k, v in territories.items() if v.player == p}
    return random.sample(ownedTerritories,1)[0]

def attackTerritory(p, state):
    territories = state.territories
    attackCapableTerritories = {k for k, v in territories.items() if v.player == p and v.armies > 1 and any(territories[e].player != p for e in v.edges)}
    if len(attackCapableTerritories) > 0:
        attackFrom = random.sample(attackCapableTerritories,1)[0]
        possibleTargets = [e for e in territories[attackFrom].edges if territories[e].player != p]
        attackTo = random.sample(possibleTargets,1)[0]
        attackDice = random.randint(1,min(3,territories[attackFrom].armies - 1))
        return [attackFrom, attackTo, attackDice]
    else:
        return False

def defendTerritory(p, state):
    territories = state.territories
    attackingTerritory, defendingTerritory, attackDice = state.attackData
    defendDice = random.randint(1,min(2,territories[defendingTerritory].armies))
    return defendDice

def occupyTerritory(p, state):
    territories = state.territories
    attackingTerritory, defendingTerritory, _ = state.attackData
    occupyingForce = random.randint(0, territories[attackingTerritory].armies - 1)
    return occupyingForce

def moveArmies(p, state):
    territories = state.territories
    moveCapableTerritories = {k for k, v in territories.items() if v.player == p and v.armies > 1 and any(territories[e].player == p for e in v.edges)}
    if len(moveCapableTerritories) > 0:
        moveFrom = random.sample(moveCapableTerritories, 1)[0]
        possibleTargets = [e for e in territories[moveFrom].edges if territories[e].player == p]
        moveTo = random.sample(possibleTargets, 1)[0]
        moveCount = random.randint(0, territories[moveFrom].armies - 1)
        if moveCount > 0:
            return [moveFrom, moveTo, moveCount]
    return False