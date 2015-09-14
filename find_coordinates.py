# This is a tool for finding coordinates of territories. 
# Load a map here, then click to print the position of the mouse click to the console.

def findCoords():
    win = GraphWin("MAP",1000,669)
    i = Image(Point(500,669/2),"C:\\Users\\Mark\\Google Drive\\Risk\\maps\\mapOLD.gif")
    i.draw(win)

    while 1>0:
        print(win.getMouse().x,win.getMouse().y)
