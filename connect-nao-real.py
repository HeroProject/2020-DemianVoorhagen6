import numpy as np
import random
import pygame
import sys
import math
import csv
from time import sleep
import os

#Start of robot part

from social_interaction_cloud.basic_connector import BasicSICConnector, BasicNaoPosture
from social_interaction_cloud.action import ActionRunner
from time import sleep

# EXPERIMENT VARIABLE
NAO_IS_OPPONENT = 1  # 1 against Nao, 0 with Nao as friend
TEST_MODE = False

if TEST_MODE:
    PERSON_ID = int(106)
else:
    PERSON_ID = int(21)  # bobby

# Game variables
GAME_DIFFICULTY = 1  # 1 for easiest, 5 for hardest

NAO_ADVICE_LEVEL = 5
IP_NAO = '192.168.0.105'

nao_recommended_move = 8  # moves are 0-6, use 8 as default because it matches no other values
played_move_after_recommendation = 0
advice_given = 0
advice_asked = 0
advice_followed = 0
advice_not_followed = 0
recommended_moves = []
played_moves_after_recommendation = []
let_nao_advice_in = 5

player_wins = 0
player_score = 0
computer_wins = 0
computer_score = 0

if NAO_IS_OPPONENT == 1:
    EYE_COLOR = str('magenta')
else:
    EYE_COLOR = str('green')

class Example:

    def __init__(self, server_ip, robot):
        self.sic = BasicSICConnector(server_ip, robot)
        self.action_runner = ActionRunner(self.sic)

    def start(self):
        self.sic.start()
        self.action_runner.load_waiting_action('set_language', 'nl-NL')
        self.action_runner.load_waiting_action('wake_up')
        self.action_runner.run_loaded_actions()
        self.action_runner.run_action('set_eye_color', EYE_COLOR)
        self.action_runner.run_waiting_action('set_breathing', True)
        self.sic.say_animated('Ik ben wakker aan het worden.')
        log = open("log_%s.txt" % PERSON_ID, "a")
        log.write('Nao said: Ik ben wakker aan het worden.\n')
        log.close()
        #self.action_runner.run_waiting_action('go_to_posture', BasicNaoPosture.LYINGBACK)
        #self.action_runner.run_waiting_action('go_to_posture', BasicNaoPosture.SIT)
        # Execute that_tickles call each time the middle tactile is touched
        self.sic.subscribe_touch_listener('MiddleTactilTouched', self.give_advice)

    def stop(self):
        self.sic.unsubscribe_touch_listener('MiddleTactilTouched')
        self.sic.say_animated('Ik ga weer slapen.')
        self.action_runner.run_action('set_eye_color', 'white')
        log = open("log_%s.txt" % PERSON_ID, "a")
        log.write('Nao said: Ik ga weer slapen.\n')
        log.close()
        self.sic.rest()
        self.sic.stop()


    def give_advice(self):
        """Callback function for touch listener. Everytime the MiddleTactilTouched event is generated, this
         callback function is called, making the robot say 'That tickles!'"""
        global advice_asked
        advice_asked += 1
        log = open("log_%s.txt" % PERSON_ID, "a")
        log.write(str('Nao touched for advice') + '\n')
        log.close()
        if NAO_IS_OPPONENT == 0:
            self.push_data('move_recommendation', 1)
        else:
            return

    def set_eye_color(self, color):
        self.action_runner.run_action('set_eye_color', color)

    def push_data(self, trigger, random_factor, **kwargs):
        global advice_given, recommended_moves, nao_recommended_move, EYE_COLOR
        if NAO_IS_OPPONENT == 1:
            EYE_COLOR = str('magenta')
        else:
            EYE_COLOR = str('green')
        if random_factor == 0:
            return
        data = kwargs.get('data', None)
        random_variable = random.randint(1, random_factor)
        if random_factor / random_variable == 1:
            if trigger == 'players_turn':
                speech = random.choice(PLAYERS_TURN_STRING)
            elif trigger == 'start':
                if NAO_IS_OPPONENT == 1:
                    speech = str('Hallo, ik ben Nao. Je kan een zet doen door te klikken op de rij waar je wilt zetten. ')
                else:
                    speech = str('Hallo, ik ben Nao. Je kan een zet doen door te klikken op de rij waar je wilt zetten. '
                                 'Om advies te krijgen over een zet druk op de ronde knop op mijn hoofd')
                self.action_runner.run_action('say_animated', speech)
                log = open("log_%s.txt" % PERSON_ID, "a")
                log.write('Nao said: ' + str(speech) + '\n')
                log.close()
                if NAO_IS_OPPONENT == 0:
                    speech = random.choice(START_GAME_WITH_NAO_STRING)
                else:
                    speech = random.choice(START_GAME_AGAINST_NAO_STRING)
            elif trigger == 'move_recommendation':
                global col, minimax_score, board
                self.action_runner.run_action('set_eye_color', 'blue')
                self.action_runner.run_action('say_animated', 'Even denken')
                self.action_runner.run_loaded_actions()
                sleep(1)
                log = open("log_%s.txt" % PERSON_ID, "a")
                log.write('Nao said: Even denken \n')
                log.close()
                col, minimax_score = minimax(board, NAO_ADVICE_LEVEL, -math.inf, math.inf, True)
                if type(col) == int:
                    nao_recommended_move = int(col)
                    data = int(col) + 1  # Add 1 to make it a human number
                    speech = 'Ik raad aan om in kolom ' + str(data) + ' te zetten'
                    recommended_moves.append(nao_recommended_move)
                    advice_given += 1
                else:
                    speech = 'Als je advies over een zet wilt hebben, druk dan op de ronde knop midden op mijn hoofd'
            elif trigger == 'game_over':
                if data == 'lost':
                    if NAO_IS_OPPONENT == 1:
                        speech = random.choice(END_GAME_PLAYER_LOST_NAO_WIN_STRING)
                        self.action_runner.run_action('do_gesture',
                                                      'animations/Stand/Exclamation/NAO/Right_Strong_EXC_03')
                    else:
                        speech = random.choice(END_GAME_PLAYER_LOST_NAO_LOST_STRING)
                        self.action_runner.run_action('do_gesture',
                                                      'animations/Stand/Negation/NAO/Center_Neutral_NEG_01')
                elif data == 'won':
                    if NAO_IS_OPPONENT == 1:
                        speech = random.choice(END_GAME_PLAYER_WIN_NAO_LOST_STRING)
                        self.action_runner.run_action('do_gesture',
                                                      'animations/Stand/Negation/NAO/Center_Neutral_NEG_01')
                        EYE_COLOR = 'red'
                    else:
                        speech = random.choice(END_GAME_PLAYER_WIN_NAO_WIN_STRING)
                        self.action_runner.run_action('do_gesture',
                                                      'animations/Stand/Exclamation/NAO/Right_Strong_EXC_03')
            self.action_runner.run_action('say_animated', speech)
            log = open("log_%s.txt" % PERSON_ID, "a")
            log.write('Nao said: ' + str(speech) + '\n')
            log.close()
        self.action_runner.run_action('set_eye_color', EYE_COLOR)


