import subprocess
import warnings
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import atexit

class Niplay:
    def __init__(self, music_path: str, replay: Optional[int] = None,
                 volume: Optional[float] = None, fade_in: Optional[int] = None , fade_out = None ,
                 max_workers = 1 , AutoCLoseWhenPythonTirnimated = True
                 ):

        self.exePath =  r"D:\MaxLife\Programming\2025Projects\CS-Rider\NiPlay\src\NiPlay\bin\Debug\net9.0\NiPlay.exe"
        self._music_path = music_path
        self._args= self.arg_caculate(volume ,fade_in ,replay ,fade_out )
        self.PID = None
        self._process = None
        self._startInfo = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        atexit.register(self._cleanup)
        self._autoClean = AutoCLoseWhenPythonTirnimated


    def arg_caculate(self, volume, fade_in, replay , fadeout):
        total_args = [self.exePath , self._music_path]
        if volume is not None: total_args += [f"volume:{volume}"]
        if fade_in is not None: total_args += [f"fadein:{fade_in}"]
        if replay is not None: total_args += [f"replay:{replay}"]

        if fadeout : warnings.warn("fadeout isnt supported")


        return total_args



    def _popen_warper(self):
        self._process = subprocess.Popen(self._args)
        self.PID = self._process.pid

    def start(self):
        """
        you need this to play the music ,
        :return:
        """
        if self._startInfo is None: #
            self._startInfo = self.executor.submit(self._popen_warper)
        return self

    def kill(self , do_print = True ):
        if self._process and self._process.poll() is None:
            self._process.terminate()
            if do_print : print("NiPlay Thread being terminated.")
        else:
            if do_print : print("NiPlay Already Finished before")

    def restart(self):
        self.kill()
        self._startInfo = None
        self.start()

    def repeat_start(self):
        self._startInfo = None
        self.start()

    def _cleanup(self):
        if self._autoClean: self.kill
