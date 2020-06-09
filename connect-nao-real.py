import numpy as np
import random
import pygame
import sys
import math
from time import sleep

#Start of robot part

from social_interaction_cloud.basic_connector import BasicSICConnector, BasicNaoPosture
from social_interaction_cloud.action import ActionRunner
from time import sleep

# Variables
NAO_IS_OPPONENT = 1  # 1 against Nao, 0 with Nao as bystander
GAME_DIFFICULTY = 1  # 1 for easiest, 5 for hardest
PERSON_ID = int(input("Voer je proef persoon ID in of vraag deze aan de onderzoeker: "))

class Example:

    def __init__(self, server_ip, robot):
        self.sic = BasicSICConnector(server_ip, robot)
        self.action_runner = ActionRunner(self.sic)

    def start(self):
        self.sic.start()
        self.action_runner.load_waiting_action('set_language', 'nl-NL')
        self.action_runner.load_waiting_action('wake_up')
        self.action_runner.run_loaded_actions()
        self.action_runner.run_waiting_action('set_breathing', True)
        self.sic.say_animated('Ik ben aan het op starten.')
        log = open("log_%s.txt" % PERSON_ID, "a")
        log.write('Nao said: Ik ben aan het op starten.\n')
        log.close()
        #self.action_runner.run_waiting_action('go_to_posture', BasicNaoPosture.LYINGBACK)
        #self.action_runner.run_waiting_action('go_to_posture', BasicNaoPosture.STAND)
        # Execute that_tickles call each time the middle tactile is touched
        self.sic.subscribe_touch_listener('MiddleTactilTouched', self.give_advice)

    def stop(self):
        self.sic.unsubscribe_touch_listener('MiddleTactilTouched')
        self.sic.rest()
        self.sic.stop()


    def give_advice(self):
        """Callback function for touch listener. Everytime the MiddleTactilTouched event is generated, this
         callback function is called, making the robot say 'That tickles!'"""
        col, minimax_score = minimax(board, GAME_DIFFICULTY, -math.inf, math.inf, True)
        if NAO_IS_OPPONENT == 0:
            self.push_data('move_recommendation', 1, data=col)
        else:
            self.action_runner.run_action('say_animated', 'Ik help alleen als we samen een potje spelen')
            log = open("log_%s.txt" % PERSON_ID, "a")
            log.write('Nao said: Ik help alleen als we samen een potje spelen.\n')
            log.close()

    def set_eye_color(self, color):
        self.action_runner.run_action('set_eye_color', color)

    def push_data(self, trigger, random_factor, **kwargs):
        if random_factor == 0:
            return
        data = kwargs.get('data', None)
        random_variable = random.randint(1, random_factor)
        if random_factor / random_variable == 1:
            if trigger == 'players_turn':
                speech = random.choice(PLAYERS_TURN_STRING)
                self.action_runner.run_action('say_animated', speech)
                log = open("log_%s.txt" % PERSON_ID, "a")
                log.write('Nao said: ' + str(speech) + '\n')
                log.close()
            elif trigger == 'start':
                speech = random.choice(START_GAME_STRING)
                self.action_runner.run_action('say_animated', speech)
                log = open("log_%s.txt" % PERSON_ID, "a")
                log.write('Nao said: ' + str(speech) + '\n')
                log.close()
                '''
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Center_Neutral_ENU_07')
                self.action_runner.run_action('say', 'Center_Neutral_ENU_07')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Center_Neutral_ENU_01')
                self.action_runner.run_action('say', 'Center_Neutral_ENU_01')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Center_Strong_ENU_01')
                self.action_runner.run_action('say', 'Center_Strong_ENU_01')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Center_Neutral_EXC_03')
                self.action_runner.run_action('say', 'Center_Neutral_EXC_03')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Center_Slow_EXC_03')
                self.action_runner.run_action('say', 'Center_Slow_EXC_03')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Center_Strong_EXC_03')
                self.action_runner.run_action('say', 'Center_Strong_EXC_03')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Left_Strong_EXC_02')
                self.action_runner.run_action('say', 'Left_Strong_EXC_02')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Center_Neutral_QUE_10')
                self.action_runner.run_action('say', 'Center_Neutral_QUE_10')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Center_Neutral_ENU_07')
                self.action_runner.run_action('say', 'Center_Neutral_ENU_07')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Right_Neutral_QUE_03')
                self.action_runner.run_action('say', 'Right_Neutral_QUE_03')
                sleep(3)
                self.action_runner.run_action('do_gesture', 'animations/Stand/Enumeration/NAO/Center_Neutral_ENU_07')
                self.action_runner.run_action('say', 'Center_Neutral_ENU_07')
                sleep(3)
                '''
                if NAO_IS_OPPONENT:
                    speech = random.choice(START_GAME_WITH_NAO_STRING)
                    self.action_runner.run_action('say_animated', speech)
                    log = open("log_%s.txt" % PERSON_ID, "a")
                    log.write('Nao said: ' + str(speech) + '\n')
                    log.close()
                else:
                    speech = random.choice(START_GAME_AGAINST_NAO_STRING)
                    self.action_runner.run_action('say_animated', speech)
                    log = open("log_%s.txt" % PERSON_ID, "a")
                    log.write('Nao said: ' + str(speech) + '\n')
                    log.close()
            elif trigger == 'move_recommendation':
                data = int(data) + 1  # Add 1 to make it a human number
                speech = 'Ik raad aan om in kolom ' + str(data) + ' te zetten'
                log = open("log_%s.txt" % PERSON_ID, "a")
                log.write('Nao said: Even denken \n')
                log.write('Nao said: ' + str(speech) + '\n')
                log.close()
                self.action_runner.run_action('set_eye_color', 'blue')
                self.action_runner.run_action('say_animated', 'Even denken')
                self.action_runner.run_loaded_actions()
                sleep(random.randint(2, 4))
                self.action_runner.run_action('say_animated', speech)
                #self.action_runner.run_loaded_actions()
                self.action_runner.run_action('set_eye_color', EYE_COLOR)
            elif trigger == 'game_over':
                if data == 'lost':
                    speech = random.choice(END_GAME_LOSS_STRING)
                    self.action_runner.run_action('say_animated', speech)
                    log = open("log_%s.txt" % PERSON_ID, "a")
                    log.write('Nao said: ' + str(speech) + '\n')
                    log.close()
                elif data == 'won':
                    speech = random.choice(END_GAME_WIN_STRING)
                    self.action_runner.run_action('say_animated', speech)
                    log = open("log_%s.txt" % PERSON_ID, "a")
                    log.write('Nao said: ' + str(speech) + '\n')
                    log.close()


