#!/usr/bin/env python3

import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import ambit
import ambit.image
import pygame
import threading
import time

DISPLAY_SIZE = (1024, 576)
DISPLAY_SCALING_FACTOR = 1  # Typical display is 1, HiDPI is 2

# Times per second to check for events.
TICKS_PER_SECOND = 60

# Times per second to redraw component state.
REDRAWS_PER_SECOND = 30

# Times per second to update layout.
LAYOUT_UPDATES_PER_SECOND = 5

# Display size scaled to DPI setting.
SURFACE_SIZE = (
        DISPLAY_SIZE[0] * DISPLAY_SCALING_FACTOR,
        DISPLAY_SIZE[1] * DISPLAY_SCALING_FACTOR)

COMPONENT_COLOR = (164, 164, 164)
COMPONENT_SELECTED_COLOR = (164, 164, 255)

COMPONENT_MARGIN = 4 * DISPLAY_SCALING_FACTOR


def initial_pos_and_slot_size(surface_size, min_slot_x, min_slot_y, max_slot_x, max_slot_y):
    count_slots_x = abs(min_slot_x - max_slot_x) + 1
    count_slots_y = abs(min_slot_y - max_slot_y) + 1
    margin_x = count_slots_x * COMPONENT_MARGIN + (COMPONENT_MARGIN * 3)
    margin_y = count_slots_y * COMPONENT_MARGIN + (COMPONENT_MARGIN * 3)
    slot_width = int((surface_size[0] - margin_x) / count_slots_x)
    slot_height = int((surface_size[1] - margin_y) / count_slots_y)
    slot_size = min([slot_width, slot_height])
    initial_pos_x = (slot_width * -min_slot_x) + int(margin_x / 2)
    initial_pos_y = (slot_height * max_slot_y) + int(margin_y / 2)
    return (initial_pos_x, initial_pos_y), slot_size


