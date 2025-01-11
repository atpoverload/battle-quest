"""
A helper to generates all potential entities for a world using a template.
This should be used in conjuction with other tools as it will have no concept
of fun or balance.
"""
import logging
import os

from argparse import ArgumentParser
from copy import deepcopy
from itertools import product

import yaml

from util import display_world_info


def generate_abilities(ability):
    pool = []
    for value in ability['value']:
        if isinstance(value, str):
            pool.append([value])
        else:
            pool.append(value)

    abilities = []
    for value in product(*pool):
        abilities.append({
            'name': f'{ability["type"]} {'+'.join(value)}',
            'type': ability['type'],
            'value': list(value),
        })
    return abilities


def generate_actions(action):
    pool = []
    for value in action['value']:
        if isinstance(value, str):
            pool.append([value])
        else:
            pool.append(value)

    actions = []
    for value in product(*pool):
        actions.append({
            'name': f'{action["type"]} {'-'.join(value)}',
            'type': action['type'],
            'value': list(value),
        })
    return actions


def generate_characters(character):
    pool = []
    for value in character['element']:
        if isinstance(value, str):
            pool.append([value])
        else:
            pool.append(value)

    characters = []
    for element in product(*pool):
        characters.append({
            'name': '+'.join(element),
            'type': character['type'],
            'element': list(dict.fromkeys(element)),
        })
    return characters


def generate_entities(generator):
    entities = {}
    if 'ability' in generator and len(generator['ability']) > 0:
        abilities = []
        for ability in generator['ability']:
            logging.info(
                'generating %s %s abilities',
                ability['type'],
                ability['value']
            )
            abilities.extend(generate_abilities(ability))
        entities['ability'] = abilities

    if 'action' in generator and len(generator['action']) > 0:
        actions = []
        for action in generator['action']:
            logging.info(
                'generating %s %s actions',
                action['type'],
                action['value']
            )
            actions.extend(generate_actions(action))
        entities['action'] = actions

    if 'character' in generator and len(generator['character']) > 0:
        characters = []
        for character in generator['character']:
            logging.info(
                'generating %s %s characters',
                character['type'],
                character['element']
            )
            characters.extend(generate_characters(character))
        entities['character'] = characters
    return entities


def parse_args():
    args = ArgumentParser()
    args.add_argument('-w', '--world', type=str)
    args.add_argument('-o', '--output', type=str)
    return args.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        format='battle-quest-world-generator (%(asctime)s) [%(levelname)s]: %(message)s',
        level=logging.INFO
    )

    logging.info('loading template from %s', args.world)
    with open(args.world, encoding='utf8') as f:
        world = yaml.load(f, yaml.Loader)

    display_world_info(world)

    if 'generator' not in world:
        logging.info('no generator options found')
        return

    generator = world['generator']

    properties = deepcopy(world['properties'])

    entities = generate_entities(generator)

    logging.info('generated entities:')
    for entity in entities:
        logging.info(f' - {entity}: {len(entities[entity])}')

    # world['properties'] = properties
    for entity in entities:
        world['entities'][entity] = entities[entity]
    del world['generator']

    with open(args.output, 'w', encoding='utf8') as f:
        yaml.dump(world, f)
    logging.info('wrote generated world to %s', args.output)


if __name__ == '__main__':
    main()
