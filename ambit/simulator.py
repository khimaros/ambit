import ambit
import ambit.fake
import ambit.render
import pygame


class Controller(ambit.Controller):
    def __init__(self, config, device=None, simulate_input=True, pygame_event_callback=None):
        if device:
            self.device = device
        else:
            self.device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        super(Controller, self).__init__(config, self.device)

        self.device.components_connected()

        pygame_event_callbacks = []
        if pygame_event_callback:
            pygame_event_callbacks.append(pygame_event_callback)
        if simulate_input:
            pygame_event_callbacks.append(self.default_pygame_event_callback)

        self.display = ambit.render.Display(self,
                shutdown_event=self.shutdown_event,
                pygame_event_callbacks=pygame_event_callbacks)

    def default_pygame_event_callback(self, event):
        index = self.display.selected_component
        if not index:
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            self.device.input_slide_up(index)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            self.device.input_slide_down(index)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            self.device.input_rotation_left(index)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            self.device.input_rotation_right(index)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.device.input_pressed(index)
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            self.device.input_released(index)

    def connect(self):
        super(Controller, self).connect()
        self.display.run()
