import json
import logging
import os

from argparse import ArgumentParser

import drawsvg as draw
import yaml

CARD_SIZE = (300, 400)
OUTER_MARGIN = 12
SPACING_MARGIN = 48

TITLE_FONT_SIZE = 48
ELEMENT_FONT_SIZE = 32
TEXT_FONT_SIZE = 32

SLOT_COLORS = {
    'move': 'orange',
    'weapon': 'green',
    'offhand': 'dodgerblue',
    'armor': 'grey',
    'consumable': 'coral',
}

ELEMENT_COLORS = {
    'any': 'black',
    'wood': 'green',
    'water': 'blue',
    'steel': 'grey',
    'stone': 'brown',
    'fire': 'red',
    'body': 'teal',
    'mind': 'purple',
    'spirit': 'orange',
}

def draw_frame(fill_color='#FFFFFF'):
    return draw.Rectangle(
        -CARD_SIZE[0] / 2,
        -CARD_SIZE[1] / 2,
        *CARD_SIZE,
        fill=fill_color,
    )


def draw_name(name):
    return draw.Text(
        name,
        TITLE_FONT_SIZE,
        -CARD_SIZE[0] / 2 + OUTER_MARGIN,
        -CARD_SIZE[1] / 2 + OUTER_MARGIN,
        text_anchor='left',
        dominant_baseline='hanging',
    )


def draw_health(health):
    l = []
    l.append(draw.Circle(
        CARD_SIZE[0] / 2 - SPACING_MARGIN,
        -CARD_SIZE[1] / 2 + 4 * OUTER_MARGIN - 6,
        35,
        stroke='black',
        stroke_width=4,
        fill='brown',
    ))
    l.append(draw.Text(
        str(health),
        TITLE_FONT_SIZE,
        CARD_SIZE[0] / 2 - SPACING_MARGIN,
        -CARD_SIZE[1] / 2 + OUTER_MARGIN,
        text_anchor='middle',
        dominant_baseline='hanging',
    ))
    return l


def draw_sprite(sprite_name):
    return draw.Image(
        -CARD_SIZE[0] / 3,
        -CARD_SIZE[1] / 4,
        4 * SPACING_MARGIN,
        4 * SPACING_MARGIN,
        path=sprite_name,
        embed=True,
    )


def draw_slot(slot):
    l = []
    l.append(draw.Rectangle(
        CARD_SIZE[0] / 2 - SPACING_MARGIN - 2 * OUTER_MARGIN - 4,
        -CARD_SIZE[1] / 2 + OUTER_MARGIN,
        60,
        60,
        stroke='black',
        stroke_width=4,
        fill=SLOT_COLORS[slot],
        rx='10'
    ))
    l.append(draw.Text(
        slot.upper()[0],
        TITLE_FONT_SIZE,
        CARD_SIZE[0] / 2 - SPACING_MARGIN,
        -CARD_SIZE[1] / 2 + OUTER_MARGIN,
        text_anchor='middle',
        dominant_baseline='hanging',
    ))
    return l


def draw_description(effect):
    path = draw.Path(stroke='gray', fill='none')
    path.M(
        CARD_SIZE[0] / 2 - 3 * OUTER_MARGIN,
        -CARD_SIZE[1] / 4
    ).L(
        CARD_SIZE[0] / 2 - 3 * OUTER_MARGIN,
        CARD_SIZE[1] / 2
    )
    description = ''
    target = effect['target'] if 'target' in effect else ''
    if effect['type'] == 'attack':
        description = f'{effect["element"].title()} {target.title()} {effect["value"]}'
    elif effect['type'] == 'condition':
        description = f'{effect["value"].title()} {target.title()}'
    elif effect['type'] == 'heal':
        description = f'Heal {target.title()} {effect["value"]}'
    elif effect['type'] == 'defense':
        description = f'{effect["element"].title()} Element'
    return draw.Text(
        description,
        TEXT_FONT_SIZE,
        path=path,
        text_anchor='left',
        dominant_baseline='hanging',
    )


def draw_elements(elements):
    l = []
    l.append(draw.Text(
        'Elements',
        ELEMENT_FONT_SIZE,
        0,
        CARD_SIZE[1] / 4,
        text_anchor='middle',
        dominant_baseline='hanging',
    ))
    element_count = len(elements)
    for i, element in enumerate(elements):
        l.append(draw.Rectangle(
            - SPACING_MARGIN / 2 +
                (SPACING_MARGIN + OUTER_MARGIN) *
            (2 * i - element_count + 1) / 2,
            CARD_SIZE[1] / 2 - SPACING_MARGIN - OUTER_MARGIN,
            SPACING_MARGIN,
            SPACING_MARGIN,
            stroke='black',
            stroke_width=4,
            fill=ELEMENT_COLORS[element]
        ))
    return l


class WorldVisualizer:
    def __init__(self, world):
        self.world = world

