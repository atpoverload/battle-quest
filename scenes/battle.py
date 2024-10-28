import json
import logging
import re

from argparse import ArgumentParser
from random import choice, shuffle

import pygame
import pygame_gui
import pygame_gui.elements.ui_button

from pygame.sprite import Sprite
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIProgressBar

from character import EMPTY_SLOT

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

all_sprites_list = pygame.sprite.Group()


def get_targets(target_kind, user, party, enemy):
    if target_kind == 'self':
        return [user]
    elif target_kind == 'other':
        return list((set(party) | set(enemy)) - set([user]))
    elif target_kind == 'ally':
        return party
    elif target_kind == 'enemy':
        return enemy


class FileSprite(Sprite):
    def __init__(self, file_path, relative_rect):
        super().__init__(all_sprites_list)

        self.image = pygame.image.load_sized_svg(
            file_path, relative_rect.size).convert()
        self.image.set_colorkey('#000000')
        self.rect = relative_rect


class ItemBattleButton(pygame_gui.elements.UIButton):
    def __init__(self, item, character, relative_rect, manager):
        super().__init__(
            relative_rect=relative_rect,
            text=item.name,
            tool_tip_text=item.description,
            object_id=ACTION_ID,
            manager=manager)
        self.item = item
        self.character = character
        self.action = item
        self.sprite = FileSprite(
            f'sprites/items/{self.item.name}.svg', relative_rect)


class HealthBar(UIProgressBar):
    def __init__(self, relative_rect, manager):
        super().__init__(relative_rect=relative_rect, manager=manager)

    def status_text(self):
        return ''


class CharacterBattleButton(pygame_gui.elements.UIButton):
    def __init__(self, character, relative_rect, manager):
        super().__init__(
            relative_rect=relative_rect,
            text=character.name,
            object_id=CHARACTER_ID,
            manager=manager)
        self.character = character


class ControlHealthBar(UIProgressBar):
    def __init__(self, character, relative_rect, manager):
        self.character = character
        super().__init__(relative_rect=relative_rect, manager=manager)

    def status_text(self):
        return f'{self.character.health} / {self.character.max_health}'


class CharacterBattlePanel:
    def __init__(self, character, origin, manager):
        self.character = CharacterBattleButton(
            character,
            pygame.Rect(origin, (200, 150)),
            manager)
        self.health_bar = HealthBar(
            relative_rect=pygame.Rect(
                (origin[0], origin[1] + 160), (200, 25)),
            manager=manager,
        )
        self.sprite = FileSprite(
            f'sprites/characters/{character.name.split("-")[0]}.svg',
            pygame.Rect(origin, (200, 150))
        )

    def enable(self):
        self.health_bar.percent_full = 100 * \
            self.character.character.health / self.character.character.max_health
        self.character.enable()

    def disable(self):
        self.health_bar.percent_full = 100 * \
            self.character.character.health / self.character.character.max_health
        self.character.disable()


class CharacterBattleControl:
    def __init__(self, character, origin, manager):
        self.items = []
        for i, item in enumerate(character.inventory.values()):
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
        self.health_bar = ControlHealthBar(
            character=character,
            relative_rect=pygame.Rect((origin[0], origin[1] - 35), (200, 25)),
            manager=manager,
        )
        self.sprite = FileSprite(
            f'sprites/characters/{character.name.split("-")[0]}.svg',
            pygame.rect.Rect(origin[0], origin[1] - 100, 200, 200)
        )
        colouredImage = pygame.Surface(self.sprite.image.get_size())
        colouredImage.fill(
            '#' + ''.join([choice('0123456789abcdef') for _ in range(6)]))

        finalImage = self.sprite.image.copy()
        finalImage.blit(colouredImage, (0, 0), special_flags=pygame.BLEND_MULT)
        self.sprite.image = finalImage

    def as_actor(self):
        [item.enable() if item.item != EMPTY_SLOT else item.disable()
         for item in self.items]
        [item.show() for item in self.items]
        self.character.disable()
        self.health_bar.percent_full = 100 * self.character.character.health / \
            self.character.character.max_health

    def as_target(self):
        [item.disable() for item in self.items]
        [item.hide() for item in self.items]
        self.character.enable()
        self.health_bar.percent_full = 100 * self.character.character.health / \
            self.character.character.max_health

    def disable(self):
        [item.disable() for item in self.items]
        [item.hide() for item in self.items]
        self.character.disable()
        self.health_bar.percent_full = 100 * self.character.character.health / \
            self.character.character.max_health


