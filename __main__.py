import json
import logging
import re

from argparse import ArgumentParser

import pygame
import pygame_gui
import pygame_gui.elements.ui_button

from scenes.battle import BattleScene
from world import WorldManager


def attack(user, target, value):
    target['health'] = max(0, target['health'] - value)


def defend(user, target, value):
    pass


def parse_args():
    args = ArgumentParser()

    args.add_argument('--world', type=str, default='./worlds/test_world.json')
    args.add_argument('--theme', type=str, default='./themes/default.json')
    args.add_argument('--resolution', type=str, default='(1200, 800)')

    args = args.parse_args()
    if re.match('\(([1-9]|([1-9][0-9]+)),\s+([1-9]|([1-9][0-9]+))\)', args.resolution) is None:
        raise AttributeError(
            'expected a pair of positive ints; got %s', args.resolution)
    args.resolution = eval(args.resolution)

    return args


def main():
    args = parse_args()
    logging.basicConfig(
        format='battle-quest (%(asctime)s) [%(levelname)s]: %(message)s', level=logging.DEBUG)

    logging.info('loading world file from %s', args.world)
    with open(args.world) as f:
        world = json.load(f)

    world = WorldManager(world)
    party = [world.new_adventurer() for _ in range(3)]
    enemy = [world.new_monster(2)]

    for member in party:
        member.inventory['mainhand'] = world.new_item()

    pygame.init()

    resolution = args.resolution
    logging.info('creating window with resolution %s', resolution)
    window_surface = pygame.display.set_mode(resolution)

    background = pygame.Surface(resolution)
    background.fill(pygame.Color('#220222'))

    manager = pygame_gui.UIManager(
        resolution,
        theme_path=args.theme
    )

    is_running = True

    scene = BattleScene(party, enemy, manager)

    while is_running:
        window_surface.blit(background, (0, 0))

        is_running = scene.process(window_surface)


if __name__ == '__main__':
    main()