# FIXME: could do more caching of calculations here
class ComponentRenderer(object):
    def __init__(self, initial_pos, slot_size, component, screen_display_surface_cache, color=COMPONENT_COLOR):
        self.component = component
        self.slot = component.slot
        self.orientation = component.orientation
        self.color = color
        self.initial_pos = initial_pos
        self.slot_size = slot_size

        self.screen_display_surface_cache = screen_display_surface_cache
        self.cached_screen_display = None

        self.wide = False
        if component.kind == ambit.Component.KIND_SLIDER:
            self.wide = True

        self.width = self.height = slot_size
        if self.wide:
            self.width += slot_size + COMPONENT_MARGIN

        self.rotate_and_place()

        self.connector_size = int(slot_size / 32)
        self.font_size = int(slot_size / 16)
        self.screen_display_size = (
            int(slot_size / 1.5),
            int(slot_size / 1.5))
        self.led_thickness = int(slot_size / 32)
        self.id_inset = self.led_thickness + COMPONENT_MARGIN * 2.2

        self.component_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.led_rect = pygame.Rect(
            self.x + self.led_thickness, self.y + self.led_thickness,
            self.w - (self.led_thickness * 2), self.h - (self.led_thickness * 2))
        self.font = pygame.font.Font(pygame.font.get_default_font(), self.font_size)
        self.display_font = pygame.font.Font(
                pygame.font.get_default_font(), self.font_size + 4)

    def sync(self):
        if self.component.index == 1:
            self.sync_screen_display()

    def sync_screen_display(self):
        if self.cached_screen_display == self.component.screen_display:
            return

        self.screen_display_surface = None

        if self.component.screen_display in self.screen_display_surface_cache:
            self.screen_display_surface = self.screen_display_surface_cache[self.component.screen_display]

        if not self.screen_display_surface:
            for path_tmpl in ('./reference/assets/%d.raw', './example/assets/%d.raw'):
                try:
                    self.screen_display_surface = ambit.image.surface(
                            path_tmpl % self.component.screen_display,
                            surface_size=self.screen_display_size)
                    break
                except:
                    self.screen_display_surface = None
                    continue

        if not self.screen_display_surface:
            self.screen_display_surface = pygame.Surface(ambit.image.IMAGE_SIZE)
            self.screen_display_surface.fill((0,0,0))

        self.screen_display_surface_cache[self.component.screen_display] = self.screen_display_surface
        self.cached_screen_display = self.component.screen_display

    def slot_coordinates(self):
        slotx, sloty = self.slot
        return (self.initial_pos[0] + (self.slot_size + COMPONENT_MARGIN) * slotx,
                self.initial_pos[1] - (self.slot_size + COMPONENT_MARGIN) * sloty)

    def orient(self):
        x, y = self.slot_coordinates()
        if self.orientation == 90:
            return x, y, self.height, self.width
        elif self.orientation == 270:
            return x, y - (self.width - self.slot_size), self.height, self.width
        elif self.orientation == 180:
            return x - (self.width - self.slot_size), y, self.width, self.height
        return x, y, self.width, self.height

    # FIXME: prepare a surface with leds, ports, etc.
    # in 0deg orientation and then rotate the entire
    # surface and blit? Text will still need to be
    # rendered after rotation.
    def root_port_position(self):
        div = 2
        if self.wide:
            div = 4
        if self.orientation == 0:
            return self.x + int(self.w / div), self.y
        if self.orientation == 90:
            return self.x + self.w, self.y + int(self.h / div)
        if self.orientation == 180:
            if self.wide:
                div = 1.33
            return self.x + int(self.w / div), self.y + self.h
        if self.orientation == 270:
            if self.wide:
                div = 1.33
            return self.x, self.y + int(self.h / div)

    def rotate_and_place(self):
        self.x, self.y, self.w, self.h = self.orient()
        self.root_port_pos = self.root_port_position()

    def draw(self, screen):
        self.draw_body(screen)
        self.draw_ports(screen)
        self.draw_id(screen)
        self.draw_slot(screen)
        self.draw_behavior(screen)
        self.draw_led(screen)
        self.draw_display(screen)
        self.draw_values(screen)

    def draw_body(self, screen):
        pygame.draw.rect(screen, self.color, self.component_rect)

    def draw_ports(self, screen):
        self.draw_root_port(screen)

    def draw_root_port(self, screen):
        pygame.draw.circle(screen, (255, 0, 0, 128),
                self.root_port_pos, self.connector_size)

    def draw_led(self, screen):
        pygame.draw.rect(screen, self.component.led,
                self.led_rect, self.led_thickness)

    def draw_id(self, screen):
        text = '[%s] %s (%s)' % (
                self.component.uid, self.component.index, self.component.kind_name())
        surface = self.font.render(text, True, (255, 255, 255))
        screen.blit(surface, (self.x + self.id_inset, self.y + self.id_inset))

    def draw_slot(self, screen):
        text = str(self.component.slot)
        surface = self.font.render(text, True, (255, 255, 255))
        screen.blit(surface, (self.x + self.id_inset, self.y + self.h - self.id_inset - surface.get_height()))

    def draw_behavior(self, screen):
        text = ''
        for input_type in self.component.callbacks:
            invocation = self.component.callbacks[input_type]
            if invocation.behavior:
                text = invocation.behavior.behavior
                break
        surface = self.font.render(text, True, (255, 255, 255))
        screen.blit(surface, (self.x + self.w - self.id_inset - surface.get_width(),
            self.y + self.h - self.id_inset - surface.get_height()))

    def draw_display(self, screen):
        if self.component.kind != ambit.Component.KIND_BASE:
            return

        isw, ish = self.screen_display_surface.get_size()
        isx = self.x + int(self.w / 2) - int(isw / 2)
        isy = self.y + int(self.h / 2) - int(ish / 2)
        screen.blit(self.screen_display_surface, (isx, isy))

        text = str(self.component.screen_string)
        fsurface = self.display_font.render(text, True, (255, 255, 255))
        fsw, fsh = fsurface.get_size()
        screen.blit(fsurface,
                (self.x + int(self.w / 2) - int(fsw / 2),
                isy + ish - int(fsh * 1.5)))

    def draw_values(self, screen):
        if self.component.kind == ambit.Component.KIND_BASE:
            return
        text = str(self.component.values)
        surface = self.font.render(text, True, (255, 255, 255))
        sw, sh = surface.get_size()
        screen.blit(surface,
                (self.x + int(self.w / 2) - int(sw / 2),
                self.y + int(self.h / 2) - int(sh / 2)))


