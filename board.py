class board():
            

    
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
            item.setRookTileNeighbors()
            
    def updateTiles(self, aScreenBoard):
        for row in aScreenBoard:
            for tile in row:
                self.columns[tile.pos[0]].setTile(tile, tile.pos[1])
        
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
    
    def setTile(self, aTile, aPos):
        for i in range(8):
            self.tiles[aPos].rect = aTile
        
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

    def setRookTileNeighbors(self):
        for i in range(self.height):
            rightNeighbor = self.neighbors[1].getTile(i)
            leftNeighbor = self.neighbors[0].getTile(i)
            rrightNeighbor = rightNeighbor.getNeighbor(0)
            lleftNeighbor = leftNeighbor.getNeighbor(4)
            uupNeighbor = self.tiles[i].neighbors[2].getNeighbor(2)
            ddownNeighbor = self.tiles[i].neighbors[6].getNeighbor(6)
            self.tiles[i].setRookNeighbor(0, rrightNeighbor.getNeighbor(2))
            self.tiles[i].setRookNeighbor(1, uupNeighbor.getNeighbor(0))
            self.tiles[i].setRookNeighbor(2, uupNeighbor.getNeighbor(4))
            self.tiles[i].setRookNeighbor(3, lleftNeighbor.getNeighbor(2))
            self.tiles[i].setRookNeighbor(4, lleftNeighbor.getNeighbor(6))
            self.tiles[i].setRookNeighbor(5, ddownNeighbor.getNeighbor(4))
            self.tiles[i].setRookNeighbor(6, ddownNeighbor.getNeighbor(0))            
            self.tiles[i].setRookNeighbor(7, rrightNeighbor.getNeighbor(6))

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
    
    def getRookNeighbor(self, i):
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
    
    def getPlayer(self):
        
        if self.isEmpty():
            return "null"
        return self.piece.player
    
    def hasMoved(self):
        if self.isEmpty():
            return True
        else:
            return self.piece.getHasMoved()

    def __init__(self, i, j):
        self.piece = "EMPTY"
        self.neighbors = []
        self.rookNeighbors = []
        self.rect = ""
        self.x = i
        self.y = j
        for _ in range(8):
            self.neighbors.append(nullTile.getSingleInstance())
            self.rookNeighbors.append(nullTile.getSingleInstance())

    def collidepoint(self, aPos):
        return self.rect.collidepoint(aPos)

    def getPos(self):
        return (self.x, self.y)
    
    def getColor(self):
        piece = self.getPiece()
        if piece == "EMPTY":
            return "NULL"
        return piece.getColor()
    
    def slide(self, dir, i):
        if i == 0:
            return self
        if not self.isEmpty():
            return False
        return self.getNeighbor(dir).slide(dir, i - 1)
    
    def setNeighbor(self, i, aTile):
        self.neighbors[i] = aTile

    def setRookNeighbor(self, i, aTile):
        self.rookNeighbors[i] = aTile

    def getNeighbor(self, i):
        return self.neighbors[i]
    
    def getRookNeighbor(self, i):
        return self.rookNeighbors[i]
    
    def getPiece(self):
        return self.piece
    
    def setPiece(self, aPiece):
        self.piece = aPiece