from move import Move, CastleRights


class GameState:
    """
    This class is responsible for storing all the information about the current
    state of a chess game.  It will also be responsible for determining the valid
    moves at the current state.  It will also keep a move log.
    """

    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.move_functions = {
            "p": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "Q": self.get_queen_moves,
            "K": self.get_king_moves,
        }

        self.white_king_location, self.black_king_location = (4, 7), (
            4,
            0,
        )  # (col, row)

        # initialise variables to store game data
        self.white_to_move = True
        self.move_log = []

        self.pins, self.checks, self.in_check = [], [], False
        self.check_mate, self.stale_mate = False, False

        self.enpassant_possible = ()
        self.enpassant_possible_log = [self.enpassant_possible]

        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [
            CastleRights(
                self.current_castling_rights.wks,
                self.current_castling_rights.bks,
                self.current_castling_rights.wqs,
                self.current_castling_rights.bqs,
            )
        ]  # initial log is [(T, T, T, T)]

    def get_all_possible_moves(self):
        """
        Iterates through all pieces of the board, calculating possible moves for every piece of the color of whose turn it is.
        """
        moves = []  # ((startCol, startRow), (endCol, endRow), board)
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of cols in given row
                color, piece = self.board[r][c][0], self.board[r][c][1]
                if (color == "b" and self.white_to_move == False) or (
                    color == "w" and self.white_to_move == True
                ):  # if the piece is black, and it's black's turn, or if piece is white, and it's white's turn:
                    self.move_functions[piece](
                        r, c, moves
                    )  # appends all moves for each pieces to list moves = []
        return moves

    def get_valid_moves(self):
        """
        All moves considering check
        """
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()

        if self.white_to_move:
            king_col, king_row = (
                self.white_king_location[0],
                self.white_king_location[1],
            )
        else:
            king_col, king_row = (
                self.black_king_location[0],
                self.black_king_location[1],
            )
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check: block check or move king
                moves = self.get_all_possible_moves()
                check = self.checks[0]  # (endCol, endRow, dir-col, dir-row)
                check_col = check[0]
                check_row = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                if (
                    piece_checking[1] == "N"
                ):  # if knight, must capture knight or move king
                    valid_squares = [(check_col, check_row)]
                else:  # else block the check
                    for i in range(1, 8):
                        valid_square = (
                            king_col + check[2] * i,
                            king_row + check[3] * i,
                        )  # check[2] == dir-col, check[3] == dir-row
                        valid_squares.append(valid_square)
                        if (
                            valid_square[0] == check_col
                            and valid_square[1] == check_row
                        ):  # go upto the check square
                            break
                # get rid of any moves that don't block check or more king
                for i in range(
                    len(moves) - 1, -1, -1
                ):  # go through backwards when removing from a list
                    if (
                        moves[i].piece_moved[1] != "K"
                    ):  # move doesn't move king, so must block or capture
                        if not (moves[i].end_col, moves[i].end_row) in valid_squares:
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
        else:  # not in check so all moves are fine
            moves = self.get_all_possible_moves()

        # to generate castle moves
        if self.white_to_move:
            self.get_castle_moves(
                7, 4, moves
            )  # can only castle if the king hasn't moved.
        else:
            self.get_castle_moves(0, 4, moves)
        return moves

    def check_for_pins_and_checks(self):
        """
        Returns if the player is in check, a list of pins, and a list of checks
        """
        pins = (
            []
        )  # square of pinned piece & direction pinned from: (endCol, endRow, dir-col, dir-row)
        checks = (
            []
        )  # squares where enemy is applying a check: (endCol, endRow, dir-col, dir-row)
        in_check = False
        if self.white_to_move:
            enemy_color, ally_color = "b", "w"
            start_col, start_row = (
                self.white_king_location[0],
                self.white_king_location[1],
            )
        else:
            enemy_color, ally_color = "w", "b"
            start_col, start_row = (
                self.black_king_location[0],
                self.black_king_location[1],
            )
        # check outward from king for pins and checks, keep track of pins.  Pin direction is OUTWARD from the KING
        directions = (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1),
        )  # (col, row): l, r, u, d, lu, ru, ld, rd
        for j in range(len(directions)):
            d = directions[j]  # (1, 1)
            possible_pin = ()  # reset possible pin for said direction
            for i in range(1, 8):  # up until the end of the board
                end_col = start_col + d[0] * i
                end_row = start_row + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    # check for pins
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # 1st allied piece could be pinned
                            possible_pin = (end_col, end_row, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction.
                            break
                    # check for checks
                    elif end_piece[0] == enemy_color:
                        piece = end_piece[1]
                        # orthogonally from king & piece == rook
                        # diagonally & piece == bishop
                        # 1 square away & piece == pawn
                        # any direction & piece == queen
                        # any direction 1 square away & piece == king
                        if (
                            (0 <= j <= 3 and piece == "R")
                            or (4 <= j <= 7 and piece == "B")
                            or (
                                i == 1
                                and piece == "p"
                                and (
                                    (enemy_color == "w" and 6 <= j <= 7)
                                    or (enemy_color == "b" and 4 <= j <= 5)
                                )
                            )
                            or (piece == "Q")
                            or (i == 1 and piece == "K")
                        ):
                            if (
                                possible_pin == ()
                            ):  # if enemyPiece in range and no pin, in_check = True.
                                in_check = True
                                checks.append((end_col, end_row, d[0], d[1]))
                                break
                            else:  # allied piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break
        # knight checks
        knight_moves = (
            (-1, -2),
            (-2, -1),
            (-2, 1),
            (-1, 2),
            (1, 2),
            (2, 1),
            (2, -1),
            (1, -2),
        )
        for m in knight_moves:
            end_col = start_col + m[0]
            end_row = start_row + m[1]
            if 0 <= end_col < 8 and 0 <= end_row < 8:
                end_piece = self.board[end_row][end_col]
                if (
                    end_piece[0] == enemy_color and end_piece[1] == "N"
                ):  # enemy knight attacking king
                    in_check = True
                    checks.append((end_col, end_row, m[0], m[1]))

        return in_check, pins, checks

    def undo_move(self):
        """
        Undo the last move made
        """
        if len(self.move_log) != 0:  # make sure that there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            # update king's location
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_col, move.start_row)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_col, move.start_row)

            self.white_to_move = not self.white_to_move  # swap players back

            # undo enpassant
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"  # leave landing sq blank
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_col, move.end_row)
            # undo a 2 sq pawn advance
            if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()

            # move rook back if a castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingside
                    self.board[move.end_row][move.end_col + 1] = self.board[
                        move.end_row
                    ][move.end_col - 1]
                    self.board[move.end_row][
                        move.end_col - 1
                    ] = "--"  # remove the old rook

                elif move.end_col - move.start_col == -2:  # queenside
                    self.board[move.end_row][move.end_col - 2] = self.board[
                        move.end_row
                    ][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"

            # undo castling rights
            self.castle_rights_log.pop()  # get rid of castle rights from move we are undoing.
            last_castle_rights = self.castle_rights_log[-1]
            self.current_castling_rights = CastleRights(
                last_castle_rights.wks,
                last_castle_rights.bks,
                last_castle_rights.wqs,
                last_castle_rights.bqs,
            )  # reinitialize castle rights to not make a copy

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            self.check_mate = False
            self.stale_mate = False

    def make_move(self, move):
        """
        Takes a Move as a parameter and executes it.  After making move, changes White to move parameter
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # log the move to undo later.

        # update the king's location
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_col, move.end_row)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_col, move.end_row)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # enpassant
        if (
            move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2
        ):  # if a pawn moves 2 squares
            self.enpassant_possible = (
                move.start_col,
                (move.start_row + move.end_row) // 2,
            )  # enpassant possible to the square where the pawn would have moved if it had only moved 1 square.
        else:
            self.enpassant_possible = ()
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "--"  # capturing the pawn

        # castling
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # to the right: king side castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1
                ]  # copy the rook to the new square
                self.board[move.end_row][move.end_col + 1] = "--"  # remove the old rook

            elif move.end_col - move.start_col == -2:  # to the left: queen side castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2
                ]
                self.board[move.end_row][move.end_col - 2] = "--"

        self.update_castle_rights(
            move
        )  # update the castling rights whenever it's a rook or a king move
        self.castle_rights_log.append(
            CastleRights(
                self.current_castling_rights.wks,
                self.current_castling_rights.bks,
                self.current_castling_rights.wqs,
                self.current_castling_rights.bqs,
            )
        )

        self.enpassant_possible_log.append(self.enpassant_possible)

        self.white_to_move = not self.white_to_move  # swap players of the gameState

    def update_castle_rights(self, move):
        """
        Update the castle rights given a move
        """
        # check if the king moved or the rock moved
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:  # whites left rock
                    self.current_castling_rights.wqs = False
                if move.start_col == 7:  # whites right rock
                    self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0:  # black left rock
                    self.current_castling_rights.bqs = False
                if move.start_col == 7:  # black right rock
                    self.current_castling_rights.bks = False
        # check if the rock is captured
        if move.piece_captured == "wR":
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.bks = False

    def get_castle_moves(self, r, c, moves):
        """
        Get all castle moves
        """
        if not self.white_to_move and self.black_king_location != (4, 0):
            return
        if self.white_to_move and self.white_king_location != (4, 7):
            return
        if not (
            self.board[r][c - 1] == "--"
            and self.board[r][c - 2] == "--"
            and self.board[r][c - 3] == "--"
        ) and not (self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--"):
            return  # if queenside and kingside blocked, return.

        if self.square_under_attack(r, c):
            return  # check if the king is inCheck as the king can't escape the check by castling
        if (self.white_to_move and self.current_castling_rights.wks) or (
            not self.white_to_move and self.current_castling_rights.bks
        ):  # kingside
            self.get_king_side_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (
            not self.white_to_move and self.current_castling_rights.bqs
        ):  # queenside
            self.get_queen_side_castle_moves(r, c, moves)

    def get_king_side_castle_moves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(
                r, c + 2
            ):
                moves.append(Move((c, r), (c + 2, r), self.board, is_castle_move=True))

    def get_queen_side_castle_moves(self, r, c, moves):
        if (
            self.board[r][c - 1] == "--"
            and self.board[r][c - 2] == "--"
            and self.board[r][c - 3] == "--"
        ):
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(
                r, c - 2
            ):  # only squares king moves through need to not be under attack.
                moves.append(Move((c, r), (c - 2, r), self.board, is_castle_move=True))

    def square_under_attack(self, r, c):
        """
        Determine if the enemy can attack the square r, c.  Returns True, False
        """

        enemy_color = "b" if self.white_to_move else "w"

        # check for knights
        knight_moves = (
            (-1, -2),
            (-2, -1),
            (-2, 1),
            (-1, 2),
            (1, 2),
            (2, 1),
            (2, -1),
            (1, -2),
        )
        for m in knight_moves:
            nr, nc = r + m[0], c + m[1]
            if 0 <= nr <= 7 and 0 <= nc <= 7:
                if self.board[nr][nc] == enemy_color + "N":
                    return True

        # check for other pieces
        directions = (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1),
        )  # (col, row): l, r, u, d, lu, ru, ld, rd
        for j in range(len(directions)):
            d = directions[j]  # (1, 1)
            for i in range(1, 8):  # up until the end of the board
                end_col = c + d[0] * i
                end_row = r + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == enemy_color:
                        piece = end_piece[1]
                        # orthogonally  && piece == rook
                        # diagonally && piece == bishop
                        # 1 square away && piece == pawn
                        # any direction & piece == queen
                        # any direction 1 square away & piece == king
                        if (
                            (0 <= j <= 3 and piece == "R")
                            or (4 <= j <= 7 and piece == "B")
                            or (
                                i == 1
                                and piece == "p"
                                and (
                                    (enemy_color == "w" and 6 <= j <= 7)
                                    or (enemy_color == "b" and 4 <= j <= 5)
                                )
                            )
                            or (piece == "Q")
                            or (i == 1 and piece == "K")
                        ):
                            return True
                        else:  # if enemy piece detected, but cannot attack, then it is blocking.
                            break
                    elif (
                        end_piece != "--"
                    ):  # if friendly piece, then also blocking this direction.
                        break
        return False

    def get_pawn_moves(self, r, c, moves):
        """
        Get all pawn moves for the pawn located at row, col and add these moves to the list
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if (
                self.pins[i][0] == c and self.pins[i][1] == r
            ):  # pins = (endCol, endRow, d[0], d[1])
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.white_to_move:  # white pawn moves
            if self.board[r - 1][c] == "--":  # moving forwards
                if not piece_pinned or pin_direction == (0, -1):
                    moves.append(Move((c, r), (c, r - 1), self.board))
                    if (
                        r == 6 and self.board[r - 2][c] == "--"
                    ):  # move 2 squares forward
                        moves.append(Move((c, r), (c, r - 2), self.board))
            if c - 1 >= 0:  # capturing left (ensures not off board)
                if self.board[r - 1][c - 1][0] == "b":
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((c, r), (c - 1, r - 1), self.board))
                elif (c - 1, r - 1) == self.enpassant_possible and self.board[r][c - 1][
                    0
                ] == "b":
                    moves.append(
                        Move((c, r), (c - 1, r - 1), self.board, is_enpassant_move=True)
                    )
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(
                            Move(
                                (c, r),
                                (c - 1, r - 1),
                                self.board,
                                is_enpassant_move=True,
                            )
                        )
            if c + 1 <= 7:  # capturing right
                if self.board[r - 1][c + 1][0] == "b":
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((c, r), (c + 1, r - 1), self.board))
                elif (c + 1, r - 1) == self.enpassant_possible and self.board[r][c + 1][
                    0
                ] == "b":
                    moves.append(
                        Move((c, r), (c + 1, r - 1), self.board, is_enpassant_move=True)
                    )
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(
                            Move(
                                (c, r),
                                (c + 1, r - 1),
                                self.board,
                                is_enpassant_move=True,
                            )
                        )

        else:  # black pawn moves
            if self.board[r + 1][c] == "--":  # moving forwards
                if not piece_pinned or pin_direction == (0, 1):
                    moves.append(Move((c, r), (c, r + 1), self.board))
                    if (
                        r == 1 and self.board[r + 2][c] == "--"
                    ):  # move 2 squares forward
                        moves.append(Move((c, r), (c, r + 2), self.board))
            if c - 1 >= 0:  # capturing left
                if self.board[r + 1][c - 1][0] == "w":
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((c, r), (c - 1, r + 1), self.board))
                elif (c - 1, r + 1) == self.enpassant_possible and self.board[r][c - 1][
                    0
                ] == "w":
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(
                            Move(
                                (c, r),
                                (c - 1, r + 1),
                                self.board,
                                is_enpassant_move=True,
                            )
                        )
            if c + 1 <= 7:  # capturing right
                if self.board[r + 1][c + 1][0] == "w":
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((c, r), (c + 1, r + 1), self.board))
                elif (c + 1, r + 1) == self.enpassant_possible and self.board[r][c + 1][
                    0
                ] == "w":
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(
                            Move(
                                (c, r),
                                (c + 1, r + 1),
                                self.board,
                                is_enpassant_move=True,
                            )
                        )

    def get_rook_moves(self, r, c, moves):
        """
        Get all Rook moves for the Rook located at row, col and add these moves to the list
        """
        piece_pinned, pin_direction = False, ()  # set  initial variables
        for i in range(len(self.pins) - 1, -1, -1):
            if (
                self.pins[i][0] == c and self.pins[i][1] == r
            ):  # (endCol, endRow, d[0], d[1]).
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])  # dir[col], dir[row]
                if self.board[r][c][1] != "Q":  # pinned piece = rook and not a queen
                    self.pins.remove(self.pins[i])
                break
        enemy_color = "b" if self.white_to_move == True else "w"
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))  # left, right, up, down
        for d in directions:
            for i in range(1, 8):
                end_col = c + d[0] * i
                end_row = r + d[1] * i
                if (
                    0 <= end_row < 8 and 0 <= end_col < 8
                ):  # confine the potential moves to the board
                    if (
                        not piece_pinned
                        or pin_direction == d
                        or pin_direction == (-d[0], -d[1])
                    ):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # if blank, append move
                            moves.append(Move((c, r), (end_col, end_row), self.board))
                        elif (
                            end_piece[0] == enemy_color
                        ):  # hits enemy piece, append then break
                            moves.append(Move((c, r), (end_col, end_row), self.board))
                            break
                        else:  # hits own color piece
                            break
                else:  # off board
                    break

    def get_bishop_moves(self, r, c, moves):
        """
        Get all Bishop moves for the Bishop located at row, col and add these moves to the list
        """
        piece_pinned, pin_direction = False, ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == c and self.pins[i][1] == r:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":  # pinned piece = bishop and not a queen
                    self.pins.remove(self.pins[i])
                break
        enemy_color = "b" if self.white_to_move == True else "w"
        directions = (
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1),
        )  # leftup, rightup, leftdown, rightdown
        for d in directions:
            for i in range(1, 8):
                end_col = c + d[0] * i
                end_row = r + d[1] * i
                if (
                    0 <= end_row < 8 and 0 <= end_col < 8
                ):  # confine the potential moves to the board
                    if (
                        not piece_pinned
                        or pin_direction == d
                        or pin_direction == (-d[0], -d[1])
                    ):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # if blank, append move
                            moves.append(Move((c, r), (end_col, end_row), self.board))
                        elif (
                            end_piece[0] == enemy_color
                        ):  # hits enemy piece, append then break
                            moves.append(Move((c, r), (end_col, end_row), self.board))
                            break
                        else:  # hits own color piece
                            break
                else:  # off board
                    break

    def get_queen_moves(self, r, c, moves):
        """
        Get all Queen moves for the Queen located at row, col and add these moves to the list
        """
        self.get_bishop_moves(r, c, moves)
        self.get_rook_moves(r, c, moves)

    def get_knight_moves(self, r, c, moves):
        """
        Get all Knight moves for the Knight located at row, col and add these moves to the list
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == c and self.pins[i][1] == r:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        potential_moves = (
            (-1, -2),
            (-2, -1),
            (-2, 1),
            (-1, 2),
            (1, 2),
            (2, 1),
            (2, -1),
            (1, -2),
        )
        ally_color = "w" if self.white_to_move == True else "b"
        for m in potential_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if (
                0 <= end_row < 8 and 0 <= end_col < 8
            ):  # confine the potential moves to the board
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((c, r), (end_col, end_row), self.board))

    def get_king_moves(self, r, c, moves):
        """
        Get all King moves for the King located at row, col and add these moves to the list
        """
        potential_moves = (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1),
        )
        ally_color = "w" if self.white_to_move == True else "b"
        for m in potential_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if (
                0 <= end_row < 8 and 0 <= end_col < 8
            ):  # confine the potential moves to the board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # empty or enemy piece
                    if ally_color == "w":  # place king on square and check for checks
                        self.white_king_location = (end_col, end_row)
                    else:
                        self.black_king_location = (end_col, end_row)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((c, r), (end_col, end_row), self.board))
                    if ally_color == "w":
                        self.white_king_location = (
                            c,
                            r,
                        )  # place king back on original location
                    else:
                        self.black_king_location = (c, r)
