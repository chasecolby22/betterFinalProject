import math
from pieces import *

class cursor(pygame.sprite.Sprite):
    def __init__(self, anImage):
        super().__init__()
        self.image = pygame.image.load(anImage).convert_alpha()
        
        self.rect = self.image.get_rect(topleft = (-100, -100)) 

    def move(self, aPos):
        self.rect = self.image.get_rect(center = aPos)  

class player():
  
    
    def hasMove(self, listOfTiles, op):
        for i in range(len(self.pieces)):

        
            if len(self.pieces[i].findMoves(listOfTiles[i], op, self.kingTile)) > 0:
                return True
        return False
    
    def start(self):
        self.pieces.append(knight(1, self.row, self.color))
        self.pieces.append(knight(6, self.row, self.color))
        self.king = king(4, self.row, self.color)
        self.pieces.append(self.king)
        self.pieces.append(queen(3, self.row, self.color))
        self.pieces.append(rook(0, self.row, self.color))
        self.pieces.append(rook(7, self.row, self.color))
        self.pieces.append(bishop(2, self.row, self.color))
        self.pieces.append(bishop(5, self.row, self.color))
        for i in range(8):
            self.pieces.append(pawn(i, self.pawnsRow, self.color))
    
    def getCheckers(self, listOfTiles, kingTile):
        checkers = []
        
        for i in range(len(self.pieces)):
            item = self.pieces[i]
            if item != self.king:
                if item.canMove(listOfTiles[i], kingTile, None):
                    listOfTiles[i].rect.circleColor = (255, 0, 0)
                    checkers.append((item.x, item.y))
        return checkers
    
    def isChecking(self, aListOfTiles, kingTile):
        checkers = self.getCheckers(aListOfTiles, kingTile)
        if len(checkers) > 0:
            kingTile.rect.circleColor = (255, 0, 0)
        return len(checkers) > 0

    def addPiece(self, aPiece):
        if aPiece != "EMPTY":
            self.pieces.append(aPiece)
    
    def clearEnPassantTile(self):
        for item in self.pieces:
            item.enPassantTile = ""

    def setEnPassantTile(self, a):
        for item in self.pieces:
            item.enPassantTile = a

    def isPlayer2(self):
        return not self.player1
   
    def setPromotion(self, a):
        self.promotion = a
        self.promotionNeeded = False

    def __init__(self, player1, aBoard):
        self.king = "EMPTY"
        self.board = aBoard
        self.kingTile = ""
        
        self.validPieceTile = ""
        self.validPieceOgPos = ""
        
        self.highlightedTile = ""
        self.enPassantTile = ""
        self.tempMoveString = ""
        self.needsUpdate = True
        self.tuple = ()
        self.posibleMoves = ""
        self.pieces = []
        self.player1 = player1
        self.dragging = False
        self.mouseDown = False
        self.promotion = ""
        self.promotionNeeded = False
        self.matchedBot = True
        self.validPiece = False
        self.originalMousePos = ""

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

    
       
    
    def getColor(self):
        return self.color
    
    
    def name(self):
        return self.pname

    
