import os
import ast
import shutil
import argparse
import logging

import math
import operator
import itertools
import random
import time

import copy
import pickle

import ai_basic
import ai_improved

import map_display




# ARGUMENT PARSING

riskPath = os.path.dirname('__file__')

argparser = argparse.ArgumentParser(description='Play RISK')
argparser.add_argument(
    '--nodisplay',
    dest='displayMap',
    action='store_const',
    const=False,
    default=True,
    help='Run without UI map animation.'
)
argparser.add_argument(
    '--log',
    dest='logPath',
    default=os.path.join(riskPath, 'logs'),
    help='Specify a folder path to log moves to.'
)
argparser.add_argument(
    '--logging-level',
    dest='loggingLevel',
    default=1,
    help=('0: No logging. ' + 
    '1: moves.log only. ' +
    '2: moves.log and gamestate.p every move. ' +
    '3: moves.log and gamestate.p for every line.')
)
argparser.add_argument(
    '--map',
    dest='mapName',
    default='default',
    help='Specify a map to use.'
)
argparser.add_argument(
    '--gamestate',
    dest='loadGamestate',
    default='',
    help='Load a gamestate.p file.'
)
argparser.add_argument(
    '--manual-playback',
    dest='manualPlayback',
    action='store_const',
    const=True,
    default=False,
    help='Run without UI map animation.'
)

args = argparser.parse_args()

displayMap = args.displayMap
manualPlayback = args.manualPlayback

loadGamestate = args.loadGamestate

mapName = args.mapName
mapPath = os.path.join(riskPath, 'custom-maps', mapName)

territoriesPath = os.path.join(mapPath, 'territories.txt')
continentsPath = os.path.join(mapPath, 'continents.txt')

logFolderPath = args.logPath
logFilePath = os.path.join(logFolderPath, 'moves.log')
logGamestatesPath = os.path.join(logFolderPath, 'gamestates')
loggingLevel = args.loggingLevel

if int(loggingLevel) > 0:
    open(logFilePath,'w').close()
    if os.path.exists(logGamestatesPath):
        shutil.rmtree(logGamestatesPath)
    os.makedirs(logGamestatesPath)
    logging.basicConfig(filename=logFilePath,level=logging.INFO)
    
def updateLog(s, startOfMove = False):
    if int(loggingLevel) > 0:
        logging.info(s)
    if int(loggingLevel) > 2 or (int(loggingLevel) > 1 and startOfMove == True):
        gameState(os.path.join(logGamestatesPath, 'gamestate-line-' + str(sum(1 for line in open(logFilePath))) + '.p'))


        
        
# GAME OBJECTS
        
class Territory:
    def __init__(self,edges,continent,pos):
        self.edges = edges
        self.continent = continent
        self.pos = pos
        self.player = ''
        self.armies = 0

class Continent:
    def __init__(self,bonus):
        self.bonus = bonus

class Player:
    def __init__(self,color,ai):
        self.armies = 0
        self.index = 0
        self.color = color
        self.ai = ai
        self.cards = []

class Card:
    def __init__(self,id,type):
        self.id = id
        self.type = type
        self.territory = ''

territories = {} 
continents = {}
players = {}
deck = []
cardBonuses = []

with open(territoriesPath) as f:
    content = f.readlines()
for line in content:
    lst = ast.literal_eval(line)
    territories[lst[0]] = Territory(lst[1],lst[2],lst[3])

with open(continentsPath) as f:
    content = f.readlines()
for line in content:
    lst = ast.literal_eval(line)
    continents[lst[0]] = Continent(lst[1])

with open('players.txt') as f:
    content = f.readlines()
for line in content:
    lst = ast.literal_eval(line)
    players[lst[0]] = Player(lst[1],lst[2])

def playersToReinforcements(numPlayers):
    switcher = {
        3: 35,
        4: 30,
        5: 25,
        6: 20,
    }
    return switcher.get(numPlayers, 20)

for p in players:
    players[p].armies = playersToReinforcements(len(players))

playerList = list(players)
random.shuffle(playerList)
for i in range(0,len(playerList)):
    players[playerList[i]].index = i

with open('cards.txt') as f:
    content = f.readlines()
cardId = 0
for line in content:
    lst = ast.literal_eval(line)
    for i in range(int(lst[1])):
        deck.append(Card(cardId,lst[0]))
        cardId += 1
random.shuffle(deck)

territoryList = list(territories)
random.shuffle(territoryList)
for card in deck:
    if card.type != 'Wildcard':
        card.territory = territoryList.pop()

