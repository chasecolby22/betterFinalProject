from game import *

pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 182, 193)
blue = (173, 216, 230)

font = pygame.font.SysFont("Arial", 42)


class onScreenTile(pygame.Rect):
    def __init__(self, aRect, aPos, aColor, aTileSize, aCompanion):
        super().__init__(aRect[0], aRect[1], aRect[2], aRect[3])
        self.tileSize = aTileSize
        self.pos = aPos
        self.companion = aCompanion
        self.color = aColor
        
        self.surr = ""
    
    def draw(self, aSurface):
        
        pygame.draw.rect(aSurface, self.color, self)
        border = self.companion.border
        if border == "black": border = black
        pygame.draw.rect(aSurface, border, self, width = self.companion.bwidth)

        if border != black:
           

            
            surr = pygame.Surface((self.tileSize, self.tileSize), pygame.SRCALPHA)
            surr.fill((border[0], border[1], border[2], 105))
            
                
            aSurface.blit(surr, self.topleft)
        if self.companion.circleColor != None:
            pygame.draw.circle(aSurface, self.companion.circleColor, self.center, self.tileSize / 3)

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
                    clicked = True
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

class onScreenSprite(pygame.sprite.Sprite):
    def __init__(self, aCompanion, aTileSize, aHeight):
        super().__init__()
        self.x = aCompanion.x
        self.y = aCompanion.y
        self.companion = aCompanion
        self.coords = ""
        self.image = False
        self.rawImage = False
        self.tileSize = aTileSize
        self.height = aHeight
        self.move()


    def updateTileSize(self, newTileSize):
        self.tileSize = newTileSize
        self.move()
        self.changeImage()

    def move(self):
        if not self.image:
            self.changeImage()
        self.coords = (100 + self.x * self.tileSize, 50 + (self.tileSize * ((self.height - 1) - self.y)))
        self.rect = self.image.get_rect(topleft = self.coords)
    
    def changeImage(self):
        transform = self.tileSize / 75
        if not self.rawImage:
            self.rawImage = "./" + self.companion.color + "/" + self.companion.name() + ".png"
        self.image = pygame.image.load(self.rawImage).convert_alpha()
        if transform != 1: self.image = pygame.transform.smoothscale_by(self.image, transform)

    def collidepoint(self, aPos):
        self.rect.collidepoint(aPos)

    def getPos(self):
        return (self.x, self.y)
    
    def setPos(self, aPos):
        self.coords = (aPos[0], aPos[1])
        self.rect = self.image.get_rect(center = self.coords)

    def update(self):
        if self.companion.wantsEaten:
            self.kill()
            return
        if self.companion.needsChanged:
            self.rawImage = False
            self.changeImage()
            self.companion.needsChanged = False
        daX = self.companion.x
        daY = self.companion.y
        if self.x != daX or self.y != daY:
            self.x = daX
            self.y = daY
            self.move()