nao = Example(IP_NAO, 'nao')
nao.start()
nao.set_eye_color(EYE_COLOR)


# End of robot part

# Randomiser settings 1 = always trigger, 2 = 50% triggered, 3 = 33%, etc
START_TRIGGER_FACTOR = 1
MOVE_RECOMMENDATION_TRIGGER_FACTOR = 1
GAME_OVER_WON_TRIGGER_FACTOR = 1
GAME_OVER_LOST_TRIGGER_FACTOR = 1
PLAYERS_TURN_TRIGGER_FACTOR = 7

# Strings
START_GAME_WITH_NAO_STRING = ['We pakken hem', 'Samen staan we sterk', 'We kunnen hem makkelijk verslaan']
START_GAME_AGAINST_NAO_STRING = ['Veel succes, ik ben er klaar voor', 'Ik ga proberen je in te maken hihi',
                                 'Ik ben benieuwd of je me kan verslaan']
PLAYERS_TURN_STRING = ['Jij bent aan de beurt', 'Jij mag nu', 'Nu ben jij aan zet']
END_GAME_PLAYER_WIN_NAO_LOST_STRING = ['Jammer... Goed gedaan!', 'Goed gespeeld! Volgende keer ga ik winnen']
END_GAME_PLAYER_WIN_NAO_WIN_STRING = ['Goedzo, we hebben gewonnen!', 'Jippie dat ging goed!']
END_GAME_PLAYER_LOST_NAO_LOST_STRING = ['Volgende keer pakken we hem', 'Jammer! We hebben het geprobeerd']
END_GAME_PLAYER_LOST_NAO_WIN_STRING = ['Jippie ik heb gewonnen', 'Volgende keer iets beter je best doen!']

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

