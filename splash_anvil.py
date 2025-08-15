
import tkinter as tk
import time
import math

class SplashAnvil(tk.Toplevel):
    def __init__(self, master=None, on_finish=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry('400x300+600+300')
        self.canvas = tk.Canvas(self, width=400, height=300, bg='white', highlightthickness=0)
        self.canvas.pack()
        self.on_finish = on_finish
        self.mallet_angle = -30  # начальный угол молотка
        self.hit_count = 0
        self.animating = True
        self.draw_static()
        self.after(500, self.animate)

    def draw_static(self):
        c = self.canvas
        c.delete('all')
        # Наковальня
        c.create_rectangle(140, 220, 260, 250, fill='#444', outline='black', width=2)
        c.create_polygon(120, 250, 280, 250, 260, 270, 140, 270, fill='#222', outline='black', width=2)
        # Человечек (голова)
        c.create_oval(190, 120, 210, 140, fill='#FFD39B', outline='black')
        # Тело
        c.create_line(200, 140, 200, 190, width=6, fill='#888')
        # Левая рука
        c.create_line(200, 150, 170, 180, width=5, fill='#888')
        # Правая рука (с молотком)
        self.draw_mallet_arm()
        # Ноги
        c.create_line(200, 190, 180, 240, width=6, fill='#888')
        c.create_line(200, 190, 220, 240, width=6, fill='#888')

    def draw_mallet_arm(self):
        c = self.canvas
        # Плечо
        c.create_line(200, 150, 230, 170, width=5, fill='#888')
        # Предплечье с молотком (вращается)
        x0, y0 = 230, 170
        length = 50
        angle = self.mallet_angle
        x1 = x0 + length * math.cos(math.radians(angle))
        y1 = y0 + length * math.sin(math.radians(angle))
        c.create_line(x0, y0, x1, y1, width=7, fill='#888')
        # Молоток
        c.create_rectangle(x1-8, y1-8, x1+8, y1+8, fill='#222', outline='black')
        c.create_rectangle(x1-2, y1-20, x1+2, y1-8, fill='#888', outline='black')

    def animate(self):
        import math
        if not self.animating:
            return
        # Фазы: swing down, hit, swing up
        if self.mallet_angle < 60:
            self.mallet_angle += 8
            self.draw_static()
            self.after(30, self.animate)
        elif self.mallet_angle < 70:
            self.mallet_angle = 70
            self.draw_static()
            self.after(120, self.animate)
        else:
            # Удар
            self.hit_count += 1
            if self.hit_count < 3:
                self.mallet_angle = -30
                self.draw_static()
                self.after(350, self.animate)
            else:
                self.animating = False
                self.after(400, self.finish)

    def finish(self):
        if self.on_finish:
            self.on_finish()
        self.destroy()
