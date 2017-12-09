import os
import ast
import math
import itertools
import random
import time
import logging
import pickle
import operator
import argparse
from graphics import *

argparser = argparse.ArgumentParser(description='Play RISK')
argparser.add_argument(
    '--nomap',
    dest='displayMap',
    action='store_const',
    const=False,
    default=True,
    help='Run without UI map animation')
argparser.add_argument(
    '--log',
    dest='logPath',
    default='moves.log',
    help='Specify a file path to log moves to.'
)

args = argparser.parse_args()

displayMap = args.displayMap
logPath = args.logPath

import ai_basic
import ai_improved

open(logPath,"w").close()
logging.basicConfig(filename=logPath,level=logging.INFO)

def gameState():
    pickle.dump([territories, continents, remainingTerritories, players],open("gamestate.p","wb"))

def aiCall(player,request):
    gameState()
    #try:
    return getattr(globals()[players[player].ai],request)(player)
    #except AttributeError:
    #    logging.info("USED BASIC AI FOR PLAYER " + p + " WITH REQUEST " + request)
    #    return getattr(ai_basic,request)(player)
        
class Territory:
    def __init__(self,edges,continent,pos):
        self.edges = edges
        self.continent = continent
        self.pos = pos
        self.player = ""
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
        self.territory = ""

territories = {} 
continents = {}
players = {}
deck = []
cardBonuses = []

with open("territories.txt") as f:
    content = f.readlines()
for line in content:
    lst = ast.literal_eval(line)
    territories[lst[0]] = Territory(lst[1],lst[2],lst[3])

with open("continents.txt") as f:
    content = f.readlines()
for line in content:
    lst = ast.literal_eval(line)
    continents[lst[0]] = Continent(lst[1])

with open("players.txt") as f:
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

with open("cards.txt") as f:
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
    if card.type != "Wildcard":
        card.territory = territoryList.pop()

with open("cardbonuses.txt") as f:
    content = f.read().splitlines()
for line in content:
    cardBonuses.append(int(line))

# Needs to deal with more turns!!!










points = {t: Circle(Point(*territories[t].pos), 5) for t in territories}
captions = {t: Text(Point(territories[t].pos[0], territories[t].pos[1] + 20), "") for t in territories}
playerNames = {p: Text(Point(70, 530 + (30 * players[p].index)),"") for p in players}
playerTerritories = {p: Text(Point(140, 530 + (30 * players[p].index)),"") for p in players}
playerCards = {p: Text(Point(180, 530 + (30 * players[p].index)),"") for p in players}
playerStrikethroughs = {p: Line(Point(45, 530 + (30 * players[p].index)), Point(195, 530 + (30 * players[p].index))) for p in players}
lines = {(t,edge): Line(Point(*territories[t].pos),Point(*territories[edge].pos)) for t in territories for edge in territories[t].edges}
messageText = Text(Point(500,730),"")
moveText = Text(Point(930,730),"")
lossLabels = {t: Text(Point(territories[t].pos[0],territories[t].pos[1]-20), "") for t in territories}
    
def initMap():
    i = Image(Point(500,680/2),os.path.join(os.path.dirname("__file__"), "map.gif"))
    i.draw(win)
    box = Rectangle(Point(30,510),Point(210,520 + (30*len(players))))
    box.setFill("grey")
    box.draw(win)
    for p in players:
        playerNames[p].setText(p)
        playerNames[p].setTextColor(players[p].color)
        playerNames[p].draw(win)
        playerTerritories[p].draw(win)
        playerTerritories[p].setTextColor(players[p].color)
        playerCards[p].draw(win)
        playerCards[p].setTextColor(players[p].color)
        playerStrikethroughs[p].setFill(players[p].color)
    for t in territories:
        points[t].draw(win)
        lossLabels[t].setTextColor("red")
        lossLabels[t].setSize(8)
        captions[t].setSize(8)
        captions[t].draw(win)
    for l in lines:
        lines[l].draw(win)

    infoBox = Rectangle(Point(0,680),Point(1000,780))
    infoBox.setFill("black")
    infoBox.draw(win)
    messageText.setTextColor("yellow")
    messageText.draw(win)
    moveText.setTextColor("white")
    moveText.draw(win)