class gameScreen():

    def convertSprites(self, aLambda, aGroup):
        array = []
        aLambda(array)
        for item in array:
            aGroup.add(onScreenSprite(item, self.tileSize, self.height))
            
    def gatherSprites(self):
        self.convertSprites(lambda array: self.game.gatherBaseSprites(array), self.allsprites)
        
        
    def menuHandle(self, aEvent):
        if self.gameMenuHandle(aEvent):
            self.menuDrawn = False
            for item in self.specialsprites:
                item.kill()

    def drawMenu(self):
        if not self.menuDrawn:
            self.convertSprites(lambda array: self.game.gatherSpecialSprites(array), self.specialsprites)
            self.menuDrawn = True
            self.updateScreen()


    def clearUpdateFlags(self):
        self.needsUpdate = False
        self.game.clearUpdateFlags()

    def __init__(self):
        
        self.allsprites = pygame.sprite.LayeredUpdates()
        self.specialsprites = pygame.sprite.Group()
        self.drawnBoard = False
        self.menuDrawn = False
        self.tileSize = 75
        self.validPiece = None
        self.background = None
        self.needsUpdate = False
        self.continueButton = None
        self.tiles = []
        self.sur = ""
        self.game = ""

    def initializeGame(self, aLambda):
        array = aLambda()
        self.game = chess(array[0], array[1], array[2], array[3])
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
        self.background = pygame.surface.Surface(self.getScreenSize(), pygame.SRCALPHA)
        for i in range(self.width):
            self.chars.append(onScreenChar(chr(i+ord("A")), i, self.height, self.background, self.tileSize))
        for i in range(self.height):
            self.chars.append(onScreenChar(str(self.height - i), self.width, i, self.background, self.tileSize))
        for item in self.chars:
            item.draw()
        for i in range(self.height):
            row = []
            for j in range(self.width):
                color = pink
                if dw:
                    
                    color = blue
                    
                if j != self.width - 1:
                    dw = not dw
                    
                tile = onScreenTile((100+j*self.tileSize, 50+i*self.tileSize, self.tileSize, self.tileSize), (j, (self.height-1)-i), color, self.tileSize, self.game.getTile(j, (self.height-1)-i))
                tile.draw(self.background)
                row.append(tile)
            self.tiles.append(row)
        
        self.drawnBoard = True
        
    def drawBoard(self):
        
        pygame.draw.rect(self.sur, black, pygame.Rect(99, 50-1, self.tileSize * self.width + 2, self.tileSize * self.height + 2), width=2)
        onScreenChar(str(math.ceil((1+self.game.turns)/2)), self.width//2, self.height + 1, self.sur, self.tileSize).draw()
        
        if not self.drawnBoard:
            self.literallyDrawBoard()
            self.sur.blit(self.background)
        else:
            self.sur.blit(self.background)
            for row in self.tiles:
                for item in row:
                    if item.companion.different:
                        item.draw(self.sur)
            for item in self.chars:
                item.draw()

  
    
    def reset(self):
        for row in self.tiles:
            for item in row:
                item.companion.circleColor = None
                

    def updateScreen(self):
        if self.needsUpdate or self.game.getNeedsUpdate():
            
            
            self.sur.fill(white)
            self.reset()
            self.game.prepare()
            self.drawBoard()
            for item in self.allsprites: item.update()
            
            self.drawSprites()
            if self.continueButton != None: self.continueButton.draw()
            pygame.display.update()
            self.clearUpdateFlags()

    def getValidPiece(self):
        
        if self.game.dragging():
            if self.validPiece == self.game.validPiece():
                return
            for item in self.allsprites:
                if item.companion == self.game.validPiece():
                    self.validPiece = item
                    return
        if self.validPiece:
            self.validPiece.move()
            self.validPiece = False
        
    def drawSprites(self):
        if self.game.validPiece():
            for item in self.allsprites:
                if item.companion == self.game.validPiece():
                    self.validPiece = item
            self.allsprites.change_layer(self.validPiece, 1)
        else:
            if self.validPiece:
                self.allsprites.change_layer(self.validPiece, 0)
                self.validPiece = None
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
        
    

    def gameMenuHandle(self, anEvent):
      
      
        if anEvent.type == pygame.MOUSEMOTION:
            if self.collidesSpecial(anEvent.pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif anEvent.type == pygame.MOUSEBUTTONUP and anEvent.button == 1:
            item = self.collidesSpecial(anEvent.pos)
            if item:
                self.game.setPromotion(item.companion.pro())
                self.game.needsMenu = False
                return True
        return False
    
    def collidesSpecial(self, aPos):
        for item in self.specialsprites:
            
            if item.rect.collidepoint(aPos):
                return item
        return False


    def updateTileSize(self):
        for item in self.allsprites:
            item.updateTileSize(self.tileSize)
        for item in self.specialsprites:
            item.updateTileSize(self.tileSize)
        self.needsUpdate = True
        self.drawnBoard = False
        
        self.resizeScreen()

    def decrementTileSize(self):
        if self.tileSize - 5 > 10:
            self.tileSize -= 5
            self.updateTileSize()    
            

    def incrementTileSize(self):
        if self.tileSize + 5 < 150:
            self.tileSize += 5
            
            self.updateTileSize()
        
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
                            tile = False
                            for row in self.tiles:
                                for item in row:
                                    if item.collidepoint(event.pos):
                                        tile = item.companion
                            if gameOver:
                                
                                if self.continueHandle(event):
                                    gameOver = False
                                    gameStarted = False
                                    self.drawnBoard = False
                                    self.allsprites.empty()
                                else:
                                    self.game.handleEvent(event, tile)
                                    
                                
                                    
                            else:
                                if self.game.gameRunning():
                                    if self.game.activePlayerHuman():
                                        anArray = self.game.handleEvent(event, tile)
                                        
                                    
                                        if anArray[0]:
                                            "Code here incase needed later, user has made a valid move"
                                        if not anArray[1] and anArray[0]:
                                            
                                            self.game.moveHumanPiece()
                                        
                                        self.getValidPiece()
                                        if self.validPiece:
                                            self.needsUpdate = True
                                            self.validPiece.setPos(event.pos)
                                        
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
        for row in self.tiles:
            for item in row:
                item.companion.reset()
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