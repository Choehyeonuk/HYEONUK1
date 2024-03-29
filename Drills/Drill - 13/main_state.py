import random
import json
import pickle
import os

from pico2d import *
import game_framework
import game_world
from zombie import Zombie
import world_build_state
import rank_state

name = "MainState"
z_list = []

def collide(a, b):
    # fill here
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False

    return True

boy = None
time = []

def enter():
    # game world is prepared already in world_build_state
    global boy
    global time
    boy = world_build_state.get_boy()
    for o in game_world.all_objects():
        if isinstance(o, Zombie):
            z_list.append(o)
    with open('ranking.json', 'r') as f:
        time = json.load(f)
    time.sort(reverse=True)


def exit():
    game_world.clear()


def pause():
    pass


def resume():
    pass


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_state(world_build_state)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_s:
            game_world.save()
        else:
            boy.handle_event(event)


def update():
    global boy
    global z_list
    global time

    for game_object in game_world.all_objects():
        game_object.update()

    for z in z_list:
        if collide(boy, z):
            time.append(get_time() - boy.start_time)
            with open('ranking.json', 'w') as f:
                json.dump(time, f)
            game_framework.change_state(rank_state)


def draw():
    clear_canvas()
    for game_object in game_world.all_objects():
        game_object.draw()
    update_canvas()






