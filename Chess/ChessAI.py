import random
import time
from PieceScores import *

CHECKMATE = 1000
STALEMATE = 0
WhiteDepth = 5
BlackDepth = 3
nextMove = None
counter = 0


"""
Score board.  +ve score is good for white, -ve score is good for black.
"""
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.staleMate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            color = square[0]
            piece = square[1]
            if square != "--":
                piecePositionScore = piecePositionScores[square][row][col]
                if color == 'w':
                    score += pieceScore[piece] + piecePositionScore * .1
                elif color == 'b':
                    score -= (pieceScore[piece] + piecePositionScore * .1)
    return score


"""
The function that is called by ChessMain
"""
def findBestMove(gs, validMoves, returnQueue):
    global nextMove, counter, WhiteDepth, BlackDepth
    startTime = time.time()
    nextMove, counter = None, 0
    depth = WhiteDepth if gs.whiteToMove else BlackDepth
    validMoves.sort(reverse=True, key=lambda move: moveSortAlgo(move, gs))
    bestScore = findMoveNegaMaxAlphaBeta(gs, validMoves, depth, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1, True if gs.whiteToMove else False)  # alpha = current max, so start lowest;  beta = current min so start hightest
    endTime = time.time()
    print(f"movesSearched: {counter}     maxScore: {bestScore:.3f}     Time: {endTime - startTime:.2f}")
    returnQueue.put(nextMove)


""""
Function to sort valid moves before they are passed into alpha-beta pruning.
Likely strongest moves should be searched first for better pruning efficiency
"""
def moveSortAlgo(move, gameState):
    score = 0

    if move.pieceCaptured != "--":
        score += 10 * pieceScore[move.pieceCaptured[1]] - pieceScore[move.pieceMoved[1]]

    if gameState.squareUnderAttack(move.endRow, move.endCol):
        if move.pieceCaptured == "--":
            score -= pieceScore[move.pieceMoved[1]]  # if a capture, already handled

    if move.pieceCaptured == "--" and gameState.squareUnderAttack(move.startRow, move.startCol):
        score += pieceScore[move.pieceMoved[1]] * 0.5

    if move.isPawnPromotion:
        score += pieceScore['Q'] - pieceScore['P']

    if move.pieceCaptured == "--":
        centerDistance = abs(3.5 - move.endRow) + abs(3.5 - move.endCol)
        score += (7 - centerDistance) * 0.1

    return score


"""
findNegaMaxAlphaBeta.  Always find the maximum score for black and white.
Alpha = Best score the current player has found so far (starts at -1000)
Beta = Best score the opponent has found so far (starts at +1000)
When beta < alpha, the maximizing player need not consider further descendants of this node, as opponent player won't let them reach it in real play.
"""
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, whiteAI):
    global nextMove, counter, WhiteDepth, BlackDepth
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE # worst scenario
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier, whiteAI)  # switch the alpha beta perspective.
        if score > maxScore:
            maxScore = score
            if (depth == WhiteDepth and whiteAI) or (depth == BlackDepth and not whiteAI):
                nextMove = move
                print(nextMove.moveID, f"{maxScore:.3f}")
        gs.undoMove()

        alpha = max(maxScore, alpha)  # pruning
        if beta <= alpha:  # we can stop searching here because opponent has already found a position limiting us to beta so will never let us reach this position in real play.
            break
    return maxScore


"""
Returns a random move.
"""
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]