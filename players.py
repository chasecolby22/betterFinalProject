import math
import time
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

    def getCheckers(self, aKing):
        checkers = []
        for item in self.pieces:
            if item.canMove(aKing.x, aKing.y):
                checkers.append((item.x, item.y))
        return checkers
    
    def isChecking(self, aKing):
        checkers = self.getCheckers(aKing)
        return len(checkers) > 0

    def addPiece(self, aPiece):
        if aPiece != "EMPTY":
            self.pieces.append(aPiece)

    def removePiece(self, aPiece):
        if aPiece != "EMPTY":
            self.pieces.remove(aPiece)
          

    def __init__(self, player1, aGame):
        self.king = "EMPTY"
        self.tempMoveString = ""
        self.pieces = []
        self.myGame = aGame
        self.myScreen = aGame.myScreen
        if player1:
            self.color = "white"
            self.row = 0
            self.pawnsRow = 1
            self.pname = "Player 1:  "
        else:
            self.color = "black"
            self.row = 7
            self.pawnsRow = 6
            self.pname = "Player 2:  "

    def hasPiece(self, col, row):
        aPiece = self.myGame.board.getTile(col, row).getPiece()
       
        if aPiece == "EMPTY":
            return False
        if aPiece.getColor() == self.color:
            return aPiece
        
        return False
    
    def getColor(self):
        return self.color
    
    def updateScreen(self):
        self.myScreen.updateScreen()
    
    def name(self):
        return self.pname

    
class humanPlayer(player):

    def checkSelection(self, validPiece, pos):
        thing = "abcdefgh"
        if not validPiece: return False
        for row in self.myGame.onScreenTiles():
            for tile in row:
                if tile.rect.collidepoint(pos):
                    col = tile.pos[0]
                    row = tile.pos[1]
                    if validPiece.cCanMove(col, row):
                        
                        startX = thing[validPiece.x]
                        startY = str(validPiece.y+1)
                        endX = thing[col]
                        endY = str(row+1)
                        promotion = " "
                        if validPiece.name() == "pawn":
                            if row == self.myGame.getNonActivePlayer().row:
                                
                                promotion = self.myGame.myScreen.drawPromotion()
                        self.tempMoveString = startX + startY + endX + endY + promotion
                        if self.tempMoveString != self.myGame.botString:
                            self.myGame.drawBot()
                            print("The bot thought about this move:  " + self.myGame.botString)
                        else:
                            self.myGame.botChoice = ""
                            print("youre so smart")
                        self.myGame.movesString += self.tempMoveString + " "
                        if promotion == " ": anArray = validPiece.canMove(col, row)
                        else: anArray = [None, False, False]
                        self.myGame.movePiece(validPiece, col, row, anArray[1], anArray[2], promotion)
                        return True
        return False
    
    def drawPosibilities(self, validPiece):
        self.myScreen.sur.fill((255, 255, 255))
        self.myScreen.drawBoard()
        moves = validPiece.findMoves()
        self.myGame.drawSquares(moves, (255, 150, 0))
        if self.myGame.checkers != "": self.myGame.drawSquares(self.myGame.checkers, (255, 0, 0))
        self.myScreen.drawSprites()

        pygame.display.update()

    def findPosibilities(self, aPos):
        for piece in self.pieces:
            if piece.rect.collidepoint(aPos):
                self.drawPosibilities(piece)
                pygame.mouse.set_cursor(pygame.cursors.diamond)
                return piece
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return False
    def takeTurn(self):
        
        self.myGame.getBotInput(10)
        running = True
        
        validPiece = False
        dragging = False
        mouseDown = False
        validPieceOgPos = ""
        originalMousePos = ""
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                   
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not validPiece:
                        for piece in self.pieces:
                            if piece.rect.collidepoint(event.pos):
                                validPiece = piece
                                validPieceOgPos = (100 + piece.x * 75 + 75/2, 50 + (7-piece.y) * 75 + 75/2)
                                dragging = False
                                mouseDown = True
                                originalMousePos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    wasClick = True
                    if dragging:
                        dragging = False
                        wasClick = False
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    
                    mouseDown = False
                    if not wasClick:
                        if self.checkSelection(validPiece, event.pos):
                            
                            running = False
                            
                        if running:
                            if validPiece: validPiece.setPos(validPieceOgPos)
                            self.updateScreen()
                            validPiece = False
                    else:
                        if validPiece and not validPiece.rect.collidepoint(event.pos):
                            if self.checkSelection(validPiece, event.pos):
                                running = False
                                
                            if running:
                                self.updateScreen()
                                validPiece = False
                            
                elif event.type == pygame.MOUSEMOTION:
                    if mouseDown:
                        
                        if compareTuple(event.pos, originalMousePos):

                            dragging = True
                    
                    if not validPiece and not self.findPosibilities(event.pos):
                        self.updateScreen()
                    elif validPiece and dragging:
                        validPiece.setPos(event.pos)
                        self.drawPosibilities(validPiece)
        return True
def compareTuple(t1, t2):
    x = t1[0] - t2[0]
    y = t1[1] - t2[1]
    return math.sqrt(x * x + y * y) > 5

class botPlayer(player):
    def __init__(self, player1, difficulty, aGame):
        super().__init__(player1, aGame)
        self.difficulty = difficulty

    def takeTurn(self):
        
        botString = self.myGame.getBotInput(self.difficulty)

        botString = self.myGame.botInput(botString)
        
        self.myGame.drawBot()
        validPiece = self.hasPiece(botString[0], botString[1]) 
        col = botString[2]
        row = botString[3]
        anArray = validPiece.canMove(col, row)
        print("Turn " + str(self.myGame.turns) + ": The bot choose:  " + self.myGame.botString)
        self.myGame.movePiece(validPiece, col, row, anArray[1], anArray[2], botString[4])
        time.sleep(0.25)
        return True