nao = Example('192.168.0.105', 'nao')
nao.start()

# End of robot part

# Randomiser settings 1 = always trigger, 2 = 50% triggered, 3 = 33%, etc
START_TRIGGER_FACTOR = 1
MOVE_RECOMMENDATION_TRIGGER_FACTOR = 10
GAME_OVER_WON_TRIGGER_FACTOR = 1
GAME_OVER_LOST_TRIGGER_FACTOR = 1
PLAYERS_TURN_TRIGGER_FACTOR = 5

# Strings
START_GAME_STRING = ['Hallo, ik ben Nao, om advies te krijgen over een zet druk op mijn hoofd']
START_GAME_WITH_NAO_STRING = ['Ik heb er zin in', 'We pakken hem']
START_GAME_AGAINST_NAO_STRING = ['Veel succes', 'Ik ben er klaar voor']
PLAYERS_TURN_STRING = ['Jij bent aan de beurt', 'Jij mag nu', 'Nu ben jij aan zet']
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
    log = open("log_%s.txt" % PERSON_ID, "a")
    log.write('Game difficulty: ' + str(GAME_DIFFICULTY) + '\n')
    log.write('Nao mode: ' + str(NAO_IS_OPPONENT) + '\n')
    log.close()
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



nao.push_data('start', START_TRIGGER_FACTOR)

if NAO_IS_OPPONENT == 1:
    EYE_COLOR = str('magenta')
else:
    EYE_COLOR = str('green')
nao.set_eye_color(EYE_COLOR)

log = open("log_%s.txt" % PERSON_ID, "a")
log.write('Starting session \n')
log.close()
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
moves = 0
winner = None

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
                label = myfont.render("1     2     3     4     5     6     7", 1, YELLOW)
                screen.blit(label, (40, 10))

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
                        screen.blit(label, (40, 10))
                        pygame.display.update()
                        draw_board(board)
                        nao.push_data('game_over', GAME_OVER_WON_TRIGGER_FACTOR, data='won')
                        winner = 'Player'
                        game_over = True

                    turn += 1
                    turn = turn % 2
                    moves += 1

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
                screen.blit(label, (40, 10))
                pygame.display.update()
                draw_board(board)
                nao.push_data('game_over', GAME_OVER_LOST_TRIGGER_FACTOR, data='lost')
                winner = 'Computer'
                game_over = True

            #print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2
            moves += 1
            nao.push_data('players_turn', PLAYERS_TURN_TRIGGER_FACTOR)
            col, minimax_score = minimax(board, GAME_DIFFICULTY, -math.inf, math.inf, True)
            nao.push_data('move_recommendation', MOVE_RECOMMENDATION_TRIGGER_FACTOR, data=col)

    if game_over:
        print_board(board)
        log = open("log_%s.txt" % PERSON_ID, "a")
        log.write('Moves made: ' + str(moves) + '\n')
        log.write('Winner: ' + str(winner) + '\n')
        log.write('Game: \n' + str(np.flip(board, 0)) + '\n')
        log.close()
        GAME_DIFFICULTY += 1
        sleep(3)
        if GAME_DIFFICULTY < 6:
            nao.action_runner.run_action('say_animated', 'We gaan nu spelen op moeilijkheidsgraad ' + str(GAME_DIFFICULTY))
            board = create_board()
            # print_board(board)
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
            moves = 0
            winner = None
        else:
            nao.action_runner.run_action('say_animated', 'Bedankt voor het spelen, vul de enquete in en vraag de onderzoeker naar de volgende stap')
            nao.stop()
            log = open("log_%s.txt" % PERSON_ID, "a")
            log.write('End of session \n')
            log.close()
            pygame.time.wait(3000)