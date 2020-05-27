import numpy as np
import random
import pygame
import sys
import math
from time import sleep

#Start of robot part

import threading
from social_interaction_cloud.basic_connector import BasicSICConnector
from time import sleep


class Example:

    def __init__(self, server_ip, robot):
        self.sic = BasicSICConnector(server_ip, robot)

        self.awake_lock = threading.Event()

    def start(self):
        # active Social Interaction Cloud connection
        self.sic.start()

        # set language to English
        self.sic.set_language('nl-NL')

        # stand up and wait until this action is done (whenever the callback function self.awake is called)
        self.sic.wake_up(self.awake)
        self.awake_lock.wait()  # see https://docs.python.org/3/library/threading.html#event-objects

        self.sic.say_animated('You can tickle me by touching my head.')
        # Execute that_tickles call each time the middle tactile is touched
        self.sic.subscribe_touch_listener('MiddleTactilTouched', self.that_tickles)

        # You have 10 seconds to tickle the robot
        #sleep(10)

    def stop(self):
        # Unsubscribe the listener if you don't need it anymore.
        self.sic.unsubscribe_touch_listener('MiddleTactilTouched')

        # Go to rest mode
        self.sic.rest()

        # close the Social Interaction Cloud connection
        self.sic.stop()

    def awake(self):
        """Callback function for wake_up action. Called only once.
        It lifts the lock, making the program continue from self.awake_lock.wait()"""

        self.awake_lock.set()

    def that_tickles(self):
        """Callback function for touch listener. Everytime the MiddleTactilTouched event is generated, this
         callback function is called, making the robot say 'That tickles!'"""

        self.sic.say_animated('That tickles!')

    def push_data(self, trigger, random_factor, **kwargs):
        if random_factor == 0:
            return
        data = kwargs.get('data', None)
        random_variable = random.randint(1, random_factor)
        if random_factor / random_variable == 1:
            print('Passed randomiser')
            if trigger == 'players_turn':
                self.sic.say_animated(random.choice(PLAYERS_TURN_STRING))
            elif trigger == 'start':
                self.sic.say_animated(random.choice(START_GAME_STRING))
                if NAO_IS_OPPONENT:
                    self.sic.say_animated(random.choice(START_GAME_WITH_NAO_STRING))
                else:
                    self.sic.say_animated(random.choice(START_GAME_AGAINST_NAO_STRING))
            elif trigger == 'move_recommendation':
                data = int(data) + 1  # Add 1 to make it a human number
                self.sic.set_eye_color(self, 'blue')
                self.sic.say_animated('Even denken')
                sleep(random.randint(1, 3))
                self.sic.say_animated('Ik raad aan om in kolom ' + str(data) + ' te zetten')
                self.sic.set_eye_color(self, EYE_COLOR)  # TODO wait for finish
            elif trigger == 'game_over':
                if data == 'lost':
                    self.sic.say_animated(random.choice(END_GAME_LOSS_STRING))
                elif data == 'won':
                    self.sic.say_animated(random.choice(END_GAME_WIN_STRING))


nao = Example('192.168.0.105', 'nao')
nao.start()

# End of robot part

# Variables
NAO_IS_OPPONENT = int(input("Voer 1 in om tegen Nao te spelen, voer 0 in om met Nao aan jou kant te spelen als vriend: "))
GAME_DIFFICULTY = int(input("Voer een getal in tussen 1 (makkelijk) en 5 (moeilijk) om de moeilijkheidsgraad in te stellen: "))
if NAO_IS_OPPONENT == 1:
    EYE_COLOR = 'red'
else:
    EYE_COLOR = 'green'
nao.sic.set_eye_color(EYE_COLOR)  # TODO check if this works

# Randomiser settings 1 = always trigger, 2 = 50% triggered, 3 = 33%, etc
START_TRIGGER_FACTOR = 1
MOVE_RECOMMENDATION_TRIGGER_FACTOR = 1
GAME_OVER_WON_TRIGGER_FACTOR = 1
GAME_OVER_LOST_TRIGGER_FACTOR = 1
PLAYERS_TURN_TRIGGER_FACTOR = 5

# Strings
START_GAME_STRING = ['Hallo, ik ben Nao, om advies te krijgen over een zet druk op a']
START_GAME_WITH_NAO_STRING = ['Ik heb er zin in', 'We pakken hem']
START_GAME_AGAINST_NAO_STRING = ['Veel succes', 'Ik ben er klaar voor']
PLAYERS_TURN_STRING = ['Jij bent aan de beurt']
END_GAME_WIN_STRING = ['Goed gedaan!', 'Je hebt goed gespeeld', 'Volgende keer een niveau hoger?']
END_GAME_LOSS_STRING = ['Volgende keer beter!', 'Jammer! Je kan volgende keer ook een niveau lager spelen']

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4


def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    nao.push_data('start', START_TRIGGER_FACTOR)
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                c + 3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                c + 3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][
                c + 3] == piece:
                return True


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col


def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (
                    int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (
                    int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()


board = create_board()
#print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == ord("a"):
                col, minimax_score = minimax(board, GAME_DIFFICULTY, -math.inf, math.inf, True)
                nao.push_data('move_recommendation', MOVE_RECOMMENDATION_TRIGGER_FACTOR, data=col)

        if event.type == pygame.QUIT:
            nao.stop()
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            # print(event.pos)
            # Ask for Player 1 Input
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("Jij hebt gewonnen!!", 1, RED)
                        nao.push_data('game_over', GAME_OVER_WON_TRIGGER_FACTOR, data='won')
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

                #print_board(board)
                draw_board(board)
                pygame.display.update()
                pygame.time.wait(500)

    # # Ask for Player 2 Input
    if turn == AI and not game_over:

        # col = random.randint(0, COLUMN_COUNT-1)
        # col = pick_best_move(board, AI_PIECE)
        col, minimax_score = minimax(board, GAME_DIFFICULTY, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            # pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("Je hebt verloren, volgende keer beter!", 1, YELLOW)
                nao.push_data('game_over', GAME_OVER_LOST_TRIGGER_FACTOR, data='lost')
                screen.blit(label, (40, 10))
                game_over = True

            #print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2
            nao.push_data('players_turn', PLAYERS_TURN_TRIGGER_FACTOR)

    if game_over:
        print_board(board)
        nao.stop()
        pygame.time.wait(3000)