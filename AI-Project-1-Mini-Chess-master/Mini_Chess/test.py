import sys

import pygame
from pygame.locals import *

import ai
import engine

pygame.init()

########################## HEADERS ##########################

# Game Setup
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 550
SQ_SIZE = 60
DIMENSION_X = 6
DIMENSION_Y = 6
FPS = 60

# BG color
BACKGROUND = pygame.Color('azure')
BOARD_COLOR_A = (239, 239, 239)
BOARD_COLOR_B = (149, 141, 148)
HOVER_COLOR = (210, 140, 80)

# Button colors
PLAY_BUTTON_COLOR = pygame.Color('bisque3')
PLAY_BUTTON_HOEVR_COLOR = pygame.Color('chartreuse1')
RESTART_BUTTON_COLOR = pygame.Color('orangered')
RESTART_BUTTON_HOVER_COLOR = pygame.Color('brown4')
BUTTON_TEXT_COLOR = pygame.Color('white')
TOGGLE_BUTTON_COLOR = pygame.Color('purple')

# Button dimensions and positions
BUTTON_WIDTH = 40
BUTTON_HEIGHT = 40
PLAY_BUTTON_POS = (200, 380)
RESTART_BUTTON_POS = (250, 380)
TOGGLE_BUTTON_1_POS = (150, 380)
TOGGLE_BUTTON_2_POS = (100, 380)
TOGGLE_BUTTON_3_POS = (150, 430)
TOGGLE_BUTTON_4_POS = (100, 430)

# Define button attributes
BUTTON_FONT = pygame.font.SysFont('Arial', 20, bold=True)
BUTTON_RADIUS = 8

# MOVES
MOVE_COUNT = 0
MAX_MOVES = 100
BLACK_AI = False
BLACK_MAN = False
WHITE_AI = False
WHITE_MAN = False

########################## PROCESS FUNCTIONS ##########################

def loadSoundEffects():

    effects = {}
    move_piece = pygame.mixer.Sound('./audios/move_pieces.wav')
    undo_move = pygame.mixer.Sound('./audios/undo_moves.wav')
    checkmate = pygame.mixer.Sound('./audios/checkmate_sound.wav')
    effects['move'] = move_piece
    effects['undo'] = undo_move
    effects['checkmate'] = checkmate
    return effects


def loadImages():

    IMAGES = {}
    pieces = ['b_B', 'b_K', 'b_N', 'b_P', 'b_Q', 'b_R',
              'w_B', 'w_K', 'w_N', 'w_P', 'w_Q', 'w_R']

    for piece in pieces:
        image = pygame.image.load('images/' + piece + '.png')
        IMAGES[piece] = pygame.transform.scale(image, (SQ_SIZE, SQ_SIZE))

    return IMAGES


def highlightSquare(WINDOW, GAME_STATE, validMoves, sqSelected, lastMove, restart):

    # Clear all highlighting when restarting the game
    if restart:
        sqSelected.clear()
        lastMove.clear()

    if len(sqSelected) != 0:
        row, col = sqSelected[0]

        # a piece that can be moved
        if GAME_STATE.board[row][col][0] == ('w' if GAME_STATE.whiteToMove else 'b'):

            # hightlight square
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            # transparency value (0 - transparent, 255 - solid)
            surface.set_alpha(100)
            surface.fill(pygame.Color('blue'))
            WINDOW.blit(surface, (col*SQ_SIZE, row*SQ_SIZE))

            # highlight for possible moves
            surface.fill(pygame.Color('yellow'))

            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    WINDOW.blit(
                        surface, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))

    # Highlight squares for checkmate
    if GAME_STATE.inCheck():
        king_row, king_col = (
            GAME_STATE.whiteKingLocation if GAME_STATE.whiteToMove else GAME_STATE.blackKingLocation)

        surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
        surface.fill(pygame.Color('red'))
        WINDOW.blit(surface, (king_col*SQ_SIZE, king_row*SQ_SIZE))

    # Highlight the last moved piece
    if len(lastMove) != 0:
        startRow, startCol = lastMove[0]
        endRow, endCol = lastMove[1]

        if startRow is not None and startCol is not None:
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            surface.fill(pygame.Color('cyan'))
            WINDOW.blit(surface, (startCol*SQ_SIZE, startRow*SQ_SIZE))

        if endRow is not None and endCol is not None:
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            surface.fill(pygame.Color('cyan'))
            WINDOW.blit(surface, (endCol*SQ_SIZE, endRow*SQ_SIZE))