class humanPlayer(player):

    def didMatchBot(self):
        return self.matchedBot
    
    def isHuman(self):
        return True
    
    def checkSelection(self, aTile, botString, op):
        thing = "abcdefgh"
        if not self.validPiece: return [False, False]
        if not aTile: return [False, False]
        self.good = False
        self.tempTile = aTile
        pos = aTile.getPos()
        self.ccol = pos[0]
        self.rrow = pos[1]
        theKingTile = self.kingTile
        if self.validPiece.isKing(): theKingTile = aTile
        if self.validPiece.cCanMove(self.validPieceTile, aTile, op, theKingTile):
            self.goodPiece = self.validPiece
            self.goodPieceTile = self.validPieceTile
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
                self.goodPieceTile = self.validPieceTile
                return self.finishSelection(botString, op)
        return [False, False]


    def finishSelection(self, botString, op):
        val = self.promotion
       
        self.tempMoveString = self.startX + self.startY + self.endX + self.endY + val
       
        if self.tempMoveString[:4] != botString[:4]:
            self.matchedBot = False
            print("The bot thought about this move:  " + botString)
        else:
            self.matchedBot = True
            print("youre so smart")
        
        if self.promotion == " ": anArray = self.validPiece.canMove(self.validPieceTile, self.tempTile, op)
        else: anArray = [None, False, False]
        
        self.tuple = (self.goodPiece, self.ccol, self.rrow, anArray[1], anArray[2], self.promotion, self.goodPieceTile)
        return [True, False]
       
    def setHighlight(self, aTile):
        if self.highlightedTile != aTile:
            self.clearHighlight()
            aTile.rect.highlight()
            self.highlightedTile = aTile
            self.needsUpdate = True

    def drawPosibilities(self, aPiece, startTile, op):
        tempMoves = aPiece.findMoves(startTile, op, self.kingTile)
        
        if self.posibleMoves != tempMoves:
            
            if len(tempMoves) != 0:
                self.setHighlight(startTile)
            else:
                self.clearHighlight()
            self.posibleMoves = tempMoves
            self.needsUpdate = True
            
           
            
        

    def findPosibilities(self, aTile, op):
        if not aTile: return False
        for piece in self.pieces:
            
            if piece.getPos() == aTile.getPos():
                
                self.drawPosibilities(piece, aTile, op)
                pygame.mouse.set_cursor(pygame.cursors.diamond)
                return piece
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        return False
    
    def clearHighlight(self):
        if self.highlightedTile != "":
            self.highlightedTile.rect.reset()
            self.needsUpdate = True
            
        self.highlightedTile = ""

    def handleEvent(self, aEvent, aTile, botString, op):
        done = False
        thePromotion = False
        if aEvent.type == pygame.MOUSEBUTTONDOWN:
            
            
            if aTile and not self.validPiece:
                for piece in self.pieces:
                    pos = aTile.getPos()
                    if piece.getPos() == pos:
                        
                        self.validPiece = piece
                        
                        self.validPieceOgPos = (100+75*pos[0]+75/2, 50 + 75*(7-pos[1]) + 75/2)
                        self.validPieceTile = aTile
                        self.dragging = False
                        self.mouseDown = True
                        self.originalMousePos = aEvent.pos
        elif aEvent.type == pygame.MOUSEBUTTONUP:
            if aTile:
                wasClick = True
                if self.dragging:
                    self.dragging = False
                    wasClick = False
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.mouseDown = False
                self.originalMousePos = ""
                
                if not wasClick:
                    if not self.checkSelection(aTile, botString, op)[0]:
                        if self.validPiece: self.validPiece.setPos(self.validPieceOgPos)
                        self.needsUpdate = True
                        self.validPiece = False
                        self.validPieceTile = ""
                        self.validPieceOgPos = ""
                        self.clearHighlight()
                        self.tempTile = ""
                    else:
                        self.clearHighlight()
                        done = True
                        
                else:
                    if self.validPiece and self.validPiece.getPos() != aTile.getPos():
                        array = self.checkSelection(aTile, botString, op)
                        if not array[0]:
                            if array[1]: thePromotion = True
                            elif self.validPiece: self.validPiece.setPos(self.validPieceOgPos)
                            self.needsUpdate = True
                            self.validPiece = False
                            self.validPieceTile = ""
                            self.validPieceOgPos = ""
                            self.clearHighlight()
                            self.tempTile = ""

                        else:
                            self.clearHighlight()
                            done = True
        elif aEvent.type == pygame.MOUSEMOTION:
            
            if self.mouseDown:
                
                
                if compareTuple(aEvent.pos, self.originalMousePos):
                    self.dragging = True
            
            if not self.validPiece and not self.findPosibilities(aTile, op):
                if self.posibleMoves != "":
                    self.posibleMoves = ""
                    self.clearHighlight()
                    self.needsUpdate = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                
                
            elif self.validPiece and self.dragging:
                self.validPiece.setPos(aEvent.pos)
                self.needsUpdate = True
            
            if self.validPiece and aTile:
                set = False
                for item in self.posibleMoves:
                    
                    if aTile == item:
                        if aTile != self.highlightedTile:
                            
                            self.setHighlight(aTile)
                            set = True
                            break
                        set = True

                if not set:
                    
                    self.clearHighlight()
                    

            
            if not aTile:    
                
                self.clearHighlight()
           

        
        return [True, done, thePromotion]

def compareTuple(t1, t2):
    x = t1[0] - t2[0]
    y = t1[1] - t2[1]
    return math.sqrt(x * x + y * y) > 5

class botPlayer(player):

    def didMatchBot(self):
        if self.started:
            
            return False
        return True
    
    def isHuman(self):
        return False
    
    def __init__(self, player1, difficulty, aBoard):
        super().__init__(player1, aBoard)
        self.started = False
        self.difficulty = difficulty

    def takeTurn(self, botString, listOfTiles, op):
        
        self.started = True
        validPiece = ""
        fromTile = ""
        toTile = ""

        for item in listOfTiles:
            if item.getPos() == (botString[0], botString[1]):
                validPiece = item.piece
                fromTile = item
            if item.getPos() == (botString[2], botString[3]):
                toTile = item
                
        

        col = botString[2]
        row = botString[3]
        
        anArray = validPiece.canMove(fromTile, toTile, op)
        
        self.tuple = (validPiece, col, row, anArray[1], anArray[2], botString[4], fromTile)
        
        
        return True