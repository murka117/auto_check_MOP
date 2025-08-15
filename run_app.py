# Запуск приложения с splash-экраном
import tkinter as tk
from splash_screen import SplashScreen

def start_main_app():
    from auto_check import App
    app = App()
    # Центрируем основное окно
    app.update_idletasks()
    w = app.winfo_width()
    h = app.winfo_height()
    sw = app.winfo_screenwidth()
    sh = app.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    app.geometry(f"{w}x{h}+{x}+{y}")
    app.deiconify()
    app.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    def on_splash_close():
        root.destroy()
        start_main_app()
    splash = SplashScreen(master=root, gif_path='splash.gif', icon_path='iconn.ico', duration=2.5)
    splash.after(int(splash.duration * 1000), on_splash_close)
    splash.mainloop()
