import random

chessPieceValuesDictionary = {'K': 0, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'p': 1} # Dictionary of the points for each piece

knightPositionalScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]  # Allows AI to recognize the positional strength of knights

bishopPositionalScores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]  # Longer diagonals are better to be on

queenPositionalScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]  # Positions that are 4 points attack weak pawns

rookPositionalScores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 2, 2, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]  # Second row is usually the best row to be on

whitePawnPositionScores = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
]  # Higher score squares are on the further end of the board

blackPawnPositionScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8]
]  # Higher score squares are at the bottom of the board

piecePositionalScores = {
    "N": knightPositionalScores,
    "Q": queenPositionalScores,
    "R": rookPositionalScores,
    "B": bishopPositionalScores,
    "bp": blackPawnPositionScores,
    "wp": whitePawnPositionScores
}

checkmateScore = 100000
stalemateScore = 0
aiSearchDepth = 3
'''
Picks and returns a random move
'''


def choose_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


'''
Method to make the first recursive call
'''

def get_best_move(gs, valid_moves):  # Helper method to call the initial recursive call and return the result at the end
    next_move_1 = None
    random.shuffle(valid_moves)
    negamax_search(gs, valid_moves, aiSearchDepth, -checkmateScore, checkmateScore, 1 if gs.whiteToMove else -1)
    return next_move_1

def negamax_search(gs, valid_moves, depth, alpha, beta, turn_multiplier):  # Alpha is the upper bound, Beta is the lower bound*
    global next_move  # Fixed global variable to match the correct variable name
    if depth == 0:
        return turn_multiplier * evaluate_board(gs)
    # Ordering the moves will implement later
    max_score = -checkmateScore
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -negamax_search(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)  # the minimum and maximum get reversed for the opponent
        if score > max_score:
            max_score = score

        if depth == aiSearchDepth:
            next_move = move  # Fixed global variable to match the correct variable name
        gs.undo_move()

        if max_score > alpha:  # Pruning happens here
            alpha = max_score
        if alpha >= beta:  # We don't need to look anymore
            break
    return max_score

'''
Positive score is good for white --> negative score is good for black
'''
def evaluate_board(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -checkmateScore  # Black wins
        else:
            return checkmateScore  # White Wins
    elif gs.stalemate:
        return stalemateScore

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            # Score will be positive if white is winning, negative if black is winning
            square = gs.board[row][col]
            if square != '--':
                # I will score the board positionally
                piece_position_score = 0
                if square[1] != 'K':
                    if square[1] == 'p':  # for pawns
                        piece_position_score = piecePositionalScores[square][row][col]
                    else:  # for other pieces
                        piece_position_score = piecePositionalScores[square[1]][row][col]  # Gets the correct score of the pieces in the correct position
                if square[0] == 'w':
                    score += chessPieceValuesDictionary[square[1]] + piece_position_score
                elif square[0] == 'b':
                    score -= chessPieceValuesDictionary[square[1]] + piece_position_score

    return score


