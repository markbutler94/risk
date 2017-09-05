import os
import ast
import math
import itertools
import random
import time
import logging
import pickle
from graphics import *

import ai_basic
import ai_improved

def gameState():
    pickle.dump([territories,remainingTerritories,players],open("gamestate.p","wb"))

def aiCall(player,request):
    gameState()
    return getattr(globals()[players[player].ai],request)(player)

open("moves.log","w").close()
logging.basicConfig(filename="moves.log",level=logging.INFO)

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
    def __init__(self,type):
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
for line in content:
    lst = ast.literal_eval(line)
    for i in range(int(lst[1])):
        deck.append(Card(lst[0]))
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
playerData = {p: Text(Point(70, 530 + (30 * players[p].index)),"") for p in players}
lines = {(t,edge): Line(Point(*territories[t].pos),Point(*territories[edge].pos)) for t in territories for edge in territories[t].edges}

for k in captions:
    captions[k].setSize(8)
    
def initMap():
    i = Image(Point(500,669/2),os.path.join(os.path.dirname("__file__"), "map.gif"))
    i.draw(win)
    box = Rectangle(Point(20,510),Point(120,520 + (30*len(players))))
    box.setFill('grey')
    box.draw(win)
    for p in players:
        playerData[p].draw(win)
    for p in points:
        points[p].draw(win)
    for l in lines:
        lines[l].draw(win)
    for c in captions:
        captions[c].draw(win)

def updateMap(highlightPlayers=[],highlightTerritories=[],highlightDefending=[]):
    for t in territories:
        points[t].setFill(players[territories[t].player].color)
            
        if t in highlightTerritories:
            points[t].setOutline('yellow')
            points[t].setWidth(2)
        else:
            points[t].setOutline('black')
            points[t].setWidth(1)
            
        captions[t].setText(t + " (" + str(territories[t].armies) + ")")
 
    for p in players:
        playerData[p].setText(p + ": " + str(players[p].armies))
        
        if p in highlightPlayers:
            playerData[p].setTextColor('yellow')
        else:
            playerData[p].setTextColor(players[p].color)

    for l in lines:
        lines[l].setFill('black')
        lines[l].setWidth(1)
        lines[l].setArrow('none')
    if len(highlightDefending) > 0:
        lines[(highlightTerritories[0],highlightDefending[0])].setFill('yellow')
        lines[(highlightTerritories[0],highlightDefending[0])].setWidth(2)
        lines[(highlightDefending[0],highlightTerritories[0])].setFill('yellow')
        lines[(highlightDefending[0],highlightTerritories[0])].setWidth(2)
        lines[(highlightTerritories[0],highlightDefending[0])].setArrow('last')









# GAME SETUP

logging.info("GAME STARTED")

#Select territories
remainingTerritories = set()
for t in territories:
    remainingTerritories.add(t)
while len(remainingTerritories) > 0:
    for p in playerList:
        if len(remainingTerritories) > 0:
            t = aiCall(p,"selectTerritory") # Should probably check that this string is acceptable?
            territories[t].player = p
            players[p].armies -= 1
            territories[t].armies += 1
            remainingTerritories.remove(t)
            logging.info(p + " gets " + t)

#Place armies
while any(players[p].armies > 0 for p in players):
    for p in playerList:
        if players[p].armies > 0:
            t = aiCall(p,"placeArmies") # Should probably check that this string is acceptable?
            territories[t].armies += 1
            players[p].armies -= 1
            logging.info(p + " fortifies " + t + " (" + str(territories[t].armies) + ") ")

win = GraphWin("RISK", 1000, 680)
initMap()

move = 0
setsTradedIn = 0









# MAIN LOOP

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
        
        tradeInBonusReceived = False
        tradeIn = aiCall(p,"redeemCards") # Should probably check that this string is acceptable?
        
        while tradeIn:
            for card in tradeIn:
                players[p].cards.remove(card)
            players[p].armies += cardBonuses[setsTradedIn]
            logging.info(p + " receives " + str(cardBonuses[setsTradedIn]) + " armies by trading a set")         
            
            for card in tradeIn:
                if not(card.territory == "") and tradeInBonusReceived == False:     # Can only receive the extra bonus once per turn
                    if territories[card.territory].armies == p:
                        players[p].armies += 2
                        logging.info(p + " receives 2 extra armies by trading a card with an owned territory (these have been placed on " + card.territory + ")")
                        tradeInBonusReceived = True
                        
            setsTradedIn +=1
            tradeIn = aiCall(p,"redeemCards") # Should probably check that this string is acceptable?

        # Reinforcing
        while players[p].armies > 0:
            t = aiCall(p,"placeReinforcements") # Should probably check that this string is acceptable?
            territories[t].armies += 1
            players[p].armies -= 1
            logging.info(p + " fortifies " + t + " (" + str(territories[t].armies) + ")")

'''         #Attacking
        attackTerritories(p)

        #see if any territories have been occupied (will use a bool flag eventually - this is a temporary measure)
        ownedTerritories = set()
        for t in territories:
            if territories[t].player == p:
                ownedTerritories.add(t)
                
        if len(ownedTerritories) > ownedTerritoriesCount:
            if len(deck) > 0:
                players[p].cards.append(deck.pop(0))

        #fortifying

        #wiping out
        for pEnemy in playerList:
            if not(any(territories[t].player == pEnemy for t in territories)):
                logging.info(p + " has ELIMINATED " + pEnemy + " on move " + str(move))
                playerList.remove(pEnemy)
                
        if len(playerList) == 1:
            logging.info(p + " WINS on move " + str(move)) '''

    move += 1
    
    if displayMap:
        updateMap() 

#EXIT

updateMap()
win.getMouse()
win.close()