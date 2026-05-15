
import pygame

class dumbPiece(pygame.sprite.Sprite):
    def __init__(self, anX, aY, aPlayer):
        super().__init__()
        self.x = anX
        self.y = aY
        self.coords = ""
        self.color = aPlayer.getColor()
        self.player = aPlayer
        self.myGame = aPlayer.myGame
        self.image = False
        self.move(anX, aY)

    def move(self, anX, aY):
        if not self.image:
            anImage = "./" + self.color + "/" + self.name() + ".png"
            self.image = pygame.image.load(anImage).convert_alpha()
        self.x = anX
        self.y = aY
        self.coords = (100 + (75*anX), 50 + (75*(7-aY)))
        self.rect = self.image.get_rect(topleft = self.coords)
        self.draw()

    def draw(self):
        self.myGame.myScreen.addSprite(self)

class piece(dumbPiece):
    
    def getColor(self):
        return self.color

    def getX(self):
        return self.x

    def getY(self):
        return self.y
    
    def getHasMoved(self):
        return self.hasMoved
    
    def setHasMoved(self, aBool):
        self.hasMoved = aBool
    
    def setCoords(self, anX, aY):
        self.x = anX
        self.y = aY

    def __init__(self, anX, aY, aPlayer):
        super().__init__(anX, aY, aPlayer)
        
        
        self.hasMoved = False
        aTile = self.myGame.getTile(anX, aY)
        self.tile = aTile
        aTile.setPiece(self)
        self.move(anX, aY)

    def move(self, anX, aY):
        super().move(anX, aY)
        self.tile = self.myGame.getTile(anX, aY)

    def setPos(self, aPos):
        self.coords = (aPos[0], aPos[1])
        self.rect = self.image.get_rect(center = self.coords)
    
    def remove(self):
        self.kill()
        self.player.removePiece(self)
        self.tile.empty()

    def getTile(self):
        return self.tile
    
    def cCanMove(self, anX, aY):
        oldX = self.x
        oldY = self.y
        if anX == oldX and oldY == aY:
            return False
        anArray = self.canMove(anX, aY)
        if not anArray:
            return False
        newTile = anArray[0]
        oldPiece = newTile.getPiece()
        oldTile = self.tile
        oldTile.empty()
        
        bad = False
        try: self.myGame.getNonActivePlayer().removePiece(oldPiece)
        except: bad = True
        newTile.setPiece(self)
        self.setCoords(anX, aY)
        if self.myGame.inCheck(self.color):
            anArray = False
        oldTile.setPiece(self)
        if not bad: self.myGame.getNonActivePlayer().addPiece(oldPiece)
        newTile.setPiece(oldPiece)
        self.setCoords(oldX, oldY)
        return anArray
    
    def isValidMove(self, tile):
        if not tile:
            return False
        if not tile.isNullTile() and (tile.isEmpty() or tile.getPlayer() != self.player):
            return True
        return False
        
    def isSuperValidMove(self, aPos):
        return self.cCanMove(aPos[0], aPos[1])
    
    def checkValidity(self, aTile, moves):
        if self.isValidMove(aTile):
            tPos = aTile.getPos()
            if self.isSuperValidMove(tPos):
                moves.append(tPos)
        return moves
        

class dumbKnight(dumbPiece):
    def name(self):
        return "knight"
        
class knight(piece):

    def canMove(self, anX, aY):
        destTile = self.myGame.getTile(anX, aY)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            return False
        for tile in self.tile.rookNeighbors:
            if tile == destTile:
                return default(destTile)
        return False
    
    def findMoves(self):
        moves = []
        for tile in self.tile.rookNeighbors:
            moves = self.checkValidity(tile, moves)
        return moves
    
    def name(self):
        return "knight"
    
class dumbRook(dumbPiece):
    def name(self):
        return "rook"
    
