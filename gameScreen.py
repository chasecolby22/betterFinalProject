from game import *

pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 182, 193)
blue = (173, 216, 230)

font = pygame.font.SysFont("Arial", 42)


class onScreenTile(pygame.Rect):
    def __init__(self, aRect, aPos, aSurface, aColor, aTileSize):
        super().__init__(aRect[0], aRect[1], aRect[2], aRect[3])
        self.tileSize = aTileSize
        self.pos = aPos
        self.color = aColor
        self.sur = aSurface
        self.border = black
        self.bwidth = 2
        self.surr = ""
        
        self.circleColor = None
        self.draw()

    def highlight(self, aColor):
        self.border = aColor
        self.bwidth = 3

    def reset(self):
        
        self.border = black
        self.bwidth = 2

    def draw(self):
        
        pygame.draw.rect(self.sur, self.color, self)
        pygame.draw.rect(self.sur, self.border, self, width = self.bwidth)

        if self.border != black:
           

            
            surr = pygame.Surface((self.tileSize, self.tileSize), pygame.SRCALPHA)
            surr.fill((self.border[0], self.border[1], self.border[2], self.tileSize))
            
                
            self.sur.blit(surr, self.topleft)
        if self.circleColor != None:
            pygame.draw.circle(self.sur, self.circleColor, self.center, self.tileSize / 3)

class button(pygame.Rect):
    def __init__(self, aRectSpec, aText, aSurface, aLambda, aColor):
        super().__init__(aRectSpec[0], aRectSpec[1], aRectSpec[2], aRectSpec[3])
        self.text = font.render(aText, True, black)
        self.text_rect = self.text.get_rect(center=self.center)
        self.sur = aSurface
        self.color = aColor
        self.oldColor = ""
        
        self.myLambda = aLambda
        
    def draw(self):

        pygame.draw.rect(self.sur, self.color, self)
        self.sur.blit(self.text, self.text_rect)
        
        

    def handleEvent(self, aEvent, aScreen):
        handled = False
        clicked = False
        if aEvent.type == pygame.MOUSEMOTION:
            if self.collidepoint(aEvent.pos):
                
                if self.oldColor == "":
                    
                    self.oldColor = self.color
                    self.color = (0, 0, 255)
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    aScreen.needsUpdate = True
                handled = True
            else:
                
                if self.oldColor != "":
                       
                        self.color = self.oldColor
                        self.oldColor = ""
                        aScreen.needsUpdate = True
        elif aEvent.type == pygame.MOUSEBUTTONUP:
            if aEvent.button == 1:
                if self.collidepoint(aEvent.pos):
                    
                    self.myLambda()
                    clicked =  True
        return clicked, handled
        
class onScreenChar():
    def __init__(self, char, x, y, aSur, aTileSize):
        tileFont = pygame.font.SysFont("Arial", aTileSize)
        self.letter = tileFont.render(char, True, black)
        self.pos = (100 + x * aTileSize + aTileSize / 2, 50 + y * aTileSize + aTileSize / 2)
        self.rect = self.letter.get_rect(center=self.pos)
        self.sur = aSur
        self.draw()
    
    def draw(self):
        self.sur.blit(self.letter, self.rect)

