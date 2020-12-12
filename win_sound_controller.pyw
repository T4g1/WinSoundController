import time
import json
import paho.mqtt.client as mqtt
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import (AudioUtilities, IAudioEndpointVolume,
                         IAudioEndpointVolumeCallback)

host = "192.168.1.13"
port = 1883
main_topic = "t4g1win"
is_running = True

sound = None
status = {}


class Sound:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

        self.min_db, self.max_db, _ = self.volume.GetVolumeRange()


    def is_muted(self):
        return self.volume.GetMute()


    def mute(self, should_mute = False):
        if should_mute:
            self.volume.SetMute(1, None)
        else:
            self.volume.SetMute(0, None)


    def toggle_mute(self):
        self.mute(not self.is_muted())


    def current_volume(self):
        return self.volume.GetMasterVolumeLevel()


    def set_volume(self, volume):
        if volume < sound.min_db:
            volume = sound.min_db
        if volume > sound.max_db:
            volume = sound.max_db

        self.volume.SetMasterVolumeLevel(volume, None)


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
            sound.toggle_mute()
        elif mute == "on" or mute == "off":
            sound.mute(mute != "on")
        else:
            print("Malformed mute command: %s" % mute)

    if volume != "":
        try:
            volume = int(volume)
        except:
            print("Malformed set volume command: %s".format(volume))
            return

        print("Got set volume command: %f" % volume)
        sound.set_volume(volume)

    publish_status(client)


def publish_status(client):
    old_status = {
        "state": status.get("state", ""),
        "volume": status.get("volume", ""),
    }

    status["state"] = "OFF" if sound.is_muted() else "ON"
    status["volume"] = sound.current_volume()

    dirty = status["state"] != old_status["state"] or status["volume"] != old_status["volume"]

    if not dirty:
        return

    print("Status: %s" % json.dumps(status))

    client.publish(get_sound_topic(), json.dumps(status))


def sound_controller():
    print("Starting sound controller")
    client = get_client()
    client.loop_start()

    try:
        print("Sound controller running")

        while is_running:
            publish_status(client)
            time.sleep(1)
    except Exception as e:
        print("Stopping sound controller")

    client.loop_stop()


if __name__ == "__main__":
    sound = Sound()
    sound_controller()
