import random

# Given the state, estimates some monotone function on the probability of player eventually winning, if it is currently the attack phase.
def evaluate_attackphase(territories, continents, players, player):
    totalArmies = 0
    myArmies = 0
    continentOccupiers = {}

    playersRemaining = set()
    for k, v in territories.items():
        totalArmies += v.armies
        if v.player == player:
            myArmies += v.armies
        playersRemaining.add(v.player)
        if not continentOccupiers.has_key(v.continent):        
            continentOccupiers[v.continent] = set()
        continentOccupiers[v.continent].add(v.player)

    completeContinents = ((name, continent) for name, continent in continents.items() if len(continentOccupiers[name]) == 1)
    myContinentBonus = 0
    enemyContinentBonus = 0
    for name, continent in completeContinents:
        if player in continentOccupiers[name]:
            myContinentBonus += continent.bonus
        else:
            enemyContinentBonus += continent.bonus

    eliminatePlayersIncentive = 1.0 / len(playersRemaining)
    continentIncentive = myContinentBonus - enemyContinentBonus
    armiesIncentive = myArmies / totalArmies
    return eliminatePlayersIncentive + continentIncentive + armiesIncentive

# Given the state, estimates some monotone function on the probability of player eventually winning, if it is currently the reinforcement phase.
def evaluate_reinforcementphase(territories, continents, players, player):
    return random.random()