def draw_character(name, character, kind):
    d = draw.Drawing(*CARD_SIZE, origin='center')
    d.append(draw_frame())
    d.append(draw_name(name.title()))
    d.extend(draw_health(character['health']))
    d.append(draw_sprite(
        f'./resources/sprites/{kind}/{name}.svg'))
    d.extend(draw_elements(character['element']))
    return d


def draw_item(name, item):
    d = draw.Drawing(*CARD_SIZE, origin='center')
    d.append(draw_frame())
    d.append(draw_name(name.title()))
    d.extend(draw_slot(item['slot']))
    d.append(draw_sprite(f'./resources/sprites/items/{name}.svg'))
    d.append(draw_description(item['effect']))
    d.extend(draw_elements(item['element']))
    return d


def draw_move(name, move):
    d = draw.Drawing(*CARD_SIZE, origin='center')
    d.append(draw_frame())
    d.append(draw_name(name.title()))
    d.append(draw_sprite(f'./resources/sprites/moves/{name}.svg'))
    d.append(draw_description(move['effect']))
    d.extend(draw_slot('move'))
    return d

def draw_card_front(name, entity_kind, entity):
    d = draw.Drawing(*CARD_SIZE, origin='center')
    d.append(draw_frame())
    d.append(draw_name(name.title()))
    d.append(draw_sprite(f'./resources/sprites/{entity_kind}/{name}.svg'))
    d.append(draw_description(entity['effect']))
    d.extend(draw_slot('move'))

def draw_card_back():
    d = draw.Drawing(*CARD_SIZE, origin='center')
    d.append(draw_frame('dodgerblue'))
    d.append(draw_name('BattleQuest'))
    return d


def maybe_create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def parse_args():
    args = ArgumentParser()
    args.add_argument('--world', type=str,
                      default='./resources/worlds/test_world.json')
    args.add_argument('--output', type=str, default='./cards')
    return args.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        format='battle-quest-visualizer (%(asctime)s) [%(levelname)s]: %(message)s', level=logging.DEBUG)

    logging.info('loading world file from %s', args.world)
    world = yaml.load(open(args.world), yaml.Loader)
    # print('a?')
    print(world['adventurers'])
    # return

    # with open(args.world) as f:
    #     world = json.load(f)

    draw_card_back().save_png(f'{args.output}/card_back.png')

    adventurers = {c: draw_character(c,
                                     world['adventurers'][c], 'adventurers') for c in world['adventurers']}
    logging.info('generated %d adventurers (%s)',
                 len(adventurers), list(adventurers.keys()))
    maybe_create_dir(f'{args.output}/adventurers')
    for name, adventurer in adventurers.items():
        # adventurer.save_svg(f'{args.output}/adventurers/{name}.svg')
        adventurer.save_png(f'{args.output}/adventurers/{name}.png')

    monsters = {c: draw_character(
        c,
        world['monsters'][c],
        'monsters'
    ) for c in world['monsters']}
    logging.info('generated %d monsters (%s)',
                 len(monsters), list(monsters.keys()))
    maybe_create_dir(f'{args.output}/monsters')
    for name, monster in monsters.items():
        # monster.save_svg(f'{args.output}/monsters/{name}.svg')
        monster.save_png(f'{args.output}/monsters/{name}.png')

    items = {c: draw_item(c, world['items'][c]) for c in world['items']}
    logging.info('generated %d items (%s)', len(items), list(items.keys()))
    maybe_create_dir(f'{args.output}/items')
    for name, item in items.items():
        # item.save_svg(f'{args.output}/items/{name}.svg')
        item.save_png(f'{args.output}/items/{name}.png')

    moves = {c: draw_move(c, world['moves'][c]) for c in world['moves']}
    logging.info('generated %d moves (%s)', len(moves), list(moves.keys()))
    maybe_create_dir(f'{args.output}/moves')
    for name, move in moves.items():
        # move.save_svg(f'{args.output}/moves/{name}.svg')
        move.save_png(f'{args.output}/moves/{name}.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd

    elements = pd.DataFrame(world['elements'])
    # print(elements)
    sns.heatmap(elements, linewidths=1, annot=True, cmap='RdBu_r')
    plt.savefig('elements.pdf', bbox_inches='tight')
    plt.close()

    import graphviz as dot

    colors = {
        1: 'blue',
        2: 'black',
        4: 'red',
    }

    element_chart = dot.Digraph()
    for e1, res in elements.iterrows():
        element_chart.node(e1)
        for e2, res in res.items():
            if res != 2.0:
                continue
            element_chart.edge(e1, e2, color=colors[int(res * 2)])
    element_chart.render('weakness-chart')

    element_chart = dot.Digraph()
    for e1, res in elements.iterrows():
        element_chart.node(e1)
        for e2, res in res.items():
            if res != 0.5:
                continue
            element_chart.edge(e1, e2, color=colors[int(res * 2)])
    element_chart.render('resistance-chart')


if __name__ == '__main__':
    main()
