import logging
import os

from argparse import ArgumentParser

import yaml

# used for the element match up charts
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import graphviz as dot

from visualizer.svg.drawer import VerticalCardDrawer


def maybe_create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def parse_args():
    args = ArgumentParser()
    args.add_argument('-w', '--world', type=str)
    args.add_argument('-o', '--output', type=str, default='./generated')
    return args.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        format='battle-quest-visualizer (%(asctime)s) [%(levelname)s]: %(message)s',
        level=logging.INFO
    )

    logging.info('loading world file from %s', args.world)
    with open(args.world, encoding='utf8') as f:
        world = yaml.load(f, yaml.Loader)

    drawer = VerticalCardDrawer(
        **world['visualizer']['tts'],
        resources='./resources/sprites',
    )
    # logging.info('card dimensions:')
    # logging.info('card size: %s', drawer.card_size)
    # logging.info('sprite size: %s', drawer.card_size)

    cardback = drawer.draw_cardback()
    # cardback.save_svg(f'{args.output}/cardback.svg')
    cardback.save_png(f'{args.output}/cardback.png')

    adventurers = {}
    for name in world['adventurers']:
        entity = world['adventurers'][name]
        adventurers[name] = drawer.draw_card(name, entity['element'])
        adventurers[name].extend(
            drawer.draw_tag(str(entity['health']), 'character'))
    logging.info('generated %d adventurers (%s)',
                 len(adventurers), list(adventurers.keys()))
    maybe_create_dir(f'{args.output}/cards/adventurers')
    for name, adventurer in adventurers.items():
        # adventurer.save_svg(f'{args.output}/cards/adventurers/{name}.svg')
        adventurer.save_png(f'{args.output}/cards/adventurers/{name}.png')

    monsters = {}
    for name in world['monsters']:
        entity = world['monsters'][name]
        monsters[name] = drawer.draw_card(name, entity['element'])
        monsters[name].extend(drawer.draw_tag(str(entity['health']), 'character'))
    logging.info('generated %d monsters (%s)',
                 len(monsters), list(monsters.keys()))
    maybe_create_dir(f'{args.output}/cards/monsters')
    for name, monster in monsters.items():
        # monster.save_svg(f'{args.output}/cards/monsters/{name}.svg')
        monster.save_png(f'{args.output}/cards/monsters/{name}.png')

    items = {}
    for name in world['items']:
        entity = world['items'][name]
        items[name] = drawer.draw_card(name, entity['element'])
        items[name].extend(drawer.draw_tag(
            entity['slot'][0].upper(), entity['slot']))
        items[name].extend(drawer.draw_effect(entity['effect']))
    logging.info('generated %d items (%s)', len(items), list(items.keys()))
    maybe_create_dir(f'{args.output}/cards/items')
    for name, item in items.items():
        # item.save_svg(f'{args.output}/cards/items/{name}.svg')
        item.save_png(f'{args.output}/cards/items/{name}.png')

    moves = {}
    for name in world['moves']:
        entity = world['moves'][name]
        moves[name] = drawer.draw_card(name, [])
        moves[name].extend(drawer.draw_tag(
            entity['effect']['type'][0].upper(), entity['effect']['type']))
        moves[name].extend(drawer.draw_effect(entity['effect']))
    logging.info('generated %d moves (%s)', len(moves), list(moves.keys()))
    maybe_create_dir(f'{args.output}/cards/moves')
    for name, move in moves.items():
        # move.save_svg(f'{args.output}/cards/moves/{name}.svg')
        move.save_png(f'{args.output}/cards/moves/{name}.png')
    
    events = {}
    for name in world['events']:
        entity = world['events'][name]
        events[name] = drawer.draw_card(name, [])
        events[name].extend(drawer.draw_tag(
            entity['effect']['type'][0].upper(), 'encounter'))
        events[name].extend(drawer.draw_effect(entity['effect']))
    logging.info('generated %d events (%s)', len(events), list(events.keys()))
    maybe_create_dir(f'{args.output}/cards/events')
    for name, move in events.items():
        # move.save_svg(f'{args.output}/cards/events/{name}.svg')
        move.save_png(f'{args.output}/cards/events/{name}.png')

    # # element match up charts
    # elements = pd.DataFrame(world['elements'])
    # # sns.heatmap(elements, linewidths=1, annot=True, cmap='RdBu_r')
    # # plt.savefig(f'{args.output}/cards/elements.pdf', bbox_inches='tight')
    # # plt.close()

    # element_chart = dot.Digraph()
    # for e1, res in elements.iterrows():
    #     element_chart.node(
    #         e1, fillcolor=ELEMENT_COLORS[e1], style='filled', shape='circle')
    #     for e2, res in res.items():
    #         if res != 2.0:
    #             continue
    #         element_chart.edge(e2, e1, color=MATCHUP_COLORS[int(res * 2)])
    # element_chart.render(f'{args.output}/cards/weakness-chart')

    # element_chart = dot.Digraph()
    # for e1, res in elements.iterrows():
    #     element_chart.node(
    #         e1, fillcolor=ELEMENT_COLORS[e1], style='filled', shape='circle')
    #     for e2, res in res.items():
    #         if res != 0.5:
    #             continue
    #         element_chart.edge(e2, e1, color=MATCHUP_COLORS[int(res * 2)])
    # element_chart.render(f'{args.output}/cards/resistance-chart')


if __name__ == '__main__':
    main()