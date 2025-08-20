import sys
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading
import time
import os

class SplashScreen(tk.Toplevel):
    def __init__(self, master=None, gif_path='splash.gif', icon_path='iconn.ico', sound_path=None, duration=2.5, **kwargs):
        super().__init__(master, **kwargs)
        self.overrideredirect(True)
        self.configure(bg='white')
        self.duration = duration
        self.gif_path = resource_path(gif_path)
        self.sound_path = sound_path
        self.frames = []
        self.frame_index = 0
        self.label = tk.Label(self, bg='white')
        self.label.pack()
        self.icon_path = icon_path
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
        self.load_gif()
        self.attributes('-alpha', 0.0)
        self.fade_in()
        self.after(0, self.play_gif)
        if sound_path and os.path.exists(sound_path):
            threading.Thread(target=self.play_sound, daemon=True).start()
        self.after(int(self.duration * 1000), self.fade_out)

    def load_gif(self):
        im = Image.open(self.gif_path)
        self.frames = []
        width, height = 340, 300
        for frame in ImageSequence.Iterator(im):
            # Растянуть содержимое кадра по ширине
            orig = frame.copy().convert('RGBA')
            stretched = orig.resize((width, height), Image.LANCZOS)
            self.frames.append(ImageTk.PhotoImage(stretched))
        self.geometry(f"{width}x{height}+{self.winfo_screenwidth()//2-width//2}+{self.winfo_screenheight()//2-height//2}")
    def fade_in(self):
        for alpha in range(0, 101, 5):
            self.attributes('-alpha', alpha/100)
            self.update()
            time.sleep(0.01)

    def play_gif(self):
        if not hasattr(self, '_playing'):
            self._playing = True
        if self.frames and self._playing:
            self.label.config(image=self.frames[self.frame_index])
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            # 0.25x скорости: задержка 240 мс на кадр (обычно 60 мс)
            self._after_id = self.after(240, self.play_gif)


    def fade_out(self):
        # Остановить анимацию гифки
        self._playing = False
        if hasattr(self, '_after_id'):
            self.after_cancel(self._after_id)
        for alpha in range(100, -1, -5):
            try:
                self.attributes('-alpha', alpha/100)
                self.update()
                time.sleep(0.01)
            except Exception:
                break
        self.destroy()
