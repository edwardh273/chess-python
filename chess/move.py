"""
Defines the move class that is passed into the move functions of the GameState
"""
class Move:

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):  # ((startCol, startRow), (endCol, endRow), board)
        # position of mouse click is format sqSelected: (col, row)
        self.startCol = startSq[0]
        self.startRow = startSq[1]
        self.endCol = endSq[0]
        self.endRow = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.moveID = f"C{self.startCol:01d}R{self.startRow:01d} -> C{self.endCol:01d}R{self.endRow:01d}"

        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)

        # enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        # castle
        self.isCastleMove = isCastleMove


    """
    Overriding the equals method. Only needed as we are using a class, would not be needed if we used strings, ints etc.
    """
    def __eq__(self, other):
        if isinstance(other, Move):  # if object other is class Move, then two moves are equivalent if their IDs are equivalent
            return self.moveID == other.moveID
        return False



class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs