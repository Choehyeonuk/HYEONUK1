from pico2d import *
import random

# Game object class here


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400, 30)


class Boy:
    def __init__(self):
        self.x, self.y = random.randint(100,700), 90
        self.v = random.randint(3, 7)
        self.dir = 1
        self.frame = random.randint(0, 7)
        self.image = load_image('animation_sheet.png')

    def update(self):
        self.frame = (self.frame + 1) % 8
        self.x += self.v * self.dir

        if self.x > 780 or self.x < 20:
            self.dir *= -1

    def draw(self):
        if self.dir > 0:
            self.image.clip_draw(self.frame * 100, 100, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)


class Ball:
    def __init__(self):
        self.x, self.y = random.randint(0, 800), 599
        self.v = random.randint(1, 7)
        self.size = random.randint(0, 1)

        if self.size == 0:
            self.image = load_image("ball21x21.png")
        else:
            self.image = load_image("ball41x41.png")

    def update(self):
        self.y -= self.v

        if self.size == 1:
            if self.y < 80:
                self.v = 0
        else:
            if self.y < 70:
                self.v = 0

    def draw(self):
        self.image.draw(self.x, self.y)

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


# initialization code
open_canvas()

team = [Boy() for i in range(11)]
balls = [Ball() for i in range(20)]
grass = Grass()

running = True

# game main loop code
while running:
    handle_events()

    for boy in team:
        boy.update()
    for ball in balls:
        ball.update()

    clear_canvas()
    grass.draw()
    for boy in team:
        boy.draw()
    for ball in balls:
        ball.draw()

    update_canvas()
    delay(0.02)
# finalization code
close_canvas()
