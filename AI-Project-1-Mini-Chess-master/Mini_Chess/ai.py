import random

pieceValue = {"K": 0, "Q": 10, "R": 4, "B": 4, "N": 7, "P": 1}

knightGoodPositions = [[1, 1, 1, 1, 1, 1],
                       [1, 2, 2, 2, 2, 1],
                       [1, 2, 3, 3, 2, 1],
                       [1, 2, 3, 3, 2, 1],
                       [1, 2, 2, 2, 2, 1],
                       [1, 1, 1, 1, 1, 1]]

bishopGoodPositions = [[3, 2, 1, 1, 2, 3],
                       [3, 3, 2, 2, 3, 3],
                       [2, 3, 3, 3, 3, 2],
                       [2, 3, 3, 3, 3, 2],
                       [3, 3, 2, 2, 3, 3],
                       [3, 2, 1, 1, 2, 3]]

queenGoodPositions = [[1, 2, 1, 1, 2, 1],
                      [1, 2, 2, 2, 2, 1],
                      [1, 2, 3, 3, 2, 1],
                      [1, 2, 3, 3, 2, 1],
                      [1, 2, 2, 2, 2, 1],
                      [1, 2, 1, 1, 2, 1]]

rookGoodPositions = [[3, 3, 3, 3, 3, 3],
                     [3, 2, 2, 2, 2, 3],
                     [1, 2, 1, 2, 1, 2],
                     [1, 2, 1, 2, 1, 2],
                     [3, 2, 2, 2, 2, 3],
                     [3, 3, 3, 3, 3, 3]]

whitePawnGoodPositions = [[5, 5, 5, 5, 5, 5],
                          [4, 4, 4, 4, 4, 4],
                          [3, 3, 3, 3, 3, 3],
                          [2, 2, 2, 2, 2, 2],
                          [1, 1, 1, 1, 1, 1],
                          [0, 0, 0, 0, 0, 0]]

blackPawnGoodPositions = [[0, 0, 0, 0, 0, 0],
                          [1, 1, 1, 1, 1, 1],
                          [1, 2, 2, 2, 2, 1],
                          [2, 3, 3, 3, 3, 2],
                          [3, 4, 4, 4, 4, 3],
                          [5, 5, 5, 5, 5, 5]]

piecePositionalScores = {"N": knightGoodPositions, "B": bishopGoodPositions, "Q": queenGoodPositions,
                         "R":  rookGoodPositions, "w_P": whitePawnGoodPositions, "b_P": blackPawnGoodPositions}


CHECKMATE = float('inf')
STALEMATE = 0
DEPTH = 4


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


def findBestMove(gamestate, validMoves):
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    counter = 0
    MinMaxWithPruning(gamestate, validMoves, DEPTH, -CHECKMATE,
                      CHECKMATE, 1 if gamestate.whiteToMove else -1)
    print(f"{counter} possible moves in depth {DEPTH}")
    return nextMove


def MinMaxWithPruning(gamestate, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gamestate)

    maxScore = -CHECKMATE
    for move in validMoves:
        gamestate.makeMove(move)
        nextMoves = gamestate.getValidMoves()
        score = -MinMaxWithPruning(gamestate, nextMoves,
                                   depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        gamestate.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:  # pruning
            break

    return maxScore


def scoreBoard(gamestate):
    if gamestate.checkMate:
        if gamestate.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE

    elif gamestate.staleMate:
        return STALEMATE

    score = 0
    for row in range(len(gamestate.board)):
        for col in range(len(gamestate.board[row])):
            square = gamestate.board[row][col]
            if square != "--":  # scoring the pieces positionally
                piecePositionalScore = 0
                if square[-1] != "K":  # king doesn't need a positional score, it just needs safety
                    if square[-1] == "P":  # different for black or white pawns
                        piecePositionalScore = piecePositionalScores[square][row][col]
                    else:  # for any other pieces regardless of the color
                        piecePositionalScore = piecePositionalScores[square[-1]][row][col]

                if square[0] == 'w':
                    score += pieceValue[square[-1]] + piecePositionalScore * .1
                elif square[0] == 'b':
                    score -= pieceValue[square[-1]] + piecePositionalScore * .1

    return score
