from move import Move, CastleRights

"""
This class is responsible for storing all the information about the current
state of a chess game.  It will also be responsible for determining the valid
moves at the current state.  It will also keep a move log.
"""
class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteKingLocation, self.blackKingLocation = (4, 7), (4, 0)  # (col, row)

        # initialise variables to store game data
        self.whiteToMove = True
        self.moveLog = []

        self.pins, self.checks, self.inCheck = [], [], False
        self.checkMate, self.staleMate = False, False

        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]

        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]  # initial log is [(T, T, T, T)]


    """
    Iterates through all pieces of the board, calculating possible moves for every piece of the color of whose turn it is.
    """
    def getAllPossibleMoves(self):
        moves = []  # ((startCol, startRow), (endCol, endRow), board)
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of cols in given row
                color, piece = self.board[r][c][0], self.board[r][c][1]
                if (color =='b' and self.whiteToMove == False) or (color =='w' and self.whiteToMove== True):  # if the piece is black, and it's black's turn, or if piece is white, and it's white's turn:
                    self.moveFunctions[piece](r, c, moves)  # appends all moves for each pieces to list moves = []
        return moves


    """
    All moves considering check
    """
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingCol, kingRow = self.whiteKingLocation[0], self.whiteKingLocation[1]
        else:
            kingCol, kingRow = self.blackKingLocation[0], self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check: block check or move king
                moves = self.getAllPossibleMoves()
                check = self.checks[0]  # (endCol, endRow, dir-col, dir-row)
                checkCol = check[0]
                checkRow = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':  # if knight, must capture knight or move king
                    validSquares = [(checkCol, checkRow)]
                else:  # else block the check
                    for i in range(1, 8):
                        validSquare = (kingCol + check[2] * i, kingRow + check[3] * i)  # check[2] == dir-col, check[3] == dir-row
                        validSquares.append(validSquare)
                        if validSquare[0] == checkCol and validSquare[1] == checkRow:  # go upto the check square
                            break
                # get rid of any moves that don't block check or more king
                for i in range(len(moves)-1, -1, -1):  # go through backwards when removing from a list
                    if moves[i].pieceMoved[1] != 'K':  # move doesn't move king, so must block or capture
                        if not (moves[i].endCol, moves[i].endRow) in validSquares:
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check so all moves are fine
            moves = self.getAllPossibleMoves()

        # to generate castle moves
        if self.whiteToMove:
            self.getCastleMoves(7,4, moves)  # can only castle if the king hasn't moved.
        else:
            self.getCastleMoves(0, 4, moves)
        return moves


    """
    Returns if the player is in check, a list of pins, and a list of checks
    """
    def checkForPinsAndChecks(self):
        pins = []  # square of pinned piece & direction pinned from: (endCol, endRow, dir-col, dir-row)
        checks = []  # squares where enemy is applying a check: (endCol, endRow, dir-col, dir-row)
        inCheck = False
        if self.whiteToMove:
            enemyColor, allyColor = "b", "w"
            startCol, startRow = self.whiteKingLocation[0], self.whiteKingLocation[1]
        else:
            enemyColor, allyColor = "w", "b"
            startCol, startRow = self.blackKingLocation[0], self.blackKingLocation[1]
        # check outward from king for pins and checks, keep track of pins.  Pin direction is OUTWARD from the KING
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1))  # (col, row): l, r, u, d, lu, ru, ld, rd
        for j in range(len(directions)):
            d = directions[j]  # (1, 1)
            possiblePin = ()  # reset possible pin for said direction
            for i in range(1, 8):  # up until the end of the board
                endCol = startCol + d[0] * i
                endRow = startRow + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    # check for pins
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endCol, endRow, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction.
                            break
                    # check for checks
                    elif endPiece[0] == enemyColor:
                        piece = endPiece[1]
                        # orthogonally from king & piece == rook
                        # diagonally & piece == bishop
                        # 1 square away & piece == pawn
                        # any direction & piece == queen
                        # any direction 1 square away & piece == king
                        if (0 <= j <= 3 and piece == 'R') or \
                                (4 <= j <= 7 and piece == 'B') or \
                                (i == 1 and piece == 'p' and ( (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5 ) )) or \
                                (piece == 'Q') or \
                                (i == 1 and piece == 'K'):
                            if possiblePin == ():  # if enemyPiece in range and no pin, inCheck = True.
                                inCheck = True
                                checks.append((endCol, endRow, d[0], d[1]))
                                break
                            else:  # allied piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break
        # knight checks
        knightMoves = ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2))
        for m in knightMoves:
            endCol = startCol + m[0]
            endRow = startRow + m[1]
            if 0 <= endCol < 8 and 0 <= endRow < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enemy knight attacking king
                    inCheck = True
                    checks.append((endCol, endRow, m[0], m[1]))

        return inCheck, pins, checks

    """
    Undo the last move made
    """
    def undoMove(self):
        if len(self.moveLog) != 0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            #update king's location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startCol, move.startRow)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startCol, move.startRow)

            self.whiteToMove = not self.whiteToMove #swap players back

            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' # leave landing sq blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endCol, move.endRow)
            # undo a 2 sq pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # move rook back if a castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"  # remove the old rook

                elif move.endCol - move.startCol == - 2:  # queenside
                    self.board[move.endRow][move.endCol -2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            # undo castling rights
            self.castleRightsLog.pop() # get rid of castle rights from move we are undoing.
            lastCastleRights = self.castleRightsLog[-1]
            self.currentCastlingRights = CastleRights(lastCastleRights.wks, lastCastleRights.bks, lastCastleRights.wqs, lastCastleRights.bqs)  # reinitialize castle rights to not make a copy

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            self.checkMate = False
            self.staleMate = False

    """
    Takes a Move as a parameter and executes it.  After making move, changes White to move parameter
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move to undo later.

        # update the king's location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endCol, move.endRow)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endCol, move.endRow)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # enpassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # if a pawn moves 2 squares
            self.enpassantPossible = (move.startCol, (move.startRow + move.endRow) // 2)  # enpassant possible to the square where the pawn would have moved if it had only moved 1 square.
        else:
            self.enpassantPossible = ()
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # capturing the pawn

        # castling
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # to the right: king side castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # copy the rook to the new square
                self.board[move.endRow][move.endCol + 1] = "--"  # remove the old rook

            elif move.endCol - move.startCol == -2:  # to the left: queen side castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        self.updateCastleRights(move)  # update the castling rights whenever it's a rook or a king move
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

        self.enpassantPossibleLog.append(self.enpassantPossible)

        self.whiteToMove = not self.whiteToMove  # swap players of the gameState

    """
    Update the castle rights given a move
    """
    def updateCastleRights(self, move):
        # check if the king moved or the rock moved
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:  # whites left rock
                    self.currentCastlingRights.wqs = False
                if move.startCol == 7:  # whites right rock
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:  # black left rock
                    self.currentCastlingRights.bqs = False
                if move.startCol == 7:  # black right rock
                    self.currentCastlingRights.bks = False
        # check if the rock is captured
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False


    """
    Get all castle moves
    """
    def getCastleMoves(self, r, c, moves):
        if not self.whiteToMove and self.blackKingLocation != (4, 0): return
        if self.whiteToMove and self.whiteKingLocation != (4, 7): return
        if not (self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--") and \
                not (self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--"):
            return  # if queenside and kingside blocked, return.

        if self.squareUnderAttack(r, c): return  # check if the king is inCheck as the king can't escape the check by castling
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):  # kingside
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):  # queenside
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((c, r), (c+2, r), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):  # only squares king moves through need to not be under attack.
                moves.append(Move((c, r), (c-2, r), self.board, isCastleMove=True))


    """
    Determine if the enemy can attack the square r, c.  Returns True, False
    """
    def squareUnderAttack(self, r, c):

        enemyColor = 'b' if self.whiteToMove else 'w'

        # check for knights
        knightMoves = ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2))
        for m in knightMoves:
            nr, nc = r + m[0], c + m[1]
            if 0 <= nr <= 7 and 0 <= nc <= 7:
                if self.board[nr][nc] == enemyColor + 'N':
                    return True

        # check for other pieces
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1))  # (col, row): l, r, u, d, lu, ru, ld, rd
        for j in range(len(directions)):
            d = directions[j]  # (1, 1)
            for i in range(1, 8):  # up until the end of the board
                endCol = c + d[0] * i
                endRow = r + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == enemyColor:
                        piece = endPiece[1]
                        # orthogonally  && piece == rook
                        # diagonally && piece == bishop
                        # 1 square away && piece == pawn
                        # any direction & piece == queen
                        # any direction 1 square away & piece == king
                        if (0 <= j <= 3 and piece == 'R') or \
                                (4 <= j <= 7 and piece == 'B') or \
                                (i == 1 and piece == 'p' and ( (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5 ) )) or \
                                (piece == 'Q') or \
                                (i == 1 and piece == 'K'):
                            return True
                        else:  # if enemy piece detected, but cannot attack, then it is blocking.
                            break
                    elif endPiece != '--':  # if friendly piece, then also blocking this direction.
                        break
        return False


    """
    Get all pawn moves for the pawn located at row, col and add these moves to the list
    """
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == c and self.pins[i][1] == r:  # pins = (endCol, endRow, d[0], d[1])
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:  # white pawn moves
            if self.board[r - 1][c] == "--":  # moving forwards
                if not piecePinned or pinDirection == (0, -1):
                    moves.append(Move((c, r),(c, r-1), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # move 2 squares forward
                        moves.append(Move((c, r),(c, r-2), self.board))
            if c - 1 >= 0:  # capturing left (ensures not off board)
                if self.board[r - 1][c - 1][0] =='b':
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((c, r),(c-1, r-1), self.board))
                elif (c-1, r-1) == self.enpassantPossible and self.board[r][c-1][0] == 'b':
                    moves.append(Move((c, r), (c-1, r-1), self.board, isEnpassantMove=True))
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((c, r), (c-1, r-1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # capturing right
                if self.board[r - 1][c + 1][0] =='b':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((c, r),(c+1, r-1), self.board))
                elif (c+1, r-1) == self.enpassantPossible and self.board[r][c+1][0] == 'b':
                    moves.append(Move((c, r), (c+1, r-1), self.board, isEnpassantMove=True))
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((c, r), (c+1, r-1), self.board, isEnpassantMove=True))

        else:  # black pawn moves
            if self.board[r + 1][c] == "--":  # moving forwards
                if not piecePinned or pinDirection == (0, 1):
                    moves.append(Move((c, r), (c, r+1), self.board))
                    if r == 1 and self.board[r+2][c] == "--":  # move 2 squares forward
                        moves.append(Move((c, r), (c, r+2), self.board))
            if c - 1 >= 0:  # capturing left
                if self.board[r + 1][c - 1][0] =='w':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((c, r),(c-1, r+1), self.board))
                elif (c-1, r+1) == self.enpassantPossible and self.board[r][c-1][0] == 'w':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((c, r), (c-1, r+1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # capturing right
                if self.board[r + 1][c + 1][0] =='w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((c, r),(c+1, r+1), self.board))
                elif (c+1, r+1) == self.enpassantPossible and self.board[r][c+1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((c, r), (c+1, r+1), self.board, isEnpassantMove=True))

    """
    Get all Rook moves for the Rook located at row, col and add these moves to the list
    """
    def getRookMoves(self, r, c, moves):
        piecePinned, pinDirection = False, ()  # set  initial variables
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == c and self.pins[i][1] == r:  # (endCol, endRow, d[0], d[1]).
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])  # dir[col], dir[row]
                if self.board[r][c][1] != 'Q': # pinned piece = rook and not a queen
                    self.pins.remove(self.pins[i])
                break
        enemyColor = 'b' if self.whiteToMove == True else 'w'
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))  # left, right, up, down
        for d in directions:
            for i in range(1, 8):
                endCol = c + d[0] * i
                endRow = r + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # confine the potential moves to the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # if blank, append move
                            moves.append(Move((c, r), (endCol, endRow), self.board))
                        elif endPiece[0] == enemyColor:  # hits enemy piece, append then break
                            moves.append(Move((c, r), (endCol, endRow), self.board))
                            break
                        else:  # hits own color piece
                            break
                else:  # off board
                    break

    """
    Get all Bishop moves for the Bishop located at row, col and add these moves to the list
    """
    def getBishopMoves(self, r, c, moves):
        piecePinned, pinDirection = False, ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == c and self.pins[i][1] == r:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # pinned piece = bishop and not a queen
                    self.pins.remove(self.pins[i])
                break
        enemyColor = 'b' if self.whiteToMove == True else 'w'
        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))  # leftup, rightup, leftdown, rightdown
        for d in directions:
            for i in range(1, 8):
                endCol = c + d[0] * i
                endRow = r + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # confine the potential moves to the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # if blank, append move
                            moves.append(Move((c, r), (endCol, endRow), self.board))
                        elif endPiece[0] == enemyColor:  # hits enemy piece, append then break
                            moves.append(Move((c, r), (endCol, endRow), self.board))
                            break
                        else:  # hits own color piece
                            break
                else:  # off board
                    break

    """
    Get all Queen moves for the Queen located at row, col and add these moves to the list
    """
    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    """
    Get all Knight moves for the Knight located at row, col and add these moves to the list
    """
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == c and self.pins[i][1] == r:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        potentialMoves = ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2))
        allyColor = 'w' if self.whiteToMove == True else 'b'
        for m in potentialMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # confine the potential moves to the board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((c, r), (endCol, endRow), self.board))

    """
    Get all King moves for the King located at row, col and add these moves to the list
    """
    def getKingMoves(self, r, c, moves):
        potentialMoves = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
        allyColor = 'w' if self.whiteToMove == True else 'b'
        for m in potentialMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # confine the potential moves to the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # empty or enemy piece
                    if allyColor == 'w':  # place king on square and check for checks
                        self.whiteKingLocation = (endCol, endRow)
                    else:
                        self.blackKingLocation = (endCol, endRow)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((c, r), (endCol, endRow), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (c, r)  # place king back on original location
                    else:
                        self.blackKingLocation = (c, r)