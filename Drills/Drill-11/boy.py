import game_framework
from pico2d import *
from ball import Ball
import main_state

import game_world

# Boy Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# Boy Jump Speed
JUMP_SPEED = 80  # 2.4m/s
MAX_HEIGHT = 250

# Boy Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

# Boy Event
RIGHT_DOWN, LEFT_DOWN, RIGHT_UP, LEFT_UP, SLEEP_TIMER, SPACE, FALL, COLLIDE = range(8)

key_event_table = {
    (SDL_KEYDOWN, SDLK_RIGHT): RIGHT_DOWN,
    (SDL_KEYDOWN, SDLK_LEFT): LEFT_DOWN,
    (SDL_KEYUP, SDLK_RIGHT): RIGHT_UP,
    (SDL_KEYUP, SDLK_LEFT): LEFT_UP,
    (SDL_KEYDOWN, SDLK_SPACE): SPACE
}


# Boy States

class IdleState:

    @staticmethod
    def enter(boy, event):
        if event == RIGHT_DOWN:
            boy.velocity = 0
        elif event == LEFT_DOWN:
            boy.velocity = 0
        elif event == RIGHT_UP:
            boy.velocity = 0
        elif event == LEFT_UP:
            boy.velocity = 0
        boy.timer = 1000

    @staticmethod
    def exit(boy, event):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        if boy.on_the_brick:
            boy.x += (main_state.brick.move_dir * main_state.brick.SPEED) * game_framework.frame_time
        boy.timer -= 1
        if boy.timer == 0:
            boy.add_event(SLEEP_TIMER)

    @staticmethod
    def draw(boy):
        if boy.dir == 1:
            boy.image.clip_draw(int(boy.frame) * 100, 300, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(int(boy.frame) * 100, 200, 100, 100, boy.x, boy.y)


class RunState:

    @staticmethod
    def enter(boy, event):
        if event == RIGHT_DOWN:
            boy.velocity = RUN_SPEED_PPS
        elif event == LEFT_DOWN:
            boy.velocity = -RUN_SPEED_PPS
        elif event == RIGHT_UP:
            boy.velocity = -RUN_SPEED_PPS
        elif event == LEFT_UP:
            boy.velocity = RUN_SPEED_PPS
        boy.dir = clamp(-1, boy.velocity, 1)

    @staticmethod
    def exit(boy, event):
        pass

    @staticmethod
    def do(boy):
        # boy.frame = (boy.frame + 1) % 8
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        boy.x += boy.velocity * game_framework.frame_time
        if boy.on_the_brick:
            boy.x += (main_state.brick.move_dir * main_state.brick.SPEED) * game_framework.frame_time
            if not main_state.collide(boy, main_state.brick):
                boy.on_the_brick = False
                boy.add_event(FALL)
        boy.x = clamp(25, boy.x, 1600 - 25)

    @staticmethod
    def draw(boy):
        if boy.dir == 1:
            boy.image.clip_draw(int(boy.frame) * 100, 100, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(int(boy.frame) * 100, 0, 100, 100, boy.x, boy.y)


class SleepState:

    @staticmethod
    def enter(boy, event):
        boy.frame = 0

    @staticmethod
    def exit(boy, event):
        pass

    @staticmethod
    def do(boy):
        if boy.on_the_brick:
            boy.x += (main_state.brick.move_dir * main_state.brick.SPEED) * game_framework.frame_time
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8

    @staticmethod
    def draw(boy):
        if boy.dir == 1:
            boy.image.clip_composite_draw(int(boy.frame) * 100, 300, 100, 100, 3.141592 / 2, '', boy.x - 25, boy.y - 25,
                                          100, 100)
        else:
            boy.image.clip_composite_draw(int(boy.frame) * 100, 200, 100, 100, -3.141592 / 2, '', boy.x + 25,
                                          boy.y - 25, 100, 100)


class JumpState:
    @staticmethod
    def enter(boy, event):
        if event == SPACE and boy.on_the_ground:
            boy.on_the_ground = False

    @staticmethod
    def exit(boy, event):
        pass

    @staticmethod
    def do(boy):
        boy.y += JUMP_SPEED * game_framework.frame_time

        if main_state.collide(boy, main_state.brick):
            boy.y = (main_state.brick.y + 20) + 38
            boy.on_the_brick = True
            boy.add_event(COLLIDE)

        if boy.y >= MAX_HEIGHT and not boy.on_the_brick:
            boy.add_event(FALL)

    @staticmethod
    def draw(boy):
        if boy.dir == 1:
            boy.image.clip_draw(0, 300, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(0, 200, 100, 100, boy.x, boy.y)


class FallState:
    @staticmethod
    def enter(boy, event):
        pass

    @staticmethod
    def exit(boy, event):
        pass

    @staticmethod
    def do(boy):
        boy.y -= JUMP_SPEED * game_framework.frame_time

        if main_state.collide(boy, main_state.brick):
            boy.y = (main_state.brick.y + 20) + 38
            boy.on_the_brick = True
            boy.add_event(COLLIDE)

        if main_state.collide(boy, main_state.grass):
            boy.y = 90
            boy.on_the_ground = True
            boy.add_event(COLLIDE)

    @staticmethod
    def draw(boy):
        if boy.dir == 1:
            boy.image.clip_draw(0, 300, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(0, 200, 100, 100, boy.x, boy.y)


next_state_table = {
    IdleState: {RIGHT_UP: RunState, LEFT_UP: RunState, RIGHT_DOWN: RunState, LEFT_DOWN: RunState,
                SLEEP_TIMER: SleepState, SPACE: JumpState, COLLIDE: IdleState},

    RunState: {RIGHT_UP: IdleState, LEFT_UP: IdleState, LEFT_DOWN: IdleState, RIGHT_DOWN: IdleState,
               SPACE: RunState, FALL: FallState},

    SleepState: {LEFT_DOWN: RunState, RIGHT_DOWN: RunState, LEFT_UP: RunState, RIGHT_UP: RunState, SPACE: IdleState},

    JumpState: {LEFT_DOWN: JumpState, LEFT_UP: JumpState, RIGHT_UP: JumpState, RIGHT_DOWN: JumpState,
                SPACE: JumpState, COLLIDE: IdleState, FALL: FallState},

    FallState: {LEFT_DOWN: FallState, LEFT_UP: FallState, RIGHT_UP: FallState, RIGHT_DOWN: FallState,
                SPACE: FallState, COLLIDE: IdleState}
}


class Boy:

    def __init__(self):
        self.x, self.y = 1600 // 2, 90
        # Boy is only once created, so instance image loading is fine
        self.image = load_image('animation_sheet.png')
        self.font = load_font('ENCR10B.TTF', 16)
        self.dir = 1
        self.velocity = 0
        self.frame = 0
        self.on_the_brick = False
        self.on_the_ground = True
        self.event_que = []
        self.cur_state = IdleState
        self.cur_state.enter(self, None)

    def get_bb(self):
        # fill here
        return 0, 0, 0, 0

    def add_event(self, event):
        self.event_que.insert(0, event)

    def update(self):
        self.cur_state.do(self)
        if len(self.event_que) > 0:
            event = self.event_que.pop()
            self.cur_state.exit(self, event)
            self.cur_state = next_state_table[self.cur_state][event]
            self.cur_state.enter(self, event)

    def draw(self):
        self.cur_state.draw(self)
        self.font.draw(self.x - 60, self.y + 50, '(Time: %3.2f)' % get_time(), (255, 255, 0))
        # fill here
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 30, self.y - 38, self.x + 30, self.y + 40

    def handle_event(self, event):
        if (event.type, event.key) in key_event_table:
            key_event = key_event_table[(event.type, event.key)]
            self.add_event(key_event)
