import pygame as p
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # hide the pygame welcome message for every new process started

WIDTH = HEIGHT = 768
DIMENSION = 8  # dimensions of chess board = 8x8
SQ_SIZE = HEIGHT // DIMENSION
IMAGES = {}
CHESS_DIR = os.path.dirname(__file__)
colors = []


"""
Highlight sq selected and available moves.
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        c, r = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):  # square selected is a piece of the person which turn it is
            surface = p.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)  # transparency value
            surface.fill(p.Color("blue"))
            screen.blit(surface, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight valid moves from that square
            surface.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(surface, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))


"""
Animating a move
"""
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # frame to move 1 sq
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        c, r = (move.startCol + dC*frame/frameCount, move.startRow + dR*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endCol + move.endRow) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


"""
Finish text
"""
def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)


"""
Initialize a global dictionary of images. This will be called exactly once in the main
"""
def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wp", "wR", "wN", "wB", "wQ", "wK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(CHESS_DIR + '/images/' + piece + '.png'),
                                          (SQ_SIZE, SQ_SIZE))  # Note: we can access an image by "IMAGES['wp']"


"""
Responsible for all the graphics within a current gameState.
"""
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


"""
Draws the squares on the board.  The top left square is always light.
"""
def drawBoard(screen):
    global colors
    colors = [p.Color('whitesmoke'), p.Color('gray50')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board using the current GameState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], (c*SQ_SIZE,r*SQ_SIZE))
