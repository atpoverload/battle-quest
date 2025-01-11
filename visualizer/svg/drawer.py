import os

import drawsvg as draw


class VerticalCardDrawer:
    def __init__(self, card, cardback, tag, sprite, element, effect, resources):
        self.card = card
        self.cardback = cardback
        self.tag = tag
        self.sprite = sprite
        self.element = element
        self.effect = effect
        self.resources = resources

        self.size = (self.card['width'], self.card['height'])
        self.center = (self.size[0] / 2, self.size[1] / 2)

        self.sprite_pos = (
            self.center[0] - self.sprite['width'] / 2,
            self.card['font_size']
        )
        self.element_pos = (
            self.sprite_pos[0] + (self.sprite['width'] -
                                  self.element['width']) / 2,
            self.sprite_pos[1] + self.sprite['height']
        )
        self.effect_pos = (
            self.sprite_pos[0], self.element_pos[1] + self.element['height'])

    def draw_cardback(self):
        d = draw.Drawing(*self.size, origin='top-left')
        d.append(
            draw.Rectangle(0, 0, *self.size, fill=self.cardback['background_color']))
        path = draw.Path()
        d.append(path.M(self.center[0], 0).L(self.center[0], self.size[1]))
        d.append(
            draw.Text(
            self.cardback['text'],
            path=path,
            text_anchor='middle',
            dominant_baseline='auto',
            font_size=self.cardback['font_size'],
            font_family=self.cardback['font_family'],
            font_color=self.cardback['font_color']
        ))
        return d

    def draw_card(self, name, elements):
        d = self.draw_face()
        # d.embed_google_font(self.fonts['font_family'])
        d.append(self.draw_background())
        d.append(self.draw_name(name.title()))
        d.append(self.draw_sprite(name))
        d.extend(self.draw_elements(elements))
        return d
    
    def draw_face(self):
        return draw.Drawing(*self.size, origin='top-left')

    def draw_background(self):
        return draw.Rectangle(0, 0, *self.size, fill=self.card['background_color'])

    def draw_name(self, name):
        return draw.Text(
            name,
            x=0,
            y=0,
            text_anchor='start',
            dominant_baseline='hanging',
            font_size=self.card['font_size'],
            font_family=self.card['font_family'],
            font_color=self.card['font_color']
        )

    def draw_tag(self, value, kind):
        l = []
        l.append(draw.Rectangle(
            x=self.size[0] - self.tag['width'],
            y=-25,
            width=self.tag['width'] + 25,
            height=self.tag['height'] + 25,
            fill=self.tag['background_colors'][kind],
            stroke='black',
            stroke_width=10,
            rx=20,
        ))
        l.append(draw.Text(
            value,
            x=self.size[0] - self.tag['width'] / 2,
            y=0,
            text_anchor='middle',
            dominant_baseline='hanging',
            font_size=self.tag['font_size'],
            font_family=self.tag['font_family'],
            font_color=self.tag['font_color'],
        ))
        return l

    def draw_sprite(self, sprite):
        return draw.Image(
            *self.sprite_pos,
            self.sprite['width'],
            self.sprite['height'],
            path=self.get_sprite(sprite),
            embed=True,
        )

    def draw_elements(self, elements):
        l = []
        element_count = len(elements)
        for i, element in enumerate(elements):
            # sprite_center = self.sprite_pos[0] + self.sprite['width'] / 2 - self.element['width']
            x = self.element_pos[0] + self.element['width'] * \
                (i - (element_count - 1) / 2)
            l.append(
                draw.Image(
                    x=x,
                    y=self.element_pos[1],
                    width=self.element['width'],
                    height=self.element['height'],
                    path=self.get_sprite(element),
                    embed=True,
                )
            )
        return l

    def draw_effect(self, effect):
        l = []
        # target = effect['target'] if 'target' in effect else ''
        if effect['type'] == 'attack':
            # print(self.center)
            # print(self.effect_pos)
            # message = f'Damage'
            l.append(draw.Text(
                'Damage',
                # x=self.effect_pos[0],
                x=self.center[0],
                y=self.effect_pos[1],
                # text_anchor='start',
                text_anchor='middle',
                dominant_baseline='hanging',
                font_size=self.effect['font_size'],
                font_family=self.effect['font_family'],
                font_color=self.effect['font_color'],
            ))
            # for value in effect['value']:
            #     l.append(draw.Image(
            #         x=self.effect_pos[0] +
            #         self.sprite['width'] - self.effect['width'],
            #         y=self.effect_pos[1],
            #         width=self.effect['width'],
            #         height=self.effect['height'],
            #         path=self.get_sprite(value),
            #         embed=True,
            #     ))
        elif effect['type'] == 'condition':
            l.append(draw.Text(
                'Apply',
                # x=self.effect_pos[0],
                x=self.center[0],
                y=self.effect_pos[1],
                # text_anchor='start',
                text_anchor='middle',
                dominant_baseline='hanging',
                font_size=self.effect['font_size'],
                font_family=self.effect['font_family'],
                font_color=self.effect['font_color'],
            ))
            # for value in effect['value']:
            #     l.append(draw.Image(
            #         x=self.effect_pos[0] +
            #         self.sprite['width'] - self.effect['width'],
            #         y=self.effect_pos[1],
            #         width=self.effect['width'],
            #         height=self.effect['height'],
            #         path=self.get_sprite(value),
            #         embed=True,
            #     ))
        elif effect['type'] == 'heal':
            l.append(draw.Text(
                f"Heal {effect['value']}",
                x=self.effect_pos[0],
                y=self.effect_pos[1],
                text_anchor='start',
                dominant_baseline='hanging',
                font_size=self.effect['font_size'],
                font_family=self.effect['font_family'],
                font_color=self.effect['font_color'],
            ))
            l.append(draw.Image(
                x=self.effect_pos[0] +
                self.sprite['width'] - self.effect['width'],
                y=self.effect_pos[1],
                width=self.effect['width'],
                height=self.effect['height'],
                path=self.get_sprite(effect['element']),
                embed=True,
            ))
        elif effect['type'] == 'defense':
            l.append(draw.Text(
                'Gain',
                x=self.effect_pos[0],
                y=self.effect_pos[1],
                text_anchor='start',
                dominant_baseline='hanging',
                font_size=self.effect['font_size'],
                font_family=self.effect['font_family'],
                font_color=self.effect['font_color'],
            ))
            l.append(draw.Image(
                x=self.effect_pos[0] +
                self.sprite['width'] - self.effect['width'],
                y=self.effect_pos[1],
                width=self.effect['width'],
                height=self.effect['height'],
                path=self.get_sprite(effect['element']),
                embed=True,
            ))
        elif effect['type'] in ['fight', 'bounty', 'bounty fight', 'market', 'station']:
            # l.append(draw.Text(
            #     effect['type'].title(),
            #     x=self.effect_pos[0],
            #     y=self.effect_pos[1],
            #     text_anchor='start',
            #     dominant_baseline='hanging',
            #     font_size=self.effect['font_size'],
            #     font_family=self.effect['font_family'],
            #     font_color=self.effect['font_color'],
            # ))
            # for value in effect['value']:
            l.append(draw.Text(
                str(effect['entity_count']),
                x=self.center[0],
                y=self.effect_pos[1],
                text_anchor='middle',
                dominant_baseline='hanging',
                font_size=self.effect['font_size'],
                font_family=self.effect['font_family'],
                font_color=self.effect['font_color'],
                # width=self.effect['width'],
                # height=self.effect['height'],
                # path=self.get_sprite(value),
                # embed=True,
            ))
        else:
            l.append(draw.Text(
                str(effect['type'].title()),
                x=self.effect_pos[0],
                y=self.effect_pos[1],
                text_anchor='start',
                dominant_baseline='hanging',
                font_size=self.effect['font_size'],
                font_family=self.effect['font_family'],
                font_color=self.effect['font_color'],
            ))
            for value in effect['value']:
                l.append(draw.Image(
                    x=self.effect_pos[0] +
                    self.sprite['width'] - self.effect['width'],
                    y=self.effect_pos[1],
                    width=self.effect['width'],
                    height=self.effect['height'],
                    path=self.get_sprite(value),
                    embed=True,
                ))
        return l

    def get_sprite(self, name):
        return os.path.join(
            self.resources,
            f'{name}.png'
        )