def updateMap(highlightPlayers=[], highlightTerritories=[], highlightDefending=[], attackLoss = "", defendLoss = "", message=""):

    pause = False

    for t in territories:
        p = territories[t].player
        if p != "":
            points[t].setFill(players[p].color)
            
        if t in highlightTerritories:
            points[t].setOutline("yellow")
            points[t].setWidth(2)
        else:
            points[t].setOutline("black")
            points[t].setWidth(1)
            
        captions[t].setText(t + " (" + str(territories[t].armies) + ")")
 
    for p in players:
        playerTerritories[p].setText(str(players[p].armies))
        playerCards[p].setText(str(len(players[p].cards)))

        if p in highlightPlayers:
            playerNames[p].setStyle("bold")
            playerTerritories[p].setStyle("bold")
            playerCards[p].setStyle("bold")
        else:
            playerNames[p].setStyle("normal")
            playerTerritories[p].setStyle("normal")
            playerCards[p].setStyle("normal")

        if p not in playerList:
            playerStrikethroughs[p].draw(win)

    for l in lines:
        lines[l].setFill("black")
        lines[l].setWidth(1)
        lines[l].setArrow("none")
    if len(highlightDefending) > 0:
        lines[(highlightTerritories[0],highlightDefending[0])].setFill("yellow")
        lines[(highlightTerritories[0],highlightDefending[0])].setWidth(2)
        lines[(highlightDefending[0],highlightTerritories[0])].setFill("yellow")
        lines[(highlightDefending[0],highlightTerritories[0])].setWidth(2)
        lines[(highlightTerritories[0],highlightDefending[0])].setArrow("last")

    for l in lossLabels:
        lossLabels[l].undraw()
    if attackLoss != "":
        lossLabels[highlightTerritories[0]].setText(attackLoss)
        lossLabels[highlightTerritories[0]].draw(win)
    if defendLoss != "":
        lossLabels[highlightDefending[0]].setText(defendLoss)
        lossLabels[highlightDefending[0]].draw(win)
        #pause = True

    messageText.setText(message)
    moveText.setText("Move: " + str(move))

    if pause:
        win.getMouse()







# GAME SETUP

logging.info("GAME STARTED")
move = 0

if displayMap:    
    win = GraphWin("RISK", 1000, 780)
    initMap()

# Select territories
remainingTerritories = set()
for t in territories:
    remainingTerritories.add(t)
while len(remainingTerritories) > 0:
    for p in playerList:
        if len(remainingTerritories) > 0:
            t = aiCall(p, "selectTerritory") # Should probably check that this string is acceptable?
            territories[t].player = p
            players[p].armies -= 1
            territories[t].armies += 1
            remainingTerritories.remove(t)
            logging.info(p + " gets " + t)
            #if displayMap:    
                #updateMap(highlightPlayers=[p], highlightTerritories=[t], message=p + " gets " + t)

# Place armies
while any(players[p].armies > 0 for p in players):
    for p in playerList:
        if players[p].armies > 0:
            t = aiCall(p, "placeArmies") # Should probably check that this string is acceptable?
            territories[t].armies += 1
            players[p].armies -= 1
            logging.info(p + " fortifies " + t + " (" + str(territories[t].armies) + ")")
            #if displayMap:    
                #updateMap(highlightPlayers=[p], highlightTerritories=[t], message=p + " fortifies " + t + " (" + str(territories[t].armies) + ")")











# MAIN LOOP

move = 1
setsTradedIn = 0