with open('cardbonuses.txt') as f:
    content = f.read().splitlines()
for line in content:
    cardBonuses.append(int(line))

    
    
    
# AI HELPER FUNCTIONS    
    
def gameState(path = 'gamestate.p', restricted = False):
    if not restricted:
        pickle.dump([territories, continents, players, deck, cardBonuses, playerList, move, currentPlayer, currentPhase],open(path,'wb'))
    else:
        # The restricted version of this function returns only the number of cards each player has, and the length of the remaining deck.
        playersRestricted = copy.deepcopy(players)
        for k, v in playersRestricted:
            v.cards = length(v.cards)
        deckRestricted = length(deck)
        pickle.dump([territories, continents, playersRestricted, deckRestricted, cardBonuses, playerList, move, currentPlayer, currentPhase],open(path,'wb'))
        
def aiCall(p,request):
    gameState(restricted = True)
    return getattr(globals()[players[p].ai],request)(p)


    

# GAME SETUP

win = GraphWin('RISK', 1000, 780)
initMap()

if loadGamestate == '':
    # If starting a new game
    move = 0
    currentPlayer = 'none'
    currentPhase = 'none'

    remainingTerritories = set()
    for t in territories:
        remainingTerritories.add(t)
    
    while any(players[p].armies > 0 for p in players):
        for p in playerList:
            currentplayer = p
            if len(remainingTerritories) > 0:
                currentPhase = 'Select territories'
                t = aiCall(p, 'selectTerritory') # TODO: Check that this string is acceptable at each aiCall
                territories[t].player = p
                players[p].armies -= 1
                territories[t].armies += 1
                remainingTerritories.remove(t)
                updateLog(p + ' gets ' + t)
                updateMap(highlightPlayers=[p], highlightTerritories=[t], message=p + ' gets ' + t)
        
            else:
                currentPhase = 'Fortify territories'
                if players[p].armies > 0:
                    t = aiCall(p, 'placeArmies')
                    territories[t].armies += 1
                    players[p].armies -= 1
                    updateLog(p + ' fortifies ' + t + ' (' + str(territories[t].armies) + ')')
                    updateMap(highlightPlayers=[p], highlightTerritories=[t], message=p + 
                    ' fortifies ' + t + ' (' + str(territories[t].armies) + ')')          
    move = 1
else:               
    # If loading from a gamestate.p file
    with open(loadGamestate, 'rb') as pickle_file:
        territories, continents, players, deck, cardBonuses, playerList, move, currentPlayer, currentPhase = pickle.load(pickle_file)
    updateMap()

        
        
        
        
# MAIN LOOP

# TODO: Sort playback from a gamestate.p file - it should join in the correct part of the main loop