def drawGameState(WINDOW, GAME_STATE, validMoves, sqSelected, lastMove, restart):
    drawBoard(WINDOW)
    highlightSquare(WINDOW, GAME_STATE, validMoves,
                    sqSelected, lastMove, restart)
    drawPieces(WINDOW, GAME_STATE.board)
    drawButtons(WINDOW, GAME_STATE)


def drawBoard(WINDOW):

    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # ADD SHAPES
    for row in range(0, DIMENSION_Y):
        for col in range(0, DIMENSION_X):
            rectangle = pygame.Rect(
                col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)

            # Calculate rank value for the current row
            rank = 6 - row

            # Calculate file value for the current column
            file_ = chr(ord('a') + col)

            # Check if mouse is hovering
            if rectangle.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(WINDOW, HOVER_COLOR, rectangle)
            elif (row + col) % 2 == 0:
                pygame.draw.rect(WINDOW, BOARD_COLOR_A, rectangle)
            else:
                pygame.draw.rect(WINDOW, BOARD_COLOR_B, rectangle)

            # Render rank value in the left cells
            if col == 0:
                font = pygame.font.SysFont('Comic Sans', 15)
                surface = font.render(str(rank), True, 'blue')
                WINDOW.blit(surface, (5, row * SQ_SIZE + 5))

            # Render file value in the bottom row
            if row == DIMENSION_Y - 1:
                font = pygame.font.SysFont('Comic Sans', 15)
                surface = font.render(file_, True, 'blue')
                WINDOW.blit(surface, (col * SQ_SIZE + 53,
                            (DIMENSION_Y-1) * SQ_SIZE + 45))


