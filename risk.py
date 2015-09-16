#rewrite default values (eg Highlights) - THEY WILL NOT WORK
# SEE THIS: http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html#other-languages-have-variables
# Use more listcomps?

import os
import ast
import math
import itertools
import random
import time
import logging
from graphics import *

open("moves.log","w").close()

logging.basicConfig(filename = os.path.join(os.path.dirname(__file__), "moves.log"),level=logging.INFO)

#CLASSES

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
    def __init__(self,color):
        self.armies = 35
        self.index = 0
        self.color = color
        self.cards = []

class Card:
    def __init__(self,type):
        self.type = type

#LOADING DATA

#territories
with open("territories.txt") as f:
    content = f.readlines()
    
territories = {} 

for line in content:
    lst = ast.literal_eval(line)
    territories[lst[0]] = Territory(lst[1],lst[2],lst[3])

#continents
with open("continents.txt") as f:
    content = f.readlines()

continents = {}

for line in content:
    lst = ast.literal_eval(line)
    continents[lst[0]] = Continent(lst[1])

#players
with open("players.txt") as f:
    content = f.readlines()

players = {}

for line in content:
    lst = ast.literal_eval(line)
    players[lst[0]] = Player(lst[1])
    
#randomise order
playerList = list(players)
random.shuffle(playerList)
for i in range(0,len(playerList)):
    players[playerList[i]].index = i

#deck
with open("cards.txt") as f:
    content = f.readlines()
    
deck = []
    
for line in content:
    lst = ast.literal_eval(line)
    for i in range(int(lst[1])):
        deck.append(Card(lst[0]))
        
#randomise order
random.shuffle(deck)

#USEFUL FUNCTIONS
    
def adjacentTerritories(user_tname):
    for t in territories[user_tname].edges:
        print(">", t)

def continentTerritories(user_cname):
    for t in territories:
        if territories[t].continent == user_cname:
            print(">", t)

def territoryInfo(user_tname):
    print("Continent:", territories[user_tname].continent)
    print("Adjacent to:")
    adjacentTerritories(user_tname)

def cardSets(playerCards):
    cardTriples = itertools.combinations(playerCards,3)
    cardSets = []
    for cardTriple in cardTriples:
        if cardTriple[0].type == cardTriple[1].type and cardTriple[0].type == cardTriple[2].type:
            cardSets.append(cardTriple)
        if cardTriple[0].type != cardTriple[1].type and cardTriple[0].type != cardTriple[2].type and cardTriple[1].type != cardTriple[2].type:
            cardSets.append(cardTriple)
    return cardSets

#DRAWING FUNCTIONS

#win = GraphWin("RISK", 1000, 680)

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

def updateMap(highlightPlayers=[],highlightTerritories=[],highlightDefending=[],pause=0):
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
    
    if pause == -1:
        win.getMouse()
    elif pause > 0:
        time.sleep(pause)

#GAME SETUP

def selectTerritoriesRandom():
    remainingTerritories = set()
    for t in territories:
        remainingTerritories.add(t)
    while len(remainingTerritories) > 0:
        for p in playerList:
            t = random.sample(remainingTerritories,1)[0]
            territories[t].player = p
            players[p].armies -= 1
            territories[t].armies += 1
            remainingTerritories.remove(t)
            logging.info(p + " gets " + t)

def placeArmiesRandom():
    while any(players[p].armies > 0 for p in players):
        for p in playerList:
            if players[p].armies > 0:
                ownedTerritories = set()
                for t in territories:
                    if territories[t].player == p:
                        ownedTerritories.add(t)
                t = random.sample(ownedTerritories,1)[0]
                territories[t].armies += 1
                players[p].armies -= 1
                logging.info(p + " fortifies " + t + " (" + str(territories[t].armies) + ") ")

logging.info("GAME STARTED")
selectTerritoriesRandom()
placeArmiesRandom()

#PLAYER TACTICS

def placeReinforcements(p):     #random
    updatedTerritories = set()  
    for i in range(1,players[p].armies+1):
        t = random.sample(ownedTerritories,1)[0]
        #updateMap([p],[t],[],0)
        territories[t].armies += 1
        players[p].armies -= 1
        updatedTerritories.add(t)
        logging.info(p + " fortifies " + t + " (" + str(territories[t].armies) + ")")
    #updateMap([p],updatedTerritories,[],0)