class rook(piece):

    def canMove(self, anX, aY):
        destTile = self.myGame.getTile(anX, aY)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            return False
        for i in range(8):
            if i % 2 == 1:
                continue
            else:
                for j in range(8):
                    if self.tile.getNeighbor(i).slide(i, j) == destTile:
                        return default(destTile)
        return False 
    
    def findMoves(self):
        moves = []
        for i in range(8):
            if i % 2 == 1:
                continue
            else:
                for j in range(8):
                    tile = self.tile.getNeighbor(i).slide(i, j)
                    moves = self.checkValidity(tile, moves)
                    if not tile or not tile.isEmpty():
                        break
                   
        return moves
    
    def name(self):
        return "rook"

class pawn(piece):

    def name(self):
        return "pawn"
    
    def canMove(self, col, row):
        magicNum = 4
        if self.player == self.myGame.player1:
            magicNum = 0
        destTile = self.myGame.getTile(col, row)
        myTile = self.getTile()
        front = myTile.getNeighbor(2+magicNum)
        if destTile == myTile.getNeighbor(1+magicNum) or destTile == myTile.getNeighbor(3+magicNum):
            
            if self.myGame.enPassantTile == destTile:
                return default(destTile)
            
            if destTile.isEmpty() or destTile.getPlayer() == self.player:
                
                return False
            else:
                return default(destTile)
            
        
        elif destTile == front.getNeighbor(2+magicNum):
        
            if self.getHasMoved() or not front.isEmpty() or not destTile.isEmpty():
                return False
            else:
                return [destTile, front, False]
        elif destTile == front:
            if not destTile.isEmpty():
                return False
            else:
                return default(destTile)
        return False
    
    def checkDiag(self, aTile):
        if aTile.isNullTile():
            return False
        if not aTile.isEmpty() and aTile.getPlayer() != self.player:
            return True
        if aTile == self.myGame.enPassantTile:
            return True
        return False
    
    def findMoves(self):
        magicNum = 4
        if self.player == self.myGame.player1:
            magicNum = 0
        myTile = self.getTile()
        front = myTile.getNeighbor(2+magicNum)
        diag1 = myTile.getNeighbor(1+magicNum)
        diag2 = myTile.getNeighbor(3+magicNum)
        moves = []
        
        
        if self.checkDiag(diag1):
            diag1pos = diag1.getPos()
            if self.isSuperValidMove(diag1pos): moves.append(diag1pos)
        if self.checkDiag(diag2): 
            diag2pos = diag2.getPos()
            if self.isSuperValidMove(diag2pos): moves.append(diag2pos)
        if front.isEmpty(): 
            fPos = front.getPos()
            if self.isSuperValidMove(fPos):
                moves.append(fPos)
            if not self.getHasMoved():
                ffront = front.getNeighbor(2+magicNum)
                ffPos = ffront.getPos()
                if ffront.isEmpty():
                    if self.isSuperValidMove(ffPos):
                        moves.append(ffPos)
        return moves
        

        
class dumbBishop(dumbPiece):
    def name(self):
        return "bishop"    

class bishop(piece):
    

    def name(self):
        return "bishop"

    def canMove(self, anX, aY):
        destTile = self.myGame.getTile(anX, aY)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            return False
        for i in range(8):
            if i % 2 == 0:
                continue
            else:
                for j in range(8):
                    if self.tile.getNeighbor(i).slide(i, j) == destTile:
                        return default(destTile)
        return False
    
    def findMoves(self):
        moves = []
        for i in range(8):
            if i % 2 == 0:
                continue
            else:
                for j in range(8):
                    posibileTile = self.tile.getNeighbor(i).slide(i, j)
                    moves = self.checkValidity(posibileTile, moves)
                   
                    if not posibileTile or not posibileTile.isEmpty():
                        break
                    
        return moves


        
