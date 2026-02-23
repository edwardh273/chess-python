import random

CHECKMATE = 1000
STALEMATE = 0
next_move = None
DEPTH = 2
counter = 0

piece_score = {"K": 0, "Q": 10, "R": 5, "B": 3.25, "N": 3, "p": 1}

# Less advanced search algorithms below


def find_best_move_no_recursion(gs, valid_moves):
    """
    Finds best move based on material alone.  Written from the perspective of player = white, AI = black.
    Finds the move that produces our opponent's lowest, maximum score.
    Looks 2 moves ahead: the current move, and the return move.
    White best score = CHECKMATE; black best score = -CHECKMATE
    """
    # from the perspective of black, worst score is CHECKMATE, best score is -CHECKMATE
    # player = white
    # AI = black

    turn_multiplier = (
        1 if gs.white_to_move else -1
    )  # default is black to move as the AI when find_best_move called => -1
    player_lowest_max_score = (
        CHECKMATE  # start of worst case scenario for AI: a white checkmated black.
    )
    best_move = None

    random.shuffle(valid_moves)  # to prevent rook moving side to side
    for ai_move in valid_moves:
        gs.make_move(ai_move)  # the AI makes a move
        player_moves = (
            gs.get_valid_moves()
        )  # for every move the AI can potentially make, get valid player moves.

        # Given an AI move, find the highest scoring responding player move.
        player_max_score = (
            -CHECKMATE
        )  # start of worst case scenario for player (white): black checkmated white
        for player_move in player_moves:
            gs.make_move(player_move)
            if gs.check_mate:
                score = (
                    -turn_multiplier * CHECKMATE
                )  # now it's black to move.  Score = CHECKMATE, the best possible scenario for white.
            elif gs.stale_mate:
                score = STALEMATE
            else:
                score = -turn_multiplier * score_material(
                    gs.board
                )  # 1 * score_material.
            if score > player_max_score:
                player_max_score = score
            gs.undo_move()

        # find lowest player_max_score and make the AI move that leads to the player's lowest_max_score.
        if (
            player_max_score < player_lowest_max_score
        ):  # Anything less than +1000 (white checkmate) is better.
            player_lowest_max_score = player_max_score
            best_move = ai_move

        gs.undo_move()
    return best_move


def find_move_min_max(gs, valid_moves, depth, white_to_move: bool):
    """
    find_move_min_max.  +ve score is good for white, -ve score is good for black.
    Simple scoring algorithm with recursion to depth.
    Returns score of board at final move and changes the value of global variable next_move.
    Sets next_move equal to the first move of the recursion tree based on the highest board score at depth = DEPTH
    Counter = number of moves evaluated.
    """
    global next_move, counter
    counter += 1

    if depth == 0:
        return score_material(gs)

    if white_to_move:
        max_score = -CHECKMATE  # worst score possible.
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(
                gs, next_moves, depth - 1, False
            )  # increments counter by 1
            if score > max_score:  # finding highest score
                max_score = score
                if (
                    depth == DEPTH
                ):  # sets next_move equal to the first move of the recursion tree
                    next_move = move
            gs.undo_move()
        return max_score
    else:
        min_score = CHECKMATE  # worst case scenario
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs, next_moves, depth - 1, True)
            if score < min_score:  # looking for minimum score
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score


def find_move_nega_max(gs, valid_moves, depth, turn_multiplier):
    """
    Same as find_move_min_max, but always tries to maximise the score.
    turn_multiplier = 1 if gs.white_to_move else -1.
    """
    global next_move, counter
    counter += 1

    if depth == 0:
        return turn_multiplier * score_material(gs.board)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max(
            gs, next_moves, depth - 1, -turn_multiplier
        )  # -ve find_move_nega_max and -turn_multiplier cancel out at turn_multiplier * score_material(gs.board) to produce +ve score
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
                print(max_score)
        gs.undo_move()
    return max_score


def score_material(board):
    """
    Score the board based on material
    """
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]
    return score
