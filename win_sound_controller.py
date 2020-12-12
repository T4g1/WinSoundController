import time
import json
import paho.mqtt.client as mqtt
from sound import Sound


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
    try:
        message = json.loads(message.payload.decode("utf-8").lower())
    except:
        return

    mute = message.get("state", "")
    volume = message.get("volume", "")

    if mute != "":
        print("Got mute command")

        if mute == "toggle":
            Sound.mute()

        elif mute == "on" or mute == "off":
            desired_status = mute == "on"
            current_statue = not Sound.is_muted()

            if desired_status != current_statue:
                Sound.mute()

        else:
            print("Malformed mute command: %s" % mute)

    if volume != "":
        try:
            volume = int(volume)
        except:
            print("Malformed set volume command: %s".format(volume))
            return

        if volume < 1:
            volume = 1
        if volume > 100:
            volume = 100

        print("Got set volume command: %d" % volume)
        Sound.volume_set(volume)

    publish_status(client)


def publish_status(client):
    status = {
        "state": "OFF" if Sound.is_muted() else "ON",
        "volume": Sound.current_volume(),
    }

    print("Status: %s" % json.dumps(status))

    client.publish(get_sound_topic(), json.dumps(status))


def sound_controller():
    print("Starting sound controller")
    client = get_client()
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
