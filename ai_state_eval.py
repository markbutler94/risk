import pickle
import copy

import ai_basic
from state_evaluators.stub import evaluate_attackphase

# General approach:
#   - Enumerate available choices
#   - For each, find out the actual/estimated resultant probability distribution over game states
#   - Using a provided heuristic state evaluator, get an expected 'value' of each possible choice
#   - Pick the choice which maximises this expected value!
# Performance will depend wholly on how good the state evaluator is at discriminating states

# AI decision implementations

def selectTerritory(p):
    return ai_basic.selectTerritory(p)

def placeArmies(p):
    return ai_basic.placeArmies(p)

def cardSets(playerCards):
    return ai_basic.cardSets(playerCards)

def redeemCards(p):
    return ai_basic.redeemCards(p)

def placeReinforcements(p):
    return ai_basic.placeReinforcements(p)

def attackTerritory(p):
    with open("gamestate.p", 'rb') as pickle_file:
        territories, continents, remainingTerritories, players = pickle.load(pickle_file)

    optimal_seen_value = evaluate_attackphase(territories, continents, players, p)
    optimal_seen_action = False
    
    for (attack_from, attack_to) in getPossibleAttacks(territories, p):
        # For now, always assume using the max available attacking/defending armies
        attack_num = min(3, territories[attack_from].armies - 1)
        defend_num = min(2, territories[attack_to].armies)

        # Get distribution of attack outcomes given the attack number and defend number
        attack_outcome_distribution = getAttackOutcomeDistribution(attack_num, defend_num)

        # Work out the distribution of resulting game states
        territories_outcome_distribution = ((pr, withAttackOutcome(territories, attack_from, attack_to, outcome, p)) for (pr, outcome) in attack_outcome_distribution)

        # Work out the distribution of heuristic value estimates
        value_distribution = ((pr, evaluate_attackphase(territoriesOutcome, continents, players, p)) for (pr, territoriesOutcome) in territories_outcome_distribution)

        expected_value = getExpectedValue(value_distribution)
        if expected_value > optimal_seen_value:
            optimal_seen_value = expected_value
            optimal_seen_action = (attack_from, attack_to, attack_num)

    return optimal_seen_action

def defendTerritory(p):
    return ai_basic.defendTerritory(p)

# Choice-enumeration helpers

def getPossibleAttacks(territories, p):
    return ((t1, t2) for t1, v in territories.items() if v.player == p and v.armies > 1 for t2 in v.edges if territories[t2].player != p)

def getAttackOutcomeDistribution(attack_num, defend_num):
    if defend_num == 1:
        if attack_num == 1:
            yield (21/36, AttackOutcome(1, 0))
            yield (15/36, AttackOutcome(0, 1))
        elif attack_num == 2:
            yield (91/216, AttackOutcome(1, 0))
            yield (125/216, AttackOutcome(0, 1))
        elif attack_num == 3:
            yield (441/1296, AttackOutcome(1, 0))
            yield (855/1296, AttackOutcome(0, 1))
    elif defend_num == 2:
        if attack_num == 1:
            yield (161/216, AttackOutcome(1, 0))
            yield (55/216, AttackOutcome(0, 1))
        elif attack_num == 2:
            yield (581/1296, AttackOutcome(2, 0))
            yield (420/1296, AttackOutcome(1, 1))
            yield (295/1296, AttackOutcome(0, 2))
        elif attack_num == 3:
            yield (2275/7776, AttackOutcome(2, 0))
            yield (2611/7776, AttackOutcome(1, 1))
            yield (2890/7776, AttackOutcome(0, 2))

class AttackOutcome:
    def __init__(self, attackerLosses, defenderLosses):
        self.attackerLosses = attackerLosses
        self.defenderLosses = defenderLosses

# State updator helpers - keep the functions pure

def withAttackOutcome(territories, attack_from, attack_to, attack_outcome, player):
    # Get copies so we can modify without affecting input
    result = copy.copy(territories)
    attacker = copy.copy(territories[attack_from])
    defender = copy.copy(territories[attack_to])

    # Apply the raw battle outcome
    attacker.armies -= attack_outcome.attackerLosses
    defender.armies -= attack_outcome.defenderLosses

    # Apply occupation if applicable
    # This mirrors the current risk.py implementation where the attacker occupies with all possible armies
    if defender.armies == 0:
        defender.player = player
        defender.armies = attacker.armies - 1
        attacker.armies = 1
        # TODO model the benefit of winning a territory (+1 card) and defeating a player (+ their cards)

    result[attack_from] = attacker
    result[attack_to] = defender
    
    return result

# Miscellaneous helpers

def getExpectedValue(value_distribution):
    result = 0
    for (pr, v) in value_distribution:
        result += pr * v
    return result