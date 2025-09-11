import tkinter as tk
from PIL import Image
import requests
from tkinter import colorchooser
import turtle as t
import random as ra
from datetime import datetime
import time
now = datetime.now()
hour = now.hour
minute = now.minute
second = now.second
microsecond = now.microsecond
def save_var(local_or_name, value):
    with open (local_or_name, "w") as f:
        f.write(str(value))
def load_var(local_or_name , difault = None):
    try:
        with open (local_or_name, "r") as f:
            data = f.read().strip()
            if data == "":
                return default
            return data
        except FileNotFoundError :
            return difault
def ri (a, b):
    return ra.randint(a, b)
def key (a, b):
    t.listen()
    t.onkeypress(a, b)
def click(a):
    t.onscreenclick(a)
def getcolor(tit):
    return colorchooser.askcolor(title = tit)
def rc (a):
    return ra.choice(a)

def leftclick (a):
    t.onscreenclick(a, btn = 1)
def middleclick (a):
    t.onscreenclick(a, btn = 2)
def rightclick (a):
    t.onscreenclick(a, btn = 3)
def move (x, y):
    t.goto(x, y)
def randcolor():
    t.colormode(255)
    r = ra.randint(1, 255)
    g = ra.randint(1, 255)
    b = ra.randint(1, 255)
    t.color ((r, g, b))
def rgbcolor(r, g, b):
    t.colormode(255)
    t.color ((r, g, b))
def getping(url):
    start = time.time()
    requests.get(url)
    end = time.time()
    return round((end - start)* 1000)
def mouseX ():
    screen = t.Screen()
    return screen.cv.winfo_pointerx() - screen.cv.winfo_rootx() - screen.window_width() // 2
def mouseY():
    screen = t.Screen()
    return screen.window_height() // 2 - (screen.cv.winfo_pointery() - screen.cv.winfo_rooty())
def hidecursor():
    root = tk.Tk()
    root.config(cursor = "none")
    root.mainloop()
def shapecursor(a):
    root = tk.Tk()
    root.config (cursor = a)
    root.mainloop()
def convert_jpg(your_format, your_image_path_or_name):
    img = Image.open(your_image_path_or_name)
    img.save(f"Tpicture.{your_format}")
def upload_gif(NameOrPath, sizeWidth, sizeHight):
    screen = turtle.Screen()
    screen.register_shape(NameOrPath)
    img_turtle = turtle.Turtle()
    img = img.resize((sizeWidth, sizeHight))
    img_turtle.shape(NameOrPath)
    img_turtle.penup()
    img_turtle.goto(0, 0)
def show_picture():
    img_turtle.showturtle()
def hide_picture():
    img_turtle.hideturtle()
