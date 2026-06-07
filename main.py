import pygame
import time
import math
pygame.mixer.init()
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()

MENU = "menu"
SETTINGS = "settings"
PLAYING = "playing"

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)
MENU_FONT = pygame.font.SysFont("comicsans", 56)
BUTTON_FONT = pygame.font.SysFont("comicsans", 34)
SMALL_FONT = pygame.font.SysFont("comicsans", 26)

INTRO_IMAGE = pygame.transform.smoothscale(
    pygame.image.load("imgs/INTRO1.jpg"), (WIDTH, HEIGHT)
)

#BACKGROUND MUSIC 
pygame.mixer.music.load("assets/retrorace-108750.mp3")
pygame.mixer.music.play(-1)
music_volume = 0.4
pygame.mixer.music.set_volume(music_volume)

FPS = 60
PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]


def draw_button(win, rect, text, mouse_pos):
    is_hovered = rect.collidepoint(mouse_pos)
    color = (245, 77, 47) if is_hovered else (202, 38, 34)
    pygame.draw.rect(win, (15, 16, 18), rect.move(4, 5), border_radius=8)
    pygame.draw.rect(win, color, rect, border_radius=8)
    pygame.draw.rect(win, (255, 230, 190), rect, 3, border_radius=8)

    label = BUTTON_FONT.render(text, True, (255, 255, 255))
    win.blit(label, label.get_rect(center=rect.center))


def draw_intro_background(win, title):
    win.blit(INTRO_IMAGE, (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 95))
    win.blit(overlay, (0, 0))

    title_text = MENU_FONT.render(title, True, (255, 245, 218))
    shadow = MENU_FONT.render(title, True, (20, 20, 20))
    title_rect = title_text.get_rect(center=(WIDTH // 2, 115))
    win.blit(shadow, title_rect.move(3, 4))
    win.blit(title_text, title_rect)


def draw_menu(win, start_button, settings_button):
    mouse_pos = pygame.mouse.get_pos()
    draw_intro_background(win, "Car Racer")
    draw_button(win, start_button, "Start Game", mouse_pos)
    draw_button(win, settings_button, "Settings", mouse_pos)
    pygame.display.update()


def draw_settings(win, volume, slider_rect, back_button):
    mouse_pos = pygame.mouse.get_pos()
    draw_intro_background(win, "Settings")

    volume_text = BUTTON_FONT.render(f"Music Volume: {int(volume * 100)}%", True, (255, 255, 255))
    win.blit(volume_text, volume_text.get_rect(center=(WIDTH // 2, 250)))

    pygame.draw.rect(win, (35, 35, 40), slider_rect, border_radius=8)
    filled_rect = slider_rect.copy()
    filled_rect.width = int(slider_rect.width * volume)
    pygame.draw.rect(win, (245, 77, 47), filled_rect, border_radius=8)
    knob_x = slider_rect.left + int(slider_rect.width * volume)
    pygame.draw.circle(win, (255, 245, 218), (knob_x, slider_rect.centery), 16)

    hint = SMALL_FONT.render("Drag the slider or use Left / Right arrows", True, (230, 230, 230))
    win.blit(hint, hint.get_rect(center=(WIDTH // 2, slider_rect.bottom + 40)))

    draw_button(win, back_button, "Back", mouse_pos)
    pygame.display.update()


def update_volume_from_mouse(slider_rect):
    mouse_x = pygame.mouse.get_pos()[0]
    volume = (mouse_x - slider_rect.left) / slider_rect.width
    return max(0, min(1, volume))



class GameInfo:
    LAPS_BY_LEVEL = {
        1: 1,
        2: 2,
    }
    LEVELS = len(LAPS_BY_LEVEL)

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0
        self.player_laps = 0
        self.computer_laps = 0

    def next_level(self):
        self.level += 1
        self.started = False
        self.player_laps = 0
        self.computer_laps = 0

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0
        self.player_laps = 0
        self.computer_laps = 0

    def required_laps(self):
        return self.LAPS_BY_LEVEL.get(self.level, self.LAPS_BY_LEVEL[self.LEVELS])

    def player_finished_level(self):
        return self.player_laps >= self.required_laps()

    def computer_finished_level(self):
        return self.computer_laps >= self.required_laps()

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.prev_x, self.prev_y = self.START_POS
        self.acceleration = 0.1
        self.crossed_finish = False

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        self.prev_x, self.prev_y = self.x, self.y
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def undo_move(self):
        self.x, self.y = self.prev_x, self.prev_y

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.prev_x, self.prev_y = self.START_POS
        self.angle = 0
        self.vel = 0
        self.crossed_finish = False


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.undo_move()
        self.vel = -self.vel
        self.move()
        
    def boost(self):
        self.vel = self.max_vel

         
class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        # self.draw_points(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        desired_angle = math.degrees(math.atan2(-x_diff, -y_diff))
        difference_in_angle = (self.angle - desired_angle + 180) % 360 - 180

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        distance_to_target = math.hypot(target[0] - self.x, target[1] - self.y)
        if distance_to_target < max(14, self.vel + 8):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def completed_path(self):
        return self.current_point >= len(self.path)

    def reset(self):
        super().reset()
        self.vel = self.max_vel
        self.current_point = 0

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2


def draw(win, images, player_car, computer_car, game_info):
    for img, pos in images:
        win.blit(img, pos)
        
        
    level_text = MAIN_FONT.render(
        f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    lap_text = MAIN_FONT.render(
        f"Lap {game_info.player_laps}/{game_info.required_laps()}", 1, (255, 255, 255))
    win.blit(lap_text, (10, HEIGHT - lap_text.get_height() - 100))

    time_text = MAIN_FONT.render(
        f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    vel_text = MAIN_FONT.render(
        f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_SPACE]:
        moved = True
        player_car.boost()
        player_car.move()
    elif keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    elif keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()


def show_message(text, player_car, computer_car, game_info, wait_time=2500):
    draw(WIN, images, player_car, computer_car, game_info)
    blit_text_center(WIN, MAIN_FONT, text)
    pygame.display.update()
    pygame.time.wait(wait_time)


def finish_level(winner, player_car, computer_car, game_info):
    completed_level = game_info.level
    winner_name = "Player" if winner == "player" else "Computer"
    show_message(
        f"Level {completed_level} winner: {winner_name}!",
        player_car,
        computer_car,
        game_info,
    )

    if winner == "computer":
        show_message("You lost the game!", player_car, computer_car, game_info)
        game_info.reset()
        player_car.reset()
        computer_car.reset()
        return

    if completed_level >= game_info.LEVELS:
        show_message("You won the game!", player_car, computer_car, game_info)
        game_info.reset()
        player_car.reset()
        computer_car.reset()
        return

    game_info.next_level()
    player_car.reset()
    computer_car.next_level(game_info.level)


def complete_computer_lap(player_car, computer_car, game_info):
    game_info.computer_laps += 1
    computer_car.crossed_finish = True

    if game_info.computer_finished_level():
        finish_level("computer", player_car, computer_car, game_info)
    else:
        computer_car.current_point = 0


def handle_collision(player_car, computer_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    computer_finish_poi_collide = computer_car.collide(
        FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        if not computer_car.crossed_finish:
            complete_computer_lap(player_car, computer_car, game_info)
    else:
        computer_car.crossed_finish = False

    if computer_car.completed_path():
        complete_computer_lap(player_car, computer_car, game_info)

    player_finish_poi_collide = player_car.collide(
        FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        elif not player_car.crossed_finish:
            player_car.crossed_finish = True
            game_info.player_laps += 1
            if game_info.player_finished_level():
                finish_level("player", player_car, computer_car, game_info)
    else:
        player_car.crossed_finish = False


run = True
screen_state = MENU
dragging_volume = False
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_car = PlayerCar(4, 4)
computer_car = ComputerCar(2, 4, PATH)
game_info = GameInfo()
start_button = pygame.Rect(WIDTH // 2 - 130, 360, 260, 62)
settings_button = pygame.Rect(WIDTH // 2 - 130, 440, 260, 62)
back_button = pygame.Rect(WIDTH // 2 - 100, 470, 200, 58)
volume_slider = pygame.Rect(WIDTH // 2 - 160, 315, 320, 18)

while run:
    clock.tick(FPS)

    if screen_state == MENU:
        draw_menu(WIN, start_button, settings_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    screen_state = PLAYING
                elif settings_button.collidepoint(event.pos):
                    screen_state = SETTINGS
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    screen_state = PLAYING
                elif event.key == pygame.K_s:
                    screen_state = SETTINGS
        continue

    if screen_state == SETTINGS:
        draw_settings(WIN, music_volume, volume_slider, back_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(event.pos):
                    screen_state = MENU
                elif volume_slider.collidepoint(event.pos):
                    dragging_volume = True
                    music_volume = update_volume_from_mouse(volume_slider)
                    pygame.mixer.music.set_volume(music_volume)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_volume = False
            elif event.type == pygame.MOUSEMOTION and dragging_volume:
                music_volume = update_volume_from_mouse(volume_slider)
                pygame.mixer.music.set_volume(music_volume)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    screen_state = MENU
                elif event.key == pygame.K_LEFT:
                    music_volume = max(0, music_volume - 0.05)
                    pygame.mixer.music.set_volume(music_volume)
                elif event.key == pygame.K_RIGHT:
                    music_volume = min(1, music_volume + 0.05)
                    pygame.mixer.music.set_volume(music_volume)
        continue

    draw(WIN, images, player_car, computer_car, game_info)
    

    while not game_info.started:
        blit_text_center(
            WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                screen_state = MENU
                game_info.reset()
                player_car.reset()
                computer_car.reset()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

        if not run or screen_state != PLAYING:
            break

    if not run or screen_state != PLAYING:
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            screen_state = MENU
            game_info.reset()
            player_car.reset()
            computer_car.reset()
            break

    if screen_state != PLAYING:
        continue

    move_player(player_car)
    computer_car.move()

    handle_collision(player_car, computer_car, game_info)

pygame.quit()
