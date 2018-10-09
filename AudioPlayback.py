from pygame import mixer


class AudioPlayback:
    """
    * Author: Phuong Le
    * Date: 22 Sep 2018
    * Start a new audio playback without opening any system application
    """

    def __init__(self, audio_path):
        self.audio_path = audio_path
        mixer.init()
        mixer.music.load(audio_path)
        mixer.music.play(1)

    @staticmethod
    def stop():
        mixer.music.stop()