while len(playerList) > 1:

    print("Move:", str(move))
    logging.info("Move: " + str(move))
    
    for p in playerList:

        # Calculating reinforcements
        reinforcements = 0
        
        ownedTerritories = {k for k, v in territories.items() if v.player == p}
        ownedTerritoriesCount = len(ownedTerritories)
        
        reinforcements += max(3, math.floor(len(ownedTerritories)/3))
        
        for c in continents:
            if all((not(territories[t].continent == c) or territories[t].player == p) for t in territories):
                reinforcements += continents[c].bonus
        players[p].armies += reinforcements
        logging.info(p + " receives " + str(reinforcements) + " armies")

        if displayMap:
            updateMap(highlightPlayers=[p], message=p + " receives " + str(reinforcements) + " armies")
        
        tradeInBonusReceived = False
        tradeIn = aiCall(p, "redeemCards") # Should probably check that this string is acceptable?
        
        while tradeIn:
            for card in tradeIn:
                players[p].cards = [c for c in players[p].cards if c.id != card.id]

                # What happens to these cards?
            players[p].armies += cardBonuses[setsTradedIn]
            logging.info(p + " receives " + str(cardBonuses[setsTradedIn]) + " armies by trading a set")         
            
            if displayMap:
                updateMap(highlightPlayers=[p], message=p + " receives " + str(cardBonuses[setsTradedIn]) + " armies by trading a set")

            for card in tradeIn:
                if not(card.territory == "") and tradeInBonusReceived == False:     # Can only receive the extra bonus once per turn
                    if territories[card.territory].armies == p:
                        players[p].armies += 2
                        logging.info(p + " receives 2 extra armies on " + card.territory)
                        tradeInBonusReceived = True

                        if displayMap:
                            updateMap(highlightPlayers=[p], highlightTerritories=[card.territory], message=p + " receives 2 extra armies on " + card.territory)
                        
            setsTradedIn +=1
            tradeIn = aiCall(p, "redeemCards") # Should probably check that this string is acceptable?

        # Reinforcing
        while players[p].armies > 0:
            t = aiCall(p, "placeReinforcements") # Should probably check that this string is acceptable?
            territories[t].armies += 1
            players[p].armies -= 1
            logging.info(p + " fortifies " + t + " (" + str(territories[t].armies) + ")")

            if displayMap:
                updateMap(highlightPlayers=[p], highlightTerritories=[t], message=p + " fortifies " + t + " (" + str(territories[t].armies) + ")")

        # Attacking
        capturedTerritory = False
        attackData = aiCall(p, "attackTerritory") # Should probably check that this string is acceptable?
        while attackData != False:
            attackingTerritory, defendingTerritory, attackDice = attackData

            logging.info(p + " attacks " + defendingTerritory + " (" + territories[defendingTerritory].player + ", " + str(territories[defendingTerritory].armies) + ") from " + attackingTerritory + " (" + str(territories[attackingTerritory].armies) + ")")
            pickle.dump(attackData,open("attackdata.p","wb"))
            defendDice = aiCall(p,"defendTerritory") # Should probably check that this string is acceptable?
            diceRollsAttack = []
            for i in range(attackDice):
                diceRollsAttack.append(random.randint(1,6))
            diceRollsDefend = []
            for i in range(defendDice):
                diceRollsDefend.append(random.randint(1,6))
            diceRollsAttack.sort(reverse = True)
            diceRollsDefend.sort(reverse = True)
            logging.info("Dice rolls: A" + str(diceRollsAttack) + "; D" + str(diceRollsDefend))

            lossesAttacker = 0
            lossesDefender = 0
            for i in range(min(attackDice,defendDice)):
                if diceRollsAttack[i] > diceRollsDefend[i]:
                    lossesDefender += 1
                else:
                    lossesAttacker += 1

            territories[attackingTerritory].armies -= lossesAttacker
            territories[defendingTerritory].armies -= lossesDefender

            logging.info("Losses: Attacker " + str(lossesAttacker) + " (" + attackingTerritory + " " + str(territories[attackingTerritory].armies) + "); Defender " + str(lossesDefender) + " (" + defendingTerritory + " " + str(territories[defendingTerritory].armies) + ")")

            if displayMap:
                updateMap(highlightPlayers=[p], highlightTerritories=[attackingTerritory], highlightDefending=[defendingTerritory], 
                          attackLoss = str(lossesAttacker), defendLoss = str(lossesDefender),
                          message=p + " attacks " + defendingTerritory + " from " + attackingTerritory)

            if territories[defendingTerritory].armies == 0:
                territories[defendingTerritory].player = p
                #occupyingArmies = diceAttack                                                               #(add potential to move more with an aiCall...)
                territories[defendingTerritory].armies += territories[attackingTerritory].armies - 1
                territories[attackingTerritory].armies = 1
                capturedTerritory = True
                logging.info(p + " has occupied " + defendingTerritory)

            if displayMap:
                updateMap() 

            attackData = aiCall(p, "attackTerritory") # Should probably check that this string is acceptable?
        
        # Receive card
        if capturedTerritory:
            if len(deck) > 0:
                players[p].cards.append(deck.pop(0))

        # Fortifying


        # Wiping out
        for e in playerList:
            if not(any(territories[t].player == e for t in territories)):
                logging.info(p + " has ELIMINATED " + e + " on move " + str(move))
                playerList.remove(e)

                # CARDS transfer
                               
        if len(playerList) == 1:
            logging.info(p + " WINS on move " + str(move))

    move += 1

    if displayMap:
        updateMap() 

# EXIT

if displayMap:  
    updateMap()
    win.getMouse()
    win.close()