"""
Defines the move class that is passed into the move functions of the GameState
"""
class Move:

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):  # ((start_col, start_row), (end_col, end_row), board)
        # position of mouse click is format sq_selected: (col, row)
        self.start_col = start_sq[0]
        self.start_row = start_sq[1]
        self.end_col = end_sq[0]
        self.end_row = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.move_id = f"C{self.start_col:01d}R{self.start_row:01d} -> C{self.end_col:01d}R{self.end_row:01d}"

        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7)

        # enpassant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        # castle
        self.is_castle_move = is_castle_move


    """
    Overriding the equals method. Only needed as we are using a class, would not be needed if we used strings, ints etc.
    """
    def __eq__(self, other):
        if isinstance(other, Move):  # if object other is class Move, then two moves are equivalent if their IDs are equivalent
            return self.move_id == other.move_id
        return False



class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs