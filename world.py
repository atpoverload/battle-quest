from character import Adventurer, Monster, new_item, new_move

ADV_COUNTER = 0
MON_COUNTER = 0


class WorldManager:
    def __init__(self, world):
        self.world = world

        self.vocations = [
            c['vocation'] for c in self.world['characters'] if 'vocation' in c]
        self.items = {item['name']: item for item in world['items']}

        self.species = [
            c['species'] for c in self.world['characters'] if 'species' in c]
        self.moves = {}
        for move in world['moves']:
            self.moves[move['name']] = new_move(move)
        for species in self.species:
            moves = {}
            for k, v in species['moves'].items():
                if v not in moves:
                    moves[v] = []
                moves[v].append(self.moves[k])
            species['moves'] = moves

    def new_adventurer(self):
        character = self.vocations[0]
        global ADV_COUNTER
        name = f'{character["name"]}-{ADV_COUNTER}'
        ADV_COUNTER += 1
        character = Adventurer(name, character)
        character.health = character.max_health
        return character

    def new_monster(self, level=1):
        character = self.species[0]
        global MON_COUNTER
        name = f'{character["name"]}-{MON_COUNTER}'
        MON_COUNTER += 1
        character = Monster(name, character)
        character.level = level
        character.health = character.max_health
        return character

    def new_item(self):
        return new_item(self.world['items'][0])
