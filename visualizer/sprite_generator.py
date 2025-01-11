""" A cellular automata sprite generator based on https://www.davebollinger.us/pixelspaceships """
import logging

from argparse import ArgumentParser
from colorsys import hsv_to_rgb
from copy import deepcopy
from math import sqrt
from itertools import product
from random import choice, seed

import PIL.Image
import yaml

from util import display_world_info

PHI = (1 + sqrt(5)) / 2


def manhattan_distance(x, y, i, j):
    return abs(x - i) + abs(y - j)


def euclidean_distance(x, y, i, j):
    return sqrt((x - i) * (x - i) + (y - j) * (y - j))


def nearest_neighbors(x, y, metric, depth):
    """ Finds all points on the grid within some distance of a central point. """
    neighbors = []
    for i, j in product(range(x - depth, x + depth + 1), range(y - depth, y + depth + 1)):
        if metric(x, y, i, j) <= depth:
            neighbors.append([i, j])
    return neighbors


def mutate(sprite, metric=manhattan_distance, depth=1):
    """
    Iterates through all cells in a matrix and uses the nearest
    neighbors to determine if a cell should transform into another kind
    of cell. This implementation randomly chooses to transform into one of
    the cells in a fixed-size neighborhood computed from some distance metric.
    """
    new_sprite = deepcopy(sprite)
    m, n = len(sprite), len(sprite[0])
    for x, y in product(range(m), range(n)):
        # fixed (i.e. negative) and empty (i.e. zero) cells cannot be transformed
        if sprite[x][y] < 1:
            continue

        # get all neighbors that are on the grid
        neighbors = nearest_neighbors(x, y, metric, depth)
        neighbors = [[i, j] for i, j in neighbors if 0 <= i < m and 0 <= j < n]

        # filter away empty cells if we are not on an edge
        cell_neighbors = nearest_neighbors(x, y, manhattan_distance, 1)
        cell_neighbors = [
            [i, j] for i, j in cell_neighbors if 0 <= i < m and 0 <= j < n]
        is_edge = any([sprite[i][j] == 0 for i, j in cell_neighbors])
        if not is_edge:
            neighbors = [[i, j] for i, j in neighbors if sprite[i][j] != 0]

        i, j = choice(neighbors)
        new_sprite[x][y] = sprite[i][j]
    return new_sprite


def inner_outline(sprite, border=None):
    """
    Iterates through all cells in a matrix and determines whether a given filled
    cell on the border of the sprite (i.e. next to empty space). If it is, its value
    becomes the border value, which is either provided or derived as a unique fixed value
    """
    if border is None:
        border = min(pixel for row in sprite for pixel in row) - 1
    new_sprite = deepcopy(sprite)
    m, n = len(sprite), len(sprite[0])
    for x, y in product(range(m), range(n)):
        # we only draw along the inner space
        if sprite[x][y] == 0:
            continue

        neighbors = nearest_neighbors(x, y, manhattan_distance, 1)
        neighbors = [[i, j] for i, j in neighbors if 0 <= i < m and 0 <= j < n]

        # for i, j in neighbors:
        #     if sprite[i][j] == 0:
        #         new_sprite[x][y] = border
        #         break

        # TODO: this seems to work the best?
        is_border = sum([sprite[i][j] == 0 for i, j in neighbors]) >= 1
        if is_border:
            new_sprite[x][y] = border
    return new_sprite


