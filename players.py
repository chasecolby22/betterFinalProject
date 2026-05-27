import math
from pieces import *
import time

class cursor(pygame.sprite.Sprite):
    def __init__(self, anImage):
        super().__init__()
        self.image = pygame.image.load(anImage).convert_alpha()
        
        self.rect = self.image.get_rect(topleft = (-100, -100)) 
        self._layer = 2

    def move(self, aPos):
        self.rect = self.image.get_rect(center = aPos)  

class player():
        
    def hasMove(self, listOfTiles, op):
        for i in range(len(self.pieces)):
            
            
            if len(self.pieces[i].findMoves(listOfTiles[i], op, self.kingTile)) > 0:
                return True
        return False
    
    def start(self):
        for i in range(2):
            for j in range(len(self.pieceList[i])):
                iitem = self.pieceList[i][j]
                if iitem != None:
                    item = iitem(j, self.pawnsRow if i == 0 else self.row, self.color)
                    if item.isKing():
                        if self.king == "EMPTY":

                            self.king = item
                        else:
                            exit()
                    self.pieces.append(item)

        
            
    
    def getCheckers(self, listOfTiles, kingTile):
        checkers = []
        
        for i in range(len(self.pieces)):
            item = self.pieces[i]
            if item != self.king:
                if item.canMove(listOfTiles[i], kingTile, None):
                    checkers.append((item.x, item.y))
        return checkers
    
    def isChecking(self, aListOfTiles, kingTile):
        
        checkers = self.getCheckers(aListOfTiles, kingTile)
        if len(checkers) > 0:
            kingTile.circleColor = (255, 0, 0)
            kingTile.different = True
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
   
    def setPromotion(self, a):
        self.promotion = a
        self.promotionNeeded = False

    def addPieces(self, aGroup):
        for item in self.pieces:
            aGroup.append(item)

    def __init__(self, player1, pieceList, height):
        self.king = "EMPTY"
        self.pieceList = pieceList
        self.kingTile = ""
        
        self.validPieceTile = ""
        self.highlightedTile = ""
        self.enPassantTile = ""
        self.tempMoveString = ""
        self.needsUpdate = True
        self.hasMadeMove = False
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
            self.oppositeRow = height - 1
            self.pname = "Player 1:  "
        else:
            self.color = "black"
            self.row = height - 1
            self.pawnsRow = height - 2
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
    
    def checkSelection(self, aTile, botString, op, gameRunning):
        thing = "abcdefgh"
        if not gameRunning: return [False, False]
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
            print(botString)
            if botString != "":
                self.startX = thing[self.validPiece.x]
                self.startY = str(self.validPiece.y+1)
                self.endX = thing[self.ccol]
                self.endY = str(self.rrow+1)
            self.promotion = " "
            self.promotionNeeded = False
            if self.validPiece.name() == "pawn":
                if self.rrow == self.oppositeRow:
                    self.promotionNeeded = True
                    self.validPieceTile.reset()
                    return [False, True]
                    
            if not self.promotionNeeded:
                self.goodPieceTile = self.validPieceTile
                self.validPieceTile.reset()
                return self.finishSelection(botString, op)
        return [False, False]


    def finishSelection(self, botString, op):
        val = self.promotion
       
        if botString != "":
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
       
    def setHighlight(self, aTile, aColor):
        if self.highlightedTile != aTile:
            self.clearHighlight()
            aTile.highlight(aColor)
            self.highlightedTile = aTile
            self.needsUpdate = True

    def drawPosibilities(self, aPiece, startTile, op):
        tempMoves = aPiece.findMoves(startTile, op, self.kingTile)
        
        if self.highlightedTile != startTile or self.posibleMoves != tempMoves:
            
            if len(tempMoves) != 0:
                self.setHighlight(startTile, (0, 100, 0))
            else:
                self.setHighlight(startTile, (255, 0, 0))
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
            self.highlightedTile.reset()
            self.needsUpdate = True
            
        self.highlightedTile = ""

    def handleEvent(self, aEvent, aTile, botString, op, gameRunning):
        done = False
        thePromotion = False
        
        if aEvent.type == pygame.MOUSEBUTTONDOWN:
            
            if aEvent.button == 1:

                if aTile :
                    if not self.validPiece:
                        
                        pos = aTile.getPos()
                        for piece in self.pieces:
                            if piece.getPos() == pos:
                                
                                self.validPiece = piece
                                
                                
                                self.validPieceTile = aTile
                                self.dragging = False
                                self.mouseDown = True
                                self.mouseDownTime = time.time()
                                self.originalMousePos = aEvent.pos
                                self.needsUpdate = True

                    else:
                        if self.validPieceTile == aTile:
                            self.dragging = True

                            pygame.mouse.set_visible = False
                            
               

        elif aEvent.type == pygame.MOUSEBUTTONUP:
            if aEvent.button == 1:
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

                        if not self.checkSelection(aTile, botString, op, gameRunning)[0]:
                            if self.validPiece: 
                                
                                self.validPieceTile.reset()
                            self.needsUpdate = True
                            self.validPiece = False
                            self.validPieceTile = ""
                            
                            
                            self.clearHighlight()
                            self.tempTile = ""
                            
                        else:
                            self.clearHighlight()
                            done = True
                            
                    else:
                        if self.validPiece and self.validPiece.getPos() != aTile.getPos():
                            array = self.checkSelection(aTile, botString, op, gameRunning)
                            if not array[0]:
                                if array[1]: thePromotion = True
                               
                                self.needsUpdate = True
                                self.validPieceTile.reset()
                                self.validPieceTile = ""
                              
                                self.posibleMoves = ""
                                self.clearHighlight()
                                
                                self.validPiece = self.findPosibilities(aTile, op)
                                if self.validPiece:
                                    self.validPieceTile = aTile
                                    
                                    
                                    
                                self.tempTile = ""

                            else:
                                
                                self.clearHighlight()
                                
                                done = True

                else:
                    if self.validPiece and self.dragging:
                        
                        self.needsUpdate = True
                        self.validPiece = False
                        
                        
                        self.validPieceTile.reset()
                        self.validPieceTile = ""
                        self.posibleMoves = ""
                        self.clearHighlight()
                        self.dragging = False

        elif aEvent.type == pygame.MOUSEMOTION:
            
            if not self.dragging:
                if self.mouseDown:
                    
                    if time.time() - self.mouseDownTime > .25:
                        if not self.dragging:
                            self.dragging = True
                            if self.validPiece: self.validPieceTile.highlight((200, 200, 0))
                    
                
                    if compareTuple(aEvent.pos, self.originalMousePos):
                        if not self.dragging:
                            self.dragging = True
                            if self.validPiece: self.validPieceTile.highlight((200, 200, 0))
            
            if not self.validPiece and not self.findPosibilities(aTile, op):
                self.posibleMoves = ""
                if aTile:
                    self.setHighlight(aTile, (255, 0, 0))
                    
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                

                
                
           
            
            if self.validPiece and aTile:
                set = False
                for item in self.posibleMoves:
                    
                    if aTile == item:
                        if aTile != self.highlightedTile:
                            
                            self.setHighlight(aTile, (0, 100, 0))
                            self.validPieceTile.highlight((139, 128, 0))    
                            set = True
                            break
                        self.validPieceTile.highlight((139, 128, 0))
                        set = True

                if not set:
                    if self.validPieceTile != aTile:
                        self.setHighlight(aTile, (255, 0, 0))
                        self.validPieceTile.highlight((139, 128, 0))
                    else:
                        self.setHighlight(aTile, (200, 200, 0))
                    
                    

            
            if not aTile:    
                
                self.clearHighlight()
            

        
        return [done, thePromotion]
    def handleNoEvent(self):
        
        if not self.dragging:
            if self.mouseDown:  
                
                if time.time() - self.mouseDownTime > .25:
                    self.dragging = True
                    if self.validPiece: self.validPieceTile.highlight((200, 200, 0))
                    self.needsUpdate = True
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
    
    def __init__(self, player1, difficulty, aPieceList, aHeight):
        super().__init__(player1, aPieceList, aHeight)
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