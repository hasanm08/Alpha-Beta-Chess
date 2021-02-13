class Board(object):

    def __init__(self, position=' ' * 64):
        self.boardposition = []
        self.setPosition(position)

    def __str__(self):
        position = []
        for x, p in enumerate(self.boardposition):
            if x > 0 and x % 8 == 0:
                position.append('/')
            if not p.isspace():
                position.append(p)
            elif position and position[-1].isdigit():
                position[-1] = str(int(position[-1]) + 1)
            else:
                position.append('1')
        return ''.join(position)

    def setPosition(self, position):
        self.boardposition = []
        for c in position:
            if c == '/':
                continue
            elif c.isdigit():
                self.boardposition.extend([' '] * int(c))
            else:
                self.boardposition.append(c)

    def getPiece(self, index):
        return self.boardposition[index]

    def getOwner(self, index):
        piece = self.getPiece(index)
        return None if piece==' ' else ('w' if piece.isupper() else 'b')

    def movePiece(self, start, end, piece):
        self.boardposition[end], self.boardposition[start] = piece,' '

    def findPiece(self, symbol):
        return ''.join(self.boardposition).find(symbol)
