import pygame
import pygame_gui

from pygame_gui.core import ObjectID


# taken from https://www.reddit.com/r/pygame/comments/v3ofs9/draw_arrow_function; highly recommend
def draw_arrow(
    surface: pygame.Surface,
    start: pygame.Vector2,
    end: pygame.Vector2,
    color: pygame.Color,
    body_width: int = 2,
    head_width: int = 4,
    head_height: int = 2,
):
    """Draw an arrow between start and end with the arrow head at the end.

    Args:
        surface (pygame.Surface): The surface to draw on
        start (pygame.Vector2): Start position
        end (pygame.Vector2): End position
        color (pygame.Color): Color of the arrow
        body_width (int, optional): Defaults to 2.
        head_width (int, optional): Defaults to 4.
        head_height (float, optional): Defaults to 2.
    """
    arrow = start - end
    angle = arrow.angle_to(pygame.Vector2(0, -1))
    body_length = arrow.length() - head_height

    # Create the triangle head around the origin
    head_verts = [
        pygame.Vector2(0, head_height / 2),  # Center
        pygame.Vector2(head_width / 2, -head_height / 2),  # Bottomright
        pygame.Vector2(-head_width / 2, -head_height / 2),  # Bottomleft
    ]
    # Rotate and translate the head into place
    translation = pygame.Vector2(
        0, arrow.length() - (head_height / 2)).rotate(-angle)
    for i in range(len(head_verts)):
        head_verts[i].rotate_ip(-angle)
        head_verts[i] += translation
        head_verts[i] += start

    pygame.draw.polygon(surface, color, head_verts)

    # Stop weird shapes when the arrow is shorter than arrow head
    if arrow.length() >= head_height:
        # Calculate the body rect, rotate and translate into place
        body_verts = [
            pygame.Vector2(-body_width / 2, body_length / 2),  # Topleft
            pygame.Vector2(body_width / 2, body_length / 2),  # Topright
            pygame.Vector2(body_width / 2, -body_length / 2),  # Bottomright
            pygame.Vector2(-body_width / 2, -body_length / 2),  # Bottomleft
        ]
        translation = pygame.Vector2(0, body_length / 2).rotate(-angle)
        for i in range(len(body_verts)):
            body_verts[i].rotate_ip(-angle)
            body_verts[i] += translation
            body_verts[i] += start

        pygame.draw.polygon(surface, color, body_verts)


# ACTION_ID = ObjectID(
#     class_id='@action_button',
#     object_id='#action_button'
# )


# CHARACTER_ID = ObjectID(
#     class_id='@character_button',
#     object_id='#character_button'
# )


# class ActionBattleButton(pygame_gui.elements.UIButton):
#     def __init__(self, action, relative_rect, manager):
#         super().__init__(
#             relative_rect=relative_rect,
#             text=action['name'],
#             tool_tip_text=action['description'],
#             object_id=ACTION_ID,
#             manager=manager)
#         self.action = action


# class ItemBattleButton(pygame_gui.elements.UIButton):
#     def __init__(self, item, character, relative_rect, manager):
#         super().__init__(
#             relative_rect=relative_rect,
#             text=item.item['name'],
#             tool_tip_text=item.item['description'],
#             object_id=ACTION_ID,
#             manager=manager)
#         self.item = item
#         self.character = character
#         self.action = item.action


# class CharacterBattleButton(pygame_gui.elements.UIButton):
#     def __init__(self, character, relative_rect, manager):
#         super().__init__(
#             relative_rect=relative_rect,
#             text=character.name,
#             object_id=CHARACTER_ID,
#             manager=manager)
#         self.character = character


# class CharacterBattlePanel:
#     def __init__(self, character, origin, manager):
#         CharacterBattleButton(
#             character,
#             pygame.Rect(origin, (200, 200)),
#             manager)


# class CharacterBattleControl:
#     def __init__(self, character, origin, manager):
#         self.items = []
#         for i, item in enumerate(character.items.values()):
#             print(character.name, item.name)
#             self.items.append(ItemBattleButton(
#                 item,
#                 character,
#                 pygame.Rect(
#                     (origin[0] + 75 * (i % 2), origin[1] + 75 * (i / 2)),
#                     (75, 75)),
#                 manager))
#         self.character = CharacterBattleButton(
#             character,
#             pygame.Rect(origin, (200, 200)),
#             manager)

#     def as_actor(self):
#         [item.enable() for item in self.items]
#         [item.show() for item in self.items]
#         self.character.disable()

#     def as_target(self):
#         [item.disable() for item in self.items]
#         [item.hide() for item in self.items]
#         self.character.enable()

#     def disable(self):
#         [item.disable() for item in self.items]
#         [item.hide() for item in self.items]
#         self.character.disable()
