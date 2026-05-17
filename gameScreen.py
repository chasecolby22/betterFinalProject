from game import chess
from pieces import *
import time
pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 182, 193)
blue = (173, 216, 230)
font = pygame.font.SysFont("Arial", 42)

class onScreenTile(pygame.Rect):
    def __init__(self, aRect, aPos, aSurface, aColor):
        super().__init__(aRect[0], aRect[1], aRect[2], aRect[3])
        self.pos = aPos
        pygame.draw.rect(aSurface, aColor, self)
        pygame.draw.rect(aSurface, black, aRect, width = 2)

class button(pygame.Rect):
    def __init__(self, aRectSpec, aText, aSurface, aLambda):
        super().__init__(aRectSpec[0], aRectSpec[1], aRectSpec[2], aRectSpec[3])
        self.text = font.render(aText, True, black)
        self.text_rect = self.text.get_rect(center=self.center)
        pygame.draw.rect(aSurface, white, self)
        aSurface.blit(self.text, self.text_rect)
        self.myLambda = aLambda
        

    def handleEvent(self, aEvent):
        handled = False
        clicked = False
        if aEvent.type == pygame.MOUSEMOTION:
            if self.collidepoint(aEvent.pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                handled = True
        elif aEvent.type == pygame.MOUSEBUTTONUP:
            if self.collidepoint(aEvent.pos):
                self.myLambda()
                clicked =  True
        return clicked, handled
        
class cursor(pygame.sprite.Sprite):
    def __init__(self, anImage):
        super().__init__()
        self.image = pygame.image.load(anImage).convert_alpha()
        
        self.rect = self.image.get_rect(topleft = (-100, -100)) 

    def move(self, aPos):
        self.rect = self.image.get_rect(center = aPos)   


class gameScreen():

    def gatherSprites(self):
        for item in self.game.player1.pieces:
            self.addSprite(item)
        for item in self.game.player2.pieces:
            self.addSprite(item)
        


    def __init__(self):
        
        self.allsprites = pygame.sprite.Group()
        self.specialsprites = pygame.sprite.Group()
        
        self.specialpieces = []
        self.specialCursor = ""
        self.tiles = []
        self.sur = ""
        self.game = ""

    def addSprite(self, aSprite):
        self.allsprites.add(aSprite)

    def drawSquares(self, positions, color):
        for tile in positions:
            i = tile[0]
            j = tile[1]
            x = 100 + 75/2 + i * 75
            y = 50 + 75/2 + ((7-j) * 75)
            
            pygame.draw.circle(self.sur, color, (x, y), 30)

    def drawBoard(self):
        dw = True
        
        pygame.draw.rect(self.sur, black, pygame.Rect(99, 49, 602, 602), width=2)
        for i in range(8):
            row = []
            for j in range(8):
                color = pink
                if dw:
                    
                    color = blue
                
                if j != 7:
                    dw = not dw
                else:
                    letter = font.render(str(8 - i), True, black)
                    self.sur.blit(letter, ((125+8*75), 60 + (i * 75)))
                tile = onScreenTile((100+j*75, 50+i*75, 75, 75), (j, 7-i), self.sur, color)
                
                row.append(tile)
            self.tiles.append(row)
        thing = "ABCDEFGH"
        for i in range(8):
            letter = font.render(thing[i], True, black)
            self.sur.blit(letter, ((125 + i * 75), 60 + 8* 75))

    def drawSpecialSquares(self, aThing, aColor):
        superThing = getattr(self.game, aThing)
        
        sqrs = superThing()
        if sqrs != '':
            if aThing == "pposibleMoves":
                self.posibleDrawn = True
                self.drawSquares(sqrs, aColor)
            else:
                if not self.posibleDrawn:
                    self.drawSquares(sqrs, aColor)
        
    def updateScreen(self):
        if self.game.getNeedsUpdate():
            
            self.game.drawCheck()
            self.game.drawBot()
            self.game.updateKingTiles()
            self.sur.fill(white)
            self.drawBoard()
            self.posibleDrawn = False
            self.drawSpecialSquares("pposibleMoves", (255, 150, 0))
            self.drawSpecialSquares("ccheckers", (255, 0, 0))
            self.drawSpecialSquares("bbotChoice", (0, 100, 0))
            
            self.drawSprites()
            
            pygame.display.update()
            self.game.clearUpdateFlags()

    def drawPromotion(self):
        if len(self.specialpieces) == 0:
            
            self.specialpieces.append(dumbQueen(9, 7, self.game.activePlayer.getColor()))
            self.specialpieces.append(dumbRook(9, 5, self.game.activePlayer.getColor()))
            self.specialpieces.append(dumbBishop(9, 3, self.game.activePlayer.getColor()))
            self.specialpieces.append(dumbKnight(9, 1, self.game.activePlayer.getColor()))
            

            for item in self.specialpieces: self.specialsprites.add(item)
            self.game.needsUpdate = True
            self.updateScreen() 

        
    def drawSprites(self):
        self.allsprites.draw(self.sur)
        self.specialsprites.draw(self.sur)
        

    def returnButton(self, aSurface, anX, aText, aLambda):
        return button((anX, 50, 200, 100), aText, aSurface, aLambda)
    
    def collidesSpecial(self, aPos):
        for item in self.specialpieces:
            if item.rect.collidepoint(aPos): return item
        return False

    def setUpStartScreen(self):
        start = pygame.display.set_mode((800, 400))
        start.fill((255, 0, 255))
       
        self.buttons = []
        self.buttons.append(self.returnButton(start, 50, "No Bots", lambda: self.thing(lambda:self.game.startGame(False, 0, False, 0))))
        self.buttons.append(self.returnButton(start, 350, "Bots", lambda: self.thing(lambda:self.game.startGame(True, 7, True, 10))))
        pygame.display.update()

    
    def startHandle(self, anEvent):
        clicked = False
        handled = False
        for butt in self.buttons:
            newclicked, newhandled = butt.handleEvent(anEvent)
            if not clicked:
                clicked = newclicked
            if not handled:
                handled = newhandled
        if not handled:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if clicked:
            return True
        return False
    

    def promotionHandle(self, anEvent):
        if anEvent.type == pygame.MOUSEMOTION:
            if self.collidesSpecial(anEvent.pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif anEvent.type == pygame.MOUSEBUTTONUP:
            item = self.collidesSpecial(anEvent.pos)
            if item:
                self.game.setPromotion(item.name())
                for item in self.specialsprites:
                    item.kill()
                self.specialpieces = []
                
                
                
                
                
                
    def thing(self, aLambda):
        self.makeMainScreen()
        aLambda()
        self.gatherSprites()
        self.updateScreen()
        
    def run(self):
        
        self.setUpStartScreen()
        running = True
        self.game = chess()
        clock = pygame.time.Clock()
        gameStarted = False
        
        while running:
            
            if gameStarted:
                self.game.getBotInput(10)
                
            eventList = pygame.event.get()
            if len(eventList) == 0:
                if gameStarted and not self.game.gameStopped() and not self.game.activePlayerHuman():
                    self.game.botTurn()
                    
                    self.updateScreen()
                    time.sleep(0.1)
            for event in eventList:
                if event.type == pygame.QUIT:
                    running = False
                else:
                    
                    if not gameStarted:
                        
                       if self.startHandle(event):
                           gameStarted = True     
                            
                        
                    elif self.game.activePlayer.promotionNeeded:
                        self.drawPromotion()
                        self.promotionHandle(event)

                                
                    else:
                        self.game.drawCheck()
                      
                        if isMouseEvent(event):
                            
                            if not self.game.gameStopped():
                                if self.game.activePlayerHuman():
                                    
                                    found = False
                                    for row in self.tiles:
                                        for tile in row:
                                            
                                            if tile.collidepoint(event.pos):
                                                anArray = self.game.handleEvent(event, tile.pos)
                                                if not anArray[0]:
                                                    running = False
                                                
                                                    
                                                if not anArray[2] and anArray[1]:
                                                    self.game.moveHumanPiece()
                                                    

                                                found = True
                                        
                                    if not found:
                                        self.game.handleEvent(event, False)

                                else:
                                    self.game.botTurn()
                                    self.updateScreen()
                                    time.sleep(0.1)
                                    
                            else:
                                gameStarted = False
                                running = False
            if gameStarted:
                
                self.updateScreen()
                clock.tick(180)
                

    def makeMainScreen(self):
        self.sur = pygame.display.set_mode((1000, 900))

def isMouseEvent(aEvent):
    return aEvent.type == pygame.MOUSEBUTTONDOWN or aEvent.type == pygame.MOUSEBUTTONUP or aEvent.type == pygame.MOUSEMOTION