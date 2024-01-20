from paho.mqtt import client as mqtt
from loguru import logger
from dotenv import dotenv_values
import time
import random
import typing


config = dotenv_values(".env")

BROKER = config["BROKER_IP"]
PORT = int(config["BROKER_PORT"])
USERNAME = config["BROKER_USER"]
PASSWORD = config["BROKER_PASS"]

INIT_RETRY_DELAY = int(config["INIT_RETRY_DELAY"])
RETRY_RATE = int(config["RETRY_RATE"])
MAX_RETRIES = int(config["MAX_RETRIES"])
MAX_RETRY_DELAY = int(config["MAX_RETRY_DELAY"])


def on_connect(
    client: mqtt.Client,
    userdata: str,
    flags: list,
    reason_code: int,
    properties: list,
):
    if reason_code == 0:
        print(f"Connection established: {reason_code}")
    else:
        print(f"Failed to connect: {reason_code}")


def create_mqtt_client() -> mqtt.Client:
    client_id = f"mqtt-pc-{random.randint(0,1000)}"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.connect(BROKER, PORT)
    return client


def on_disconnect(
    client: mqtt.Client,
    userdata: str,
    flags: list,
    reason_code: int,
    properties: list,
):
    num_retries = 0
    backoff = INIT_RETRY_DELAY
    while num_retries < MAX_RETRIES:
        logger.info(f"Retrying {num_retries + 1}/{MAX_RETRIES}")
        time.sleep(backoff)
        try:
            client.reconnect()
            logger.info("Reconnected")
            return
        except Exception as e:
            logger.error(f"Reconnect failed: {e}")

        backoff = min(backoff * RETRY_RATE, MAX_RETRY_DELAY)
        num_retries += 1
    logger.error("Reconnect attempts unsuccessful")


def echo(topic: str, data: str):
    print(f"{topic}: {data}")


def attach_callback(callback: typing.Callable):
    def inner(client: mqtt.Client, userdata: str, msg: mqtt.MQTTMessage):
        topic = msg.topic
        data = msg.payload.decode()
        return callback(topic, data)
    return inner


def on_publish():
    pass


def main():
    test_sub()
    # test_pub()


def test_sub():
    mqtt_sub = create_mqtt_client()
    mqtt_sub.on_message = attach_callback(echo)
    mqtt_sub.subscribe("test")
    mqtt_sub.loop_forever()
    # mqtt_sub.loop_start()
    # # stuff
    # mqtt_sub.loop_stop()  # handles disconnect


def send_msg(client: mqtt.Client, topic, msg):
    result = client.publish(topic, msg)
    status = result[0]
    return status


def test_pub():
    mqtt_pub = create_mqtt_client()
    mqtt_pub.loop_start()
    send_msg(mqtt_pub, "test", "hello")
    mqtt_pub.loop_stop()


if __name__ == "__main__":
    main()
