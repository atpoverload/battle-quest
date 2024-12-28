import logging
import os

from argparse import ArgumentParser
from itertools import product
from random import choice

import yaml


def new_character(template):
    name = 'shaman'
    health = 10
    elements = list(set(choice(product(*template['elements']['pools']))))
    elements.sort()
    return (
        name,
        {
            "health": health,
            "element": elements
        })


def maybe_create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def parse_args():
    args = ArgumentParser()
    args.add_argument('-t', '--template', type=str)
    args.add_argument('-o', '--output', type=str)
    return args.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        format='battle-quest-world-generator (%(asctime)s) [%(levelname)s]: %(message)s',
        level=logging.DEBUG
    )

    logging.info('loading template from %s', args.world)
    with open(args.world, encoding='utf8') as f:
        world_template = yaml.load(f, yaml.Loader)

    generator = world_template['generator']
    for character in generator['character']:
        character_template = generator['character'][character]
        elements = [choice(e) for e in character_template['elements']['pool']]
        character = {
            'health': health,
            'elements': elements,
            'effect': None,
        }
        


if __name__ == '__main__':
    main()
