
import pygame

class dumbPiece(pygame.sprite.Sprite):
    def __init__(self, anX, aY, aColor):
        super().__init__()
        self.x = anX
        self.y = aY
        self.coords = ""
        self.color = aColor
        
        
        self.image = False
        self.move(anX, aY)

    def isKing(self):
        return False
    
    def move(self, anX, aY):
        if not self.image:
            self.changeImage()
        self.x = anX
        self.y = aY
        self.coords = (100 + (75*anX), 50 + (75*(7-aY)))
        self.rect = self.image.get_rect(topleft = self.coords)

    def changeImage(self):
        anImage = "./" + self.color + "/" + self.name() + ".png"
        self.image = pygame.image.load(anImage).convert_alpha()
        
    def collidepoint(self, aPos):
        self.rect.collidepoint(aPos)
        
       

class piece(dumbPiece):
    
    def getColor(self):
        return self.color

    def getX(self):
        return self.x

    def getY(self):
        return self.y
    
    def getPos(self):
        return (self.x, self.y)
    
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
        self.needsRemoved = False
        self.opponent = ""
        
        self.move(anX, aY)

    def setOp(self, a):
        self.opponent = a

    def op(self):
        return self.opponent
    
    def setPos(self, aPos):
        self.coords = (aPos[0], aPos[1])
        self.rect = self.image.get_rect(center = self.coords)
    
    def remove(self, aTile):
        self.kill()
        self.needsRemoved = True
        aTile.empty()
    
    def cCanMove(self, presentTile, futureTile, opListOfCheckers, kingTile):
        
        oldX = self.x
        oldY = self.y
        anX = futureTile.x
        aY = futureTile.y
        if anX == oldX and oldY == aY:
            return False
        anArray = self.canMove(presentTile, futureTile, opListOfCheckers)
        if not anArray:
            return False
        newTile = anArray[0]
        oldPiece = newTile.getPiece()
        oldTile = presentTile
        oldTile.empty()
        
        
        self.op().removePiece(oldPiece)
        
        newTile.setPiece(self)
        self.setCoords(anX, aY)
        if self.op().isChecking(opListOfCheckers, kingTile):
            anArray = False
        oldTile.setPiece(self)
        self.op().addPiece(oldPiece)
        newTile.setPiece(oldPiece)
        self.setCoords(oldX, oldY)
        return anArray
    
    def isValidMove(self, tile):
        if not tile or tile.isNullTile():
            return False
        
        if tile.isEmpty() or tile.getColor() != self.color:
            return True
        return False
        
    def isSuperValidMove(self, fromTile, toTile, op, kingTile):
        return self.cCanMove(fromTile, toTile, op, kingTile)
    
    def checkValidity(self, aTile, moves, fromTile, op, kingTile):
        if self.isValidMove(aTile):
            tPos = aTile.getPos()
            if self.isSuperValidMove(fromTile, aTile, op, kingTile):
                moves.append(tPos)
        return moves
        

class dumbKnight(dumbPiece):
    def name(self):
        return "knight"
        
class knight(piece):

    def canMove(self, fromTile, destTile, _):
        
        if not destTile.isEmpty() and destTile.getColor() == self.color:
            return False
        for tile in fromTile.rookNeighbors:
            if tile == destTile:
                return default(destTile)
        return False
    
    def findMoves(self, fromTile, op, kingTile):
        moves = []
        for tile in fromTile.rookNeighbors:
            moves = self.checkValidity(tile, moves, fromTile, op, kingTile)
        return moves
    
    def name(self):
        return "knight"
    
class dumbRook(dumbPiece):
    def name(self):
        return "rook"
    
class rook(piece):

    def canMove(self, fromTile, destTile, _):
        
        if not destTile.isEmpty() and destTile.getColor() == self.color:
            return False
        for i in range(8):
            if i % 2 == 1:
                continue
            else:
                for j in range(8):
                    if fromTile.getNeighbor(i).slide(i, j) == destTile:
                        return default(destTile)
        return False 
    
    def findMoves(self, fromTile, op, kingTile):
        moves = []
        for i in range(8):
            if i % 2 == 1:
                continue
            else:
                for j in range(8):
                    tile = fromTile.getNeighbor(i).slide(i, j)
                    moves = self.checkValidity(tile, moves, fromTile, op, kingTile)
                    if not tile or not tile.isEmpty():
                        break
                   
        return moves
    
    def name(self):
        return "rook"

class pawn(piece):

    def name(self):
        return "pawn"
    
    def canMove(self, myTile, destTile, _):
        magicNum = 4
        if self.op().isPlayer2():
            magicNum = 0
        front = myTile.getNeighbor(2+magicNum)
        if destTile == myTile.getNeighbor(1+magicNum) or destTile == myTile.getNeighbor(3+magicNum):
            
            if self.op().enPassantTile == destTile:
                return default(destTile)
            
            if destTile.isEmpty() or destTile.getColor() == self.color:
                
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
        if not aTile.isEmpty() and aTile.getColor() != self.color:
            return True
        if aTile == self.op().enPassantTile:
            return True
        return False
    
    def findMoves(self, myTile, op, kingTile):
        
        magicNum = 4
        if self.op().isPlayer2():
            magicNum = 0
        front = myTile.getNeighbor(2+magicNum)
        diag1 = myTile.getNeighbor(1+magicNum)
        diag2 = myTile.getNeighbor(3+magicNum)
        moves = []
        
        
        if self.checkDiag(diag1):
            
            if self.isSuperValidMove(myTile, diag1, op, kingTile): moves.append(diag1.getPos())
        if self.checkDiag(diag2): 
            
            if self.isSuperValidMove(myTile, diag2, op, kingTile): moves.append(diag2.getPos())
        if front.isEmpty(): 
            
            if self.isSuperValidMove(myTile, front, op, kingTile):
                moves.append(front.getPos())
            if not self.getHasMoved():
                ffront = front.getNeighbor(2+magicNum)
                if ffront.isEmpty():
                    if self.isSuperValidMove(myTile, ffront, op, kingTile):
                        moves.append(ffront.getPos())
        return moves
        

        
