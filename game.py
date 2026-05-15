from botHandler import botHandler
from board import board
from players import *

class game():
    def __init__(self, aScreen):
        
        self.board = ""
        self.player1 = ""
        self.player2 = ""
        self.activePlayer = ""
        self.turns = 0
        self.movesString = ""
        self.botString = ""
        self.enPassantTile = ""
        self.checkers = ""
        self.myScreen = aScreen
        self.myBotHandler = botHandler()
        self.botChoice = ""
        self.promotionSquares = ""
        
        self.botStarted = self.myBotHandler.startBot()

    def onScreenTiles(self):
        return self.myScreen.tiles
    
    def getBotInput(self, aDifficulty):
        self.botString = self.myBotHandler.getBotInput(self.movesString, aDifficulty)[9:14]
        return self.botString
    
    def drawSquares(self, aList, Color):
        self.myScreen.drawSquares(aList, Color)

    def startGame(self, player1bot, player1dif, player2bot, player2dif):
        self.board = board()
        self.player1 = ""
        self.player2 = ""
        self.turns = 0
        self.movesString = ""
        self.botString = ""
        self.myScreen.makeMainScreen()
        if not self.botStarted:
            print("Sorry bot is sleepy")
            self.player1 = humanPlayer(True, self)
            self.player2 = humanPlayer(False, self)
            
        
        else:
            if player1bot:
                self.player1 = botPlayer(True, player1dif, self)
            else:
                self.player1 = humanPlayer(True, self)
            if player2bot:
                self.player2 = botPlayer(False, player2dif, self)
            else:
                self.player2 = humanPlayer(False, self)
        self.player1.start()
        self.player2.start()
        self.activePlayer = self.player1
        self.myScreen.updateScreen()

        
    def step(self):
        self.drawCheck()
        if not self.activePlayer.takeTurn():
            return False
        self.drawCheck()
        return True

    def drawBot(self):
        anArray = self.parseThings(self.botString[0], self.botString[1], self.botString[2], self.botString[3])
        squares = []
        squares.append((anArray[0], anArray[1]))
        squares.append((anArray[2], anArray[3]))
        
        self.botChoice = squares
        

    

    def drawCheck(self):
        if self.inCheck(self.activePlayer.getColor()):
            daKing = self.activePlayer.king
            self.checkers = self.getNonActivePlayer().getCheckers(daKing)
            
            self.checkers.append((daKing.x, daKing.y))
            
            self.myScreen.updateScreen()
            
        else:
            self.checkers = ""
                
    def hasPiece(self, col, row):
        return self.activePlayer.hasPiece(col, row)
    
    def gameStopped(self):
        if len(self.player1.pieces) == 1 and len(self.player2.pieces) == 1:
            print("The game was a stalemate")
            return True
        if self.activePlayer.hasMove():
            return False
        if self.inCheck(self.color()):
            self.winner()
        else:
            print("The game was a stalemate")
        return True
    
    def parseThings(self, a, b, c, d):
        row = int(b) - 1
        col = ord(a) - ord('a')
        newRow = int(d) - 1
        newCol = ord(c) - ord('a')
        return [col, row, newCol, newRow]
    
    def botInput(self, aString):
        promote = False
        if len(aString) > 4:
            promote = aString[4]
        array = self.parseThings(aString[0], aString[1], aString[2], aString[3])
        
        
        self.movesString += aString + " "
        self.botString = aString
        
        array.append(promote)
        return array

    def getNonActivePlayer(self):
        if self.p1act():
            return self.player2
        return self.player1
    
    def p1act(self):
        return self.activePlayer == self.player1
    
    def winner(self):
        print(self.getNonActivePlayer().name() + "won!")

    def inCheck(self, aColor):
        if aColor == self.player1.color:
            return self.player2.isChecking(self.player1.king)
        
        return self.player1.isChecking(self.player2.king)
    
    def color(self):
        return self.activePlayer.getColor()

    def switchPlayer(self):
        if self.p1act():
            self.activePlayer = self.player2
        else:
            self.activePlayer = self.player1
            self.turns += 1

    def activePlayerPrompt(self, aString):
        return self.activePlayer.name() + aString
    
    def getTile(self, x, y):
        return self.board.getTile(x, y)

    def movePiece(self, aPiece, col, row, enPassantTile, castle, promotion):
        
        destTile = self.getTile(col, row)
        eatenPiece = destTile.piece
        
        if aPiece.name() == "pawn":
            if row == self.getNonActivePlayer().row:
                aPiece.remove()
                match promotion:
                    case "q":
                        aPiece = queen(-2, -2, self.activePlayer)
                    case "n":
                        aPiece = knight(-2, -2, self.activePlayer)
                    case "r":
                        aPiece = rook(-2, -2, self.activePlayer)
                    case "b":
                        aPiece = bishop(-2, -2, self.activePlayer)
                self.activePlayer.addPiece(aPiece)
                self.myScreen.addSprite(aPiece)

        
        if eatenPiece != "EMPTY":
            eatenPiece.remove()
        elif aPiece.name() == "pawn" and self.enPassantTile == destTile:
            magicNum = 0
            if self.p1act():
                magicNum = 4
            destTile.getNeighbor(2+magicNum).piece.remove()
        if enPassantTile:
            self.enPassantTile = enPassantTile
        else:
            self.enPassantTile = ""
        if castle:
            magicNum = 0
            if castle[0] == 7:
                magicNum = 2
            self.movePiece(self.board.getTile(castle[0], self.activePlayer.row).getPiece(), 3+magicNum, self.activePlayer.row, False, False, False)
            self.switchPlayer()

        destTile.setPiece(aPiece)
        aPiece.tile.empty()
        aPiece.setHasMoved(True)
        aPiece.move(col, row)
        self.switchPlayer()
        self.myScreen.updateScreen()