def findCoords():
    win = GraphWin("MAP",1000,669)
    i = Image(Point(500,669/2),"C:\\Users\\Mark\\Google Drive\\Risk\\testmap.gif")
    i.draw(win)

    while 1>0:
        print(win.getMouse().x,win.getMouse().y)