class BattleScene:
    def __init__(self, party, enemy, manager: pygame_gui.UIManager):
        self.manager = manager
        self.clock = pygame.time.Clock()

        self.party = party
        self.party_ui = [CharacterBattleControl(
            character,
            (250 * i + 50, 350),
            self.manager
        ) for i, character in enumerate(party)]

        self.enemy = enemy
        self.enemy_ui = [CharacterBattlePanel(
            character,
            (300, 25),
            self.manager
        ) for _, character in enumerate(enemy)]

        self.confirm_button = pygame_gui.elements.ui_button.UIButton(
            pygame.Rect((300, 225), (200, 50)),
            text='Confirm'
        )
        self.confirm_button.disable()
        self.confirm_button.hide()

        self.turn_order = []
        self.last_frame = 0
        self.selected = None
        self.actions = {member.name: None for member in self.party}

    def process(self, window_surface):
        if len(self.turn_order) > 0:
            [member.disable() for member in self.party_ui]
            [member.disable() for member in self.enemy_ui]
        elif self.selected is None:
            [member.as_actor() for member in self.party_ui]
            [member.disable() for member in self.enemy_ui]

        if len(self.turn_order) > 0 or any(e is None for e in self.actions.values()):
            self.confirm_button.disable()
            self.confirm_button.hide()
        else:
            self.confirm_button.enable()
            self.confirm_button.show()

        time_delta = self.clock.tick(60) / 1000.0
        self.last_frame += time_delta
        if len(self.turn_order) > 0 and self.last_frame > 1.00:
            # logs = []
            # for character in self.turn_order:
            #     selected, targets=self.actions[character.name]
            #     for target in targets:
            #         logs.extend(selected(character, target))
            # [logging.debug(log) for log in logs]

            character = self.turn_order.pop(0)
            selected, targets = self.actions[character.name]
            for target in targets:
                [logging.debug(log) for log in selected(character, target)]
            self.last_frame = 0

            if len(self.turn_order) == 0:
                for character in self.party + self.enemy:
                    character.is_defending = False
                self.turn_order = []
                self.actions = {member.name: None for member in self.party}

        all_sprites_list.draw(window_surface)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info('exiting')
                return False

            if len(self.turn_order) > 0:
                continue

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.confirm_button:
                logging.info('running the battle step')
                self.actions = {
                    k: (v[0].action, [c.character for c in v[1]]) for k, v in self.actions.items()}
                for enemy in self.enemy:
                    logging.debug('selecting enemy actions')
                    action = choice(enemy.moves)
                    if action.target == 'allies':
                        targets = self.enemy
                    elif action.target == 'enemies':
                        targets = self.party
                    else:
                        targets = [choice(
                            get_targets(action.target, enemy, self.enemy, self.party))]
                    logging.debug(
                        'targeting %s with %s\'s %s',
                        [target.name for target in targets],
                        enemy.name,
                        action.name
                    )
                    self.actions[enemy.name] = (action, targets)

                characters = self.party + self.enemy
                shuffle(characters)
                turn_order = {}
                for character in characters:
                    priority = character.priority + \
                        1000 * self.actions[character.name][0].priority
                    if priority not in turn_order:
                        turn_order[priority] = []
                    turn_order[priority].append(character)
                characters = []
                for priority in sorted(turn_order.keys(), reverse=True):
                    characters.extend(turn_order[priority])
                self.turn_order = characters

                logging.debug(
                    'turn order: %s',
                    [character.name for character in self.turn_order]
                )

                # logs=[]
                # for character in characters:
                #     selected, targets=self.actions[character.name]
                #     for target in targets:
                #         logs.extend(selected(character, target))
                # [logging.debug(log) for log in logs]
                # for character in characters:
                #     character.is_defending = False
                # self.actions = {member.name: None for member in self.party}

                self.last_frame = 0.50

            else:
                if self.selected is None and event.type == pygame_gui.UI_BUTTON_PRESSED and isinstance(event.ui_element, ItemBattleButton):
                    logging.debug(
                        'user selected %s\'s %s', event.ui_element.character.name, event.ui_element.item.name)
                    if event.ui_element.item == EMPTY_SLOT:
                        logging.debug(
                            'ignoring selection of %s\'s %s since it has no action',
                            event.ui_element.character.name,
                            event.ui_element.item.name
                        )
                    elif self.actions[event.ui_element.character.name] is not None:
                        logging.debug(
                            'overriding %s selection for %s',
                            self.actions[event.ui_element.character.name][0].item.name,
                            event.ui_element.character.name
                        )
                        self.actions[event.ui_element.character.name] = None

                    if event.ui_element.item != EMPTY_SLOT:
                        self.selected = event.ui_element
                        logging.debug(
                            'start targeting for %s\'s %s', self.selected.character.name, self.selected.item.name)
                        if self.selected.action.target == 'allies':
                            self.actions[self.selected.character.name] = (
                                self.selected, self.party)
                        elif self.selected.action.target == 'enemies':
                            self.actions[self.selected.character.name] = (
                                self.selected, self.enemy)
                        else:
                            targets = get_targets(
                                self.selected.action.target, self.selected.character, self.party, self.enemy)
                            logging.debug(
                                'available targets: %s',
                                [target.name for target in targets]
                            )
                            [member.as_target() if member.character.character in targets else member.disable(
                            ) for member in self.party_ui]
                            [member.enable() if member.character.character in targets else member.disable()
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
                    self.actions[self.selected.character.name] = (
                        self.selected, targets)
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
        if len(self.turn_order) == 0:
            for _, action in self.actions.items():
                if action is not None:
                    action, targets = action
                    for target in targets:
                        start = pygame.Vector2(
                            action.get_relative_rect().center)
                        stop = pygame.Vector2(
                            target.get_relative_rect().center)
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