class Display(object):
    def __init__(self, ctrl, close_on_exit=False, shutdown_event=None,
            pygame_event_callbacks=None):
        self.screen = None
        self.surface = None
        self.surface_size = SURFACE_SIZE
        self.ctrl = ctrl
        self.close_on_exit = close_on_exit
        self.selected_component = 0
        self.pygame_event_callbacks = pygame_event_callbacks
        self.screen_display_surface_cache = {}
        self.cached_extrema = None
        if shutdown_event:
            self.shutdown_event = shutdown_event
        else:
            self.shutdown_event = threading.Event()
        self.thread = threading.Thread(target=self.worker)

    def open(self):
        pygame.init()
        pygame.key.set_repeat(500, 100)
        self.update_display()
        self.layout_changed()

    def update_display(self):
        self.screen = pygame.display.set_mode(self.surface_size, pygame.RESIZABLE)
        self.surface = pygame.Surface(self.surface_size)
        self.screen.fill((0, 0, 0))
        pygame.display.flip()
        self.cached_extrema = None
        self.layout_changed()

    def prepare_sprites(self, initial_pos, slot_size, root):
        sprites = []
        sp = ComponentRenderer(
                initial_pos, slot_size, root,
                self.screen_display_surface_cache)
        sprites.append(sp)
        for port in root.children:
            component = root.children[port]
            if not component:
                continue
            sprites.extend(self.prepare_sprites(initial_pos, slot_size, component))
        return sprites

    def layout_changed(self):
        extrema = self.ctrl.layout.extrema()
        if self.cached_extrema == extrema:
            return
        min_x, min_y, max_x, max_y = extrema
        initial_pos, slot_size = initial_pos_and_slot_size(
                self.surface_size, min_x, min_y, max_x, max_y)
        root = self.ctrl.layout.find_component(1)
        self.sprites = self.prepare_sprites(initial_pos, slot_size, root)
        self.screen.fill((0, 0, 0))
        self.cached_extrema = min_x, min_y, max_x, max_y
        self.screen_display_surface_cache = {}
        # TODO: draw the underlying grid

    def draw(self):
        for sp in self.sprites:
            sp.sync()
            if sp.component.index == self.selected_component:
                sp.color = COMPONENT_SELECTED_COLOR
            else:
                sp.color = COMPONENT_COLOR
            sp.draw(self.screen)

    def shutdown(self):
        print('[R] Shutting down at user request.')
        self.shutdown_event.set()
        if self.close_on_exit:
            self.ctrl.close()

    def tick(self):
        # TODO: only redraw if layout *or* component state changed.
        if self.tick_count % int(TICKS_PER_SECOND / LAYOUT_UPDATES_PER_SECOND) == 0:
            pygame.display.flip()
            self.layout_changed()
            self.draw()
            pygame.display.flip()
        if self.tick_count % int(TICKS_PER_SECOND / REDRAWS_PER_SECOND) == 0:
            pygame.display.flip()
            self.draw()
            pygame.display.flip()

        event = pygame.event.poll()
        if event.type == pygame.NOEVENT:
            return

        if event.type == pygame.VIDEORESIZE:
            self.surface_size = event.size
            self.update_display()
        elif event.type == pygame.QUIT:
            self.shutdown()
        elif event.type == pygame.KEYDOWN and event.key in (
                pygame.K_q, pygame.K_ESCAPE):
            self.shutdown()
        elif event.type == pygame.KEYUP and event.key == pygame.K_TAB:
            self.ctrl.rotate(90)
        elif event.type == pygame.KEYDOWN:
            k_int_map = {
                    pygame.K_0: 0,
                    pygame.K_1: 1,
                    pygame.K_2: 2,
                    pygame.K_3: 3,
                    pygame.K_4: 4,
                    pygame.K_5: 5,
                    pygame.K_6: 6,
                    pygame.K_7: 7,
                    pygame.K_8: 8,
                    pygame.K_9: 9,
            }
            if event.key in k_int_map:
                self.selected_component = k_int_map[event.key]

        if self.pygame_event_callbacks:
            for callback in self.pygame_event_callbacks:
                callback(event)

    def run(self):
        self.open()
        self.thread.start()

    def worker(self):
        self.tick_count = 0
        while not self.shutdown_event.is_set():
            self.tick()
            self.tick_count += 1
            time.sleep(1 / TICKS_PER_SECOND)
