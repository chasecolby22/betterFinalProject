from botHandler import botHandler
from board import board
from players import *

 

class game(board):

    def dragging(self):
        return self.activePlayer.dragging
    
    def validPiece(self):
        return self.activePlayer.validPiece

    def gatherSpecialSprites(self, aGroup):
        for item in self.specialPieces:
            aGroup.append(item)
        self.needsUpdate = True

    def gatherBaseSprites(self, aGroup):
        
        self.runBoth(lambda a: a.addPieces(aGroup) )
        
    def __init__(self, width, height, pieceList):
        super().__init__(width, height)
        self.player1 = ""
        self.player2 = ""
        self.pieceList = pieceList
        self.activePlayer = ""
        self.turns = 0
        
        self.movesString = ""
        self.needsMenu = False
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
        return self.needsUpdate or self.player1.needsUpdate or self.player2.needsUpdate
        
    
    def clearUpdateFlags(self):
       
        self.needsUpdate = False
           
        self.player1.needsUpdate = False
        self.player2.needsUpdate = False


class chess(game):

    @classmethod
    def standardGame(cls, aScreen):
        thing = cls(8, 8, cls.standardPieceList(), True)
        thing.startGame(0, 0)
        aScreen.game = thing
        aScreen.startGame()
        
    
    @classmethod
    def botGame(cls, aScreen):
        thing = cls(8, 8, cls.standardPieceList(), True)
        thing.startGame(5, 10)
        aScreen.game = thing
        aScreen.startGame()
    
    @classmethod
    def startTest(cls, aScreen):
        thing = cls(16, 4, cls.testPieceList(), True)
        thing.startGame(0, 0)

        aScreen.game = thing
        aScreen.startGame() 

    @classmethod
    def grabThings(cls):
        
        return ["No Bots", lambda aScreen: cls.standardGame(aScreen), "Bots", lambda aScreen: cls.botGame(aScreen), "test", lambda aScreen: cls.startTest(aScreen)]
    
    @classmethod
    def standardPieceList(cls):
        return [[pawn, pawn, pawn, pawn, pawn, pawn, pawn, pawn], [rook, knight, bishop, queen, king, bishop, knight, rook]]

    @classmethod
    def testPieceList(cls):
        return [[pawn, pawn, None, pawn, pawn, pawn, pawn, pawn, pawn, pawn, pawn, pawn, pawn, pawn, pawn, pawn], [rook, rook, knight, knight, bishop, bishop, queen, queen, king, queen, bishop, bishop, None, knight, rook, rook]]
    

    
    def __init__(self, width, height, pieceList, wantsBot):

        
        super().__init__(width, height, pieceList)
        
        self.botString = ""
        self.knowsCheck = False
        self.theGameIsStopped = False
        self.knowsGameIsStopped = False
        self.knowsBot = False
        self.enPassantTile = ""
        self.width = width
        self.height = height
        self.specialPieces = []
        self.checkers = ""
        if wantsBot:
            self.myBotHandler = botHandler()
            self.botChoice = ""
            self.botStarted = self.myBotHandler.startBot()
        else:
            self.botStarted = False

    
    def handleNoEvent(self):
        if not self.gameRunning(): return False
        if self.activePlayer.isHuman(): 
            
            self.activePlayer.handleNoEvent()
        else: self.botTurn()
        return True
    
    def clearKnowsFlags(self):
        self.knowsBot = False
        self.knowsCheck = False
        self.knowsGameIsStopped = False

    def setPromotion(self, a):
        self.activePlayer.setPromotion(a)
        self.finishSelection()

    def activePlayerHuman(self):
        return self.activePlayer.isHuman()
        
    def drawPos(self):
        pos = False
        for tile in self.posibleMoves():
            if tile.border == (255, 100, 0): tile.reset()
            tile.circleColor = (255, 150, 0)
            tile.different = True

            pos = True
        return pos
    
    def prepare(self):
        if self.drawPos():
            pass
        else:
            self.drawCheck()
            self.drawBot()


    def handleEvent(self, aEvent, theTile):
        if self.activePlayerHuman():
            
            
            result = self.activePlayer.handleEvent(aEvent, theTile, self.grabBotString(), self.grabPlayerTiles(self.getNonActivePlayer()), self.gameRunning())
            if self.activePlayer.promotionNeeded: 
                self.needsMenu = True
                self.drawPromotion()
            return result
    
    def drawPromotion(self):
        array = [7, 5, 3, 1]
        if self.height < 5:
            array = [3, 2, 1, 0]
        self.specialPieces.append(dumbQueen(self.width+1, array[0], self.color()))
        self.specialPieces.append(dumbRook(self.width+1, array[1], self.color()))
        self.specialPieces.append(dumbBishop(self.width+1, array[2], self.color()))
        self.specialPieces.append(dumbKnight(self.width+1, array[3], self.color()))
        self.needsUpdate = True

    
    
    def moveHumanPiece(self):
        self.movesString += self.activePlayer.tempMoveString + " "
        self.moveThePiece()
        
        self.resetEventFlags()
        

    def getBotInput(self, aDifficulty):
        if self.botStarted:
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
    
    def posibleMoves(self):
        
        return self.activePlayer.posibleMoves
    
    def bbotChoice(self):
        return self.botChoice
    
    def createPlayer1(self, aDifficulty = 0):
        if aDifficulty == 0:
            self.createHumanPlayer1()
        else:
            self.createBotPlayer1(aDifficulty)
    
    def createPlayer2(self, aDifficulty = 0):
        if aDifficulty == 0:
            self.createHumanPlayer2()
        else:
            self.createBotPlayer2(aDifficulty)

    def createHumanPlayer1(self):
        self.player1 = humanPlayer(True, self.pieceList, self.height)

    def createHumanPlayer2(self):
        self.player2 = humanPlayer(False, self.pieceList, self.height)

    def createBotPlayer1(self, aDifficulty):
        self.player1 = botPlayer(True, aDifficulty, self.pieceList, self.height)

    def createBotPlayer2(self, aDifficulty):
        self.player2 = botPlayer(False, aDifficulty, self.pieceList, self.height)
       
    def startGame(self, player1dif, player2dif):
        
        self.player1 = ""
        self.player2 = ""
        self.turns = 0
        self.movesString = ""
        self.botString = ""
        
        if not self.botStarted:
            print("Sorry bot is sleepy")
            self.createHumanPlayer1()
            self.createHumanPlayer2()
        
        else:
            self.createPlayer1(player1dif)
            self.createPlayer2(player2dif)
            
        self.player1.start()
        self.player2.start()
        self.player1.kingTile = self.getTile(self.player1.king.x, self.player1.king.y)
        self.player2.kingTile = self.getTile(self.player2.king.x, self.player2.king.y)
        self.attachAll()
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
        print("Turn " + str(math.ceil(self.turns/2)) + ": The " + self.getNonActivePlayer().name() + "bot choose:  " + botString)
        
        time.sleep(.25)
        return True

    def drawBot(self):
       
        if self.botStarted:
            
            if not self.getNonActivePlayer().didMatchBot():
                
                anArray = self.getSpecialArray()
                squares = []
                squares.append(self.getTile(anArray[0], anArray[1]))
                squares.append(self.getTile(anArray[2], anArray[3]))
                
                self.botChoice = squares
                
            else:
                
                self.botChoice = ""
            
            for item in self.botChoice:
                
                item.circleColor = (0, 100, 0) 
                item.different = True

    

    def drawCheck(self):
        if not self.activePlayer.dragging:
            if not self.knowsCheck:

                if self.inCheck():
                    daKing = self.activePlayer.king
                    tempChecker =  self.nonActiveCheckers()
                    
                    tempChecker.append(self.getTile(daKing.x, daKing.y))
                    
                    if tempChecker != self.checkers:
                        
                        self.checkers = tempChecker
                    
                else:
                    if self.checkers != "":
                        for item in self.checkers:
                            item.reset()
                        self.checkers = ""
                self.knowsCheck = True
            
            
                    
            for item in self.checkers:
                item.highlight((255, 100, 0))

            
        

    def grabPlayerTiles(self, aPlayer):
        tiles = []
        for item in aPlayer.pieces:
            tiles.append(self.getTile(item.x, item.y))
        return tiles
    
    def nonActiveCheckers(self):
        dp = self.getNonActivePlayer()
        theCheckers = dp.getCheckers(self.grabPlayerTiles(dp), self.activePlayer.kingTile)
        array = []
        for item in theCheckers:
            array.append(self.getTile(item[0], item[1]))
        return array

    def activePlayerHasMove(self):
        dp = self.activePlayer
        return dp.hasMove(self.grabPlayerTiles(dp), self.grabPlayerTiles(self.getNonActivePlayer()))
    

    def gameRunning(self):
        if not self.knowsGameIsStopped:
       
            self.theGameIsStopped = self.gameStopped()
            self.knowsGameIsStopped = True
        return not self.theGameIsStopped
    
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
        promote = " "
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
        
        return len(self.nonActiveCheckers()) > 0
        
    
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

  
    def setEnPassantTile(self, a):
        self.enPassantTile = a
        self.player1.setEnPassantTile(a)
        self.player2.setEnPassantTile(a)

    def clearEnPassantTile(self):
        self.enPassantTile = ""
        self.player1.clearEnPassantTile()
        self.player2.clearEnPassantTile()
            
    def eatPiece(self, aPiece, aTile):
        self.getNonActivePlayer().pieces.remove(aPiece)
        aPiece.wantsEaten = True
        aTile.empty()

    def grabBotString(self):
        if self.botStarted:
            if not self.knowsBot:
                self.getBotInput(10)
                self.knowsBot = True
        return self.botString

    def movePiece(self, aPiece, col, row, enPassantTile, castle, promotion, startTile):
        
        destTile = self.getTile(col, row)
        eatenPiece = destTile.piece
        
        if promotion != " ":
            
            thing = ""
            match promotion:
                case "q":
                    thing = queen
                case "n":
                    thing = knight
                case "r":
                    thing = rook
                case "b":
                    thing = bishop
            
            aPiece.__class__ = thing
            aPiece.needsChanged = True
            
        
        if eatenPiece != "EMPTY":
            self.eatPiece(eatenPiece, destTile)
            
        elif aPiece.name() == "pawn" and self.enPassantTile == destTile:
            magicNum = 0
            if self.p1act():
                magicNum = 4
            theOneTile = destTile.getNeighbor(2+magicNum)
            theOnePiece = theOneTile.piece
            
            self.eatPiece(theOnePiece, theOneTile)
            
        if enPassantTile:
            self.setEnPassantTile(enPassantTile)
            
        else:
            self.clearEnPassantTile()
        if castle:
            magicNum = 0
            if castle[0] == 7:
                magicNum = 2
            theTile = self.getTile(castle[0], self.activePlayer.row)
            self.movePiece(theTile.getPiece(), 3+magicNum, self.activePlayer.row, False, False, " ", theTile)
            self.switchPlayer()
            self.turns -= 2

        destTile.setPiece(aPiece)
        
        startTile.empty()
        aPiece.setHasMoved(True)
        aPiece.move(col, row)
        if aPiece.isKing(): self.activePlayer.kingTile = destTile
        self.switchPlayer()
        self.clearKnowsFlags()
        self.oldBotString = self.botString
        self.activePlayer.hasMadeMove = True
        self.needsUpdate = True