while len(playerList) > 1:

    print('Move:', str(move), ' -- Players:', len(playerList))
    updateLog('Move: ' + str(move),True)
    
    for p in playerList:
        currentPlayer = p
        
        # Reinforcements
        reinforcements = 0
        
        ownedTerritories = {k for k, v in territories.items() if v.player == p}       
        reinforcements += max(3, math.floor(len(ownedTerritories)/3))
        
        for c in continents:
            if all((not(territories[t].continent == c) or territories[t].player == p) for t in territories):
                reinforcements += continents[c].bonus
        players[p].armies += reinforcements
        updateLog(p + ' receives ' + str(reinforcements) + ' armies')
        updateMap(highlightPlayers=[p], message=p + ' receives ' + str(reinforcements) + ' armies')
        
        tradeInBonusReceived = False
        tradeIn = aiCall(p, 'redeemCards')
        
        while tradeIn:
            for card in tradeIn:
                players[p].cards = [c for c in players[p].cards if c.id != card.id]
                # What happens to these cards?
            
            cardBonus = cardBonuses.pop(0)
            cardBonuses.append(cardBonuses[-1] + 5)     # Keep the list of cardBonuses at full length by adding another entry to the end.
            players[p].armies += cardBonus
            updateLog(p + ' receives ' + str(cardBonus) + ' armies by trading a set')         
            updateMap(highlightPlayers=[p], message=p + ' receives ' + str(cardBonus) + ' armies by trading a set')

            for card in tradeIn:
                if not(card.territory == '') and tradeInBonusReceived == False:     # Can only receive the extra bonus once per turn
                    if territories[card.territory].armies == p:
                        players[p].armies += 2
                        updateLog(p + ' receives 2 extra armies on ' + card.territory)
                        tradeInBonusReceived = True

                        if displayMap:
                            updateMap(highlightPlayers=[p], highlightTerritories=[card.territory], message=p + ' receives 2 extra armies on ' + card.territory)
                        
            tradeIn = aiCall(p, 'redeemCards')

        # Reinforcing
        while players[p].armies > 0:
            t = aiCall(p, 'placeReinforcements')
            territories[t].armies += 1
            players[p].armies -= 1
            updateLog(p + ' fortifies ' + t + ' (' + str(territories[t].armies) + ')')
            updateMap(highlightPlayers=[p], highlightTerritories=[t], message=p + ' fortifies ' + t + ' (' + str(territories[t].armies) + ')')

        # Attacking
        capturedTerritory = False
        attackData = aiCall(p, 'attackTerritory')
        while attackData != False:
            attackingTerritory, defendingTerritory, attackDice = attackData

            updateLog(p + ' attacks ' + territories[defendingTerritory].player + '\'s ' + defendingTerritory + 
            ' (' +  str(territories[defendingTerritory].armies) + ') from ' + attackingTerritory + 
            ' (' + str(territories[attackingTerritory].armies) + ')')
            pickle.dump(attackData,open('attackdata.p','wb'))
            defendDice = aiCall(p,'defendTerritory')
            diceRollsAttack = []
            for i in range(attackDice):
                diceRollsAttack.append(random.randint(1,6))
            diceRollsDefend = []
            for i in range(defendDice):
                diceRollsDefend.append(random.randint(1,6))
            diceRollsAttack.sort(reverse = True)
            diceRollsDefend.sort(reverse = True)
            updateLog('Dice rolls: A' + str(diceRollsAttack) + '; D' + str(diceRollsDefend))

            lossesAttacker = 0
            lossesDefender = 0
            for i in range(min(attackDice,defendDice)):
                if diceRollsAttack[i] > diceRollsDefend[i]:
                    lossesDefender += 1
                else:
                    lossesAttacker += 1

            territories[attackingTerritory].armies -= lossesAttacker
            territories[defendingTerritory].armies -= lossesDefender

            updateLog('Losses: A' + str(lossesAttacker) + ' ' + attackingTerritory + 
            ' (' + str(territories[attackingTerritory].armies) + '); D' + str(lossesDefender) + 
            ' ' + defendingTerritory + ' (' +  str(territories[defendingTerritory].armies) + ')')
            updateMap(highlightPlayers=[p], highlightTerritories=[attackingTerritory], highlightDefending=[defendingTerritory], 
            attackLoss = str(lossesAttacker), defendLoss = str(lossesDefender),
            message=p + ' attacks ' + defendingTerritory + ' from ' + attackingTerritory)

            if territories[defendingTerritory].armies == 0:
                territories[defendingTerritory].player = p
                #occupyingArmies = diceAttack       # TODO: add potential to move more with an aiCall
                territories[defendingTerritory].armies += territories[attackingTerritory].armies - 1
                territories[attackingTerritory].armies = 1
                capturedTerritory = True
                updateLog(p + ' has occupied ' + defendingTerritory + '. ' + attackingTerritory +
                '(' + str(territories[attackingTerritory].armies) + '), ' + defendingTerritory + 
                '(' + str(territories[defendingTerritory].armies) + ').')

            updateMap() 

            attackData = aiCall(p, 'attackTerritory')
        
        if capturedTerritory:
            if len(deck) > 0:
                players[p].cards.append(deck.pop(0))

        # TODO: Fortifying

        # Wiping out
        for e in playerList:
            if not(any(territories[t].player == e for t in territories)):
                updateLog(p + ' has eliminated ' + e + ' on move ' + str(move))
                playerList.remove(e)

                for c in players[e].cards:
                    players[p].cards.append(c)
    
        if len(playerList) == 1:
            print(p + ' wins.')
            updateLog(p + ' wins on move ' + str(move))

    move += 1

    updateMap()

    if manualPlayback and not displayMap:       # If manualPlayback and displayMap are both true then we already
        input("Press Enter to continue...")     # pause after each move, so do not need this line.




# EXIT

if displayMap:  
    updateMap()
    win.getMouse()
    win.close()
    
    
    
    
# MAP DISPLAY

def initMap()
    if displayMap:
        map_display.init_map()

def updateMap(highlightPlayers=[], highlightTerritories=[], highlightDefending=[], attackLoss='', defendLoss='', message=''):
    if displayMap:
        map_display.update_map(highlightPlayers, highlightTerritories, highlightDefending, attackLoss, defendLoss, message)