from graphics import *

points = {t: Circle(Point(*territories[t].pos), 5) for t in territories}
captions = {t: Text(Point(territories[t].pos[0], territories[t].pos[1] + 20), '') for t in territories}
playerNames = {p: Text(Point(70, 530 + (30 * players[p].index)),'') for p in players}
playerTerritories = {p: Text(Point(140, 530 + (30 * players[p].index)),'') for p in players}
playerCards = {p: Text(Point(180, 530 + (30 * players[p].index)),'') for p in players}
playerStrikethroughs = {p: Line(Point(45, 530 + (30 * players[p].index)), Point(195, 530 + (30 * players[p].index))) for p in players}
lines = {(t,edge): Line(Point(*territories[t].pos),Point(*territories[edge].pos)) for t in territories for edge in territories[t].edges}
messageText = Text(Point(500,730),'')
moveText = Text(Point(930,730),'')
lossLabels = {t: Text(Point(territories[t].pos[0],territories[t].pos[1]-20), '') for t in territories}

def init_map():
    imagePath = os.path.join(mapPath, 'map.gif')
    i = Image(Point(500,680/2), imagePath)
    i.draw(win)
    box = Rectangle(Point(30,510),Point(210,520 + (30*len(players))))
    box.setFill('grey')
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
        lossLabels[t].setTextColor('red')
        lossLabels[t].setSize(8)
        captions[t].setSize(8)
        captions[t].draw(win)
    for l in lines:
        lines[l].draw(win)

    infoBox = Rectangle(Point(0,680),Point(1000,780))
    infoBox.setFill('black')
    infoBox.draw(win)
    messageText.setTextColor('yellow')
    messageText.draw(win)
    moveText.setTextColor('white')
    moveText.draw(win)

def update_map(highlightPlayers=[], highlightTerritories=[], highlightDefending=[], attackLoss = '', defendLoss = '', message=''):

    pause = False

    for t in territories:
        p = territories[t].player
        if p != '':
            points[t].setFill(players[p].color)
            
        if t in highlightTerritories:
            points[t].setOutline('yellow')
            points[t].setWidth(2)
        else:
            points[t].setOutline('black')
            points[t].setWidth(1)
            
        captions[t].setText(t + ' (' + str(territories[t].armies) + ')')
 
    for p in players:
        playerTerritories[p].setText(str(players[p].armies))
        playerCards[p].setText(str(len(players[p].cards)))

        if p in highlightPlayers:
            playerNames[p].setStyle('bold')
            playerTerritories[p].setStyle('bold')
            playerCards[p].setStyle('bold')
        else:
            playerNames[p].setStyle('normal')
            playerTerritories[p].setStyle('normal')
            playerCards[p].setStyle('normal')

        if p not in playerList:
            playerStrikethroughs[p].draw(win)
            
            # TODO - now seems to crash

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

    for l in lossLabels:
        lossLabels[l].undraw()
    if attackLoss != '':
        lossLabels[highlightTerritories[0]].setText(attackLoss)
        lossLabels[highlightTerritories[0]].draw(win)
    if defendLoss != '':
        lossLabels[highlightDefending[0]].setText(defendLoss)
        lossLabels[highlightDefending[0]].draw(win)
        if manualPlayback:
            pause = True

    messageText.setText(message)
    moveText.setText('Move: ' + str(move))

    if pause:
        win.getMouse()