class king(piece):

    def name(self):
        return "king"
    
    def canMove(self, anX, aY, ):
        destTile = self.myGame.getTile(anX, aY)
        answer = default(destTile)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            answer = False
        for i in range(8):
            if self.tile.getNeighbor(i) == destTile and answer:
                return answer
        rightCastle = self.tile.getNeighbor(0).getNeighbor(0)
        leftCastle = self.tile.getNeighbor(4).getNeighbor(4)
        if not self.hasMoved and rightCastle == destTile:
            if self.myGame.inCheck(self.color) or rightCastle.getNeighbor(0).hasMoved():
                return False
            if not rightCastle.getNeighbor(4).isEmpty() or not rightCastle.isEmpty():
                return False
            self.setCoords(anX-1, aY)
            if self.myGame.inCheck(self.color):
                self.setCoords(anX-2, aY)
                return False
            self.setCoords(anX, aY)
            if self.myGame.inCheck(self.color):
                self.setCoords(anX-2, aY)
                return False
            self.setCoords(anX-2, aY)
            return [destTile, False, [7]]
        if not self.hasMoved and leftCastle == destTile:
            if self.myGame.inCheck(self.color) or leftCastle.getNeighbor(4).getNeighbor(4).hasMoved():
                return False
            if not leftCastle.getNeighbor(4).isEmpty() or not leftCastle.isEmpty() or not leftCastle.getNeighbor(0).isEmpty():
                return False
            self.setCoords(anX+1, aY)
            if self.myGame.inCheck(self.color):
                self.setCoords(anX+2, aY)
                return False
            self.setCoords(anX, aY)
            if self.myGame.inCheck(self.color):
                self.setCoords(anX+2, aY)
                return False
            self.setCoords(anX+2, aY)
            return [destTile, False, [0]]
        
    def findMoves(self):
        moves = []
        myTile = self.getTile()
        for i in range(8):
            tile = self.tile.getNeighbor(i)
            moves = self.checkValidity(tile, moves)
        rightCastle = self.tile.getNeighbor(0).getNeighbor(0)
        leftCastle = self.tile.getNeighbor(4).getNeighbor(4)
        
        if not self.hasMoved and not self.myGame.inCheck(self.color):
            if not rightCastle.getNeighbor(0).hasMoved():
                
                rCpos = rightCastle.getPos()
                anX = rCpos[0]
                aY = rCpos[1]
                if rightCastle.isEmpty() and rightCastle.getNeighbor(4).isEmpty():
                    self.setCoords(anX-1, aY)
                    if not self.myGame.inCheck(self.color):
                        self.setCoords(anX, aY)
                        if not self.myGame.inCheck(self.color):
                            moves.append(rCpos)
                
            if not leftCastle.getNeighbor(4).getNeighbor(4).hasMoved():
                lCpos = leftCastle.getPos()
                anX = lCpos[0]
                aY = lCpos[1]
                if leftCastle.isEmpty() and leftCastle.getNeighbor(0).isEmpty() and leftCastle.getNeighbor(4).isEmpty():
                    self.setCoords(anX+1, aY)
                    if not self.myGame.inCheck(self.color):
                        self.setCoords(anX, aY)
                        if not self.myGame.inCheck(self.color):
                            
                            moves.append(lCpos)

        self.setCoords(myTile.getPos()[0], myTile.getPos()[1])
        return moves
                    
class dumbQueen(dumbPiece):
    def name(self):
        return "queen"

class queen(piece):

    def name(self):
        return "queen"
    
    def canMove(self, anX, aY):
        destTile = self.myGame.getTile(anX, aY)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            return False
        for i in range(8):
            for j in range(8):
                if self.tile.getNeighbor(i).slide(i, j) == destTile:
                    return default(destTile)
        return False
    
    def findMoves(self):
        moves = []
        for i in range(8):
            for j in range(8):
                tile = self.tile.getNeighbor(i).slide(i, j)
                moves = self.checkValidity(tile, moves)
                if not tile or not tile.isEmpty():
                    break

        return moves

def default(aTile):
    return [aTile, False, False] 
