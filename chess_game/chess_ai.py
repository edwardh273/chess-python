import random
import time
from piece_scores import *

CHECKMATE = 1000
STALEMATE = 0
white_depth = 5
black_depth = 3
next_move = None
counter = 0


def score_board(gs):
    """
    Score board.  +ve score is good for white, -ve score is good for black.
    """
    if gs.check_mate:
        if gs.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stale_mate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            color = square[0]
            piece = square[1]
            if square != "--":
                piece_position_score = piece_position_scores[square][row][col]
                if color == 'w':
                    score += piece_score[piece] + piece_position_score * .1
                elif color == 'b':
                    score -= (piece_score[piece] + piece_position_score * .1)
    return score


def find_best_move(gs, validMoves, returnQueue):
    """
    The function that is called by chess_main
    """
    global next_move, counter, white_depth, black_depth
    start_time = time.time()
    next_move, counter = None, 0
    depth = white_depth if gs.white_to_move else black_depth
    validMoves.sort(reverse=True, key=lambda move: move_sort_algo(move, gs))
    best_score = find_move_nega_max_alpha_beta(gs, validMoves, depth, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1, True if gs.white_to_move else False)  # alpha = current max, so start lowest;  beta = current min so start hightest
    end_time = time.time()
    print(f"movesSearched: {counter}     maxScore: {best_score:.3f}     Time: {end_time - start_time:.2f}")
    returnQueue.put(next_move)


def move_sort_algo(move, game_state):
    """
    Function to sort valid moves before they are passed into alpha-beta pruning.
    Likely strongest moves should be searched first for better pruning efficiency
    """
    score = 0

    if move.piece_captured != "--":
        score += 10 * piece_score[move.piece_captured[1]] - piece_score[move.piece_moved[1]]

    if game_state.square_under_attack(move.end_row, move.end_col):
        if move.piece_captured == "--":
            score -= piece_score[move.piece_moved[1]]  # if a capture, already handled

    if move.piece_captured == "--" and game_state.square_under_attack(move.start_row, move.start_col):
        score += piece_score[move.piece_moved[1]] * 0.5

    if move.is_pawn_promotion:
        score += piece_score['Q'] - piece_score['P']

    if move.piece_captured == "--":
        center_distance = abs(3.5 - move.end_row) + abs(3.5 - move.end_col)
        score += (7 - center_distance) * 0.1

    return score


def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier, white_ai):
    """
    find_move_nega_max_alpha_beta.  Always find the maximum score for black and white.
    Alpha = Best score the current player has found so far (starts at -1000)
    Beta = Best score the opponent has found so far (starts at +1000)
    When beta < alpha, the maximizing player need not consider further descendants of this node, as opponent player won't let them reach it in real play.
    """
    global next_move, counter, white_depth, black_depth
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE # worst scenario
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_moves, depth-1, -beta, -alpha, -turn_multiplier, white_ai)  # switch the alpha beta perspective.
        if score > max_score:
            max_score = score
            if (depth == white_depth and white_ai) or (depth == black_depth and not white_ai):
                next_move = move
                print(next_move.move_id, f"{max_score:.3f}")
        gs.undo_move()

        alpha = max(max_score, alpha)  # pruning
        if beta <= alpha:  # we can stop searching here because opponent has already found a position limiting us to beta so will never let us reach this position in real play.
            break
    return max_score


def find_random_move(valid_moves):
    """
    Returns a random move.
    """
    return valid_moves[random.randint(0, len(valid_moves)-1)]