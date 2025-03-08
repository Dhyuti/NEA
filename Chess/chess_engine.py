"""
This file is responsible for storing all the information about the
state of the Chess Game. It is also responsible for validating moves
made by the user. It will also keep a move log.
"""

import pygame


class GameState:
    def __init__(self):
        # Board is an 8x8 2d List, each element of the list has 2 characters.
        # The first character represents the color of the piece: 'b' or 'w'
        # The second character represents the type of the piece:
        #   'K', 'Q', 'R', 'B', 'N', 'P'
        # "--" represents an empty space with no piece.
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

        self.moveMapping = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
        }
        self.whiteToMove = True
        self.moveLog = []
        # Exact location of white king and black king
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.inCheck = False
        # List of pinned pieces
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        # Coordinates for the square where it is possible to do en passant
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        # Castle Rights
        self.whiteCastleKingside = True
        self.whiteCastleQueenside = True
        self.blackCastleKingside = True
        self.blackCastleQueenside = True
        # Keeps track of the castles available
        self.castleRightsLog = [
            CastleRights(
                self.whiteCastleKingside,
                self.blackCastleKingside,
                self.whiteCastleQueenside,
                self.blackCastleQueenside,
            )
        ]

    def makeMove(self, move):
        # New position of the piece on the board
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # Replaces the initial position of the piece with a blank space
        self.board[move.startRow][move.startCol] = "--"
        # Keeps track of the move in order to undo
        self.moveLog.append(move)
        # Switches turns #updating the location of the king once moved
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        # Pawn Promotion
        running = True
        if move.isPawnPromotion:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.board[move.endRow][move.endCol] = (
                                move.pieceMoved[0] + "Q"
                            )
                            running = False
                        if event.key == pygame.K_r:
                            self.board[move.endRow][move.endCol] = (
                                move.pieceMoved[0] + "R"
                            )
                            running = False
                        if event.key == pygame.K_b:
                            self.board[move.endRow][move.endCol] = (
                                move.pieceMoved[0] + "B"
                            )
                            running = False
                        if event.key == pygame.K_n:
                            self.board[move.endRow][move.endCol] = (
                                move.pieceMoved[0] + "N"
                            )
                            running = False

        # Enpassant Move
        if move.isEnpassantMove:
            # Captures the move
            self.board[move.startRow][move.endCol] = "--"

        # Updating the enpassantPossible variable
        # Should only update the variable when a pawn has moved two squares
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            # The row position of the enpassant is the average of the starting
            # and ending row of the move made by the opponent.
            # The columns stay the same
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()
        self.enpassantPossibleLog.append(self.enpassantPossible)
        # Updating the rights to castle - Only when the rook or the king moves
        self.updateCastleRights(move)
        self.castleRightsLog.append(
            CastleRights(
                self.whiteCastleKingside,
                self.blackCastleKingside,
                self.whiteCastleQueenside,
                self.blackCastleQueenside,
            )
        )

        # Castling Moves
        if move.castle:
            # Kingside castle
            if move.endCol - move.startCol == 2:
                # Moves the rook
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                    move.endCol + 1
                ]
                # Empty space where the Rook was
                self.board[move.endRow][move.endCol + 1] = "--"
            # Queenside Castling
            else:
                # Moves the rook
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                    move.endCol - 2
                ]
                # Empty space where the Rook was
                self.board[move.endRow][move.endCol - 2] = "--"

    def undoMove(self):
        # Makes sure that the user has made a move previously
        if len(self.moveLog) != 0:
            # Returns and deletes the last move
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # Switches turns back to original user
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # Undoing enpassant move
            if move.isEnpassantMove:
                # Removes the pawn that was moved
                self.board[move.endRow][move.endCol] = "--"
                # Puts the opponent's pawn back onto the correct square
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            # Gets rid of the last item
            self.enpassantPossibleLog.pop()
            # sets the new items to the value of the last item in the log
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            # Undoing Castling Rights
            # Getting rid of the new castle rights from the move that is undone
            self.castleRightsLog.pop()
            # Sets the current castle rights to the last one in the list
            castleRights = self.castleRightsLog[-1]
            self.whiteCastleKingside = castleRights.wks
            self.blackCastleKingside = castleRights.bks
            self.whiteCastleQueenside = castleRights.wqs
            self.blackCastleQueenside = castleRights.bqs

            # Undoing a Castle
            if move.castle:
                # Kingside castle
                if move.endCol - move.startCol == 2:
                    # Moves the rook
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                        move.endCol - 1
                    ]
                    # Empty space where the Rook was
                    self.board[move.endRow][move.endCol - 1] = "--"
                # Queenside Castling
                else:
                    # Moves the rook
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][
                        move.endCol + 1
                    ]
                    # Empty space where the Rook was
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.checkmate = False
            self.stalemate = False

    """
    Will update the rights to castle based on the move
    """

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.whiteCastleQueenside = False
            self.whiteCastleKingside = False
        elif move.pieceMoved == "bk":
            self.blackCastleQueenside = False
            self.blackCastleKingside = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                # Left Rook
                if move.startCol == 0:
                    self.whiteCastleQueenside = False
                # Right Rook
                elif move.startCol == 7:
                    self.whiteCastleKingside = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                # left Rook
                if move.startCol == 0:
                    self.blackCastleQueenside = False
                # Right Rook
                elif move.startCol == 7:
                    self.blackCastleKingside = False

    """
    function for valid moves
    """

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            # Single Check
            if len(self.checks) == 1:
                # Blocking a check means you have to move a piece between
                # the enemy piece and the king
                moves = self.getAllPossibleMoves()
                # Checks the information about the check
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                # Gets the piece that is causing the check
                pieceCausingCheck = self.board[checkRow][checkCol]
                # Squares that can be moved to
                validSquares = []
                # If the piece causing the check is a knight,
                # the king must be moved or the knight must be captured
                if pieceCausingCheck[1] == "N":
                    # The only piece you can capture is the knight
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        # check[2] and check[3] are the directions of the check
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        # Once you get to the piece the check must end
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # Need to get rid of any moves that do not block the check
                # or move the king
                for i in range(len(moves) - 1, -1, -1):
                    # If the move doesn't move the king then it must block or
                    # capture the piece causing the check
                    if moves[i].pieceMoved[1] != "K":
                        # Move doesn't block the check or capture the piece
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            # The check is a double check so the king must move
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        # King is not in check so all moves are valid
        else:
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves

    def squareUnderAttack(self, r, c, friendly):
        enemyColour = "w" if friendly == "b" else "b"
        directions = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    # There is no attack in that direction
                    if endPiece[0] == friendly:
                        break
                    elif endPiece[0] == enemyColour:
                        type = endPiece[1]
                        if (
                            (0 <= j <= 3 and type == "R")
                            or (4 <= j <= 7 and type == "B")
                            or (
                                i == 1
                                and type == "p"
                                and (
                                    (enemyColour == "w" and 6 <= j <= 7)
                                    or (enemyColour == "b" and 4 <= j <= 5)
                                )
                            )
                            or (type == "Q")
                            or (i == 1 and type == "K")
                        ):
                            return True
                        # There are no impending checks by the enemy piece
                        else:
                            break
                else:
                    break
        # Check for Knight Checks
        directions = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        for m in directions:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                # Checks if the enemy Knight is attacking the king
                if endPiece[0] == enemyColour and endPiece[1] == "N":
                    return True
        return False

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColour = "b"
            friendly = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColour = "w"
            friendly = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # Checking from the kings location outwards for pins and checks
        directions = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    # Removes the possibility of the king being able to move
                    # in the same direction away from enemy piece whilst
                    # still being in check.
                    if endPiece[0] == friendly and endPiece[1] != "K":
                        # The first friendly piece could be pinned
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        # No pin or check possible in this direction as
                        # it is the second friendly piece
                        else:
                            break
                    elif endPiece[0] == enemyColour:
                        type = endPiece[1]
                        """
                            There are 5 possibilities for a piece to be
                            pinned/checked
                            1 - The piece is in front/behind or to the
                            left/right of the king and is a Rook
                            2 - The piece is diagonally away from the
                            King and is Bishop
                            3 - the piece is 1 square away diagonally
                            from the King and is a pawn
                            4 - The piece is in any direction and is a
                            Queen
                            5 - The piece is 1 square away in any
                            direction and is a King
                            (Kings cannot be next to each other)
                        """
                        if (
                            (0 <= j <= 3 and type == "R")
                            or (4 <= j <= 7 and type == "B")
                            or (
                                i == 1
                                and type == "p"
                                and (
                                    (enemyColour == "w" and 6 <= j <= 7)
                                    or (enemyColour == "b" and 4 <= j <= 5)
                                )
                            )
                            or (type == "Q")
                            or (i == 1 and type == "K")
                        ):
                            # If there is no pins there must be a check
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            # There is a piece blocking so there must be a pin
                            else:
                                pins.append(possiblePin)
                                break
                        # There are no impending checks by the enemy piece
                        else:
                            break
                else:
                    break

        # Check for Knight Checks
        directions = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        for m in directions:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                # Checks if the enemy Knight is attacking the king
                if endPiece[0] == enemyColour and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    """
    function for all the moves
    """

    def getAllPossibleMoves(self):
        # Start with an empty list
        moves = []
        # Will go through the board 8 times for each row
        for r in range(len(self.board)):
            # Goes through the columns in each row
            for c in range(len(self.board[r])):
                # Gives the first character of each piece
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (
                    turn == "b" and not self.whiteToMove
                ):
                    piece = self.board[r][c][1]
                    # Calls the appropiate function based
                    self.moveMapping[piece](r, c, moves)
        return moves

    """
    Gets all the move for pawns and adds these moves to the list
    """

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            kingRow, kingCol = self.whiteKingLocation
            enemyColour = "b"
        else:
            moveAmount = 1
            startRow = 1
            kingRow, kingCol = self.blackKingLocation
            enemyColour = "w"

        # Moving
        # 1 square pawn move
        if self.board[r + moveAmount][c] == "--":
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r + moveAmount, c), self.board))
                # 2 square pawn move
                if r == startRow and self.board[r + 2 * moveAmount][c] == "--":
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
        # Capturing
        if c - 1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                # Diagonal Left Capture
                if self.board[r + moveAmount][c - 1][0] == enemyColour:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board))
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    isAttackingPiece = isBlockingPiece = False
                    if kingRow == r:
                        # Checks if the king is left of the pawn
                        if kingCol < c:
                            """
                            Inside range is between the king and pawn,
                            outside range is between the pawn and the end
                            of the board
                            """
                            # Gives the list of values between king and pawn
                            insideRange = range(kingCol + 1, c - 1)
                            # Gives list of values between pawn and
                            # end of the board
                            outsideRange = range(c + 1, 8)
                        # King is to the rigth of the pawn
                        else:
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c - 2, -1, -1)
                        for i in insideRange:
                            # There is a piece blocking
                            if self.board[r][i] != "--":
                                isBlockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            # There is an attacking piece
                            if square[0] == enemyColour and (
                                square[1] == "R" or square[1] == "Q"
                            ):
                                isAttackingPiece = True
                            elif square != "--":
                                isBlockingPiece = True
                    if not isAttackingPiece or isBlockingPiece:
                        moves.append(
                            Move(
                                (r, c),
                                (r + moveAmount, c - 1),
                                self.board,
                                isEnpassantMove=True,
                            )
                        )
        if c + 1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                # Diagonal Right Capture
                if self.board[r + moveAmount][c + 1][0] == enemyColour:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    isAttackingPiece = isBlockingPiece = False
                    if kingRow == r:
                        # Checks if the king is left of the pawn
                        if kingCol < c:
                            """
                            Inside range is between the king and pawn,
                            outside range is between the pawn and the
                            end of the board
                            """
                            # Gives the list of values between king and pawn
                            insideRange = range(kingCol + 1, c)
                            # Give list of vlaues between pawn
                            # and end of the board
                            outsideRange = range(c + 2, 8)
                        # King is to the rigtht of the pawn
                        else:
                            insideRange = range(kingCol - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            # There is a piece blocking
                            if self.board[r][i] != "--":
                                isBlockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            # There is an attacking piece
                            if square[0] == enemyColour and (
                                square[1] == "R" or square[1] == "Q"
                            ):
                                isAttackingPiece = True
                            elif square != "--":
                                isBlockingPiece = True
                        if not isAttackingPiece or isBlockingPiece:
                            moves.append(
                                Move(
                                    (r, c),
                                    (r + moveAmount, c + 1),
                                    self.board,
                                    isEnpassantMove=True,
                                )
                            )

    """
    Gets all the move for Rooks and adds these moves to the list
    """

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                # We cannot get rid of the queen from a pin on the rook moves,
                # we will only remove it on a bishop
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        # Rooks move--> up, left, down, right
        # list of tuples of all the possible directions for Rooks
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        if self.whiteToMove:
            enemyColour = "b"
        else:
            enemyColour = "w"
        for d in directions:
            for i in range(1, 8):
                # Gets all the rows in the given direction
                endRow = r + d[0] * i
                # Gets all the columns in the given direction
                endCol = c + d[1] * i
                # Checks if the piece is on the board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    # Checks if the pin is in the direction
                    # or the opposite direction as well
                    if (
                        not piecePinned
                        or pinDirection == d
                        or pinDirection == (-d[0], -d[1])
                    ):
                        endSquare = self.board[endRow][endCol]
                        # Check if the squares in the given direction are empty
                        if endSquare == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        # Check if the first index of the piece in the
                        # underlying text based game is the enemy colour
                        elif endSquare[0] == enemyColour:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        # When the endSquare is off the board
                        else:
                            break
                else:
                    break

    """
    Gets all the move for Knights and adds these moves to the list
    """

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        directions = (
            (1, -2),
            (2, -1),
            (2, 1),
            (1, 2),
            (-1, 2),
            (-2, 1),
            (-2, -1),
            (-1, -2),
        )
        if self.whiteToMove:
            friendly = "w"
        else:
            friendly = "b"
        for i in directions:
            endRow = r + i[0]
            endCol = c + i[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endSquare = self.board[endRow][endCol]
                    # Only have to mention friendly piece
                    if endSquare[0] != friendly:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Gets all the move for Bishops and adds these moves to the list
    """

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        if self.whiteToMove:
            enemyColour = "b"
        else:
            enemyColour = "w"
        for d in directions:
            for i in range(1, 8):
                # Gets all the rows in the given direction
                endRow = r + d[0] * i
                # Gets all the columns in the given direction
                endCol = c + d[1] * i
                # Checks if the piece is on the board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if (
                        not piecePinned
                        or pinDirection == d
                        or pinDirection == (-d[0], -d[1])
                    ):
                        endSquare = self.board[endRow][endCol]
                        # Checks if the squares in the given direction is empty
                        if endSquare == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        # Checks if the first index of the piece in the
                        # underlying text based game is the enemy colour
                        elif endSquare[0] == enemyColour:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        # When the endSquare is off the board
                        else:
                            break
                else:
                    break

    """
    Gets all the move for Queens and adds these moves to the list
    """

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        # Possible row direction for possible moves
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        # Possible column direction for possible moves
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        if self.whiteToMove:
            friendly = "w"
        else:
            friendly = "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endSquare = self.board[endRow][endCol]
                if endSquare[0] != friendly:
                    # Place the king on the end square and check for checks
                    if friendly == "w":
                        # Temporarily moves king
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        # Temporarily moves king
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # Placing the king back in its original position
                    if friendly == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        self.getCastleMoves(r, c, moves, friendly)

    """
    Generating all the valid castle moves for the king at the
    specific row and column and adding them to the list of moves
    """

    def getCastleMoves(self, r, c, moves, friendly):
        inCheck = self.squareUnderAttack(r, c, friendly)
        if inCheck:
            # Cannot castle if in check
            return
        if (self.whiteToMove and self.whiteCastleKingside) or (
            not self.whiteToMove and self.blackCastleKingside
        ):
            self.getKingsideCastleMoves(r, c, moves, friendly)
        if (self.whiteToMove and self.whiteCastleQueenside) or (
            not self.whiteToMove and self.blackCastleQueenside
        ):
            self.getQueensideCastleMoves(r, c, moves, friendly)

    """
    Generates Kingside castle moves - will only be called if the
    player still has the rights to castle
    """

    def getKingsideCastleMoves(self, r, c, moves, friendly):
        if (
            self.board[r][c + 1] == "--"
            and self.board[r][c + 2] == "--"
            and not self.squareUnderAttack(r, c + 1, friendly)
            and not self.squareUnderAttack(r, c + 2, friendly)
        ):
            moves.append(Move((r, c), (r, c + 2), self.board, castle=True))

    """
    Generates Queenside castle moves - will only be called if the
    player still has the rights to castle
    """

    def getQueensideCastleMoves(self, r, c, moves, friendly):
        # Will check if the squares between the king and the rook is clear
        # and if the two squares to the left of the king is not under attack
        if (
            self.board[r][c - 1] == "--"
            and self.board[r][c - 2] == "--"
            and self.board[r][c - 3] == "--"
            and not self.squareUnderAttack(r, c - 1, friendly)
            and not self.squareUnderAttack(r, c - 2, friendly)
        ):
            moves.append(Move((r, c), (r, c - 2), self.board, castle=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # Creating a dictionary that will map the computer notation
    # of the board into algebraic notation
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    # Inlcusion of an optional parameter
    def __init__(self, startSq, endSq, board, isEnpassantMove=False, castle=False):
        # startSq is a tuple
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn Promotion
        # The game starts of with 0 pawn promotions
        self.isPawnPromotion = False
        # These are the conditions for pawn promotion
        if (self.pieceMoved == "wp" and self.endRow == 0) or (
            self.pieceMoved == "bp" and self.endRow == 7
        ):
            self.isPawnPromotion = True
        # Enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.isCapture = self.pieceCaptured != "--"
        self.castle = castle
        # Hash Function - Generates a unique id from 0 to 7777
        # (Each number represents the start/end row or column)
        self.moveId = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )

    """
    Comparing objects
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    # overriding the str() function
    def __str__(self):
        # Castle Move
        # 'O-O' is Kingside Castle, 'O-O-O' is Queenside Castle
        if self.castle:
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.getRankFile(self.endRow, self.endCol)
        # Pawn Moves
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
        # Other Pieces moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare
