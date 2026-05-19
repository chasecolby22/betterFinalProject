from game import chess
import pygame

import time
pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 182, 193)
blue = (173, 216, 230)
font = pygame.font.SysFont("Arial", 42)
surs = dict()
class onScreenTile(pygame.Rect):
    def __init__(self, aRect, aPos, aSurface, aColor):
        super().__init__(aRect[0], aRect[1], aRect[2], aRect[3])
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
            if self.border not in surs.keys():

            
                surr = pygame.Surface((75, 75), pygame.SRCALPHA)
                surr.fill((self.border[0], self.border[1], self.border[2], 75))
                surs[self.border] = surr
                
            self.sur.blit(surs[self.border], self.topleft)
        if self.circleColor != None:
            pygame.draw.circle(self.sur, self.circleColor, self.center, 25)

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

   


    def __init__(self):
        
        self.allsprites = pygame.sprite.Group()
        self.specialsprites = pygame.sprite.Group()
        self.drawnBoard = False
        self.menuDrawn = False
        

        self.tiles = []
        self.sur = ""
        self.game = ""

    def standard(self):
        self.height = 8
        self.width = 8
        self.pieceList = chess.standardPieceList()
        self.wantsBot = True

    def test(self):
        self.height = 12
        self.width = 4
        self.pieceList = chess.test()
        self.wantsBot = False

    def addSprite(self, aSprite):
        self.allsprites.add(aSprite)

    def drawBoard(self):
        y = 50
        pygame.draw.rect(self.sur, black, pygame.Rect(99, y-1, 75 * self.width + 2, 75 * self.height + 2), width=2)
       
        for i in range(self.height):
            letter = font.render(chr(i+ ord("A")), True, black)
            self.sur.blit(letter, ((125 + i * 75), y+10 + self.height* 75))
        for i in range(self.width):
            letter = font.render(str(self.width - i), True, black)
            self.sur.blit(letter, ((125+self.width*75), y+10 + (i * 75)))
        if not self.drawnBoard:
            dw = True
            
            
            for i in range(self.height):
                row = []
                for j in range(self.width):
                    color = pink
                    if dw:
                        
                        color = blue
                    
                    if j != 7:
                        dw = not dw
                        
                    tile = onScreenTile((100+j*75, y+i*75, 75, 75), (j, (self.height-1)-i), self.sur, color)
                    tile.draw()
                    row.append(tile)
                self.tiles.append(row)
            self.game.updateTiles(self.tiles)
            
            self.drawnBoard = True
        else:
            for row in self.tiles:
                for item in row:
                    item.draw()

  
    
    def reset(self):
        for row in self.tiles:
            for item in row:
                item.circleColor = None

    def updateScreen(self):
        if self.game.getNeedsUpdate():
            
            self.sur.fill(white)
            self.reset()
            self.game.prepare()
            self.drawBoard()
    
            
            self.drawSprites()
            
            pygame.display.update()
            self.game.clearUpdateFlags()

        
    def drawSprites(self):
        self.allsprites.draw(self.sur)
        self.specialsprites.draw(self.sur)
        

    def returnButton(self, aSurface, anX, aText, aLambda):
        return button((anX, 50, 200, 100), aText, aSurface, aLambda)
    
    def startBotGame(self):
        self.standard()
        self.game = chess(self.width, self.height, self.pieceList, self.wantsBot)
        self.thing(lambda: self.game.startGame(5, 10))

    def startStandardGame(self):
        self.standard()
        self.game = chess(self.width, self.height, self.pieceList, self.wantsBot)
        self.thing(lambda: self.game.startGame(0, 0))
    
    def startTest(self):
        self.test()
        self.game = chess(self.width, self.height, self.pieceList, self.wantsBot)
        self.thing(lambda: self.game.startGame(0, 0))


    def setUpStartScreen(self):
        start = pygame.display.set_mode((1000, 400))
        start.fill((255, 0, 255))
       
        self.buttons = []
        self.buttons.append(self.returnButton(start, 50, "No Bots", lambda: self.startStandardGame()))
        self.buttons.append(self.returnButton(start, 350, "Bots", lambda: self.startBotGame()))
        self.buttons.append(self.returnButton(start, 650, "test", lambda: self.startTest()))
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
        
                
    def thing(self, aLambda):
        self.makeMainScreen()
        aLambda()
        self.gatherSprites()
        self.drawBoard()
        self.updateScreen()
        
    def run(self):
        
        self.setUpStartScreen()
        running = True
        clock = pygame.time.Clock()
        gameStarted = False
        self.knowsBot = False
        while running:
            
            if gameStarted and not self.knowsBot:
                self.knowsBot = True
                self.game.getBotInput(10)
                
            eventList = pygame.event.get()
            if len(eventList) == 0:
                if gameStarted and self.game.handleNoEvent():
                    
                    self.updateScreen()
                    time.sleep(0.25)
            for event in eventList:
                if event.type == pygame.QUIT:
                    running = False
                else:
                    
                    if not gameStarted:
                        
                       if self.startHandle(event):
                           
                           gameStarted = True     
                            
                        
                    elif self.game.needsMenu:
                        self.drawMenu()
                        self.menuHandle(event)
                        self.knowsBot = False

                                
                    else:
                        self.game.drawCheck()
                      
                        if isMouseEvent(event):
                            
                            if not self.game.gameStopped():
                                if self.game.activePlayerHuman():
                                    anArray = self.game.handleEvent(event)
                                    
                                    if not anArray[0]:
                                        running = False
                                    if anArray[1]:
                                        self.knowsBot = False
                                    if not anArray[2] and anArray[1]:
                                        
                                        self.game.moveHumanPiece()
                                    

                                else:
                                    self.game.botTurn()
                                    self.updateScreen()
                                    time.sleep(0.25)
                                    
                            else:
                                gameStarted = False
                                running = False
            if gameStarted:
                
                self.updateScreen()
                clock.tick(60)
                

    def makeMainScreen(self):
        self.sur = pygame.display.set_mode((self.width*75 + 300, self.height*75 + 200))

def isMouseEvent(aEvent):
    return aEvent.type == pygame.MOUSEBUTTONDOWN or aEvent.type == pygame.MOUSEBUTTONUP or aEvent.type == pygame.MOUSEMOTION