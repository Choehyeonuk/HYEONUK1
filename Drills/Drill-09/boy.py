from pico2d import *

# Boy Event
RIGHT_DOWN, LEFT_DOWN, RIGHT_UP, LEFT_UP, RSHIFT_DOWN, RSHIFT_UP, LSHIFT_DOWN, LSHIFT_UP, TIMER_OUT = range(9)

key_event_table = {
    (SDL_KEYDOWN, SDLK_RIGHT): RIGHT_DOWN,
    (SDL_KEYDOWN, SDLK_LEFT): LEFT_DOWN,
    (SDL_KEYDOWN, SDLK_RSHIFT): RSHIFT_DOWN,
    (SDL_KEYDOWN, SDLK_LSHIFT): LSHIFT_DOWN,
    (SDL_KEYUP, SDLK_RIGHT): RIGHT_UP,
    (SDL_KEYUP, SDLK_LEFT): LEFT_UP,
    (SDL_KEYUP, SDLK_RSHIFT): RSHIFT_UP,
    (SDL_KEYUP, SDLK_LSHIFT): LSHIFT_UP
}

Push_Shift = 0


# Boy States

class IdleState:
    @staticmethod
    def enter(boy, event):
        boy.velocity = 0

    @staticmethod
    def exit(boy, event):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.dir == 1:
            boy.image.clip_draw(boy.frame * 100, 300, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 200, 100, 100, boy.x, boy.y)


class RunState:
    @staticmethod
    def enter(boy, event):
        if event == RIGHT_DOWN:
            boy.velocity += 1
        elif event == RIGHT_UP:
            boy.velocity -= 1
        elif event == LEFT_DOWN:
            boy.velocity -= 1
        elif event == LEFT_UP:
            boy.velocity += 1
        boy.dir = boy.velocity

    @staticmethod
    def exit(boy, event):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.velocity
        boy.x = clamp(25, boy.x, 800 - 25)

    @staticmethod
    def draw(boy):
        if boy.velocity > 0:
            boy.image.clip_draw(boy.frame * 100, 100, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 0, 100, 100, boy.x, boy.y)


class DashState:
    @staticmethod
    def enter(boy, event):
        global Push_Shift

        if Push_Shift == 1:
            if event == RSHIFT_DOWN or event == LSHIFT_DOWN:
                if boy.velocity > 0:
                    boy.velocity += 2
                else:
                    boy.velocity -= 2
            boy.timer = 150

    @staticmethod
    def exit(boy, event):
        if event == RSHIFT_UP or event == LSHIFT_UP:
            if boy.velocity > 0:
                boy.velocity = 1
            else:
                boy.velocity = -1
        elif event == TIMER_OUT:
            if boy.velocity > 0:
                boy.velocity = 1
            else:
                boy.velocity = -1

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.timer -= 1
        boy.x += boy.velocity
        boy.x = clamp(25, boy.x, 800 - 25)
        if boy.timer == 0:
            DashState.exit(boy, TIMER_OUT)

    @staticmethod
    def draw(boy):
        if boy.velocity > 0:
            boy.image.clip_draw(boy.frame * 100, 100, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 0, 100, 100, boy.x, boy.y)


next_state_table = {
    IdleState: {RIGHT_UP: RunState, LEFT_UP: RunState,
                RIGHT_DOWN: RunState, LEFT_DOWN: RunState,
                RSHIFT_UP: IdleState, LSHIFT_UP: IdleState,
                RSHIFT_DOWN: IdleState, LSHIFT_DOWN: IdleState},

    RunState: {RIGHT_UP: IdleState, LEFT_UP: IdleState,
               RIGHT_DOWN: IdleState, LEFT_DOWN: IdleState,
               RSHIFT_UP: RunState, LSHIFT_UP: RunState,
               RSHIFT_DOWN: DashState, LSHIFT_DOWN: DashState},

    DashState: {RSHIFT_UP: RunState, LSHIFT_UP: RunState, TIMER_OUT: RunState,
                RSHIFT_DOWN: DashState, LSHIFT_DOWN: DashState,
                RIGHT_UP: IdleState, LEFT_UP: IdleState,
                RIGHT_DOWN: IdleState, LEFT_DOWN: IdleState}
}


class Boy:

    def __init__(self):
        self.x, self.y = 800 // 2, 90
        self.image = load_image('animation_sheet.png')
        self.dir = 1
        self.velocity = 0
        self.frame = 0
        self.timer = 0
        self.event_que = []
        self.cur_state = IdleState
        self.cur_state.enter(self, None)

    def update_state(self):
        if len(self.event_que) > 0:
            event = self.event_que.pop()
            self.cur_state.exit(self, event)
            self.cur_state = next_state_table[self.cur_state][event]
            self.cur_state.enter(self, event)

    def change_state(self, state):
        # fill here
        pass

    def add_event(self, event):
        # fill here
        self.event_que.insert(0, event)

    def update(self):
        # fill here
        self.cur_state.do(self)
        if len(self.event_que) > 0:
            event = self.event_que.pop()
            self.cur_state.exit(self, event)
            self.cur_state = next_state_table[self.cur_state][event]
            self.cur_state.enter(self, event)

    def draw(self):
        # fill here
        self.cur_state.draw(self)

    def handle_event(self, event):
        # fill here
        global Push_Shift
        if (event.type, event.key) in key_event_table:
            key_event = key_event_table[(event.type, event.key)]
            if key_event == RSHIFT_DOWN or key_event == LSHIFT_DOWN:
                Push_Shift += 1
            elif key_event == RSHIFT_UP or key_event == LSHIFT_UP:
                Push_Shift -= 1
            self.add_event(key_event)
