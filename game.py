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
        self.winnerPrinted = False
        self.needsUpdate = True

    def getNonActivePlayer(self):
        if self.p1act():
            return self.player2
        return self.player1

    def runBoth(self, aLambda):
        aLambda(self.player1)
        aLambda(self.player2)

    def attachPieces(self, aPlayer):
        for item in aPlayer.pieces:
            pos = item.getPos()
            self.getTile(pos[0], pos[1]).piece = item

    def attachAll(self):
        self.runBoth(lambda a: self.attachPieces(a))

    def getNeedsUpdate(self):
        if self.needsUpdate:
            return True
        if self.player1.needsUpdate:
            return True
        return self.player2.needsUpdate
    
    def clearUpdateFlags(self):
       
        self.needsUpdate = False
           
        self.player1.needsUpdate = False
        self.player2.needsUpdate = False

    def eatPieces(self, aPlayer):
        for piece in aPlayer.pieces:
            if piece.needsRemoved:
                aPlayer.removePiece(piece)



class chess(game):
    def __init__(self):
        super().__init__()
        
        self.botString = ""
        self.knowsCheck = False
        self.enPassantTile = ""
        
        self.checkers = ""
        self.myBotHandler = botHandler()
        self.botChoice = ""
        self.botStarted = self.myBotHandler.startBot()

    def setPromotion(self, a):
        self.activePlayer.setPromotion(a)
        self.finishSelection()

    def activePlayerHuman(self):
        return self.activePlayer.isHuman()
    
   

    def handleEvent(self, aEvent, aTile):
        theTile = False
        if aTile: theTile = self.getTile(aTile[0], aTile[1])
        return self.activePlayer.handleEvent(aEvent, theTile, self.botString, self.grabPlayerTiles(self.getNonActivePlayer()))
    
    
    def moveHumanPiece(self):
        self.movesString += self.activePlayer.tempMoveString + " "
        self.moveThePiece()
        
        self.resetEventFlags()
        

    def getBotInput(self, aDifficulty):
        self.botString = self.myBotHandler.getBotInput(self.movesString, aDifficulty)[9:14]
        return self.botString
    
    def resetEventFlags(self):
        na = self.getNonActivePlayer()
        na.validPiece = False
        na.dragging = False
        na.mouseDown = False
        na.posibleMoves = ""
        na.validPieceOgPos = ""
        na.validPieceTile = ""

    def ccheckers(self):
        return self.checkers
    
    def pposibleMoves(self):
        return self.activePlayer.posibleMoves
    
    def bbotChoice(self):
        
        return self.botChoice
    
    def updateKingTiles(self):
        self.runBoth(lambda a: self.assignKingTile(a))
        
    
    def assignKingTile(self, aPlayer):
        if aPlayer.needsKingTile:
            dk = aPlayer.king
            aPlayer.kingTile = self.getTile(dk.x, dk.y)
            aPlayer.needsKingTile = False

    def attachOpponent(self, aPlayer):
        value = self.player1
        if aPlayer == value:
            value = self.player2
        for piece in aPlayer.pieces:
            piece.setOp(value)

    def attachOp(self):
        self.runBoth(lambda a: self.attachOpponent(a))
       

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
        self.updateKingTiles()
        self.attachAll()
        self.attachOp()
        self.activePlayer = self.player1

    def finishSelection(self):
        self.activePlayer.finishSelection(self.botString, self.grabPlayerTiles(self.getNonActivePlayer()))
        self.moveHumanPiece()

    def moveThePiece(self):
        t = self.activePlayer.tuple
        self.movePiece(t[0], t[1], t[2], t[3], t[4], t[5], t[6])
    
    def botTurn(self):
        botString = self.getBotInput(self.activePlayer.difficulty)

        botThing = self.botInput(botString)
        
        self.activePlayer.takeTurn(botThing, self.getTiles(), self.grabPlayerTiles(self.getNonActivePlayer()))
        
        self.moveThePiece()
        self.drawBot()
        self.drawCheck()
        self.needsUpdate = True
        print("Turn " + str(self.turns) + ": The bot choose:  " + botString)
        
        return True

    def drawBot(self):
        
        if not self.getNonActivePlayer().didMatchBot():
            
            anArray = self.getSpecialArray()
            squares = []
            squares.append((anArray[0], anArray[1]))
            squares.append((anArray[2], anArray[3]))
            
            self.botChoice = squares
            
        else:
            
            self.botChoice = ""
        

    

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
        return dp.getCheckers(self.grabPlayerTiles(dp), self.activePlayer.kingTile)

    def activePlayerHasMove(self):
        dp = self.activePlayer
        return dp.hasMove(self.grabPlayerTiles(dp), self.grabPlayerTiles(self.getNonActivePlayer()))
    
    def gameStopped(self):
        if len(self.player1.pieces) == 1 and len(self.player2.pieces) == 1:
            if not self.winnerPrinted:
                print("The game was a stalemate")
                self.winnerPrinted = True
            return True
        if self.activePlayerHasMove():
            return False
        if self.inCheck():
            self.winner()
        else:
            if not self.winnerPrinted:
                print("The game was a stalemate")
                self.winnerPrinted = True
        return True
    
    def parseThings(self, a, b, c, d):
        row = int(b) - 1
        col = ord(a) - ord('a')
        newRow = int(d) - 1
        newCol = ord(c) - ord('a')
        return [col, row, newCol, newRow]
    
    def getBotSpecialArray(self):
        return self.parseThings(self.botString[0], self.botString[1], self.botString[2], self.botString[3])
    
    def getSpecialArray(self):
        return self.parseThings(self.oldBotString[0], self.oldBotString[1], self.oldBotString[2], self.oldBotString[3])
    
    def botInput(self, aString):
        promote = False
        if len(aString) > 4:
            promote = aString[4]
        
        
        
        self.movesString += aString + " "
        self.botString = aString
        array = self.getBotSpecialArray()
        array.append(promote)
        return array

    
    
    def p1act(self):
        return self.activePlayer == self.player1
    
    def winner(self):
        if not self.winnerPrinted:
            print(self.getNonActivePlayer().name() + "won!")
            self.winnerPrinted = True

    def inCheck(self):
        return self.getNonActivePlayer().isChecking(self.grabPlayerTiles(self.getNonActivePlayer()), self.activePlayer.kingTile)
        
    
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

    def eatAllPieces(self):
        self.eatPieces(self.player1)
        self.eatPieces(self.player2)
  

    def movePiece(self, aPiece, col, row, enPassantTile, castle, promotion, startTile):
        
        destTile = self.getTile(col, row)
        eatenPiece = destTile.piece
        
        if promotion != " ":
            '''
            aPiece.remove(startTile)
            match promotion:
                case "q":
                    aPiece = queen(-2, -2, self.activePlayer.getColor())
                case "n":
                    aPiece = knight(-2, -2, self.activePlayer.getColor())
                case "r":
                    aPiece = rook(-2, -2, self.activePlayer.getColor())
                case "b":
                    aPiece = bishop(-2, -2, self.activePlayer.getColor())
            self.activePlayer.addPiece(aPiece)
            aPiece.setOp(self.getNonActivePlayer())
            self.newPiece = aPiece
            '''
            thing = ""
            match promotion:
                case "queen":
                    thing = queen
                case "knight":
                    thing = knight
                case "rook":
                    thing = rook
                case "bishop":
                    thing = bishop
            aPiece.__class__ = thing
            aPiece.changeImage()
        
        if eatenPiece != "EMPTY":
            eatenPiece.remove(destTile)
        elif aPiece.name() == "pawn" and self.enPassantTile == destTile:
            magicNum = 0
            if self.p1act():
                magicNum = 4
            destTile.getNeighbor(2+magicNum).piece.remove(destTile)
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
            theTile = self.getTile(castle[0], self.activePlayer.row)
            self.movePiece(theTile.getPiece(), 3+magicNum, self.activePlayer.row, False, False, " ", theTile)
            self.switchPlayer()

        destTile.setPiece(aPiece)
        
        startTile.empty()
        aPiece.setHasMoved(True)
        aPiece.move(col, row)
        self.switchPlayer()
        self.knowsCheck = False
        self.eatAllPieces()
        self.oldBotString = self.botString
        self.needsUpdate = True