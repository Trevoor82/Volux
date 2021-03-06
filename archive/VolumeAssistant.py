from _thread import start_new_thread  # used to run functions in parallel
import cpaudio
import time


class VolumeAssistant:
    def __init__(self):
        self.running = False
        self.volume = (
            10
        )  # TODO: change this to poll the actual volume on scroll detection
        self.muted = False  # TODO: change this to reflect reality
        self.previous_volume = 0
        self.mixer = cpaudio.MixerController()

    def start(self, pollFreq):
        def _startthread(self, pollFreq):
            self.running = True
            self.display = self._get_display_size()
            poll = 1 / pollFreq
            while self.running is True:
                # // THREAD CODE //
                mouse = self._get_mouse_coords()
                print(self._get_percentage(mouse, self.display))
                time.sleep(poll)
                # // END THREAD CODE //
            print("volume assistant thread terminating...")
            print("volume assistant thread terminated.")

        start_new_thread(_startthread, (self, pollFreq))

    def stop(self):
        self.running = False

    def ismuted(self):
        return self.mixer.gmute()

    def _get_percentage(self, child, parent):
        percentages = {
            "x": (child["x"] / parent["x"]) * 100,
            "y": (child["y"] / parent["y"]) * 100,
        }
        return percentages

    def _get_mouse_coords(self, display):
        data = display.Display().screen().root.query_pointer()._data
        return {"x": data["root_x"], "y": data["root_y"]}

    def _get_display_size(self, root):
        return {"x": root.winfo_screenwidth(), "y": root.winfo_screenheight()}
