def verifySelectTerritory(state, t):
    if not(t in state.remainingTerritories):
        throw("Territory " + t + " is not available")

def verifyPlaceArmies(state, p, t):
    if not(t in state.territories):
        throw("Territory " + t + " does not exist")
    if state.territories[t].player != p:
        throw("Territory " + t + " does not belong to player " + p)

def verifyPlaceReinforcements(state, p, t):
    if not(t in state.territories):
        throw("Territory " + t + " does not exist")
    if state.territories[t].player != p:
        throw("Territory " + t + " does not belong to player " + p)

def verifyAttackTerritory(state, p):
    if state.attackData:
        attackFrom, attackTo, attackCount = state.attackData
        if not(attackFrom in state.territories):
            throw("Territory " + attackFrom + " (attacker) does not exist")
        if not(attackTo in state.territories):
            throw("Territory " + attackTo + " (defender) does not exist")
        attackingTerritory = state.territories[attackFrom]
        defendingTerritoriy = state.territories[attackTo]
        if attackingTerritory.player != p:
            throw("Territory " + attackFrom + " (attacker) does not belong to attacking player " + p)
        if defendingTerritoriy.player == p:
            throw("Territory " + attackTo + " (defender) already belongs to attacking player " + p)
        if attackCount < 1:
            throw("Cannot attack with fewer armies than 1 (" + str(attackCount) + ")")
        if attackCount > 3:
            throw("Cannot attack with more armies than 3 (" + str(attackCount) + ")")
        if attackCount >= attackingTerritory.armies:
            throw("Cannot attack with " + str(attackCount) + " armies from a territory with only " + str(state.territories[attackFrom].armies))

def verifyDefendTerritory(state, defendCount):
    if state.attackData:
        _, attackTo, attackCount = state.attackData
        if not(attackTo in state.territories):
            throw("Territory " + attackTo + " (defender) does not exist")
        defendingTerritory = state.territories[attackTo]
        if defendCount < 1:
            throw("Cannot defend with fewer armies than 1 (" + str(defendCount) + ")")
        if defendCount > defendingTerritory.armies:
            throw("Cannot defend with more armies (" + str(defendCount) + ") than the territory has (" + str(defendingTerritory.armies) + ")")
        if defendCount > 2:
            throw("Cannot defend with more than 2 armies (" + str(defendCount) + ")")

def verifyOccupyTerritory(state, occupyingForce):
    if state.attackData:
        attackFrom, _, _ = state.attackData
        if not(attackFrom in state.territories):
            throw("Territory " + attackFrom + " (attacker) does not exist")
        attackingTerritory = state.territories[attackFrom]
        if occupyingForce < 0:
            throw("Cannot occupy with negative armies (" + str(occupyingForce) + ")")
        if occupyingForce > attackingTerritory.armies - 1:
            throw("Cannot occupy with " + str(occupyingForce) + " armies from a territory with only " + str(attackingTerritory.armies))

def throw(message):
    raise AssertionError(message)