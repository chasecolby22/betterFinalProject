from botHandler import botHandler
from board import board
from players import *

class game(board):
    def __init__(self):
        super().__init__()
        self.player1 = ""
        self.player2 = ""
        self.activePlayer = ""
        self.turns = 0
        self.movesString = ""
        self.botString = ""
        self.winnerPrinted = False
        self.knowsCheck = False
        
        self.enPassantTile = ""
        self.newPiece = ""
        self.needsPromotion = False
        self.checkers = ""
        self.myBotHandler = botHandler()
        self.botChoice = ""
        self.needsUpdate = True
        self.promotionSquares = ""
        
        self.botStarted = self.myBotHandler.startBot()

    def activePlayerHuman(self):
        return self.activePlayer.isHuman()
    
    def handleEvent(self, aEvent, aTile, botString):
        
        return self.activePlayer.handleEvent(aEvent, aTile, botString)
    
    def getNeedsUpdate(self):
        if self.needsUpdate:
            return True
        if self.player1.needsUpdate:
            return True
        return self.player2.needsUpdate
    
    def clearUpdateFlags(self):

        self.player1.needsUpdate = False
        self.player2.needsUpdate = False

    def moveHumanPiece(self):
        self.movesString += self.activePlayer.tempMoveString + " "
        aTuple = self.activePlayer.humanSelection
        self.resetEventFlags()
        self.movePiece(aTuple[0], aTuple[1], aTuple[2], aTuple[3], aTuple[4], aTuple[5])

    
    def getBotInput(self, aDifficulty):
        self.botString = self.myBotHandler.getBotInput(self.movesString, aDifficulty)[9:14]
        return self.botString
    
    def resetEventFlags(self):
        na = self.getNonActivePlayer()
        na.validPiece = False
        na.dragging = False
        na.mouseDown = False
        na.posibleMoves = ""

    def ccheckers(self):
        return self.checkers
    
    def pposibleMoves(self):
        return self.activePlayer.posibleMoves
    
    def bbotChoice(self):
        
        if self.getNonActivePlayer().matchedBot:
            return ""
        return self.botChoice
    
    def updateKingTiles(self):
        self.assignKingTile(self.player1)
        self.assignKingTile(self.player2)
    
    def assignKingTile(self, aPlayer):
        if aPlayer.needsKingTile:
            dk = aPlayer.king
            aPlayer.kingTile = self.getTile(dk.x, dk.y)
            aPlayer.needsKingTile = False

    def startGame(self, player1bot, player1dif, player2bot, player2dif):
        
        self.player1 = ""
        self.player2 = ""
        self.turns = 0
        self.movesString = ""
        self.botString = ""

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
        self.player1.op = self.player2
        self.player2.op = self.player1
        self.updateKingTiles()
        self.activePlayer = self.player1

        
    def botTurn(self):
        botString = self.getBotInput(self.activePlayer.difficulty)

        botString = self.botInput(botString)
        
        self.activePlayer.takeTurn(botString)
        self.drawBot()
        self.drawCheck()
        t = self.activePlayer.botTuple
        self.movePiece(t[0], t[1], t[2], t[3], t[4], t[5])
        print("Turn " + str(self.turns) + ": The bot choose:  " + botString)
        
        return True

    def drawBot(self):
        anArray = self.getSpecialArray()
        squares = []
        squares.append((anArray[0], anArray[1]))
        squares.append((anArray[2], anArray[3]))
        
        self.botChoice = squares
        self.needsUpdate = True
        

    

    def drawCheck(self):
        if not self.knowsCheck:

            if self.inCheck():
                daKing = self.activePlayer.king
                tempChecker =  self.nonActiveCheckers()
                
                tempChecker.append((daKing.x, daKing.y))
                
                if tempChecker != self.checkers:
                    self.needsUpdate = True
                    self.checkers = tempChecker
                
            else:
                if self.checkers != "":
                    self.checkers = ""
                    self.needsUpdate = True
            self.knowsCheck = True

    def grabPlayerTiles(self, aPlayer):
        tiles = []
        for item in aPlayer.pieces:
            tiles.append(self.getTile(item.x, item.y))
        return tiles
    
    def nonActiveCheckers(self):
        dp = self.getNonActivePlayer()
        return dp.getCheckers(self.grabPlayerTiles(dp))

    def activePlayerHasMove(self):
        dp = self.activePlayer
        return dp.hasMove(self.grabPlayerTiles(dp))


    def hasPiece(self, col, row):
        return self.activePlayer.hasPiece(col, row)
    
    def gameStopped(self):
        if len(self.player1.pieces) == 1 and len(self.player2.pieces) == 1:
            print("The game was a stalemate")
            return True
        if self.activePlayerHasMove():
            return False
        if self.inCheck():
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
    
    def getSpecialArray(self):
        return self.parseThings(self.botString[0], self.botString[1], self.botString[2], self.botString[3])
    
    def botInput(self, aString):
        promote = False
        if len(aString) > 4:
            promote = aString[4]
        
        
        
        self.movesString += aString + " "
        self.botString = aString
        array = self.getSpecialArray()
        array.append(promote)
        return array

    def getNonActivePlayer(self):
        if self.p1act():
            return self.player2
        return self.player1
    
    def p1act(self):
        return self.activePlayer == self.player1
    
    def winner(self):
        if not self.winnerPrinted:
            print(self.getNonActivePlayer().name() + "won!")
            self.winnerPrinted = True

    def inCheck(self):
        return self.getNonActivePlayer().isChecking()
        
    
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

  

    def movePiece(self, aPiece, col, row, enPassantTile, castle, promotion):
        
        destTile = self.getTile(col, row)
        eatenPiece = destTile.piece
        
        if promotion != " ":
       
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
            self.newPiece = aPiece

        
        if eatenPiece != "EMPTY":
            eatenPiece.remove()
        elif aPiece.name() == "pawn" and self.enPassantTile == destTile:
            magicNum = 0
            if self.p1act():
                magicNum = 4
            destTile.getNeighbor(2+magicNum).piece.remove()
        if enPassantTile:
            self.enPassantTile = enPassantTile
            self.player1.enPassantTile = enPassantTile
            self.player2.enPassantTile = enPassantTile
        else:
            self.enPassantTile = ""
            self.player1.enPassantTile = ""
            self.player2.enPassantTile = ""
        if castle:
            magicNum = 0
            if castle[0] == 7:
                magicNum = 2
            self.movePiece(self.getTile(castle[0], self.activePlayer.row).getPiece(), 3+magicNum, self.activePlayer.row, False, False, False)
            self.switchPlayer()

        destTile.setPiece(aPiece)
        aPiece.tile.empty()
        aPiece.setHasMoved(True)
        aPiece.move(col, row)
        self.switchPlayer()
        
        self.needsUpdate = True