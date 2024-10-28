class Character:
    @property
    def health(self):
        raise NotImplementedError(f'no health for unimplemented character')

    @property
    def element(self):
        raise NotImplementedError(f'no element for unimplemented character')

    @property
    def is_defending(self):
        raise NotImplementedError(f'no defending for unimplemented character')

    @property
    def condition(self):
        raise NotImplementedError(f'no condition for unimplemented character')

    @property
    def priority(self):
        raise NotImplementedError(f'no priority for unimplemented character')

    @property
    def max_health(self):
        raise NotImplementedError(f'no max health for unimplemented character')

    @health.setter
    def health(self, value: int):
        raise NotImplementedError(
            f'no changing health for unimplemented character')

    @condition.setter
    def condition(self, value: str):
        raise NotImplementedError(
            f'no changing status for unimplemented character')

    @is_defending.setter
    def is_defending(self, value: bool):
        raise NotImplementedError(
            f'no changing is_defending for unimplemented character')


def flat_damage(user: Character, target: Character, value: int):
    if not target.is_defending:
        target.health -= value
        return [f'{target.name} is dealt {value} damage']
    else:
        return [f'{target.name} blocked the attack']


def elemental_damage(user: Character, target: Character, element: str, value: int):
    if not target.is_defending():
        target.health -= value
        return [f'{target.name} is dealt {value} damage']
    else:
        return [f'{target.name} blocked the attack']


def heal(user: Character, target: Character, value: int):
    target.health += value
    return [f'{target.name} is healed for {value}']


def defend(user: Character, target: Character):
    target.is_defending = True
    return [f'{target.name} is defending']


def apply_condition(user: Character, target: Character, condition: str):
    target.status = condition
    return [f'{target.name} has {condition}']


class _EmptySlot:
    def __init__(self):
        self.name = 'empty'
        self.description = 'an empty inventory slot'

    @property
    def slot(self):
        raise NotImplementedError(f'no slot for empty slot')

    @property
    def target(self):
        raise NotImplementedError(f'no target for empty slot')

    def __call__(self, user: Character, target: Character):
        raise NotImplementedError(f'no call for empty slot')


EMPTY_SLOT = _EmptySlot()


class DictAction:
    def __init__(self, action: dict[str, str]):
        self.action = action
        self.name = action['name']
        self.description = action['description']
        self.target = action['target']
        self.priority = action['priority']


class DictItem(DictAction):
    def __init__(self, item: dict[str, str]):
        super().__init__(item)
        self.slot = item['slot']


class FlatAttackItem(DictItem):
    def __init__(self, item: dict[str, str]):
        super().__init__(item)
        self.value = item['attack']['value']

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + flat_damage(user, target, self.value)


class ElementalAttackItem(DictItem):
    def __init__(self, item: dict[str, str]):
        super().__init__(item)
        self.element = item['attack']['element']
        self.value = item['attack']['value']
        self.target = item['attack']['target']

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + elemental_damage(user, target, self.element, self.value)


class HealingItem(DictItem):
    def __init__(self, item: dict[str, str]):
        super().__init__(item)
        self.value = item['heal']['value']
        self.target = item['heal']['target']

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + heal(user, target, self.value)


class DefendingItem(DictItem):
    def __init__(self, item: dict[str, str]):
        super().__init__(item)

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + defend(user, target)


class ApplyConditionItem(DictItem):
    def __init__(self, item: dict[str, str]):
        super().__init__(item)
        self.condition = item['status']['condition']

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + apply_condition(user, target, self.condition)


def new_item(item: dict[str, str]):
    if 'attack' in item:
        if item['attack']['type'] == 'flat':
            return FlatAttackItem(item)
        elif item['attack']['type'] == 'elemental':
            return ElementalAttackItem(item)
    elif 'heal' in item:
        return HealingItem(item)
    elif 'defend' in item:
        return DefendingItem(item)
    elif 'status' in item:
        return ApplyConditionItem(item)
    else:
        raise ValueError(
            'no supported action found for {} ({})'.format(
                item['name'],
                item.keys()
            ))


