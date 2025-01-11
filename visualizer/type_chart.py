""" A tool that draws the type relationships as a heatmap. """
import logging

from argparse import ArgumentParser
from colorsys import hsv_to_rgb
from copy import deepcopy
from math import sqrt
from itertools import product
from random import choice, seed

import matplotlib.pyplot as plt
import pandas as pd
import PIL.Image
import yaml

from seaborn import heatmap

from util import display_world_info

def parse_args():
    args = ArgumentParser()
    args.add_argument('-w', '--world', type=str)
    args.add_argument('-o', '--output', type=str)
    return args.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        format='battle-quest-visualizer-type_chart (%(asctime)s) [%(levelname)s]: %(message)s',
        level=logging.INFO
    )

    logging.info('loading template from %s', args.world)
    with open(args.world, encoding='utf8') as f:
        world = yaml.load(f, yaml.Loader)

    display_world_info(world)

    affinities = pd.DataFrame(data=world['properties']['element']['affinity'])
    affinities.columns = list(map(lambda s: s.title(), affinities.columns))
    affinities.index = list(map(lambda s: s.title(), affinities.index))    
    
    fig, ax = plt.subplots(figsize=(5, 5))
    heatmap(
        affinities,
        linewidths=2,
        cmap=['tab:blue', 'tab:green', 'tab:red'],
        annot=True,
        fmt="1.1f",
        cbar=False,
        ax=ax
    )
    plt.savefig(args.output, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    main()
