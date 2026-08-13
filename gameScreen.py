from game import *

pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 182, 193)
blue = (173, 216, 230)
font = pygame.font.SysFont("Arial", 42)

def corner(aValue):
    return (aValue[0]+150, aValue[1]+50)



class onScreenTile(pygame.Rect):
    def __init__(self, aRect, aColor, aTileSize, aModel):
        super().__init__(aRect[0], aRect[1], aRect[2], aRect[3])

        self.tileSize = aTileSize #New tiles get created with resize
        
        self.model = aModel #Logic tile

        self.color = aColor #On screen color
        
    
    def draw(self, aSurface):
        
        pygame.draw.rect(aSurface, self.color, self) #Draw myself

        border = self.model.border
        if border == "black": border = black
        pygame.draw.rect(aSurface, border, self, width = self.model.bwidth) #Draw border

        if border != black:
           

            #Draw highlight
            surr = pygame.Surface((self.tileSize, self.tileSize), pygame.SRCALPHA)
            surr.fill((border[0], border[1], border[2], 105))
            
                
            aSurface.blit(surr, self.topleft)

        if self.model.circleColor != None:
            #Draw circle
            pygame.draw.circle(aSurface, self.model.circleColor, self.center, self.tileSize / 3)

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
        
        pygame.draw.rect(self.sur, self.color, self) #background
        self.sur.blit(self.text, self.text_rect)#Text
        
        

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
                    
                    self.myLambda(aScreen)
                    clicked = True
        return clicked, handled
        
class onScreenChar():
    def __init__(self, char, x, y, aSur, aTileSize):
        tileFont = pygame.font.SysFont("Arial", aTileSize)
        self.letter = tileFont.render(char, True, black)
        hts = aTileSize / 2
        self.pos = corner( (x * aTileSize + hts, y * aTileSize + hts))
        
        self.rect = self.letter.get_rect(center=self.pos)
        self.sur = aSur
        self.draw()
    
    def draw(self):
        self.sur.blit(self.letter, self.rect)

class onScreenSprite(pygame.sprite.Sprite):
    def __init__(self, aModel, aTileSize, aHeight):
        super().__init__()
        self.model = aModel #Logic piece
        self.x = aModel.x 
        self.y = aModel.y
        self.coords = ""
        self.gameChosen = False
        self.image = False
        self._layer = 0
        self.rawImage = False
        self.tileSize = aTileSize
        self.height = aHeight
        self.move()

    def updateTileSize(self, newTileSize):
        self.tileSize = newTileSize
        self.changeImage()
        self.move()

    def move(self):
        if not self.image:
            self.changeImage()
        self.coords = corner((self.x * self.tileSize, self.tileSize * ((self.height - 1) - self.y)))
        self.rect = self.image.get_rect(topleft = self.coords)
    
    def changeImage(self):
        thing = "-old"
        magicNum = 75
        if thing != "-old":
            magicNum = 100
        
        transform = self.tileSize / magicNum
        if not self.rawImage:
            image = "./" + self.model.color + thing +"/" + self.model.name() + ".png"
            self.rawImage = pygame.image.load(image).convert_alpha()
        if transform != 1: self.image = pygame.transform.smoothscale_by(self.rawImage, transform)
        else: self.image = self.rawImage

    def collidepoint(self, aPos):
        self.rect.collidepoint(aPos)

    def getPos(self):
        return (self.x, self.y)
    
    def setPos(self, aPos):
        self.coords = (aPos[0], aPos[1])
        self.rect = self.image.get_rect(center = self.coords)

    def update(self):
        if self.model.wantsEaten:
            self.kill()
            return
        if self.model.needsChanged:
            self.rawImage = False
            self.changeImage()
            self.model.needsChanged = False
        daX = self.model.x
        daY = self.model.y
        if self.x != daX or self.y != daY:
            self.x = daX
            self.y = daY
            self.move()

