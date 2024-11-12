import telebot
import random

bot = telebot.TeleBot('7014423546:AAFsOHSNtuh6DNOCPLWTiUt07G0CmtUruaI')

# Словари для хранения активных игр
single_player_games = {}
multi_player_games = {}
game_requests = {}

# Инициализация игры для одиночного игрока
def init_single_player_game(chat_id):
    game_board = [' ' for _ in range(9)]
    single_player_games[chat_id] = {'board': game_board, 'player_turn': True}

# Отправка игрового поля для одиночного игрока
def send_game_board(chat_id, message=""):
    game_board = single_player_games[chat_id]['board']
    board_str = ''
    for i in range(3):
        row = ' | '.join(game_board[i * 3:i * 3 + 3])
        board_str += f'{row}\n'
        if i < 2:
            board_str += '- + - + -\n'
    bot.send_message(chat_id, f'{message}\n{board_str}')

# Проверка победителя
def check_winner(board):
    win_conditions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != ' ':
            return board[condition[0]]
    return None

# Инициализация игры для мультиплеера
def init_game(chat_id):
    game_board = [' ' for _ in range(9)]
    multi_player_games[chat_id] = {'board': game_board, 'turn': 'X', 'player_X': None, 'player_O': None}

# Отправка игрового поля в мультиплеере
def send_board(chat_id, message=""):
    game_board = multi_player_games[chat_id]['board']
    board_str = ''
    for i in range(3):
        row = ' | '.join(game_board[i * 3:i * 3 + 3])
        board_str += f'{row}\n'
        if i < 2:
            board_str += '- + - + -\n'
    bot.send_message(chat_id, f'{message}\n{board_str}')

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = (
        "Доступные команды:\n\n"
        "/start_single_player - Начать игру против бота (одиночный режим)\n"
        "/play - Начать мультиплеерную игру (в одном чате)\n"
        "/help - Показать этот список команд\n\n"
        "Правила игры:\n"
        "1. Игровое поле состоит из 9 ячеек, каждая из которых пронумерована от 1 до 9.\n"
        "2. Игроки поочередно вводят номер ячейки, чтобы сделать ход.\n"
        "3. Побеждает тот, кто первым выстроит линию из 3 символов (по горизонтали, вертикали или диагонали).\n"
        "4. В одиночной игре вы играете против бота.\n"
    )
    bot.send_message(message.chat.id, help_text)

# Обработчик команды /start_single_player
@bot.message_handler(commands=['start_single_player'])
def handle_start_single_player(message):
    init_single_player_game(message.chat.id)
    send_game_board(message.chat.id, "Новая игра началась! Ваш ход. Используйте номера ячеек (1-9) для совершения хода.")

# Обработчик для хода игрока в одиночной игре
@bot.message_handler(func=lambda message: message.chat.id in single_player_games)
def handle_single_player_move(message):
    chat_id = message.chat.id
    game = single_player_games.get(chat_id)
    if game and game['player_turn']:
        try:
            move = int(message.text) - 1
            if 0 <= move <= 8 and game['board'][move] == ' ':
                game['board'][move] = 'X'
                if check_winner(game['board']) == 'X':
                    send_game_board(chat_id, "Вы победили! Поздравляем!")
                    del single_player_games[chat_id]
                    return
                elif ' ' not in game['board']:
                    send_game_board(chat_id, "Ничья!")
                    del single_player_games[chat_id]
                    return
                game['player_turn'] = False
                bot.send_message(chat_id, "Ход компьютера...")
                ai_move = random.choice([i for i in range(9) if game['board'][i] == ' '])
                game['board'][ai_move] = 'O'
                send_game_board(chat_id)
                if check_winner(game['board']) == 'O':
                    send_game_board(chat_id, "Вы проиграли. Попробуйте еще раз!")
                    del single_player_games[chat_id]
                    return
                elif ' ' not in game['board']:
                    send_game_board(chat_id, "Ничья!")
                    del single_player_games[chat_id]
                    return
                game['player_turn'] = True
            else:
                bot.send_message(chat_id, "Неверный ход! Попробуйте еще раз.")
        except ValueError:
            bot.send_message(chat_id, "Введите число от 1 до 9.")
    else:
        bot.send_message(chat_id, "Сейчас не ваш ход.")

# Обработчик команды /play для начала мультиплеерной игры
@bot.message_handler(commands=['play'])
def start_multiplayer_game(message):
    if message.chat.id in multi_player_games:
        bot.send_message(message.chat.id, "Игра уже идет в этом чате.")
        return
    init_game(message.chat.id)
    bot.send_message(message.chat.id, "Новая игра началась! Игрок X начинает. Используйте номера ячеек (1-9) для хода.")
    send_board(message.chat.id)

# Обработчик ходов в мультиплеере
@bot.message_handler(func=lambda message: message.chat.id in multi_player_games)
def handle_multiplayer_move(message):
    chat_id = message.chat.id
    game = multi_player_games.get(chat_id)
    if not game:
        return

    try:
        move = int(message.text) - 1
        if 0 <= move <= 8 and game['board'][move] == ' ':
            current_turn = game['turn']
            game['board'][move] = current_turn
            if check_winner(game['board']):
                send_board(chat_id, f"Игрок {current_turn} победил!")
                del multi_player_games[chat_id]
                return
            elif ' ' not in game['board']:
                send_board(chat_id, "Ничья!")
                del multi_player_games[chat_id]
                return
            game['turn'] = 'O' if current_turn == 'X' else 'X'
            send_board(chat_id, f"Ход игрока {game['turn']}:")

        else:
            bot.send_message(chat_id, "Неверный ход! Попробуйте снова.")
    except ValueError:
        bot.send_message(chat_id, "Введите число от 1 до 9.")


bot.polling()