nao.push_data('start', START_TRIGGER_FACTOR)

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
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
nao.action_runner.run_action('say_animated', 'We gaan nu spelen op moeilijkheidsgraad ' + str(GAME_DIFFICULTY))
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            '''if event.key == ord("a"):
                col, minimax_score = minimax(board, GAME_DIFFICULTY, -math.inf, math.inf, True)
                nao.push_data('move_recommendation', MOVE_RECOMMENDATION_TRIGGER_FACTOR, data=col)'''

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
                    if len(recommended_moves) > len(played_moves_after_recommendation):
                        played_moves_after_recommendation.append(col)
                        played_move_after_recommendation = col
                    if nao_recommended_move < 8:
                        if played_move_after_recommendation == nao_recommended_move:
                            advice_followed += 1
                        else:
                            advice_not_followed += 1
                    nao_recommended_move = 8

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("Jij hebt gewonnen!!", 1, RED)
                        screen.blit(label, (40, 10))
                        pygame.display.update()
                        draw_board(board)
                        nao.push_data('game_over', GAME_OVER_WON_TRIGGER_FACTOR, data='won')
                        winner = 'Player'
                        player_wins += 1
                        player_score += (1 * GAME_DIFFICULTY)
                        game_over = True

                    turn += 1
                    turn = turn % 2
                    moves += 1
                    if len(get_valid_locations(board)) == 0:
                        game_over = True

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
                computer_wins += 1
                computer_score += (1 * GAME_DIFFICULTY)
                game_over = True

            #print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2
            moves += 1
            if len(get_valid_locations(board)) == 0:
                game_over = True
            if not game_over:
                nao.push_data('players_turn', PLAYERS_TURN_TRIGGER_FACTOR)
            if NAO_IS_OPPONENT == 0:
                let_nao_advice_in -= 1
                if let_nao_advice_in == 0:
                    nao.push_data('move_recommendation', MOVE_RECOMMENDATION_TRIGGER_FACTOR)
                    let_nao_advice_in = random.randint(5, 10)
            label = myfont.render("1     2     3     4     5     6     7", 1, YELLOW)
            screen.blit(label, (40, 10))

    if game_over:
        print_board(board)

        person_fieldnames = ['PERSON_ID', 'NAO_IS_OPPONENT', 'GAME_DIFFICULTY', 'moves', 'winner', 'advice_given',
                             'advice_asked', 'advice_followed', 'advice_not_followed', 'recommended_moves',
                             'played_moves_after_recommendation']
        person_file_exists = os.path.isfile("log_%s_csv.csv" % PERSON_ID)
        csv_person = open("log_%s_csv.csv" % PERSON_ID, "a")
        person_writer = csv.DictWriter(csv_person, fieldnames=person_fieldnames)
        if not person_file_exists:
            person_writer.writeheader()
        person_writer.writerow({'PERSON_ID': PERSON_ID, 'NAO_IS_OPPONENT': NAO_IS_OPPONENT,
                                'GAME_DIFFICULTY': GAME_DIFFICULTY, 'moves': moves, 'winner': winner,
                                'advice_given': advice_given, 'advice_asked': advice_asked,
                                'advice_followed': advice_followed, 'advice_not_followed': advice_not_followed,
                                'recommended_moves': recommended_moves,
                                'played_moves_after_recommendation': played_moves_after_recommendation})
        csv_person.close()

        log = open("log_%s.txt" % PERSON_ID, "a")
        log.write('Game difficulty: ' + str(GAME_DIFFICULTY) + '\n')
        log.write('Nao mode: ' + str(NAO_IS_OPPONENT) + '\n')
        log.write('Total moves: ' + str(moves) + '\n')
        log.write('Winner: ' + str(winner) + '\n')
        log.write('Game: \n' + str(np.flip(board, 0)) + '\n')
        log.write('Advices Given: ' + str(advice_given) + '\n')
        log.write('Advices Asked: ' + str(advice_asked) + '\n')
        log.write('Advices Followed: ' + str(advice_followed) + '\n')
        log.write('Advices Not Followed: ' + str(advice_not_followed) + '\n')
        log.write('Recommended Moves: \n' + str(recommended_moves) + '\n')
        log.write('Played Moves After Recommendations: \n' + str(played_moves_after_recommendation) + '\n')
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
            winner = None
        else:
            master_fieldnames = ['PERSON_ID', 'NAO_IS_OPPONENT', 'moves', 'player_wins', 'player_score',
                                 'computer_wins', 'computer_score', 'advice_given', 'advice_asked', 'advice_followed',
                                 'advice_not_followed', 'recommended_moves', 'played_moves_after_recommendation']
            master_file_exists = os.path.isfile("master_csv_log.csv")
            csv_master = open("master_csv_log.csv", "a")
            master_writer = csv.DictWriter(csv_master, fieldnames=master_fieldnames)
            if not master_file_exists:
                master_writer.writeheader()
            master_writer.writerow({'PERSON_ID': PERSON_ID, 'NAO_IS_OPPONENT': NAO_IS_OPPONENT,
                                    'moves': moves,
                                    'player_wins': player_wins, 'player_score': player_score,
                                    'computer_wins': computer_wins, 'computer_score': computer_score,
                                    'advice_given': advice_given, 'advice_asked': advice_asked,
                                    'advice_followed': advice_followed, 'advice_not_followed': advice_not_followed,
                                    'recommended_moves': recommended_moves,
                                    'played_moves_after_recommendation': played_moves_after_recommendation})
            csv_master.close()
            nao.action_runner.run_action('say_animated', 'Bedankt voor het spelen, vul de enquete in en vraag de onderzoeker naar de volgende stap')
            nao.stop()
            log = open("log_%s.txt" % PERSON_ID, "a")
            log.write('End of session \n')
            log.close()
            pygame.time.wait(3000)