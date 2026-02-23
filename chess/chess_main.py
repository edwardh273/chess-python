from multiprocessing import Process, Queue
from chess_game_state import GameState
from chess_ai import find_best_move, find_random_move
from move import Move
from display_funcs import *

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
    load_images()  # only do this once before the while loop

    # setup variables
    running = True
    move_made = False
    game_over = False
    ai_thinking = False
    chess_ai_process = None
    gs = GameState()  # initialize the GameState, white_to_move = True
    sq_selected = ()  # no square is selected initially.  Keeps track of last click of user (tuple: (col, row))
    player_clicks = []  # keep track of player clicks (two tuples: [(4, 7), (4, 5)])

    white_player = True  # if a human is playing white, then True.  If AI is playing, then false
    black_player = False  # same as above, but for black.


    valid_moves = gs.get_valid_moves()
    print()
    print("-----White to move-----")

    while running:

        is_human_turn = (gs.white_to_move and white_player) or (not gs.white_to_move and black_player)

        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    # pygame .get_pos is opposite to how you slice the array of the gs.board
                    location = p.mouse.get_pos()  # (col, row): (0,0)==top left;   (col=0, row=7)==bottom left;     (7, 7)==bottom right
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sq_selected == (col, row):  # the user clicked  the same square twice
                        sq_selected = ()  # deselect
                        player_clicks = []  # reset
                        print("user clicked same square twice, reset player_clicks")

                    else:
                        sq_selected = (col, row)
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 2 and is_human_turn:  # if a user has made their second click, update the board and clear player_clicks
                        print("2 clicks: attempt move:")
                        print(player_clicks)
                        move_attempt = Move(player_clicks[0], player_clicks[1], gs.board)  # creates object of class Move(startSq, endSq, board)
                        for i in range(len(valid_moves)):
                            if move_attempt == valid_moves[i]:  # if move is in all moves, make move, change move_made variable, clear player_clicks.
                                gs.make_move(valid_moves[i])
                                move_made = True
                                sq_selected = ()
                                player_clicks = []
                        if not move_made:  # if len(player_clicks == 2) but move not a valid move, clear player_clicks
                            sq_selected = ()
                            player_clicks = []
                            print(player_clicks)

            elif e.type == p.KEYDOWN and is_human_turn:
                if e.key == p.K_z and len(gs.move_log) > 0:  # undo when 'z' is pressed.
                    if white_player and black_player:  # if both human players, undo the last human move
                        gs.undo_move()
                        valid_moves = gs.get_valid_moves()
                        game_over = False
                    if white_player and not black_player:  # if only white human player
                        gs.undo_move()
                        gs.undo_move()
                        valid_moves = gs.get_valid_moves()
                        game_over = False

        if game_over:  # end of game logic
            clock.tick(5)
            if gs.in_check:
                if gs.white_to_move:
                    draw_text(screen, "Black wins by checkmate")
                else:
                    draw_text(screen, "White wins by checkmate")
            else:
                draw_text(screen, "Stalemate")
        else:
            clock.tick(MAX_FPS)


        # chess_ai logic
        if not is_human_turn and not game_over:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()
                chess_ai_process = Process(target=find_best_move, args=(gs, valid_moves, return_queue))
                chess_ai_process.start()

            if not chess_ai_process.is_alive():  # if done thinking.
                ai_move = return_queue.get()
                if ai_move is not None:
                    gs.make_move(ai_move)
                    move_made = True
                else:  # if checkmate inevitable
                    if valid_moves:
                        ai_move = find_random_move(valid_moves)
                        gs.make_move(ai_move)
                        move_made = True
                ai_thinking = False


        if move_made:  # only calculate new moves after each turn, not each frame.
            animate_move(gs.move_log[-1], screen, gs.board, clock)
            print([move.move_id for move in gs.move_log])
            print()
            print("-----White to move-----") if gs.white_to_move else print("-----Black to move-----")
            valid_moves = gs.get_valid_moves()
            if not valid_moves:  # if no valid moves for next turn then game_over
                game_over = True
            move_made = False


        p.display.flip()  # updates the full display Surface to the screen.
        draw_game_state(screen, gs, valid_moves, sq_selected)


if __name__ == "__main__":
    main()