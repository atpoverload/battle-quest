import logging
import os

from argparse import ArgumentParser

import drawsvg as draw
import yaml

# used for the element match up charts
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import graphviz as dot


class VerticalCardDrawer:
    def __init__(self, card_dims, colors, fonts, resources):
        self.card_dims = card_dims
        self.colors = colors
        self.fonts = fonts
        self.resources = resources

        self.card_size = (
            self.card_dims['card_width'], self.card_dims['card_height'])
        self.sprite_width = self.card_dims['sprite_width']
        self.sprite_height = self.card_dims['sprite_height']
        self.element_width = self.card_dims['element_width']
        self.element_height = self.card_dims['element_height']
        self.effect_width = self.card_dims['effect_width']
        self.effect_height = self.card_dims['effect_height']

        self.margin = self.card_dims['margin']
        self.center = (self.card_size[0] / 2, self.card_size[1] / 2)
        self.sprite_pos = (
            self.center[0] - self.sprite_width / 2,
            self.fonts['name_size'] + self.margin
        )
        self.elements_y = self.sprite_pos[1] + self.sprite_height + self.margin
        self.effect_pos = (self.margin,
                           self.elements_y + self.element_height + 2 * self.margin)

    def draw(self, name, elements):
        d = draw.Drawing(*self.card_size, origin='top-left')
        d.append(self.draw_background())
        d.embed_google_font(self.fonts['font_family'])
        d.append(self.draw_name(name.title()))
        d.append(self.draw_sprite(name))
        d.extend(self.draw_elements(elements))
        return d

    def draw_background(self):
        return draw.Rectangle(0, 0, *self.card_size, fill=self.colors['background'])

    def draw_name(self, name):
        return draw.Text(
            name,
            x=self.margin,
            y=0,
            font_size=self.fonts['name_size'],
            text_anchor='start',
            dominant_baseline='hanging',
            font_family=self.fonts['font_family']
        )

    def draw_tag(self, value, kind):
        l = []
        l.append(draw.Rectangle(
            x=self.card_size[0] - self.effect_width -
                (len(str(value)) - 1) * (2 * self.margin + 10),
            y=-15,
            width=2 * self.effect_width,
            height=self.effect_height + self.margin + 10,
            fill=self.colors['tag_colors'][kind],
            stroke='black',
            stroke_width=4,
            rx=20,
        ))
        l.append(draw.Text(
            f'{value}',
            x=self.card_size[0] - self.margin,
            y=0,
            font_size=self.fonts['effect_size'],
            text_anchor='end',
            dominant_baseline='hanging',
            font_family=self.fonts['font_family']
        ))
        return l

    def draw_sprite(self, sprite):
        return draw.Image(
            *self.sprite_pos,
            self.sprite_width,
            self.sprite_height,
            path=self.get_sprite(sprite),
            embed=True,
        )

    def draw_elements(self, elements):
        l = []
        element_count = len(elements)
        for i, element in enumerate(elements):
            x = self.center[0] + self.element_width * (i - element_count / 2)
            l.append(
                draw.Image(
                    x=x,
                    y=self.elements_y,
                    width=self.element_width,
                    height=self.element_height,
                    path=self.get_sprite(element),
                    embed=True,
                )
            )
        return l

    def draw_effect(self, effect):
        l = []
        target = effect['target'] if 'target' in effect else ''
        if effect['type'] == 'attack':
            message = f"Deal {effect['value']}"
            l.append(draw.Text(
                message,
                x=self.effect_pos[0] + self.margin,
                y=self.effect_pos[1],
                font_size=self.fonts['effect_size'],
                text_anchor='start',
                dominant_baseline='hanging',
            ))
            l.append(draw.Image(
                x=self.card_size[0] - self.margin - self.effect_width,
                y=self.effect_pos[1] + 5,
                width=self.effect_width,
                height=self.effect_height,
                path=self.get_sprite(effect['element']),
                embed=True,
            ))
        elif effect['type'] == 'condition':
            l.append(draw.Text(
                f"Apply {effect['value']}",
                x=self.center[0],
                y=self.effect_pos[1],
                font_size=self.fonts['effect_size'],
                text_anchor='middle',
                dominant_baseline='hanging',
            ))
            # l.append(draw.Image(
            #     x=self.card_size[0] - self.margin - self.effect_width,
            #     y=self.effect_pos[1] + 5,
            #     width=self.effect_width,
            #     height=self.effect_height,
            #     path=self.get_sprite(effect['value']),
            #     embed=True,
            # ))
        elif effect['type'] == 'heal':
            l.append(draw.Text(
                f"Heal {effect['value']}",
                x=self.center[0],
                y=self.effect_pos[1],
                font_size=self.fonts['effect_size'],
                text_anchor='middle',
                dominant_baseline='hanging',
            ))
        elif effect['type'] == 'defense':
            l.append(draw.Text(
                'Gain',
                x=self.effect_pos[0] + self.margin,
                y=self.effect_pos[1],
                font_size=self.fonts['effect_size'],
                text_anchor='start',
                dominant_baseline='hanging',
            ))
            l.append(draw.Image(
                x=self.effect_pos[0] + 2.75 * self.effect_width,
                y=self.effect_pos[1] + 5,
                width=self.effect_width,
                height=self.effect_height,
                path=self.get_sprite(effect['element']),
                embed=True,
            ))
        return l

    def get_sprite(self, name):
        return os.path.join(
            self.resources,
            f'{name}.svg'
        )


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

    adventurers = {}
    for name in world['adventurers']:
        entity = world['adventurers'][name]
        adventurers[name] = drawer.draw(name, entity['element'])
        adventurers[name].extend(
            drawer.draw_tag(entity['health'], 'character'))
    logging.info('generated %d adventurers (%s)',
                 len(adventurers), list(adventurers.keys()))
    maybe_create_dir(f'{args.output}/adventurers')
    for name, adventurer in adventurers.items():
        # adventurer.save_svg(f'{args.output}/adventurers/{name}.svg')
        adventurer.save_png(f'{args.output}/adventurers/{name}.png')

    monsters = {}
    for name in world['monsters']:
        entity = world['monsters'][name]
        monsters[name] = drawer.draw(name, entity['element'])
        monsters[name].extend(drawer.draw_tag(entity['health'], 'character'))
    logging.info('generated %d monsters (%s)',
                 len(monsters), list(monsters.keys()))
    maybe_create_dir(f'{args.output}/monsters')
    for name, monster in monsters.items():
        # monster.save_svg(f'{args.output}/monsters/{name}.svg')
        monster.save_png(f'{args.output}/monsters/{name}.png')

    items = {}
    for name in world['items']:
        entity = world['items'][name]
        items[name] = drawer.draw(name, entity['element'])
        items[name].extend(drawer.draw_tag(
            entity['slot'][0].upper(), entity['slot']))
        items[name].extend(drawer.draw_effect(entity['effect']))
    logging.info('generated %d items (%s)', len(items), list(items.keys()))
    maybe_create_dir(f'{args.output}/items')
    for name, item in items.items():
        # item.save_svg(f'{args.output}/items/{name}.svg')
        item.save_png(f'{args.output}/items/{name}.png')

    moves = {}
    for name in world['moves']:
        entity = world['moves'][name]
        moves[name] = drawer.draw(name, [])
        moves[name].extend(drawer.draw_tag(
            entity['effect']['type'][0].upper(), entity['effect']['type']))
        moves[name].extend(drawer.draw_effect(entity['effect']))
    logging.info('generated %d moves (%s)', len(moves), list(moves.keys()))
    maybe_create_dir(f'{args.output}/moves')
    for name, move in moves.items():
        # move.save_svg(f'{args.output}/moves/{name}.svg')
        move.save_png(f'{args.output}/moves/{name}.png')

    # # element match up charts
    # elements = pd.DataFrame(world['elements'])
    # # sns.heatmap(elements, linewidths=1, annot=True, cmap='RdBu_r')
    # # plt.savefig(f'{args.output}/elements.pdf', bbox_inches='tight')
    # # plt.close()

    # element_chart = dot.Digraph()
    # for e1, res in elements.iterrows():
    #     element_chart.node(
    #         e1, fillcolor=ELEMENT_COLORS[e1], style='filled', shape='circle')
    #     for e2, res in res.items():
    #         if res != 2.0:
    #             continue
    #         element_chart.edge(e2, e1, color=MATCHUP_COLORS[int(res * 2)])
    # element_chart.render(f'{args.output}/weakness-chart')

    # element_chart = dot.Digraph()
    # for e1, res in elements.iterrows():
    #     element_chart.node(
    #         e1, fillcolor=ELEMENT_COLORS[e1], style='filled', shape='circle')
    #     for e2, res in res.items():
    #         if res != 0.5:
    #             continue
    #         element_chart.edge(e2, e1, color=MATCHUP_COLORS[int(res * 2)])
    # element_chart.render(f'{args.output}/resistance-chart')


if __name__ == '__main__':
    main()
