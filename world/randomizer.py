"""
A helper to generates all potential entities for a world using a template.
This should be used in conjuction with other tools as it will have no concept
of fun or balance.
"""
import logging
import os

from argparse import ArgumentParser
from copy import deepcopy
from pprint import pformat
from random import choice, randint, seed

import yaml

from util import display_world_info


def parse_args():
    args = ArgumentParser()
    args.add_argument('-w', '--world', type=str)
    args.add_argument('-o', '--output', type=str)
    return args.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        format='battle-quest-world-randomizer (%(asctime)s) [%(levelname)s]: %(message)s',
        level=logging.INFO
    )

    logging.info('loading generated world from %s', args.world)
    with open(args.world, encoding='utf8') as f:
        world = yaml.load(f, yaml.Loader)

    display_world_info(world)

    if 'randomizer' not in world:
        logging.info('no randomizer options found')
        return

    randomizer = world['randomizer']
    if 'seed' in randomizer:
        logging.info('setting seed to %d', randomizer['seed'])
        seed(randomizer['seed'])

    entities = deepcopy(world['entities'])
    properties = deepcopy(world['properties'])

    logging.info('randomized entities:')

    # check if we need to create a new type chart
    if 'element' in randomizer and len(randomizer['element']) > 0:
        elements = world['properties']['element']['values']
        new_elements = set()
        for value in randomizer['element']:
            if value in elements:
                new_elements.add(value)
            else:
                new_elements.update(value)

        logging.info('randomizing element affinities for %s', new_elements)

        # TODO: there's probably an optimization here
        for e1 in new_elements:
            for e2 in elements:
                properties['element']['affinity'][e1][e2] = choice(
                    [0.5, 1.0, 2.0])
                properties['element']['affinity'][e2][e1] = choice(
                    [0.5, 1.0, 2.0])

    if 'character' in randomizer and len(randomizer['character']) > 0:
        e_groups = world['properties']['element']['group']
        new_characters = []
        counter = 0
        for character_group in randomizer['character']:
            count = character_group['count']
            logging.info(
                'generating %s randomized %s %s characters',
                count,
                '/'.join(character_group.get('type', ['any'])),
                '/'.join(character_group.get('element', ['any']))
            )

            # TODO: what a mess!
            character_pool = []
            for character in entities['character']:
                add_to_pool = 0
                if 'type' in character_group:
                    if character['type'] in character_group['type']:
                        add_to_pool += 1
                else:
                    add_to_pool += 1

                if 'element' in character_group:
                    element_filter = set()
                    for elem in character_group['element']:
                        if elem in elements:
                            element_filter.add(elem)
                        elif elem in e_groups:
                            element_filter.update(e_groups[elem])
                    if len(set(character['element']) & element_filter) > 0:
                        add_to_pool += 1
                else:
                    add_to_pool += 1

                if add_to_pool == 2:
                    character_pool.append(character)

            characters = [deepcopy(choice(character_pool))
                          for _ in range(count)]
            for character in characters:
                character['name'] = f'# {counter:04d}'
                character['health'] = randint(*character_group['health'])
                # TODO: need to find a way to enforce filters on the effects
                if 'effect' in character_group:
                    character['effect'] = []
                    for effect in character_group['effect']:
                        character['effect'].append(
                            choice(world['entities'][effect]))
                counter += 1
            new_characters.extend(characters)
        entities['character'] = new_characters

    world['properties'] = properties
    world['entities'] = entities
    world['description'] = f'a generated world for {world['name']}'
    del world['randomizer']

    with open(args.output, 'w', encoding='utf8') as f:
        yaml.dump(world, f)
    logging.info('wrote randomized world to %s', args.output)


if __name__ == '__main__':
    main()
