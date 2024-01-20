from gpiozero import Motor
from paho.mqtt import client as mqtt
from dotenv import dotenv_values
from mqtt_utils import create_mqtt_client, attach_callback


config = dotenv_values(".env")

get_motor_pins = lambda pins: [int(pin) for pin in pins.split(",")]

left_motor = Motor(*get_motor_pins(config["LEFT_MOTOR_PINS"]))
right_motor = Motor(*get_motor_pins(config["RIGHT_MOTOR_PINS"]))
jump_motor = Motor(*get_motor_pins(config["JUMP_MOTOR_PINS"]))


def set_drive_throttle(topic: str, msg: str):
    print(msg)
    throttle = [min(max(float(num), -1), 1) for num in msg.split(";")]
    left_motor.value = throttle[0]
    right_motor.value = throttle[1]
    jump_motor.value = throttle[2]


def main():
    mqtt_client = create_mqtt_client()
    mqtt_client.on_message = attach_callback(set_drive_throttle)
    mqtt_client.subscribe("antbot/throttle")
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