def attackTerritories(p):       #random
    logging.info(p + " is attacking")  
    canAttackTerritories = set()
    for t in ownedTerritories:
        if territories[t].armies > 1 and any(territories[edge].player != p for edge in territories[t].edges):
            canAttackTerritories.add(t)
    while len(canAttackTerritories) > 0:                    # If we have a territory we can attack from
        if random.random() < 0.9:                          # Chance of attacking
            logging.info(p + " can attack from: " + str(canAttackTerritories))
            t = random.sample(canAttackTerritories,1)[0]    # Choose one territory to attack from, t
            possibleTargets = set()                         # Generate set of targets which can be attacked from t
            for edge in territories[t].edges:
                if territories[edge].player!= p:
                    possibleTargets.add(edge)
            logging.info("> Chosen: " + t)
            logging.info("Possible targets: " + str(possibleTargets))
            tDefend = random.sample(possibleTargets,1)[0]  # Choose attack target, tDefend
            logging.info("> Chosen: " + tDefend)
            diceAttack = random.randint(1,min(3,territories[t].armies - 1))     # Choose number of dice
            diceDefend = min(defendTerritory(),territories[tDefend].armies)
            diceRollsAttack = []
            for i in range(diceAttack):
                diceRollsAttack.append(random.randint(1,6))
            diceRollsDefend = []
            for i in range(diceDefend):
                diceRollsDefend.append(random.randint(1,6))
            diceRollsAttack.sort(reverse = True)
            diceRollsDefend.sort(reverse = True)
            logging.info("Dice rolls: A" + str(diceRollsAttack) + "; D" + str(diceRollsDefend))
            lossesAttack = 0
            lossesDefend = 0
            compares = min(diceAttack,diceDefend)           # Number of dice to compare
            for i in range(compares):
                if diceRollsAttack[i] > diceRollsDefend[i]:
                    lossesDefend += 1
                else:
                    lossesAttack += 1
            logging.info("Losses: A" + str(lossesAttack) + "; D" + str(lossesDefend))
                    
            #updateMap([p],[t],[tDefend],0)
            
            territories[t].armies -= lossesAttack
            territories[tDefend].armies -= lossesDefend
            
            if territories[tDefend].armies == 0:
                occupyingArmies = diceAttack
                #(add potential to move more...)
                territories[tDefend].armies += occupyingArmies
                territories[tDefend].player = p
                territories[t].armies -= occupyingArmies
                logging.info(p + " has occupied " + tDefend)
            
            #updateMap([p],[t],[tDefend],0)            
            
            canAttackTerritories = set()
            for t in ownedTerritories:
                if territories[t].armies > 1 and any(territories[edge].player != p for edge in territories[t].edges):
                    canAttackTerritories.add(t)
            
        else:  
            # If we have decided not to attack
            logging.info(p + " has decided to cease attacking")
            break
            
def defendTerritory():          #random
    if random.getrandbits(1) == 1:
        return 1
    else:
        return 2

#MAIN LOOP

#initMap()
move = 0

while len(playerList) > 1 and move < 10:
    print("Move:", str(move))
    logging.info("Move: " + str(move))
    for p in playerList:
        #reinforcements
        reinforcements = 0
        
        ownedTerritories = set()
        for t in territories:
            if territories[t].player == p:
                ownedTerritories.add(t)
        ownedTerritoriesCount = len(ownedTerritories)
        
        reinforcements += max(3,math.floor(len(ownedTerritories) / 3))
        
        for c in continents:
            if all((not(territories[t].continent == c) or territories[t].player == p) for t in territories):
                reinforcements += continents[c].bonus
        players[p].armies += reinforcements
        logging.info(p + " receives " + str(reinforcements) + " armies")

        print(list(cardSet[i].type for i in range(3) for cardSet in cardSets(players[p].cards)))
        print(str(len(cardSets(players[p].cards))))

        if len(players[p].cards) > 4:
            #must redeem

        #placing armies (randomly)
        placeReinforcements(p)

        #attacking
        attackTerritories(p)

        #see if any territories have been occupied (will use a bool flag eventually - this is a temporary measure)
        ownedTerritories = set()
        for t in territories:
            if territories[t].player == p:
                ownedTerritories.add(t)
                
        if len(ownedTerritories) > ownedTerritoriesCount:
            if len(deck) > 0:
                players[p].cards.append(deck.pop(0))
                print(p + " gets  a card: " + players[p].cards[-1].type)

        #fortifying

        #wiping out
        for pEnemy in playerList:
            if not(any(territories[t].player == pEnemy for t in territories)):
                logging.info(p + " has ELIMINATED " + pEnemy + " on move " + str(move))
                playerList.remove(pEnemy)
                
        if len(playerList) == 1:
            logging.info(p + " WINS on move " + str(move))

    #updateMap([],[],[],0)
    move += 1

#EXIT

#updateMap()
#win.close()