class gameScreen():

    def convertSprites(self, aLambda, aGroup):
        sprites = []
        aLambda(sprites)
        for sprite in sprites:
            aGroup.add(onScreenSprite(sprite, self.tileSize, self.height))
            
    def gatherSprites(self):
        self.convertSprites(lambda sprites: self.game.gatherBaseSprites(sprites), self.allsprites)
        
    def menuHandle(self, aEvent):
        if self.gameMenuHandle(aEvent):
            self.menuDrawn = False
            for item in self.specialsprites:
                item.kill()

    def drawMenu(self):
        if not self.menuDrawn:
            self.convertSprites(lambda sprites: self.game.gatherSpecialSprites(sprites), self.specialsprites)
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
        self.sur = "" #main game drawing surface
        self.game = "" #main game logic object

    def initializeGame(self):
        
        self.width = self.game.width
        self.height = self.game.height

    def literallyDrawBoard(self):
        dw = True
        self.chars = []
        self.tiles = []
        self.background = pygame.surface.Surface(self.getScreenSize(), pygame.SRCALPHA)
        ts = self.tileSize
        for i in range(self.width):
            self.chars.append(onScreenChar(chr(i+ord("A")), i, self.height, self.background, ts))
        for i in range(self.height):
            self.chars.append(onScreenChar(str(self.height - i), self.width, i, self.background, ts))
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
                c = corner((j*ts, i*ts))
                tile = onScreenTile((c[0], c[1], ts, ts), color, ts, self.game.getTile(j, (self.height-1)-i))
                tile.draw(self.background)
                row.append(tile)
            self.tiles.append(row)
        
        self.drawnBoard = True
        
    def drawBoard(self):
        c = corner((-1, -1))
        pygame.draw.rect(self.sur, black, pygame.Rect(c[0], c[1], self.tileSize * self.width + 2, self.tileSize * self.height + 2), width=2)
        onScreenChar(str(math.ceil((1+self.game.turns)/2)), self.width//2, self.height + 1, self.sur, self.tileSize).draw()
        
        if not self.drawnBoard:
            self.literallyDrawBoard()
            self.sur.blit(self.background)
        else:
            self.sur.blit(self.background)
            for row in self.tiles:
                for item in row:
                    if item.model.cdifferent or item.model.bdifferent:
                        item.draw(self.sur)

    
    def reset(self):
        for row in self.tiles:
            for item in row:
                item.model.resetDot()
                

    def updateScreen(self):
        #This only gets called once the game has started
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
        gr = self.game.gameRunning()
        if self.game.dragging() or not gr:
            if self.validPiece == self.game.validPiece():
                return
            for item in self.allsprites:
                    
                if item.model == self.game.validPiece():
                    self.validPiece = item
                    self.allsprites.change_layer(self.validPiece, 1)
                    return
        if self.validPiece:
            self.validPiece.move()
            self.allsprites.change_layer(self.validPiece, 0)
            self.validPiece = False
        
    def drawSprites(self):
        
        self.allsprites.draw(self.sur)
        self.specialsprites.draw(self.sur)
        

    def returnButton(self, anX, aText, aLambda):

        return button((300*anX + 100, 150, 200, 100), aText, self.sur, aLambda, (0, 255, 255))
    
   
    def startGame(self):
        self.initializeGame()
        self.makeMainScreen()
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

    def chess(self):
        self.gameClass = chess
        

    def setUpChooseScreen(self):
        self.sur = pygame.display.set_mode((1000, 400))
        self.sur.fill(white)
        self.buttons = []
        self.buttons.append(self.returnButton(1, "Chess", lambda a: self.chess()))
        self.needsUpdate = True
        self.drawStartScreen()

    def setUpStartScreen(self):
        self.sur = pygame.display.set_mode((1500, 400))
        self.sur.fill(white)
       
        self.buttons = []
        things = self.gameClass.grabThings()
        for i in range(len(things)//2):
            self.buttons.append(self.returnButton(i, things[i *2], things[i * 2 + 1]))
        self.needsUpdate = True
        self.drawStartScreen()

    def endMenuHandle(self, handled):
        if not handled:
          
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
       
       

    def startHandle(self, anEvent):
        
        clicked = False
        handled = False
        for butt in self.buttons:
            newclicked, newhandled = butt.handleEvent(anEvent, self)
            if not clicked:
                  
                clicked = newclicked

            if not handled:
               
                handled = newhandled
        self.endMenuHandle(handled)
        return clicked
        
    def continueHandle(self, anEvent):
        clicked, handled = self.continueButton.handleEvent(anEvent, self)
        self.endMenuHandle(handled)
        return clicked
        
    

    def gameMenuHandle(self, anEvent):
      
      
        if anEvent.type == pygame.MOUSEMOTION:
            if self.collidesSpecial(anEvent.pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif anEvent.type == pygame.MOUSEBUTTONUP and anEvent.button == 1:
            item = self.collidesSpecial(anEvent.pos)
            return self.game.selectedItem(item)
            
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
        self.gameChosen = False
        self.setUpChooseScreen()
        self.continueButton = None

    def run(self):
        
        self.setUpChooseScreen()
        running = True
        gameOver = False
        gameChosen = False
        clock = pygame.time.Clock()
        gameStarted = False
       
        while running:
            "hI"
                
            eventList = pygame.event.get()
            if len(eventList) == 0:
                if gameStarted:
                    
                    self.game.handleNoEvent()
                    
            for event in eventList:
                
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEWHEEL:
                    if gameStarted:
                        if event.y == -1:
                            self.decrementTileSize()
                        elif event.y == 1:
                            self.incrementTileSize()
                else:
                    if not gameChosen:
                        
                        if self.startHandle(event):
                            gameChosen = True
                            self.setUpStartScreen()
                        self.drawStartScreen()
                        
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
                                            tile = item.model
                                if gameOver:
                                    
                                    if self.continueHandle(event):
                                        gameOver = False
                                        gameStarted = False
                                        self.drawnBoard = False
                                        gameChosen = False
                                        self.allsprites.empty()
                                    else:
                                        self.game.handleEvent(event, tile)
                                        
                                    
                                        
                                else:
                                    if self.game.gameRunning():
                                        if self.game.activePlayerHuman():
                                            anArray = self.game.handleEvent(event, tile)
                                            
                                        
                                            if not anArray[0]:
                                                "Code here incase needed later, user has made a valid move"
                                            if not anArray[1] and anArray[0]:
                                                
                                                self.game.moveHumanPiece()
                                            
                                            self.getValidPiece()
                                            if self.validPiece:
                                                self.needsUpdate = True
                                                self.validPiece.setPos(event.pos)
                                            
                                    else:
                                        
                                        gameOver = True
                                        
                                        self.continueButton = button((self.width*self.tileSize+175, 50+self.height*self.tileSize, 200, 50), "New Game", self.sur, lambda a: self.startNewGame(), (0, 100, 0))
                                        self.needsUpdate = True
                                    
                                
                                
                                
            if gameStarted:
                
                self.updateScreen()
                clock.tick(60)
                
    def getScreenSize(self):
        return (self.width*self.tileSize + 400, self.height*self.tileSize + 200)

    def resizeScreen(self):
        for row in self.tiles:
            for item in row:
                item.model.reset()
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