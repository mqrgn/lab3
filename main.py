import random
import time

import pygame

# --- ИГРОВЫЕ КОНСТАНТЫ ---
# Состояния игры
GAME_STATE_START_SCREEN = 0
GAME_STATE_RUNNING = 1
GAME_STATE_PAUSED = 2
GAME_STATE_GAME_OVER = 3

# Размеры окна
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
BLOCK_SIZE = 20

# Цвета (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 192, 0)
DARK_GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 150, 255)

# Настройки скорости
INITIAL_SPEED = 10
SPEED_INCREASE_INTERVAL = 5  # Увеличивать скорость каждые N очков
SPEED_INCREASE_AMOUNT = 2

# Настройки бонусов
BONUS_FOOD_PROBABILITY = 0.2  # 20% шанс, что следующая еда будет бонусной
BONUS_FOOD_LIFETIME = 5.0  # Бонусная еда исчезает через 5 секунд


def load_resources():
    global FONT_STYLE, LARGE_FONT, EAT_SOUND, CRASH_SOUND

    # Шрифты
    FONT_STYLE = pygame.font.SysFont('bahnschrift', 15)
    LARGE_FONT = pygame.font.SysFont('bahnschrift', 30)

    pygame.mixer.init()

    EAT_SOUND = pygame.mixer.Sound('eat.wav')
    CRASH_SOUND = pygame.mixer.Sound('crash.wav')




def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(score))
    except Exception as e:
        print(f"Ошибка сохранения рекорда: {e}")


