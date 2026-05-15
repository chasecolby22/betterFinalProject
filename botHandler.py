import subprocess

class botHandler():
    def __init__(self):
        self.process = ""
    
    def readLine(self):
        return self.process.stdout.readline().strip()
    
    def botCommand(self, aCommand):
        self.process.stdin.write(aCommand+"\n")
        self.process.stdin.flush()

    def startBot(self):
        try:
            self.process = subprocess.Popen("./stockfish/stockfish-windows-x86-64-avx2.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
        except:
            return False
        self.botCommand("uci")
        self.botCommand("ucinewgame")
        line = self.process.stdout.readline()
        while line != "uciok\n":
            line = self.process.stdout.readline()
        return True
    
    
    
    def getBotInput(self, movesString, aDifficulty):
        if movesString != "":
            self.botCommand("position startpos moves " + movesString)
        else:
            self.botCommand("position startpos")
        self.botCommand("go depth " + str(aDifficulty))
        aBotInput = self.readLine()
        while len(aBotInput) < 13 or aBotInput[:8] != "bestmove":
            aBotInput = self.readLine()
            
        
        
        return aBotInput