def draw_sprite(sprite, palettes, mirror=False, rescaling=16):
    m, n = len(sprite), len(sprite[0])
    if mirror:
        sprite_r = [pixel[::-1] for pixel in sprite]
        N = 2 * n
    else:
        N = n
    image = PIL.Image.new(mode='RGBA', size=(N, m))
    for x, y in product(range(m), range(N)):
        if mirror and y >= N // 2:
            val = sprite_r[x][y - N // 2]
        else:
            val = sprite[x][y]
        if val != 0:
            palette = palettes[val]
            if isinstance(palette, tuple):
                # if it's a tuple, assume it's actually a color
                image.putpixel((y, x), palette)
            else:
                # otherwise assume it's a grid of colors
                image.putpixel((y, x), palette[x][y])
    image = image.resize(
        (rescaling * N, rescaling * m),
        PIL.Image.Resampling.NEAREST
    )
    return image


# TODO: this is a horrible way to do this. the world should specify the palette
def create_palette(
    hue,
    sat,
    val,
    alpha,
    m,
    n,
):
    palette = [[(*map(int, hsv_to_rgb(
        hue(i, j),
        sat(i, j),
        val(i, j)
    )), alpha(i, j)) for i in range(n)] for j in range(m)]
    return palette


COCKPIT = create_palette(
    lambda x, y: 0.50 - (y - 6) / 12 / 12,
    lambda x, y: 0.60 -
    sqrt(abs((x - 6) * (x - 6) + (y - 6) * (y - 6))) / 12 / 2,
    lambda x, y: 200 - 12 * (y - 6),
    lambda x, y: 255,
    12,
    12,
)


def create_ship_palette(hue):
    b_hue = (hue + 1 / PHI) % 1
    c_hue = (hue + 0.5) % 1
    cb_hue = (c_hue + 1 / PHI) % 1
    return {
        -100: COCKPIT,
        1: create_palette(
            lambda x, y: hue - sqrt((x - 6) * (x - 6) +
                                    (y - 6) * (y - 6)) / 12 / 4,
            lambda x, y: 0.75 -
            sqrt(abs((x - 6) * (x - 6) + (y - 6) * (y - 6))) / 12 / 2,
            lambda x, y: 220 - 12 * abs(y - 6),
            lambda x, y: 255,
            12,
            12,
        ),
        -1: create_palette(
            lambda x, y: hue - abs(y - 6) / 12 / 12 / 2,
            lambda x, y: 0.25 +
            sqrt(abs((x - 6) * (x - 6) + (y - 6) * (y - 6))) / 12 / 2,
            lambda x, y: 150 + 6 * (y - 6),
            lambda x, y: 255,
            12,
            12,
        ),
        # -1: (0, 0, 0, 255),
        2: create_palette(
            lambda x, y: c_hue - (y - 6) / 12 / 12,
            lambda x, y: 0.50 -
            sqrt(abs((x - 6) * (x - 6) + (y - 6) * (y - 6))) / 12 / 2,
            lambda x, y: 175 - 12 * abs(y - 6),
            lambda x, y: 255,
            12,
            12,
        ),
        -2: create_palette(
            lambda x, y: c_hue - (y - 6) / 12 / 12,
            lambda x, y: 0.40 -
            sqrt(abs((x - 6) * (x - 6) + (y - 6) * (y - 6))) / 12 / 2,
            lambda x, y: 150 - 12 * abs(y - 6),
            lambda x, y: 255,
            12,
            12,
        ),
    }


def parse_args():
    args = ArgumentParser()
    args.add_argument('-w', '--world', type=str)
    args.add_argument('-o', '--output', type=str)
    return args.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        format='battle-quest-visualizer-sprite_generator (%(asctime)s) [%(levelname)s]: %(message)s',
        level=logging.INFO
    )

    logging.info('loading template from %s', args.world)
    with open(args.world, encoding='utf8') as f:
        world = yaml.load(f, yaml.Loader)

    display_world_info(world)

    if 'visualizer' not in world or 'sprite_generator' not in world['visualizer']:
        logging.info('no sprite generator options found')
        return

    options = world['visualizer']['sprite_generator']
    if 'seed' in options:
        logging.info('setting seed to %d', options['seed'])
        seed(options['seed'])

    templates = {}
    for template in options['template']:
        with open(options['template'][template], encoding='utf8') as f:
            templates[template] = [[
                int(value) for value in line.strip().split(' ') if value.lstrip('-').isdigit()
            ] for line in f.readlines()]

    palettes = {}
    for palette in options['palette']:
        palettes[palette] = create_ship_palette(
            options['palette'][palette]['hue'])
        # with open(options['template'][template], encoding='utf8') as f:
        #     templates[template] = [[
        #         int(value) for value in line.strip().split(' ') if value.lstrip('-').isdigit()
        #     ] for line in f.readlines()]

    # TODO: much of this needs to live in the config
    # palettes = {
    #     'fighter': create_ship_palette(0.20),
    #     'scout': create_ship_palette(0.40),
    #     'carrier': create_ship_palette(0.60),
    #     'station': create_ship_palette(0.80),
    # }

    # form = [
    #     'fighter',
    #     'scout',
    #     'carrier',
    #     'station',
    # ]

    species = list(templates.keys())
    form = list(palettes.keys())

    for n, character in enumerate(world['entities']['character']):
        s = [element for element in character['element'] if element in species][0]
        template = templates[s]
        f = [element for element in character['element'] if element in form][0]
        palette = palettes[f]
        seed(hash(tuple([character['name']] + character['element'])))
        sprite = inner_outline(
            mutate(template, depth=species.index(s) + 1), border=-1)
        image = draw_sprite(sprite, palette, mirror=True, rescaling=16)
        image.save(f'{args.output}/{character['name']}.png')

    logging.info('wrote %d random sprites to %s', n, args.output)


if __name__ == '__main__':
    main()
