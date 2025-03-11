class Move():
    # Convert board coordinates to chess notation
    ranksToRows = {"1": 5, "2": 4, "3": 3, "4": 2, "5": 1, "6": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        
        # Pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'w_P' and self.endRow == 0) or (self.pieceMoved == 'b_P' and self.endRow == 5):
            self.isPawnPromotion = True

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


class GameState():

    def __init__(self) -> None:

        self.board = [
            ['b_R', 'b_N', 'b_B', 'b_Q', 'b_K', 'b_R'],
            ['b_P', 'b_P', 'b_P', 'b_P', 'b_P', 'b_P'],
            ['--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--'],
            ['w_P', 'w_P', 'w_P', 'w_P', 'w_P', 'w_P'],
            ['w_R', 'w_N', 'w_B', 'w_Q', 'w_K', 'w_R']
        ]

        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves,
                              'N': self.getKnightMoves, 'B': self.getBishopMoves,
                              'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []

        # King locations
        self.whiteKingLocation = (5, 4)
        self.blackKingLocation = (0, 4)

        # Checkmate and stalemate
        self.checkMate = False
        self.staleMate = False

    # Move handling
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # Update king's location
        if move.pieceMoved == 'b_K':
            self.blackKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'w_K':
            self.whiteKingLocation = (move.endRow, move.endCol)

        # Pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + '_Q'

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # Update king's location if moved
            if move.pieceMoved == 'b_K':
                self.blackKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'w_K':
                self.whiteKingLocation = (move.startRow, move.startCol)

    def getValidMoves(self):
        """Returns a list of all valid moves for the current player, considering check situations."""
        moves = self.getAllPossibleMoves()

        for i in range(len(moves)-1, -1, -1):  
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    def inCheck(self):
        return self.squareUnderAttack(self.whiteKingLocation if self.whiteToMove else self.blackKingLocation)

    def squareUnderAttack(self, position):
        self.whiteToMove = not self.whiteToMove  
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  

        for move in oppMoves:
            if move.endRow == position[0] and move.endCol == position[1]:
                return True
        return False

    # Generate all possible moves
    def getAllPossibleMoves(self):
        moves = []
        for r in range(6):
            for c in range(6):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][2]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    # Pawn Moves
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  
            if r > 0:
                if self.board[r-1][c] == "--":
                    moves.append(Move((r, c), (r-1, c), self.board))
                if c-1 >= 0 and self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                if c+1 < 6 and self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else:  
            if r < 5:
                if self.board[r+1][c] == "--":
                    moves.append(Move((r, c), (r+1, c), self.board))
                if c-1 >= 0 and self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                if c+1 < 6 and self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    # Knight Moves
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), 
                      (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow, endCol = r + m[0], c + m[1]
            if 0 <= endRow < 6 and 0 <= endCol < 6:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Empty or enemy piece
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # Rook Moves
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 6):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 6 and 0 <= endCol < 6:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Ally piece
                        break
                else:  # Off board
                    break

    # Bishop Moves
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 6):  
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 6 and 0 <= endCol < 6:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Ally piece
                        break
                else:  # Off board
                    break

    # Queen Moves
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # King Moves
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                     (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in kingMoves:
            endRow, endCol = r + m[0], c + m[1]
            if 0 <= endRow < 6 and 0 <= endCol < 6:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Not an ally piece (empty or enemy)
                    moves.append(Move((r, c), (endRow, endCol), self.board))