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
def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        c, r = sq_selected
        if gs.board[r][c][0] == ("w" if gs.white_to_move else "b"):  # square selected is a piece of the person which turn it is
            surface = p.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)  # transparency value
            surface.fill(p.Color("blue"))
            screen.blit(surface, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight valid moves from that square
            surface.fill(p.Color("yellow"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(surface, (SQ_SIZE * move.end_col, SQ_SIZE * move.end_row))


"""
Animating a move
"""
def animate_move(move, screen, board, clock):
    global colors
    d_r = move.end_row - move.start_row
    d_c = move.end_col - move.start_col
    frames_per_square = 10  # frame to move 1 sq
    frame_count = (abs(d_r) + abs(d_c)) * frames_per_square
    for frame in range(frame_count + 1):
        c, r = (move.start_col + d_c*frame/frame_count, move.start_row + d_r*frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_col + move.end_row) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                en_passant_row = (move.end_row + 1) if move.piece_captured[0] == 'b' else (move.end_row - 1)
                end_square = p.Rect(move.end_col * SQ_SIZE, en_passant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


"""
Finish text
"""
def draw_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color("Black"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)


"""
Initialize a global dictionary of images. This will be called exactly once in the main
"""
def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wp", "wR", "wN", "wB", "wQ", "wK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(CHESS_DIR + '/images/' + piece + '.png'),
                                          (SQ_SIZE, SQ_SIZE))  # Note: we can access an image by "IMAGES['wp']"


"""
Responsible for all the graphics within a current gameState.
"""
def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)  # draw squares on the board
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)  # draw pieces on top of those squares


"""
Draws the squares on the board.  The top left square is always light.
"""
def draw_board(screen):
    global colors
    colors = [p.Color('whitesmoke'), p.Color('gray50')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board using the current GameState.board
"""
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], (c*SQ_SIZE,r*SQ_SIZE))
