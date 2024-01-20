import pygame
import time
import os
import typing
import math
import argparse
from mqtt_utils import create_mqtt_client, send_msg


MAX_VEL_LIN = 2
MAX_VEL_ANG = 360
WHEEL_TRACK = 12 * 2.54 / 100
WHEEL_RADIUS = 4 * 2.54 / 100
DRIVE_RPM = 227
LAUNCHER_RPM = 6

TURN_DAMPING_FACTOR = 2
THROTTLE_LIM = [-0.5, 0.5]

JOYSTICK_THRESH = 0.05

KEY_TURN_FACTOR = 0.7

WINDOW_SIZE = (700, 500)


# Helper class for printing text to pygame window
# Source: https://www.pygame.org/docs/ref/joystick.html
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 25)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


def send_vel(mqtt_client, motion_axes, use_controller, limit):
    if use_controller:
        adjusted_axes = [
            ax if abs(ax) > JOYSTICK_THRESH else 0 for ax in motion_axes
        ]
        adjusted_axes[1] *= -1
        adjusted_axes[2] *= -1

        throttle = calc_throttle(adjusted_axes)
    else:
        keys = pygame.key.get_pressed()
        throttle = calc_throttle_keys(keys)
    
    if limit:
        limit_throttle(throttle)

    [wheel_vel, robot_vel, launcher_vel] = calc_vel(throttle)
    if USE_MQTT:
        send_msg(
            mqtt_client,
            "antbot/throttle",
            f"{throttle[0]};{throttle[1]};{throttle[2]}",
        )

    return throttle, wheel_vel, robot_vel, launcher_vel


def calc_throttle(axes):
    # Throttle convention: wheel spinning forwards = positive

    r = math.sqrt(math.pow(axes[0], 2) + math.pow(axes[1], 2))
    theta = math.atan2(axes[1], axes[0])
    throttle_l = r * (math.sin(theta) + math.cos(theta) / TURN_DAMPING_FACTOR)
    throttle_r = r * (math.sin(theta) - math.cos(theta) / TURN_DAMPING_FACTOR)
    throttle = [throttle_l, throttle_r, axes[2]]
    return throttle


def calc_throttle_keys(keys):
    throttle = [0, 0, 0]
    if keys[pygame.K_w]:
        throttle[0] += 1
        throttle[1] += 1
    if keys[pygame.K_s]:
        throttle[0] -= 1
        throttle[1] -= 1
    if keys[pygame.K_a]:
        if keys[pygame.K_w] or keys[pygame.K_s]:
            throttle[0] *= KEY_TURN_FACTOR
        else:
            throttle[0] -= 1
            throttle[1] += 1
    if keys[pygame.K_d]:
        if keys[pygame.K_w] or keys[pygame.K_s]:
            throttle[1] *= KEY_TURN_FACTOR
        else:
            throttle[0] += 1
            throttle[1] -= 1
    if keys[pygame.K_i]:
        throttle[2] = 1
    if keys[pygame.K_k]:
        throttle[2] = -1
    return throttle


def limit_throttle(throttle: list[float]) -> list[float]:
    for i in range(len(throttle) - 1):
        throttle[i] = min(max(throttle[i], THROTTLE_LIM[0]), THROTTLE_LIM[1])
    return throttle


def calc_vel(throttle):
    rpm_to_rads = 2 * math.pi / 60
    wheel_vel = [
        throttle[0] * DRIVE_RPM * rpm_to_rads,
        throttle[1] * DRIVE_RPM * rpm_to_rads,
    ]

    v = WHEEL_RADIUS / 2 * (wheel_vel[0] + wheel_vel[1])
    w = WHEEL_RADIUS / WHEEL_TRACK * (wheel_vel[1] - wheel_vel[0])
    robot_vel = [v, w]

    launcher_vel = throttle[2] * LAUNCHER_RPM * rpm_to_rads

    return [wheel_vel, robot_vel, launcher_vel]


def main():
    mqtt_client = None
    if USE_MQTT:
        mqtt_client = create_mqtt_client()
        mqtt_client.loop_start()
    pygame.init()

    pygame.joystick.init()

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Antbot Controller")

    text_print = TextPrint()

    joysticks: typing.Dict[int, pygame.joystick.JoystickType] = {}

    motion_axes = [0, 0, 0]

    go = True
    limit = True

    while go:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                go = False

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 1:
                    print(f"Jump triggered by controller {event.instance_id}")

            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    motion_axes[0] = event.value
                if event.axis == 1:
                    motion_axes[1] = event.value
                if event.axis == 3:
                    motion_axes[2] = event.value
                if event.axis == 4:
                    if event.value > 0:
                        limit = False
                    else:
                        limit = True

            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)

                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connected")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected")

        screen.fill((255, 255, 255))
        text_print.reset()

        for joy in joysticks.values():
            id = joy.get_instance_id()
            text_print.tprint(screen, f"Controller {id}")
            text_print.indent()
            text_print.tprint(screen, f"Joystick name: {joy.get_name()}")
            text_print.tprint(screen, f"GUID: {joy.get_guid()}")
            text_print.tprint(screen, f"Power level: {joy.get_power_level()}")
            text_print.tprint(screen, f"Axes values:")
            text_print.indent()
            for i in range(joy.get_numaxes()):
                text_print.tprint(screen, str(joy.get_axis(i)))
            text_print.unindent()
            text_print.tprint(
                screen,
                f"Button values: {[joy.get_button(i) for i in range(joy.get_numbuttons())]}",
            )
            text_print.tprint(
                screen,
                f"Hat values: {[joy.get_hat(i) for i in range(joy.get_numhats())]}",
            )
            text_print.unindent()

        text_print.tprint(screen, "")

        [throttle, wheel_vel, robot_vel, launcher_vel] = send_vel(
            mqtt_client, motion_axes, bool(joysticks), limit
        )

        text_print.tprint(
            screen,
            f"Velocity [m/s, deg/s]: [{robot_vel[0]:.1f}, {math.degrees(robot_vel[1]):.1f}]",
        )
        text_print.tprint(
            screen, f"Wheel throttle: [{throttle[0]:.3f}, {throttle[1]:.3f}]"
        )
        text_print.tprint(
            screen,
            f"Wheel speeds L-R [rad/s]: [{wheel_vel[0]:.3f}, {wheel_vel[1]:.3f}]",
        )
        text_print.tprint(screen, "")
        text_print.tprint(screen, f"Launcher throttle: [{throttle[2]:.3f}]")
        text_print.tprint(
            screen,
            f"Launcher speed [rad/s]: [{launcher_vel:.3f}]",
        )

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    if USE_MQTT:
        mqtt_client.loop_stop()


if __name__ == "__main__":
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    global USE_MQTT
    USE_MQTT = not args.debug
    main()
