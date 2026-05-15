from game import game
from pieces import *

pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 182, 193)
blue = (173, 216, 230)
font = pygame.font.SysFont("Arial", 42)

class onScreenTile():
    def __init__(self, aRect, aPos):
        self.rect = aRect
        self.pos = aPos

class button(pygame.Rect):
    def __init__(self, aRectSpec, aText, aSurface, aLambda):
        super().__init__(aRectSpec[0], aRectSpec[1], aRectSpec[2], aRectSpec[3])
        self.text = font.render(aText, True, black)
        self.text_rect = self.text.get_rect(center=self.center)
        self.drawOn(aSurface)
        self.myLambda = aLambda
    
    def drawOn(self, aSurface):
        pygame.draw.rect(aSurface, white, self)
        aSurface.blit(self.text, self.text_rect)

    def handleClick(self, aPos):
        if self.collidepoint(aPos):
            self.myLambda()
            return True
        return False
        
        

class gameScreen():
    def __init__(self):
        
        self.allsprites = pygame.sprite.Group()
        self.specialsprites = pygame.sprite.Group()
        self.specialpieces = []
        
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
                rect = pygame.Rect(100+j*75, 50+i*75, 75, 75)
                tile = onScreenTile(rect, (j, 7-i))
                row.append(tile)
                if dw:
                    
                    pygame.draw.rect(self.sur, blue, rect)
                    pygame.draw.rect(self.sur, black, rect, width=2)
                else:
                    pygame.draw.rect(self.sur, pink, rect)
                    pygame.draw.rect(self.sur, black, rect, width=2)
                if j != 7:
                    dw = not dw
                else:
                    letter = font.render(str(8 - i), True, black)
                    self.sur.blit(letter, ((125+8*75), 60 + (i * 75)))
            self.tiles.append(row)
        thing = "ABCDEFGH"
        for i in range(8):
            letter = font.render(thing[i], True, black)
            self.sur.blit(letter, ((125 + i * 75), 60 + 8* 75))

    def updateScreen(self):
        self.sur.fill(white)
        self.drawBoard()
        if self.game.checkers != "": self.drawSquares(self.game.checkers, (255, 0, 0))
        if self.game.botChoice != "": self.drawSquares(self.game.botChoice, (0, 100, 0))
        
        
        self.drawSprites()
        pygame.display.update()

    def drawPromotion(self):
        
        self.specialpieces.append(dumbQueen(9, 7, self.game.activePlayer))
        self.specialpieces.append(dumbRook(9, 5, self.game.activePlayer))
        self.specialpieces.append(dumbBishop(9, 3, self.game.activePlayer))
        self.specialpieces.append(dumbKnight(9, 1, self.game.activePlayer))
        for item in self.specialpieces: self.specialsprites.add(item)
        self.updateScreen()
        running = True
        while running:
            selection = ""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    for item in self.specialpieces:
                        if item.rect.collidepoint(event.pos):
                            match item.name():
                                case "queen":
                                    
                                    selection = "q"
                                case "rook":

                                    selection = "r"
                                case "knight":
                                    selection = "n"
                                case "bishop":
                                    selection = "b"
                            
                            for item in self.specialsprites:
                                item.kill()
                            return selection
                elif event.type == pygame.MOUSEMOTION:
                    set = False
                    for item in self.specialpieces:
                        if item.rect.collidepoint(event.pos):
                            pygame.mouse.set_cursor(pygame.cursors.ball)
                            set = True
                    if not set:
                        pygame.mouse.set_cursor(pygame.cursors.arrow)
                        

        
    def drawSprites(self):
        self.allsprites.draw(self.sur)
        self.specialsprites.draw(self.sur)

    def startScreen(self):
        start = pygame.display.set_mode((800, 400))
        start.fill((255, 0, 255))
       
        buttons = []
        buttons.append(button((50, 100, 200, 100), "No Bots", start, lambda:self.game.startGame(False, 0, False, 0)))
        buttons.append(button((350, 100, 200, 100), "Bots", start, lambda:self.game.startGame(True, 5, True, 10)))
        pygame.display.update()
        running = True
        self.game = game(self)
        gameStarted = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    for butt in buttons:
                        if butt.handleClick(event.pos):
                            gameStarted = True
                
            if gameStarted:
                if not self.game.gameStopped():
                    if not self.game.step():
                        running = False
                else:
                    gameStarted = False
                    

    def makeMainScreen(self):
        self.sur = pygame.display.set_mode((1000, 900))

