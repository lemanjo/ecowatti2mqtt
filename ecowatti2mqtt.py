import paho.mqtt.client as mqtt
import json
from ecowatti import EcowattiConfig, Ecowatti
from pydantic import BaseModel
from datetime import datetime, timedelta


class Config(BaseModel):
    mqtt_client_name: str
    mqtt_topic_header: str
    mqtt_host: str
    mqtt_port: int
    mqtt_timeout: int
    mqtt_username: str
    mqtt_password: str
    serial_device: str
    serial_timeout: int
    config_update_interval: int
    sensor_update_interval: int


def parse_config() -> Config:
    with open("config.json", "rb") as cfg_file:
        json_data = json.load(cfg_file)

    return Config(**json_data)


def on_connect(client, userdata, flags, rc):
    # callback for CONNACK response from the server.
    print("Connected with result code "+str(rc))

# callback for received messages


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def main():
    config = parse_config()

    client = mqtt.Client(config.mqtt_client_name)
    client.on_connect = on_connect
    client.on_message = on_message

    client.username_pw_set(config.mqtt_username, config.mqtt_password)
    client.connect(config.mqtt_host, config.mqtt_port, config.mqtt_timeout)

    client.loop_start()

    ecowatti_config = EcowattiConfig(
        config.serial_device, serial_timeout=config.serial_timeout)

    ecowatti = Ecowatti(ecowatti_config)

    for sensor in ecowatti._temperature_sensors:
        topic = f"{config.mqtt_topic_header}/ecowatti-temperature-{sensor.name.lower()}/config"
        payload = {
            "unique_id": f"ecowatti-{sensor.name.lower()}-temperature",
            "device_class": "temperature",
            "name": f"Ecowatti {sensor.name} temp",
            "state_topic": f"{config.mqtt_topic_header}/ecowatti-temperature-{sensor.name.lower()}/state",
            "unit_of_measurement": "°C",
            "icon": "hass:thermometer",
            "value_template": "{{ value_json.temperature }}"
        }

        client.publish(topic, json.dumps(payload))

    last_config_update = datetime.now()

    ecowatti.update_all_temperatures()

    for sensor in ecowatti._temperature_sensors:
        topic = f"{config.mqtt_topic_header}/ecowatti-temperature-{sensor.name.lower()}/state"
        data = {'temperature':  sensor.value}
        client.publish(topic, json.dumps(data))

    last_sensor_update = datetime.now()

    while True:
        if datetime.now() > last_config_update+timedelta(minutes=config.config_update_interval):
            for sensor in ecowatti._temperature_sensors:
                topic = f"{config.mqtt_topic_header}/ecowatti-temperature-{sensor.name.lower()}/config"
                payload = {
                    "unique_id": f"ecowatti-{sensor.name.lower()}-temperature",
                    "device_class": "temperature",
                    "name": f"Ecowatti {sensor.name} temp",
                    "state_topic": f"{config.mqtt_topic_header}/ecowatti-temperature-{sensor.name.lower()}/state",
                    "unit_of_measurement": "°C",
                    "icon": "hass:thermometer",
                    "value_template": "{{ value_json.temperature }}"
                }

                client.publish(topic, json.dumps(payload))

                last_config_update = datetime.now()

        if datetime.now() > last_sensor_update + timedelta(minutes=config.sensor_update_interval):
            ecowatti.update_all_temperatures()

            for sensor in ecowatti._temperature_sensors:
                topic = f"{config.mqtt_topic_header}/ecowatti-temperature-{sensor.name.lower()}/state"
                data = {'temperature':  sensor.value}
                client.publish(topic, json.dumps(data))

            last_sensor_update = datetime.now()


if __name__ == "__main__":
    main()
