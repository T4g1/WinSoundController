import paho.mqtt.client as mqtt
import time

host = "192.168.1.13"
port = 1883
main_topic = "t4g1win"
is_running = True


def get_sound_topic():
    return "%s/sound" % main_topic


def get_sound_command_topic():
    return "%s/set" % get_sound_topic()


def get_client():
    client = mqtt.Client("T4g1-Win")
    client.connect(host, port)

    client.subscribe(get_sound_command_topic())

    client.on_message = on_message

    return client


def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)


def sound_controller():
    print("Starting sound controller")
    client = get_client()
    client.publish(get_sound_topic(), "on")

    client.loop_start()

    try:
        print("Sound controller running")

        while is_running:
            time.sleep(1)
    except:
        print("Stopping sound controller")

    client.loop_stop()


if __name__ == "__main__":
    sound_controller()
