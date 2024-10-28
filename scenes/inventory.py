import json
import logging
import re

from argparse import ArgumentParser
from random import choice, shuffle

import pygame
import pygame_gui
import pygame_gui.elements.ui_button

from pygame_gui.core import ObjectID

import scenes.ui as bqui

# from world import WorldManager

ACTION_ID = ObjectID(
    class_id='@action_button',
    object_id='#action_button'
)


CHARACTER_ID = ObjectID(
    class_id='@character_button',
    object_id='#character_button'
)


def get_users(item, party):
    if target_kind == 'self':
        return user
    elif target_kind == 'other':
        return list((set(party) | set(enemy)) - set([user]))
    elif target_kind == 'ally':
        return party
    elif target_kind == 'enemy':
        return enemy


class ItemBattleButton(pygame_gui.elements.UIButton):
    def __init__(self, item, character, relative_rect, manager):
        super().__init__(
            relative_rect=relative_rect,
            text=item.item['name'],
            tool_tip_text=item.item['description'],
            object_id=ACTION_ID,
            manager=manager)
        self.item = item
        self.character = character
        self.action = item.action


class CharacterBattleButton(pygame_gui.elements.UIButton):
    def __init__(self, character, relative_rect, manager):
        super().__init__(
            relative_rect=relative_rect,
            text=character.name,
            object_id=CHARACTER_ID,
            manager=manager)
        self.character = character


class CharacterBattlePanel:
    def __init__(self, character, origin, manager):
        CharacterBattleButton(
            character,
            pygame.Rect(origin, (200, 200)),
            manager)


class CharacterBattleControl:
    def __init__(self, character, origin, manager):
        self.items = []
        for i, item in enumerate(character.items.values()):
            self.items.append(ItemBattleButton(
                item,
                character,
                pygame.Rect(
                    (origin[0] + 75 * (i % 2), origin[1] + 75 * (i / 2)),
                    (75, 75)),
                manager))
        self.character = CharacterBattleButton(
            character,
            pygame.Rect(origin, (200, 200)),
            manager)

    def as_actor(self):
        [item.enable() for item in self.items]
        [item.show() for item in self.items]
        self.character.disable()

    def as_target(self):
        [item.disable() for item in self.items]
        [item.hide() for item in self.items]
        self.character.enable()

    def disable(self):
        [item.disable() for item in self.items]
        [item.hide() for item in self.items]
        self.character.disable()


class InventoryScene:
    def __init__(self, party, enemy, manager):
        self.manager = manager
        self.clock = pygame.time.Clock()

        self.party = party
        self.party_ui = [CharacterBattleControl(
            character,
            (250 * i + 100, 300),
            self.manager
        ) for i, character in enumerate(party)]

        self.enemy = enemy
        self.enemy_ui = [CharacterBattleButton(
            character,
            pygame.Rect((350, 100), (200, 200)),
            self.manager
        ) for _, character in enumerate(enemy)]

        self.confirm_button = pygame_gui.elements.ui_button.UIButton(
            (100, 200),
            text='Confirm'
        )
        self.confirm_button.disable()

        self.selected = None
        self.actions = {member.name: None for member in self.party}

    def process(self, window_surface):
        if self.selected is None:
            [member.as_actor() for member in self.party_ui]
            [member.disable() for member in self.enemy_ui]

        if any(e is None for e in self.actions.values()):
            self.confirm_button.disable()
        else:
            self.confirm_button.enable()

        time_delta = self.clock.tick(60) / 1000.0
        # if len(log) > 0 and time_delta > 0.50:
        #     message = log.pop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info('exiting')
                return False

            # if message is not None and event.type == pygame.MOUSEBUTTONDOWN:
            #     pass

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.confirm_button:
                logging.info('running the battle step')
                for e in self.enemy:
                    logging.debug('selecting enemy actions')
                    action = choice(e.species['monster']['actions'])
                    if action == 'attack':
                        target = choice(self.party)
                    targets = choice(get_targets(
                        action['target'], e, self.enemy, self.party))
                    logging.debug(
                        'targeting %s with %s\'s %s',
                        targets,
                        e.name,
                        action['name']
                    )
                    self.actions[e.name] = (action, choice(targets))
                turn_order = self.party + self.enemy
                shuffle(turn_order)
                logging.debug(
                    'turn order: %s',
                    [character.name for character in turn_order]
                )
                for character in turn_order:
                    self.selected, targets = self.actions[character.name]
                    self.selected.action(character, targets)
                # log = []
                self.actions = {member.name: None for member in self.party}

            else:
                if self.selected is None and event.type == pygame_gui.UI_BUTTON_PRESSED and isinstance(event.ui_element, ItemBattleButton):
                    logging.debug(
                        'user selected %s\'s %s', event.ui_element.character.name, event.ui_element.item.name)
                    if event.ui_element.item.action is None:
                        logging.debug(
                            'ignoring selection of %s\'s %s since it has no action',
                            event.ui_element.character.name,
                            event.ui_element.item.name
                        )
                    elif self.actions[event.ui_element.character.name] is not None:
                        logging.debug(
                            'overriding %s selection for %s',
                            self.actions[event.ui_element.character.name]['action'].item.name,
                            event.ui_element.character.name
                        )
                        self.actions[event.ui_element.character.name] = None

                    if event.ui_element.item.action is not None:
                        self.selected = event.ui_element
                        logging.debug(
                            'start targeting for %s\'s %s', self.selected.character.name, self.selected.item.name)
                        targets = get_targets(
                            self.selected.action['target'], self.selected.character, self.party, self.enemy)
                        logging.debug(
                            'available targets: %s',
                            [target.name for target in targets]
                        )
                        [member.as_target() if member.character.character in targets else member.disable(
                        ) for member in self.party_ui]
                        [member.enable() if member.character in targets else member.disable()
                            for member in self.enemy_ui]
                        self.selected.show()
                elif self.selected is not None and event.type == pygame_gui.UI_BUTTON_PRESSED and isinstance(event.ui_element, CharacterBattleButton):
                    logging.debug(
                        'targeting %s with %s\'s %s',
                        event.ui_element.character.name,
                        self.selected.character.name,
                        self.selected.item.name
                    )
                    targets = [event.ui_element]
                    self.actions[self.selected.character.name] = {
                        'action': self.selected,
                        'targets': targets
                    }
                    self.selected = None

                if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    if self.selected is not None:
                        logging.debug('cancelled %s\'s %s targeting',
                                      self.selected.character.name, self.selected.item.name)
                        self.selected = None
                    elif any(e is not None for e in self.actions.values()):
                        logging.debug('cancelled all targeted actions')
                        self.actions = {
                            member.name: None for member in self.party}

            self.manager.process_events(event)

        self.manager.update(time_delta)
        self.manager.draw_ui(window_surface)

        if self.selected is not None:
            center = pygame.Vector2(self.selected.get_relative_rect().center)
            end = pygame.Vector2(pygame.mouse.get_pos())
            bqui.draw_arrow(
                window_surface,
                center,
                end,
                pygame.Color('tomato2'),
                10,
                20,
                12
            )
        for _, action in self.actions.items():
            if action is not None:
                action, targets = action.values()
                for target in targets:
                    start = pygame.Vector2(action.get_relative_rect().center)
                    stop = pygame.Vector2(target.get_relative_rect().center)
                    stop = start.move_towards(
                        stop, 0.90 * start.distance_to(stop))
                    bqui.draw_arrow(
                        window_surface,
                        start,
                        stop,
                        pygame.Color('dodgerblue'),
                        10,
                        20,
                        12
                    )

        pygame.display.update()
        return True
