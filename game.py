from botHandler import botHandler
from board import board
from players import *

 

class game(board):

    def gatherSpecialSprites(self, aGroup):
        for item in self.specialPieces:
            aGroup.add(item)
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
        if self.needsUpdate:
            return True
        if self.player1.needsUpdate:
            return True
        return self.player2.needsUpdate
    
    def clearUpdateFlags(self):
       
        self.needsUpdate = False
           
        self.player1.needsUpdate = False
        self.player2.needsUpdate = False



class chess(game):

    def handleNoEvent(self):
        if self.gameStopped(): return False
        if self.activePlayer.isHuman(): return False
        self.botTurn()
        return True

    def collidesSpecial(self, aPos):
        for item in self.specialPieces:
            if item.rect.collidepoint(aPos):
                return item
        return False
    
    def menuHandle(self, anEvent):
      
            
        if anEvent.type == pygame.MOUSEMOTION:
            if self.collidesSpecial(anEvent.pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif anEvent.type == pygame.MOUSEBUTTONUP:
            item = self.collidesSpecial(anEvent.pos)
            if item:
                self.setPromotion(item.pro())
                
                self.specialPieces = []
                self.needsMenu = False
                return True
        return False
    
    @classmethod
    def standardPieceList(cls):
        return [[pawn, pawn, pawn, pawn, pawn, pawn, pawn, pawn], [rook, knight, bishop, queen, king, bishop, knight, rook]]

    @classmethod
    def test(cls):
        return [[pawn, pawn, pawn, pawn], [rook, queen, king, rook]]
    
    def __init__(self, width, height, pieceList, wantsBot):

        
        super().__init__(width, height, pieceList)
        
        self.botString = ""
        self.knowsCheck = False
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

    def setPromotion(self, a):
        self.activePlayer.setPromotion(a)
        self.finishSelection()

    def activePlayerHuman(self):
        return self.activePlayer.isHuman()
        
    def drawPos(self):
        pos = False
        for tile in self.posibleMoves():
            if tile.rect.border == (255, 100, 0): tile.rect.reset()
            tile.rect.circleColor = (255, 150, 0)

            pos = True
        return pos
    
    def prepare(self):
        if self.drawPos():
            pass
        else:
            self.drawCheck()
            self.drawBot()


    def handleEvent(self, aEvent):
        theTile = False
        pos = aEvent.pos
        for tile in self.getTiles():
            
            if tile.collidepoint(pos):
                theTile = tile
                break
        
        result = self.activePlayer.handleEvent(aEvent, theTile, self.botString, self.grabPlayerTiles(self.getNonActivePlayer()))
        if self.activePlayer.promotionNeeded: 
            self.needsMenu = True
            self.drawPromotion()
        return result
    
    def drawPromotion(self):
        array = [7, 5, 3, 1]
        if self.height < 5:
            array = [3, 2, 1, 0]
        self.specialPieces.append(dumbQueen(self.width+1, array[0], self.color(), self.height))
        self.specialPieces.append(dumbRook(self.width+1, array[1], self.color(), self.height))
        self.specialPieces.append(dumbBishop(self.width+1, array[2], self.color(), self.height))
        self.specialPieces.append(dumbKnight(self.width+1, array[3], self.color(), self.height))
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
    
    def updateKingTiles(self):
        self.runBoth(lambda a: self.assignKingTile(a))
        
    
    def assignKingTile(self, aPlayer):
        
        dk = aPlayer.king
        aPlayer.kingTile = self.getTile(dk.x, dk.y)
        aPlayer.needsKingTile = False
       
    def startGame(self, player1dif, player2dif):
        
        self.player1 = ""
        self.player2 = ""
        self.turns = 0
        self.movesString = ""
        self.botString = ""

        if not self.botStarted:
            print("Sorry bot is sleepy")
            self.player1 = humanPlayer(True, self.pieceList, self.height)
            self.player2 = humanPlayer(False, self.pieceList, self.height)
            
        
        else:
            if player1dif != 0:
                self.player1 = botPlayer(True, player1dif, self.pieceList, self.height)
            else:
                self.player1 = humanPlayer(True, self.pieceList, self.height)
            if player2dif != 0:
                self.player2 = botPlayer(False, player2dif, self.pieceList, self.height)
            else:
                self.player2 = humanPlayer(False, self.pieceList, self.height)
        self.player1.start()
        self.player2.start()
        self.updateKingTiles()
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
                item.rect.circleColor = (0, 100, 0) 

    

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
                            item.rect.reset()
                        self.checkers = ""
                self.knowsCheck = True
            
            
                    
            for item in self.checkers:
                item.rect.highlight((255, 100, 0))

            
        

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
        aPiece.kill()
        aTile.empty()


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
            aPiece.changeImage()
        
        if eatenPiece != "EMPTY":
            self.eatPiece(eatenPiece, destTile)
            
        elif aPiece.name() == "pawn" and self.enPassantTile == destTile:
            magicNum = 0
            if self.p1act():
                magicNum = 4
            theOnePiece = destTile.getNeighbor(2+magicNum).piece
            self.eatPiece(theOnePiece, destTile)
            
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
            self.turns -= 1

        destTile.setPiece(aPiece)
        
        startTile.empty()
        aPiece.setHasMoved(True)
        aPiece.move(col, row)
        if aPiece.isKing(): self.activePlayer.kingTile = destTile
        self.switchPlayer()
        self.knowsCheck = False
        self.oldBotString = self.botString
        self.needsUpdate = True