def drawPieces(WINDOW, Board):

    IMAGES = loadImages()

    for row in range(DIMENSION_X):
        for col in range(DIMENSION_Y):
            piece = Board[col][row]
            if piece != '--':
                WINDOW.blit(IMAGES[piece], pygame.Rect(
                    row*SQ_SIZE, col*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawButtons(WINDOW, GAME_STATE):

    play_button_rect = ''
    restart_button_rect = ''

    # # ==> Show Text (Opponent)
    drawTextMessage(WINDOW, "Black", [10, 392], pygame.Color('darkmagenta'))
    drawTextMessage(WINDOW, "White", [10, 442], pygame.Color('darkmagenta'))
    drawTextMessage(WINDOW, "MoveCount", [
                    10, 490], pygame.Color('darkmagenta'))
    drawTextMessage(WINDOW, MOVE_COUNT, [120, 430], pygame.Color('red'))
    turn = "Black's Thinking..." if not GAME_STATE.whiteToMove else "White's Thinking..."
    drawTextMessage(WINDOW, turn, [80, 525], pygame.Color('olivedrab4'))

    # ==> Restart Button

    icon_image = pygame.image.load('./icons/re2.png')

    # Draw "Restart" button
    restart_button_rect = pygame.Rect(
        RESTART_BUTTON_POS[0], RESTART_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(WINDOW, RESTART_BUTTON_COLOR,
                     restart_button_rect, border_radius=BUTTON_RADIUS)

    # Draw the icon on the button (adjust the position as needed)
    icon_rect = icon_image.get_rect(center=(
        restart_button_rect.centerx, restart_button_rect.centery))  # Adjust the icon position
    WINDOW.blit(icon_image, icon_rect)

    # ==> Toggle Button (Black Selection)
    black_ai = pygame.Color('blue') if BLACK_AI else pygame.Color('gainsboro')
    black_man = pygame.Color('blue') if BLACK_MAN else pygame.Color('gainsboro')

    makeButton(WINDOW, TOGGLE_BUTTON_2_POS, BUTTON_WIDTH, BUTTON_HEIGHT, TEXT='AI', BTN_COLOR=black_ai, BTN_RADIUS=15)
    makeButton(WINDOW, TOGGLE_BUTTON_1_POS, BUTTON_WIDTH+50, BUTTON_HEIGHT, TEXT='HUMAN', BTN_COLOR=black_man, BTN_RADIUS=15)
    
    # ==> Toggle Button (White Selection)
    white_ai = pygame.Color('blue') if WHITE_AI else pygame.Color('gainsboro')
    white_man = pygame.Color('blue') if WHITE_MAN else pygame.Color('gainsboro')

    makeButton(WINDOW, TOGGLE_BUTTON_4_POS, BUTTON_WIDTH, BUTTON_HEIGHT, TEXT='AI', BTN_COLOR=white_ai, BTN_RADIUS=15)
    makeButton(WINDOW, TOGGLE_BUTTON_3_POS, BUTTON_WIDTH+50, BUTTON_HEIGHT, TEXT='HUMAN', BTN_COLOR=white_man, BTN_RADIUS=15)


def animateMove(move, WINDOW, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framePerSquare
    IMAGES = loadImages()

    for frame in range(frameCount + 1):
        row, col = (move.startRow + dR*frame/frameCount,
                    move.startCol + dC*frame/frameCount)

        # redraw the board
        drawBoard(WINDOW)
        drawPieces(WINDOW, board)

        # erase piece from ending square
        endSquare = pygame.Rect(move.endCol*SQ_SIZE,
                                move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(WINDOW, (BOARD_COLOR_A if (
            (move.endRow+move.endCol) % 2 == 0) else BOARD_COLOR_B), endSquare)

        # draw captured piece onto the square
        if move.pieceCaptured != '--':
            WINDOW.blit(IMAGES[move.pieceCaptured], endSquare)

        # draw moving piece
        WINDOW.blit(IMAGES[move.pieceMoved], pygame.Rect(
            col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.update()
        clock.tick(60)


def drawCheckText(screen, text):
    font = pygame.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, pygame.Color('Red'))
    textLocation = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT).move(
        WINDOW_WIDTH/2 - textObject.get_width()/2, WINDOW_HEIGHT/2 - textObject.get_height()*6)
    screen.blit(textObject, textLocation)


def drawGameOverText(screen, text, textColor):
    font = pygame.font.SysFont("Helvetica", 18, True, False)
    textObject = font.render(text, 0, pygame.Color(textColor))
    textLocation = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT).move(
        WINDOW_WIDTH/2 - textObject.get_width()/2, WINDOW_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)


def makeButton(WINDOW, POSITION, WIDTH, HEIGHT, TEXT, BTN_COLOR, BTN_RADIUS=0):

    # button_color = BTN_COLOR if TOOGLE_BUTTON_CLICKED else BTN_COLOR_2
    toggle_button_rect = pygame.Rect(POSITION[0], POSITION[1], WIDTH, HEIGHT)
    pygame.draw.rect(WINDOW, BTN_COLOR, toggle_button_rect,
                     border_radius=BTN_RADIUS)

    # Draw the selected player on the toggle button
    font = pygame.font.Font(None, 24)
    toggle_text = font.render(TEXT, True, pygame.Color('white'))
    toggle_text_rect = toggle_text.get_rect(center=toggle_button_rect.center)
    WINDOW.blit(toggle_text, toggle_text_rect)


def drawTextMessage(WINDOW, TEXT, POSITION, TEXT_COLOR):

    font = pygame.font.SysFont("Arial", 17, True, False)
    textObject = font.render(str(TEXT), 1, TEXT_COLOR)
    textLocation = pygame.Rect(
        POSITION[0], POSITION[1], WINDOW_WIDTH, WINDOW_HEIGHT)
    WINDOW.blit(textObject, textLocation)


########################## MAIN FUNCTION ##########################


def main():
    # initialize pygame
    pygame.init()

    # variables
    pieceClickCount = 0
    selectedSq = []
    animate = False
    # human -> TRUE, AI -> FALSE (white)
    playerOne = True
    # -Do- (black)
    playerTwo = True
    lastMove = []
    opponent_selection = True
    global MOVE_COUNT, MAX_MOVES, BLACK_AI, BLACK_MAN, WHITE_AI, WHITE_MAN

    # Set Display
    WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('♟️ Mini Chess ♟️')
    clock = pygame.time.Clock()

    # Set GameState
    GAME_STATE = engine.GameState()
    validMoves = GAME_STATE.getValidMoves()
    moveMade = False
    gameOver = False

    # Define the board area rect
    board_rect = pygame.Rect(
        0, 0, DIMENSION_X * SQ_SIZE, DIMENSION_Y * SQ_SIZE)

    # Button Rects
    play_button_rect = pygame.Rect(
        PLAY_BUTTON_POS[0], PLAY_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT)
    restart_button_rect = pygame.Rect(
        RESTART_BUTTON_POS[0], RESTART_BUTTON_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT)
    black_human_rect = pygame.Rect(TOGGLE_BUTTON_1_POS[0], TOGGLE_BUTTON_1_POS[1], BUTTON_WIDTH+50, BUTTON_HEIGHT)
    black_ai_rect = pygame.Rect(TOGGLE_BUTTON_2_POS[0], TOGGLE_BUTTON_2_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT)
    
    white_human_rect = pygame.Rect(TOGGLE_BUTTON_3_POS[0], TOGGLE_BUTTON_3_POS[1], BUTTON_WIDTH+50, BUTTON_HEIGHT)
    white_ai_rect = pygame.Rect(TOGGLE_BUTTON_4_POS[0], TOGGLE_BUTTON_4_POS[1], BUTTON_WIDTH, BUTTON_HEIGHT)

    # The main game loop
    running = True
    while running:

        # render game elements
        WINDOW.fill(BACKGROUND)
        clock.tick(FPS)
        restart = False

        # check if Human is playing...
        humanPlayer = (GAME_STATE.whiteToMove and playerOne) or (
            not GAME_STATE.whiteToMove and playerTwo)

        # Event handling
        for event in pygame.event.get():

            # QUIT Game
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # handle piece movement
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not gameOver:
                    # Click squares to move the piece
                    if board_rect.collidepoint(event.pos):
                        if humanPlayer:
                            y_coord = event.pos[0] // SQ_SIZE
                            x_coord = event.pos[1] // SQ_SIZE

                            # if same square is clicked twice then reset
                            if selectedSq == (x_coord, y_coord):
                                selectedSq = ()
                                pieceClickCount = 0
                            else:
                                selectedSq.append((x_coord, y_coord))
                                pieceClickCount += 1

                            # when the piece are to be moved
                            if pieceClickCount == 2:

                                move = engine.Move(
                                    selectedSq[0], selectedSq[1], GAME_STATE.board)
                                print(move.getChessNotation())

                                # if move is valid then make move
                                for i in range(len(validMoves)):
                                    if move == validMoves[i]:
                                        GAME_STATE.makeMove(move)
                                        moveMade = True
                                        animate = True
                                        lastMove = selectedSq
                                        MOVE_COUNT += 1

                                        # playing move piece sound
                                        sound_effects = loadSoundEffects()
                                        sound_effects['move'].play()

                                        pieceClickCount = 0
                                        selectedSq = []

                                if not moveMade:
                                    pieceClickCount = 1
                                    selectedSq.remove(selectedSq[0])

                # opponent selection
                if black_ai_rect.collidepoint(event.pos):
                    BLACK_AI = True
                    BLACK_MAN = False
                    playerTwo = False

                    # restart
                    GAME_STATE = engine.GameState()
                    validMoves = GAME_STATE.getValidMoves()
                    selectedSq = []
                    pieceClickCount = 0
                    moveMade = False
                    animate = False
                    restart = True
                    gameOver = False
                    MOVE_COUNT = 0

                if black_human_rect.collidepoint(event.pos):
                    BLACK_MAN = True
                    BLACK_AI = False
                    playerTwo = True

                    # restart
                    GAME_STATE = engine.GameState()
                    validMoves = GAME_STATE.getValidMoves()
                    selectedSq = []
                    pieceClickCount = 0
                    moveMade = False
                    animate = False
                    restart = True
                    gameOver = False
                    MOVE_COUNT = 0

                if white_ai_rect.collidepoint(event.pos):
                    WHITE_AI = True
                    WHITE_MAN = False
                    playerOne = False

                    # restart
                    GAME_STATE = engine.GameState()
                    validMoves = GAME_STATE.getValidMoves()
                    selectedSq = []
                    pieceClickCount = 0
                    moveMade = False
                    animate = False
                    restart = True
                    gameOver = False
                    MOVE_COUNT = 0

                if white_human_rect.collidepoint(event.pos):
                    WHITE_MAN = True
                    WHITE_AI = False
                    playerOne = True

                    # restart
                    GAME_STATE = engine.GameState()
                    validMoves = GAME_STATE.getValidMoves()
                    selectedSq = []
                    pieceClickCount = 0
                    moveMade = False
                    animate = False
                    restart = True
                    gameOver = False
                    MOVE_COUNT = 0


                # Check if "Restart" button is clicked
                if restart_button_rect.collidepoint(event.pos):
                    GAME_STATE = engine.GameState()
                    validMoves = GAME_STATE.getValidMoves()
                    selectedSq = []
                    pieceClickCount = 0
                    moveMade = False
                    animate = False
                    restart = True
                    gameOver = False
                    MOVE_COUNT = 0

            # handle undo moves
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:  # undo when z is pressed
                    # Check if there are at least two moves to undo
                    if len(GAME_STATE.moveLog) >= 2:
                        # Undo the last two moves (one AI move and one human move)
                        move = GAME_STATE.undoMove(2)
                        moveMade = True
                        animate = False
                        sound_effects = loadSoundEffects()
                        sound_effects['undo'].play()
                        lastMove = [(move.startRow, move.startCol),
                                    (move.endRow, move.endCol)]
                    else:
                        print("Not enough moves to undo.")

        #! AI Move
        if not humanPlayer:
            if not gameOver:
                aiMove = ai.findBestMove(
                    GAME_STATE, validMoves)  # optimum approach

                if aiMove is None:
                    aiMove = validMoves[0]
                    print("GAME OVER")

                GAME_STATE.makeMove(aiMove)
                moveMade = True
                animate = True
                MOVE_COUNT += 1

                # playing piece moving sound
                sound_effects = loadSoundEffects()
                sound_effects['move'].play()

                # track last move
                lastMove = [(aiMove.startRow, aiMove.startCol),
                            (aiMove.endRow, aiMove.endCol)]

        # update valid moves
        if moveMade:
            if animate:
                animateMove(GAME_STATE.moveLog[-1],
                            WINDOW, GAME_STATE.board, clock)
            validMoves = GAME_STATE.getValidMoves()
            moveMade = False
            animate = False

        # Set Game State
        drawGameState(WINDOW, GAME_STATE, validMoves,
                      selectedSq, lastMove, restart)

        # check message handling section
        if GAME_STATE.inCheck():
            drawCheckText(WINDOW, 'Check')

        # game over handling section
        if GAME_STATE.checkMate:
            gameOver = True
            if GAME_STATE.whiteToMove:
                drawGameOverText(WINDOW, 'Black wins by Checkmate', 'Red')
            else:
                drawGameOverText(WINDOW, 'White wins by Checkmate', 'Green')

            # sound_effect = loadSoundEffects()
            # sound_effect['checkmate'].play()

        if GAME_STATE.staleMate:
            gameOver = True
            drawGameOverText(WINDOW, 'Stalemate', 'Red')

        # Update the window state
        pygame.display.update()


if __name__ == '__main__':
    main()
