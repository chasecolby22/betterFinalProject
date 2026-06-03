class board():
            

    def print(self):
        print()
        for i in range(self.height):
            print("|", end="")
            for j in range(self.width):
                
                item = self.getTile(j, self.height-1 - i)
                value = ""
                color = 30
                if not item.isEmpty():
                    value = item.piece.name()
                    if item.getColor() == "white":
                        color = 34
                    else:
                        color = 31
                       
                while len(value) < 6:
                    value += " "
                print("\033[" + str(color) + "m" + value+ "\033[0m", "|", end="")
            value = ""
            while len(value) < self.width * 8 + 1:
                value += "-"
            print()
            print(value)

    def __init__(self, width, height):
        self.columns = []
        self.tiles = False
        self.height = height
        for i in range(width):
            self.columns.append(column(i, height))

        for i in range(width):
            leftNeighbor = nullColumn.getSingleInstance()
            rightNeighbor = nullColumn.getSingleInstance()
            if i != 0:
                leftNeighbor = self.columns[i-1]
            if i != width - 1:
                rightNeighbor = self.columns[i+1]
            self.columns[i].setNeighbors(leftNeighbor, rightNeighbor)
            
        for item in self.columns:
            item.setTileNeighbors()
        for item in self.columns:
            item.setKnightTileNeighbors()
        
    def setPiece(self, aPiece):
        aPos = aPiece.getPos()
        self.getTile(aPos[0], aPos[1]).setPiece(aPiece)
    
    def getTile(self, col, row):
        return self.columns[col].getTile(row)
    
    def getTiles(self):
        if not self.tiles:
            self.tiles = []
            for col in self.columns:
                for tile in col.tiles:
                    self.tiles.append(tile) 
        return self.tiles

class nullColumn():
    singleInstance = ""
    
    @classmethod
    def getSingleInstance(cls):
        if cls.singleInstance == "":
            cls.singleInstance = cls()
        return cls.singleInstance
    
    def getTile(self, i):
        return nullTile.getSingleInstance()

class column():
        
    def __init__(self, i, height):
        self.tiles = []
        self.neighbors = []
        self.height = height
        for j in range(height):
            self.tiles.append(tile(i, j))
        for _ in range(2):
            self.neighbors.append(None)
        for i in range(height):
            if i != 0:
                self.tiles[i].setNeighbor(6, self.tiles[i-1])
            if i != height-1:
                self.tiles[i].setNeighbor(2, self.tiles[i+1])

    def setNeighbors(self, left, right):
        self.neighbors[0] = left
        self.neighbors[1] = right

    def setTileNeighbors(self):
        for i in range(self.height):
            rightNeighbor = self.neighbors[1].getTile(i)
            leftNeighbor = self.neighbors[0].getTile(i)

            self.tiles[i].setNeighbor(0, rightNeighbor)
            self.tiles[i].setNeighbor(1, rightNeighbor.getNeighbor(2))
            self.tiles[i].setNeighbor(7, rightNeighbor.getNeighbor(6))
            
            self.tiles[i].setNeighbor(4, leftNeighbor)
            self.tiles[i].setNeighbor(3, leftNeighbor.getNeighbor(2))
            self.tiles[i].setNeighbor(5, leftNeighbor.getNeighbor(6))

    def setKnightNeighbors(self, i, aListOfNeighbors):
        for j in range(8):
            self.tiles[i].setKnightNeighbor(j, aListOfNeighbors[j])

    def setKnightTileNeighbors(self):
        for i in range(self.height):
            rightNeighbor = self.neighbors[1].getTile(i)
            leftNeighbor = self.neighbors[0].getTile(i)
            rrightNeighbor = rightNeighbor.getNeighbor(0)
            lleftNeighbor = leftNeighbor.getNeighbor(4)
            uupNeighbor = self.tiles[i].neighbors[2].getNeighbor(2)
            ddownNeighbor = self.tiles[i].neighbors[6].getNeighbor(6)
            knightNeighbors = []
            knightNeighbors.append(rrightNeighbor.getNeighbor(2))
            knightNeighbors.append(uupNeighbor.getNeighbor(0))
            knightNeighbors.append(uupNeighbor.getNeighbor(4))
            knightNeighbors.append(lleftNeighbor.getNeighbor(2))
            knightNeighbors.append(lleftNeighbor.getNeighbor(6))
            knightNeighbors.append(ddownNeighbor.getNeighbor(4))
            knightNeighbors.append(ddownNeighbor.getNeighbor(0))
            knightNeighbors.append(rrightNeighbor.getNeighbor(6))
            self.setKnightNeighbors(i, knightNeighbors)

    def getTile(self, i):
        return self.tiles[i]

class nullTile():
    singleInstance = ""
    
    @classmethod
    def getSingleInstance(cls):
        if cls.singleInstance == "":
            cls.singleInstance = cls()
        return cls.singleInstance
    
    def getNeighbor(self, i):
        return self
    
    def getKnightNeighbor(self, i):
        return self
    
    def slide(self, dir, i):
        return False

    def hasMoved(self):
        return True
    
    def isNullTile(self):
        return True
    
class tile():
    def empty(self):
        self.piece = "EMPTY"

    def isNullTile(self):
        return False

    def isEmpty(self):
        return self.piece == "EMPTY"
    
    def hasMoved(self):
        if self.isEmpty():
            return True
        
        return self.piece.getHasMoved()

    def __init__(self, i, j):
        self.piece = "EMPTY"
        self.neighbors = []
        self.knightNeighbors = []
        self.different = False
        self.circleColor = None
        self.border = "black"
        self.bwidth = 2
        self.x = i
        self.y = j
        for _ in range(8):
            self.neighbors.append(nullTile.getSingleInstance())
            self.knightNeighbors.append(nullTile.getSingleInstance())

    def highlight(self, aColor):
        self.border = aColor
        self.different = True
        self.bwidth = 3

    def reset(self):
        self.border = "black"
        self.bwidth = 2
        self.different = False


    def getPos(self):
        return (self.x, self.y)
    
    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def isSame(self, aPiece):
        return self.piece == aPiece

    def matches(self, aColor):
        if self.isEmpty():
            return False
        return self.getColor() == aColor

    def getColor(self):
       
        if self.isEmpty():
            return "NULL"
        return self.piece.getColor()
    
    def slide(self, dir, i):
        if i == 0:
            return self
        if not self.isEmpty():
            return False
        return self.getNeighbor(dir).slide(dir, i - 1)
    
    def setNeighbor(self, i, aTile):
        self.neighbors[i] = aTile

    def setKnightNeighbor(self, i, aTile):
        self.knightNeighbors[i] = aTile

    def getNeighbor(self, i):
        return self.neighbors[i]
    
    def getKnightNeighbor(self, i):
        return self.knightNeighbors[i]
    
    def getPiece(self):
        return self.piece
    
    def setPiece(self, aPiece):
        self.piece = aPiece