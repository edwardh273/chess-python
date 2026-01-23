from multiprocessing import Process, Queue
from ChessGameState import GameState
from ChessAI import findBestMove, findRandomMove
from Move import Move
from DisplayFuncs import *

WIDTH = HEIGHT = 768
DIMENSION = 8  # dimensions of chess board = 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15

def main():
    """
    The main driver for our code.  This will handle user input and updating the graphics.
    """
    # set up the game
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    loadImages()  # only do this once before the while loop

    # setup variables
    running = True
    moveMade = False
    gameOver = False
    AIThinking = False
    chessAIProcess = None
    gs = GameState()  # initialize the GameState, whiteToMove = True
    sqSelected = ()  # no square is selected initially.  Keeps track of last click of user (tuple: (col, row))
    playerClicks = []  # keep track of player clicks (two tuples: [(4, 7), (4, 5)])

    whitePlayer = True  # if a human is playing white, then True.  If AI is playing, then false
    blackPlayer = False  # same as above, but for black.


    validMoves = gs.getValidMoves()
    print()
    print("-----White to move-----")

    while running:

        isHumanTurn = (gs.whiteToMove and whitePlayer) or (not gs.whiteToMove and blackPlayer)

        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    # pygame .get_pos is opposite to how you slice the array of the gs.board
                    location = p.mouse.get_pos()  # (col, row): (0,0)==top left;   (col=0, row=7)==bottom left;     (7, 7)==bottom right
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (col, row):  # the user clicked  the same square twice
                        sqSelected = ()  # deselect
                        playerClicks = []  # reset
                        print("user clicked same square twice, reset playerClicks")

                    else:
                        sqSelected = (col, row)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2 and isHumanTurn:  # if a user has made their second click, update the board and clear playerClicks
                        print("2 clicks: attempt move:")
                        print(playerClicks)
                        moveAttempt = Move(playerClicks[0], playerClicks[1], gs.board)  # creates object of class Move(startSq, endSq, board)
                        for i in range(len(validMoves)):
                            if moveAttempt == validMoves[i]:  # if move is in all moves, make move, change moveMade variable, clear playerClicks.
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:  # if len(playerClicks == 2) but move not a valid move, clear playerClicks
                            sqSelected = ()
                            playerClicks = []
                            print(playerClicks)

            elif e.type == p.KEYDOWN and isHumanTurn:
                if e.key == p.K_z and len(gs.moveLog) > 0:  # undo when 'z' is pressed.
                    if whitePlayer and blackPlayer:  # if both human players, undo the last human move
                        gs.undoMove()
                        validMoves = gs.getValidMoves()
                        gameOver = False
                    if whitePlayer and not blackPlayer:  # if only white human player
                        gs.undoMove()
                        gs.undoMove()
                        validMoves = gs.getValidMoves()
                        gameOver = False

        if gameOver:  # end of game logic
            clock.tick(5)
            if gs.inCheck:
                if gs.whiteToMove:
                    drawText(screen, "Black wins by checkmate")
                else:
                    drawText(screen, "White wins by checkmate")
            else:
                drawText(screen, "Stalemate")
        else:
            clock.tick(MAX_FPS)


        # ChessAI logic
        if not isHumanTurn and not gameOver:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()
                chessAIProcess = Process(target=findBestMove, args=(gs, validMoves, returnQueue))
                chessAIProcess.start()

            if not chessAIProcess.is_alive():  # if done thinking.
                AIMove = returnQueue.get()
                if AIMove is not None:
                    gs.makeMove(AIMove)
                    moveMade = True
                else:  # if checkmate inevitable
                    if validMoves:
                        AIMove = findRandomMove(validMoves)
                        gs.makeMove(AIMove)
                        moveMade = True
                AIThinking = False


        if moveMade:  # only calculate new moves after each turn, not each frame.
            animateMove(gs.moveLog[-1], screen, gs.board, clock)
            print([move.moveID for move in gs.moveLog])
            print()
            print("-----White to move-----") if gs.whiteToMove else print("-----Black to move-----")
            validMoves = gs.getValidMoves()
            if not validMoves:  # if no valid moves for next turn then gameOver
                gameOver = True
            moveMade = False


        p.display.flip()  # updates the full display Surface to the screen.
        drawGameState(screen, gs, validMoves, sqSelected)


if __name__ == "__main__":
    main()