def generate_position(snake_body):
    while True:
        # Умножаем на BLOCK_SIZE, чтобы позиция была ровной
        new_pos = [random.randrange(0, SCREEN_WIDTH // BLOCK_SIZE) * BLOCK_SIZE,
                   random.randrange(0, SCREEN_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE]

        # Проверка, что позиция не занята змейкой
        if new_pos not in snake_body:
            return new_pos


def reset_game(high_score_val):
    # Инициализация змейки
    snake_pos = [100, 60]
    snake_body = [[100, 60], [80, 60], [60, 60]]
    snake_direction = 'RIGHT'

    # Еда
    food_pos = generate_position(snake_body)

    # Бонусная еда
    bonus_food_pos = None
    bonus_food_spawn_time = 0

    # Счет и скорость
    score = 0
    current_speed = INITIAL_SPEED

    # Состояние
    game_state = GAME_STATE_START_SCREEN

    return {
        'snake_pos': snake_pos,
        'snake_body': snake_body,
        'snake_direction': snake_direction,
        'food_pos': food_pos,
        'bonus_food_pos': bonus_food_pos,
        'bonus_food_spawn_time': bonus_food_spawn_time,
        'score': score,
        'current_speed': current_speed,
        'game_state': game_state,
        'high_score': high_score_val
    }


# --- ФУНКЦИИ ОТОБРАЖЕНИЯ ---

def show_score(score, high_score, current_speed):
    score_text = FONT_STYLE.render(f"Счет: {score}", True, WHITE)
    high_score_text = FONT_STYLE.render(f"Рекорд: {high_score}", True, WHITE)
    speed_text = FONT_STYLE.render(f"Скорость: {current_speed}", True, WHITE)

    screen.blit(score_text, [10, 10])
    # Рекорд справа
    screen.blit(high_score_text, [SCREEN_WIDTH - high_score_text.get_width() - 10, 10])
    screen.blit(speed_text, [10, 35])


def draw_elements(game_data):
    """Отрисовывает змейку и еду."""
    # Рисуем змейку
    # Голова
    head = game_data['snake_body'][0]
    pygame.draw.rect(screen, DARK_GREEN, pygame.Rect(head[0], head[1], BLOCK_SIZE, BLOCK_SIZE))
    # Тело
    for pos in game_data['snake_body'][1:]:
        pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

    # Рисуем обычную еду
    pygame.draw.rect(screen, RED,
                     pygame.Rect(game_data['food_pos'][0], game_data['food_pos'][1], BLOCK_SIZE, BLOCK_SIZE))

    # Рисуем бонусную еду, если она есть
    if game_data['bonus_food_pos']:
        pygame.draw.rect(screen, YELLOW,
                         pygame.Rect(game_data['bonus_food_pos'][0], game_data['bonus_food_pos'][1], BLOCK_SIZE,
                                     BLOCK_SIZE))


def show_message(msg, color, y_offset=0):
    """Отображает большое сообщение по центру экрана."""
    message = LARGE_FONT.render(msg, True, color)
    rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(message, rect)


# --- ИНИЦИАЛИЗАЦИЯ ---

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()

load_resources()  # Загружаем шрифты и звуки

# Загружаем рекорд и инициализируем игру
INITIAL_HIGH_SCORE = load_high_score()
game_data = reset_game(INITIAL_HIGH_SCORE)
current_game_state = game_data['game_state']

# --- ОСНОВНАЯ ИГРОВАЯ ПЕТЛЯ ---

running = True
while running:

    # 1. ОБРАБОТКА СОБЫТИЙ
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:

            # Общее управление
            if event.key == pygame.K_SPACE:
                if current_game_state == GAME_STATE_START_SCREEN:
                    current_game_state = GAME_STATE_RUNNING
                elif current_game_state == GAME_STATE_GAME_OVER:
                    # Начать новую игру
                    game_data = reset_game(game_data['high_score'])
                    current_game_state = GAME_STATE_RUNNING

            # Пауза
            if event.key == pygame.K_p and current_game_state in [GAME_STATE_RUNNING, GAME_STATE_PAUSED]:
                if current_game_state == GAME_STATE_RUNNING:
                    current_game_state = GAME_STATE_PAUSED
                else:
                    current_game_state = GAME_STATE_RUNNING

            # Управление змейкой (только в режиме RUNNING)
            if current_game_state == GAME_STATE_RUNNING:
                if event.key == pygame.K_UP and game_data['snake_direction'] != 'DOWN':
                    game_data['snake_direction'] = 'UP'
                elif event.key == pygame.K_DOWN and game_data['snake_direction'] != 'UP':
                    game_data['snake_direction'] = 'DOWN'
                elif event.key == pygame.K_LEFT and game_data['snake_direction'] != 'RIGHT':
                    game_data['snake_direction'] = 'LEFT'
                elif event.key == pygame.K_RIGHT and game_data['snake_direction'] != 'LEFT':
                    game_data['snake_direction'] = 'RIGHT'

    # 2. ОБНОВЛЕНИЕ СОСТОЯНИЯ
    if current_game_state == GAME_STATE_RUNNING:

        # 2.1. Движение змейки
        if game_data['snake_direction'] == 'UP':
            game_data['snake_pos'][1] -= BLOCK_SIZE
        elif game_data['snake_direction'] == 'DOWN':
            game_data['snake_pos'][1] += BLOCK_SIZE
        elif game_data['snake_direction'] == 'LEFT':
            game_data['snake_pos'][0] -= BLOCK_SIZE
        elif game_data['snake_direction'] == 'RIGHT':
            game_data['snake_pos'][0] += BLOCK_SIZE

        # 2.2. Телепортация через стены
        if game_data['snake_pos'][0] < 0:
            game_data['snake_pos'][0] = SCREEN_WIDTH - BLOCK_SIZE
        elif game_data['snake_pos'][0] >= SCREEN_WIDTH:
            game_data['snake_pos'][0] = 0

        if game_data['snake_pos'][1] < 0:
            game_data['snake_pos'][1] = SCREEN_HEIGHT - BLOCK_SIZE
        elif game_data['snake_pos'][1] >= SCREEN_HEIGHT:
            game_data['snake_pos'][1] = 0

        # Добавляем новую голову
        game_data['snake_body'].insert(0, list(game_data['snake_pos']))

        # 2.3. Проверка на еду
        eaten = False

        # Проверка обычной еды
        if game_data['snake_pos'][0] == game_data['food_pos'][0] and game_data['snake_pos'][1] == game_data['food_pos'][
            1]:
            game_data['score'] += 1
            eaten = True

        # *** ИСПРАВЛЕНИЕ: Проверка бонусной еды ***
        # Нужно сравнивать X с X, и Y с Y
        if game_data['bonus_food_pos'] and \
                game_data['snake_pos'][0] == game_data['bonus_food_pos'][0] and \
                game_data['snake_pos'][1] == game_data['bonus_food_pos'][1]:
            game_data['score'] += 5  # Больше очков
            game_data['bonus_food_pos'] = None
            game_data['bonus_food_spawn_time'] = 0
            eaten = True  # Еда съедена

        if eaten:
            if EAT_SOUND: EAT_SOUND.play()

            # Увеличение скорости
            if game_data['score'] % SPEED_INCREASE_INTERVAL == 0 and game_data['score'] > 0:
                game_data['current_speed'] += SPEED_INCREASE_AMOUNT

            # Генерация новой обычной еды
            game_data['food_pos'] = generate_position(game_data['snake_body'])

            # Шанс появления бонусной еды
            if random.random() < BONUS_FOOD_PROBABILITY and not game_data['bonus_food_pos']:
                game_data['bonus_food_pos'] = generate_position(game_data['snake_body'] + [game_data['food_pos']])
                game_data['bonus_food_spawn_time'] = time.time()

        else:
            # Еда не съедена: удаляем хвост
            game_data['snake_body'].pop()

        # 2.4. Таймер бонусной еды
        if game_data['bonus_food_pos'] and (time.time() - game_data['bonus_food_spawn_time'] > BONUS_FOOD_LIFETIME):
            game_data['bonus_food_pos'] = None
            game_data['bonus_food_spawn_time'] = 0

        # 2.5. Проверки на столкновение

        # Столкновение с собственным телом
        for block in game_data['snake_body'][1:]:
            if game_data['snake_pos'][0] == block[0] and game_data['snake_pos'][1] == block[1]:
                current_game_state = GAME_STATE_GAME_OVER
                break

        # Если проиграли, проигрываем звук
        if current_game_state == GAME_STATE_GAME_OVER:
            if CRASH_SOUND:
                CRASH_SOUND.play()

        # 2.6. Обновление рекорда
        if game_data['score'] > game_data['high_score']:
            game_data['high_score'] = game_data['score']
            save_high_score(game_data['high_score'])

    # 3. Отрисовка
    screen.fill(BLACK)

    # Отрисовка игровых элементов
    if current_game_state != GAME_STATE_START_SCREEN:
        draw_elements(game_data)
        show_score(game_data['score'], game_data['high_score'], game_data['current_speed'])

    # Отрисовка состояний
    if current_game_state == GAME_STATE_START_SCREEN:
        show_message("ЗМЕЙКА", BLUE, -80)
        show_message(f"Рекорд: {game_data['high_score']}", WHITE, -20)
        show_message("Нажмите ПРОБЕЛ, чтобы начать (P - Пауза)", WHITE, 40)

    elif current_game_state == GAME_STATE_PAUSED:
        show_message("ПАУЗА", WHITE, 0)

    elif current_game_state == GAME_STATE_GAME_OVER:
        show_message("ИГРА ОКОНЧЕНА!", RED, -50)
        show_message(f"Финальный счет: {game_data['score']}", WHITE, 10)
        show_message("Нажмите ПРОБЕЛ для новой игры", WHITE, 50)

    # Обновляем экран
    pygame.display.flip()

    # Устанавливаем FPS
    if current_game_state == GAME_STATE_RUNNING:
        clock.tick(game_data['current_speed'])
    else:
        # Снижаем частоту обновления для меню и паузы
        clock.tick(15)

# Корректное завершение работы
pygame.quit()
quit()