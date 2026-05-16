import math
from pieces import *

class player():
  
    
    def hasMove(self):
        for item in self.pieces:
            if len(item.findMoves()) > 0:
                return True
        return False
    
    def start(self):
        self.pieces.append(knight(1, self.row, self))
        self.pieces.append(knight(6, self.row, self))
        self.king = king(4, self.row, self)
        self.pieces.append(self.king)
        self.pieces.append(queen(3, self.row, self))
        self.pieces.append(rook(0, self.row, self))
        self.pieces.append(rook(7, self.row, self))
        self.pieces.append(bishop(2, self.row, self))
        self.pieces.append(bishop(5, self.row, self))
        for i in range(8):
            self.pieces.append(pawn(i, self.pawnsRow, self))

    def getTile(self, anX, aY):
        return self.board.getTile(anX, aY)
    
    def getCheckers(self):
        checkers = []
        aKing = self.op.king
        for item in self.pieces:
            if item.canMove(aKing.x, aKing.y):
                checkers.append((item.x, item.y))
        return checkers
    
    def isChecking(self):
        checkers = self.getCheckers()
        return len(checkers) > 0

    def addPiece(self, aPiece):
        if aPiece != "EMPTY":
            self.pieces.append(aPiece)

    def removePiece(self, aPiece):
        if aPiece != "EMPTY":
            self.pieces.remove(aPiece)

    def isPlayer1(self):
        return self.player1

    def __init__(self, player1, aBoard):
        self.king = "EMPTY"
        self.board = aBoard
        self.op = ""
        self.enPassantTile = ""
        self.tempMoveString = ""
        self.needsUpdate = True
        self.humanSelection = ()
        self.posibleMoves = ""
        self.pieces = []
        self.player1 = player1
        self.dragging = False
        self.mouseDown = False
        self.promotionNeeded = False
        self.matchedBot = True
        self.validPiece = False
        self.originalMousePos = ""
        self.validPieceOgPos = ""

        if player1:
            self.color = "white"
            self.row = 0
            self.pawnsRow = 1
            self.oppositeRow = 7
            self.pname = "Player 1:  "
        else:
            self.color = "black"
            self.row = 7
            self.pawnsRow = 6
            self.oppositeRow = 0
            self.pname = "Player 2:  "

    def hasPiece(self, col, row):
        for item in self.pieces:
            if item.tile.getPos() == (col, row):
                return True
        return False
       
    
    def getColor(self):
        return self.color
    
    
    def name(self):
        return self.pname

    
class humanPlayer(player):

    def isHuman(self):
        return True
    
    def checkSelection(self, aTile, botString):
        thing = "abcdefgh"
        if not self.validPiece: return [False, False]
        if not aTile: return [False, False]
        self.good = False
        self.ccol = aTile[0]
        self.rrow = aTile[1]
        if self.validPiece.cCanMove(self.ccol, self.rrow):
            self.goodPiece = self.validPiece
            self.good = True
            self.startX = thing[self.validPiece.x]
            self.startY = str(self.validPiece.y+1)
            self.endX = thing[self.ccol]
            self.endY = str(self.rrow+1)
            self.promotion = " "
            self.promotionNeeded = False
            if self.validPiece.name() == "pawn":
                if self.rrow == self.oppositeRow:
                    self.promotionNeeded = True
                    return [False, True]
                    
            if not self.promotionNeeded:
                return self.finishSelection(botString)
        return [False, False]


    def finishSelection(self, botString):
       
        self.tempMoveString = self.startX + self.startY + self.endX + self.endY + self.promotion
        
        if self.tempMoveString != botString:
            self.matchedBot = False
            print("The bot thought about this move:  " + botString)
        else:
            self.matchedBot = True
            print("youre so smart")
        
        if self.promotion == " ": anArray = self.validPiece.canMove(self.ccol, self.rrow)
        else: anArray = [None, False, False]
        self.humanSelection = (self.goodPiece, self.ccol, self.rrow, anArray[1], anArray[2], self.promotion)
        
        return [True, False]
       
    
    def drawPosibilities(self, validPiece):

        self.posibleMoves = validPiece.findMoves()
        self.needsUpdate = True
        

    def findPosibilities(self, aTile):
   
        for piece in self.pieces:
            
            if piece.tile.getPos() == aTile:
                
                self.drawPosibilities(piece)
                pygame.mouse.set_cursor(pygame.cursors.diamond)
                return piece
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.posibleMoves = ""
        self.needsUpdate = True
        return False
    
    def handleEvent(self, aEvent, aTile, botString):
        done = False
        thePromotion = False
        if aEvent.type == pygame.MOUSEBUTTONDOWN:
            
            
            if not self.validPiece:
                for piece in self.pieces:
                    if piece.tile.getPos() == aTile:
                        
                        self.validPiece = piece
                        self.validPieceOgPos = (100 + piece.x * 75 + 75/2, 50 + (7-piece.y)*75 + 75/2)
                        self.dragging = False
                        self.mouseDown = True
                        self.originalMousePos = aEvent.pos
        elif aEvent.type == pygame.MOUSEBUTTONUP:
  
            wasClick = True
            if self.dragging:
                self.dragging = False
                wasClick = False
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.mouseDown = False
            self.originalMousePos = ""
            
            if not wasClick:
                if not self.checkSelection(aTile, botString)[0]:
                    if self.validPiece: self.validPiece.setPos(self.validPieceOgPos)
                    self.needsUpdate = True
                    self.validPiece = False
                else:
                    done = True
                    
            else:
                if self.validPiece and self.validPiece.tile.getPos() != aTile:
                    array = self.checkSelection(aTile, botString)
                    if not array[0]:
                        if array[1]: thePromotion = True
                        elif self.validPiece: self.validPiece.setPos(self.validPieceOgPos)
                        self.needsUpdate = True
                        self.validPiece = False

                    else:
                        
                        done = True
        elif aEvent.type == pygame.MOUSEMOTION:
           
            if self.mouseDown:
                
                
                if compareTuple(aEvent.pos, self.originalMousePos):
                    self.dragging = True
            
            if not self.validPiece and not self.findPosibilities(aTile):
                if self.posibleMoves != "":
                    self.posibleMoves = ""
                    self.needsUpdate = True
                
                
            elif self.validPiece and self.dragging:
                self.validPiece.setPos(aEvent.pos)
                self.needsUpdate = True
                
                
        
        return [True, done, thePromotion]

def compareTuple(t1, t2):
    x = t1[0] - t2[0]
    y = t1[1] - t2[1]
    return math.sqrt(x * x + y * y) > 5

class botPlayer(player):

    def isHuman(self):
        return False
    
    def __init__(self, player1, difficulty, aBoard):
        super().__init__(player1, aBoard)
        
        self.difficulty = difficulty

    def takeTurn(self, botString):
        
        
        validPiece = self.hasPiece(botString[0], botString[1]) 
        col = botString[2]
        row = botString[3]
        anArray = validPiece.canMove(col, row)
        
        self.botTuple = (validPiece, col, row, anArray[1], anArray[2], botString[4])
        
        
        return True