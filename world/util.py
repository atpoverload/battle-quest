import logging

from pprint import pformat

def display_world_info(world):
    logging.basicConfig(
        format='battle-quest-world-util (%(asctime)s) [%(levelname)s]: %(message)s',
        level=logging.DEBUG
    )
    
    logging.info(f'information for {world["name"]} world')

    logging.info('elements:\n' + pformat(world['properties']['element']['group']))
    
    logging.info('conditions:\n' + pformat(world['properties']['condition']['group']))

    logging.info('actions:\n' + pformat(world['properties']['action']['values']))
    
    logging.info('abilities:\n' + pformat(world['properties']['ability']['values']))