def new_status():
    return {
        'health': 0,
        'defending': False,
        'condition': None,
    }


def new_inventory():
    return {
        'mainhand': EMPTY_SLOT,
        'offhand': EMPTY_SLOT,
        'trinket1': EMPTY_SLOT,
        'trinket2': EMPTY_SLOT,
        'trinket3': EMPTY_SLOT,
    }


class StatusCharacter(Character):
    def __init__(self, name):
        self.name = name
        self.status = new_status()

    @property
    def health(self):
        return self.status['health']

    @property
    def condition(self):
        return self.status['condition']

    @property
    def is_defending(self):
        return self.status['defending']

    @health.setter
    def health(self, value: int):
        self.status['health'] = min(max(0, value), self.max_health)

    @condition.setter
    def condition(self, value):
        self.status['condition'] = value

    @is_defending.setter
    def is_defending(self, value: bool):
        self.status['defending'] = value

    def refresh(self):
        self.health = self.max_health
        self.is_defending = False
        self.condition = None


class Adventurer(StatusCharacter):
    def __init__(self, name, vocation: dict[str, str]):
        super().__init__(name)
        self.vocation = vocation
        self.allowed_items = self.vocation['items']

        self.inventory = new_inventory()

    @property
    def element(self):
        return None

    @property
    def priority(self):
        return 0

    @property
    def max_health(self):
        return self.vocation['health']


class DictMove(DictAction):
    def __init__(self, move: dict[str, str]):
        super().__init__(move)


class FlatAttackMove(DictMove):
    def __init__(self, move: dict[str, str]):
        super().__init__(move)
        self.value = move['attack']['value']

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + flat_damage(user, target, self.value)


class ElementalAttackMove(DictMove):
    def __init__(self, move: dict[str, str]):
        super().__init__(move)
        self.element = move['attack']['element']
        self.value = move['attack']['value']

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + elemental_damage(user, target, self.element, self.value)


class HealingMove(DictMove):
    def __init__(self, move: dict[str, str]):
        super().__init__(move)
        self.value = move['heal']['value']

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + heal(user, target, self.value)


class DefendingMove(DictMove):
    def __init__(self, move: dict[str, str]):
        super().__init__(move)

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + defend(user, target)


class ApplyConditionMove(DictMove):
    def __init__(self, move: dict[str, str]):
        super().__init__(move)
        self.condition = move['status']['condition']

    def __call__(self, user: Character, target: Character):
        return [f'{user.name} uses {self.name}'] + apply_condition(user, target, self.condition)


def new_move(move: dict[str, str]):
    if 'attack' in move:
        if move['attack']['type'] == 'flat':
            return FlatAttackMove(move)
        elif move['attack']['type'] == 'elemental':
            return ElementalAttackMove(move)
    elif 'heal' in move:
        return HealingMove(move)
    elif 'defend' in move:
        return DefendingMove(move)
    elif 'status' in move:
        return ApplyConditionMove(move)
    else:
        raise ValueError(
            'no supported action found for {} ({})'.format(
                move['name'],
                move.keys()
            ))


class Monster(StatusCharacter):
    def __init__(self, name, species):
        super().__init__(name)

        self.species = species

        self._level = 0
        self._max_health = 0
        self.moves = []

        self.level = 1

    @property
    def priority(self):
        return 0

    @property
    def element(self):
        return self.species['element']

    @property
    def max_health(self):
        return self._max_health

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        gained = value - self._level
        self._max_health += gained * self.species['health']
        new_moves = [move for moves in map(lambda i: i[1], filter(
            lambda i: value >= i[0], self.species['moves'].items())) for move in moves]
        self.moves.extend(new_moves)
        self._level = value


def new_character(name, character):
    if 'vocation' in character:
        return Adventurer(name, character['vocation'])
    elif 'species' in character:
        return Monster(name, character['species'])
    else:
        raise NotImplementedError(
            f'no supported character type in [{character.keys()}]')