class gameScreen():

    def gatherSprites(self):
        self.game.gatherBaseSprites(self.allsprites)
        
        
    def menuHandle(self, aEvent):
        if self.game.menuHandle(aEvent):
            self.menuDrawn = False
            for item in self.specialsprites:
                item.kill()

    def drawMenu(self):
        if not self.menuDrawn:
            self.game.gatherSpecialSprites(self.specialsprites)
            self.menuDrawn = True
            self.updateScreen()

   


    def clearUpdateFlags(self):
        self.needsUpdate = False
        self.game.clearUpdateFlags()
    def __init__(self):
        
        self.allsprites = pygame.sprite.Group()
        self.specialsprites = pygame.sprite.Group()
        self.drawnBoard = False
        self.menuDrawn = False
        self.tileSize = 75
        
        self.needsUpdate = False
        self.continueButton = None
        self.tiles = []
        self.sur = ""
        self.game = ""

    def initializeGame(self, aLambda):
        array = aLambda()
        self.game = chess(array[0], array[1], array[2], array[3], self.tileSize)
        self.width = array[0]
        self.height = array[1]

    def standard(self):
        return lambda: chess.standard()
        

    def addSprite(self, aSprite):
        self.allsprites.add(aSprite)

    def literallyDrawBoard(self):
        dw = True
        self.chars = []
        self.tiles = []
        
        for i in range(self.width):
            self.chars.append(onScreenChar(chr(i+ord("A")), i, self.height, self.sur, self.tileSize))
        for i in range(self.height):
            self.chars.append(onScreenChar(str(self.height - i), self.width, i, self.sur, self.tileSize))
        for item in self.chars:
            item.draw()
        for i in range(self.height):
            row = []
            for j in range(self.width):
                color = pink
                if dw:
                    
                    color = blue
                
                if j != 7:
                    dw = not dw
                    
                tile = onScreenTile((100+j*self.tileSize, 50+i*self.tileSize, self.tileSize, self.tileSize), (j, (self.height-1)-i), self.sur, color, self.tileSize)
                tile.draw()
                row.append(tile)
            self.tiles.append(row)
        self.game.updateTiles(self.tiles)
        
        self.drawnBoard = True
        
    def drawBoard(self):
        
        pygame.draw.rect(self.sur, black, pygame.Rect(99, 50-1, self.tileSize * self.width + 2, self.tileSize * self.height + 2), width=2)
        onScreenChar(str(math.ceil((1+self.game.turns)/2)), self.width//2, self.height + 1, self.sur, self.tileSize).draw()
        
        if not self.drawnBoard:
            self.literallyDrawBoard()
        else:
            for row in self.tiles:
                for item in row:
                    item.draw()
            for item in self.chars:
                item.draw()

  
    
    def reset(self):
        for row in self.tiles:
            for item in row:
                item.circleColor = None

    def updateScreen(self):
        if self.needsUpdate or self.game.getNeedsUpdate():
            
            
            self.sur.fill(white)
            self.reset()
            self.game.prepare()
            self.drawBoard()
    
            
            self.drawSprites()
            if self.continueButton != None: self.continueButton.draw()
            pygame.display.update()
            self.clearUpdateFlags()

        
    def drawSprites(self):
        self.allsprites.draw(self.sur)
        self.specialsprites.draw(self.sur)
        

    def returnButton(self, anX, aText, aLambda):
        return button((anX, 50, 200, 100), aText, self.sur, aLambda, (0, 255, 255))
    
    def startBotGame(self):
        
        self.startGame(self.standard(), 5, 10)
   

    def startStandardGame(self):
        
        self.startGame(self.standard())
    
    def startTest(self):
        
        self.startGame(lambda: chess.test())

    def startGame(self, aLambda, x = 0, y = 0):
        self.initializeGame(aLambda)
        self.makeMainScreen()
        self.game.startGame(x, y)
        self.gatherSprites()
        self.drawBoard()
        self.updateScreen()

    def drawStartScreen(self):
        if self.needsUpdate:
            
            
            
            self.sur.fill(white)
            
            for item in self.buttons:
                
                item.draw()
            pygame.display.update()
            self.needsUpdate = False

    def setUpStartScreen(self):
        self.sur = pygame.display.set_mode((1000, 400))
        self.sur.fill(white)
       
        self.buttons = []
        self.buttons.append(self.returnButton(50, "No Bots", lambda: self.startStandardGame()))
        self.buttons.append(self.returnButton(350, "Bots", lambda: self.startBotGame()))
        self.buttons.append(self.returnButton(650, "test", lambda: self.startTest()))
        self.needsUpdate = True
        self.drawStartScreen()

    def endMenuHandle(self, handled, clicked):
        if not handled:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if clicked:
            return True
        return False

    def startHandle(self, anEvent):
        
        clicked = False
        handled = False
        for butt in self.buttons:
            newclicked, newhandled = butt.handleEvent(anEvent, self)
            if not clicked:
                  
                clicked = newclicked
            
            if not handled:
                handled = newhandled
        return self.endMenuHandle(handled, clicked)
        
    def continueHandle(self, anEvent):
        clicked, handled = self.continueButton.handleEvent(anEvent, self)
        return self.endMenuHandle(handled, clicked)
        
    def decrementTileSize(self):
        if self.tileSize - 5 > 10:
            self.tileSize -= 5
            self.drawnBoard = False
            self.game.updateTileSize(self.tileSize)
            self.resizeScreen()
            

    def incrementTileSize(self):
        if self.tileSize + 5 < 150:
            self.tileSize += 5
            self.drawnBoard = False
            self.game.updateTileSize(self.tileSize)
            self.resizeScreen()

            
        
    def startNewGame(self):
        self.setUpStartScreen()
        self.continueButton = None

    def run(self):
        
        self.setUpStartScreen()
        running = True
        gameOver = False
        clock = pygame.time.Clock()
        gameStarted = False
       
        while running:
            
                
            eventList = pygame.event.get()
            if len(eventList) == 0:
                if gameStarted:
                    
                    self.game.handleNoEvent()
                    
            for event in eventList:
                
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEWHEEL:
                    
                    if event.y == -1:
                        self.decrementTileSize()
                    elif event.y == 1:
                        self.incrementTileSize()
                else:
                    
                    if not gameStarted:
                        
                        if self.startHandle(event):
                           
                           gameStarted = True    
                        self.drawStartScreen() 
                        
                        
                    elif self.game.needsMenu:
                        self.drawMenu()
                        self.menuHandle(event)
                        

                                
                    else:
                        self.game.drawCheck()
                      
                        if isMouseEvent(event):
                            if gameOver:
                                
                                if self.continueHandle(event):
                                    gameOver = False
                                    gameStarted = False
                                    self.drawnBoard = False
                                    self.allsprites.empty()
                                else:
                                    self.game.handleEvent(event)
                                    
                                
                                    
                            else:
                                if self.game.gameRunning():
                                    if self.game.activePlayerHuman():
                                        anArray = self.game.handleEvent(event)
                                        
                                    
                                        if anArray[0]:
                                            "Code here incase needed later, user has made a valid move"
                                        if not anArray[1] and anArray[0]:
                                            
                                            self.game.moveHumanPiece()
                                        
                                else:
                                    
                                    gameOver = True
                                    
                                    self.continueButton = button((self.width*self.tileSize+175, 50+self.height*self.tileSize, 200, 50), "New Game", self.sur, lambda: self.startNewGame(), (0, 100, 0))
                                    self.needsUpdate = True
                                    
                                
                                
                                
            if gameStarted:
                
                self.updateScreen()
                clock.tick(60)
                
    def getScreenSize(self):
        return (self.width*self.tileSize + 400, self.height*self.tileSize + 200)

    def resizeScreen(self):
        newScreenSize = self.getScreenSize()
        if newScreenSize[0] > self.screenSize[0] or newScreenSize[1] > self.screenSize[1]:
            self.screenSize = newScreenSize
            self.drawMainScreen()

    def drawMainScreen(self):
        self.sur = pygame.display.set_mode((self.screenSize))

    def makeMainScreen(self):
        self.screenSize = self.getScreenSize()
        self.drawMainScreen()

def isMouseEvent(aEvent):
    return aEvent.type == pygame.MOUSEMOTION or aEvent.type == pygame.MOUSEBUTTONDOWN or aEvent.type == pygame.MOUSEBUTTONUP