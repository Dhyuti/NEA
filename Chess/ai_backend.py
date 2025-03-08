import random

# Dictionary of the points for each piece
piece_scores = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

# Positions that are 4 points attack weak pawns
queen_scores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1],
]

# Second row is usally the best row to be on for rooks
rook_scores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 2, 2, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4],
]

# Longer diagonals are better to be on
bishop_scores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4],
]

# Allows AI to recgonise the positional strength of knights
knight_scores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

# Higher score squares are on the further end of the board
white_pawn_scores = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

# Higher score squares are at the bottom of the board
black_pawn_scores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
]

piece_pos_scores = {
    "N": knight_scores,
    "Q": queen_scores,
    "R": rook_scores,
    "B": bishop_scores,
    "bp": black_pawn_scores,
    "wp": white_pawn_scores,
}

CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3


# Picks and returns a random move
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


# Method to make the first recursive call
# Helper method to call initial recursive call and return result at the end
def find_best_move(gs, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    turn_multiplier = 1 if gs.whiteToMove else -1
    neg_max_alpha_beta(
        gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, turn_multiplier
    )
    return next_move


# Alpha is the upper bound, Beta is the lower bound*
def neg_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(gs)
    # Ordering the moves - will implement later
    maxScore = -CHECKMATE
    for move in valid_moves:
        gs.makeMove(move)
        next_moves = gs.getValidMoves()
        # The minimum and maximum get reversed for the opponent
        score = -neg_max_alpha_beta(
            gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier
        )
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                next_move = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


"""
Postive score is good for white --> negative score is good for black
"""


def score_board(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            # Black wins
            return -CHECKMATE
        else:
            # White Wins
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            # Score positive if white is winning, negative if black is winning
            square = gs.board[row][col]
            if square != "--":
                # I will score the board positionally
                pos_score = 0
                if square[1] != "K":
                    # For pawns
                    if square[1] == "p":
                        pos_score = piece_pos_scores[square][row][col]
                    # For other pieces
                    else:
                        # Get correct score of pieces in the correct position
                        pos_score = piece_pos_scores[square[1]][row][col]
                if square[0] == "w":
                    score += piece_scores[square[1]] + pos_score
                elif square[0] == "b":
                    score -= piece_scores[square[1]] + pos_score
    return score