class dumbBishop(dumbPiece):
    def name(self):
        return "bishop"    

class bishop(piece):
    

    def name(self):
        return "bishop"

    def canMove(self, fromTile, destTile, _):
        
        if not destTile.isEmpty() and destTile.getColor() == self.color:
            return False
        for i in range(8):
            if i % 2 == 0:
                continue
            else:
                for j in range(8):
                    if fromTile.getNeighbor(i).slide(i, j) == destTile:
                        return default(destTile)
        return False
    
    def findMoves(self, fromTile, op, kingTile):
        moves = []
        for i in range(8):
            if i % 2 == 0:
                continue
            else:
                for j in range(8):
                    posibileTile = fromTile.getNeighbor(i).slide(i, j)
                    moves = self.checkValidity( posibileTile, moves, fromTile, op, kingTile)
                   
                    if not posibileTile or not posibileTile.isEmpty():
                        break
                    
        return moves


        
class king(piece):

    def name(self):
        return "king"
    
    def isKing(self):
        return True
    
    def canMove(self, fromTile, destTile, op):
      
        answer = default(destTile)
        if not destTile.isEmpty() and destTile.getColor() == self.color:
            answer = False
        for i in range(8):
            if fromTile.getNeighbor(i) == destTile and answer:
                return answer
        rightCastle = fromTile.getNeighbor(0).getNeighbor(0)
        leftCastle = fromTile.getNeighbor(4).getNeighbor(4)
        pos = destTile.getPos()
        anX = pos[0]
        aY = pos[1]
        if not self.hasMoved and rightCastle == destTile:
            if self.op().isChecking(op, fromTile) or rightCastle.getNeighbor(0).hasMoved():
                return False
            if not rightCastle.getNeighbor(4).isEmpty() or not rightCastle.isEmpty():
                return False
            self.setCoords(anX-1, aY)
            if self.op().isChecking(op, rightCastle.getNeighbor(4)):
                self.setCoords(anX-2, aY)
                return False
            self.setCoords(anX, aY)
            if self.op().isChecking(op, destTile):
                self.setCoords(anX-2, aY)
                return False
            self.setCoords(anX-2, aY)
            return [destTile, False, [7]]
        if not self.hasMoved and leftCastle == destTile:
            if self.op().isChecking(op, fromTile) or leftCastle.getNeighbor(4).getNeighbor(4).hasMoved():
                return False
            if not leftCastle.getNeighbor(4).isEmpty() or not leftCastle.isEmpty() or not leftCastle.getNeighbor(0).isEmpty():
                return False
            self.setCoords(anX+1, aY)
            if self.op().isChecking(op, leftCastle.getNeighbor(0)):
                self.setCoords(anX+2, aY)
                return False
            self.setCoords(anX, aY)
            if self.op().isChecking(op, destTile):
                self.setCoords(anX+2, aY)
                return False
            self.setCoords(anX+2, aY)
            return [destTile, False, [0]]
        
    def findMoves(self, myTile, op, _):
        moves = []
        
        for i in range(8):
            tile = myTile.getNeighbor(i)
            moves = self.checkValidity(tile, moves, myTile, op, tile)
        rightCastle = myTile.getNeighbor(0).getNeighbor(0)
        leftCastle = myTile.getNeighbor(4).getNeighbor(4)
        
        if not self.hasMoved and not self.op().isChecking(op, myTile):
            if not rightCastle.getNeighbor(0).hasMoved():
                
                rCpos = rightCastle.getPos()
                anX = rCpos[0]
                aY = rCpos[1]
                if rightCastle.isEmpty() and rightCastle.getNeighbor(4).isEmpty():
                    self.setCoords(anX-1, aY)
                    if not self.op().isChecking(op, rightCastle.getNeighbor(4)):
                        self.setCoords(anX, aY)
                        if not self.op().isChecking(op, rightCastle):
                            moves.append(rCpos)
                
            if not leftCastle.getNeighbor(4).getNeighbor(4).hasMoved():
                lCpos = leftCastle.getPos()
                anX = lCpos[0]
                aY = lCpos[1]
                if leftCastle.isEmpty() and leftCastle.getNeighbor(0).isEmpty() and leftCastle.getNeighbor(4).isEmpty():
                    self.setCoords(anX+1, aY)
                    if not self.op().isChecking(op, leftCastle.getNeighbor(0)):
                        self.setCoords(anX, aY)
                        if not self.op().isChecking(op, leftCastle):
                            
                            moves.append(lCpos)

        self.setCoords(myTile.getPos()[0], myTile.getPos()[1])
        return moves
                    
class dumbQueen(dumbPiece):
    def name(self):
        return "queen"

class queen(piece):

    def name(self):
        return "queen"

    
    def canMove(self, fromTile, destTile, _):
        
        if not destTile.isEmpty() and destTile.getColor() == self.color:
            return False
        for i in range(8):
            for j in range(8):
                if fromTile.getNeighbor(i).slide(i, j) == destTile:
                    return default(destTile)
        return False
    
    def findMoves(self, fromTile, op, kingTile):
        moves = []
        
        for i in range(8):
            for j in range(8):
                tile = fromTile.getNeighbor(i).slide(i, j)
                moves = self.checkValidity(tile, moves, fromTile, op, kingTile)
                if not tile or not tile.isEmpty():
                    break

        return moves

def default(aTile):
    return [aTile, False, False] 
