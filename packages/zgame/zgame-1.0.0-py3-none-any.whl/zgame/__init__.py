import tkinter as tk

class _zg:
    def __init__(self, width=500, height=500, title="zgame"):
        self.root = tk.Tk()
        self.root.title(title)
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.items = {}
        self.root.update()  # ensure canvas has proper size

    def fill(self, color="white"):
        self.canvas.delete("all")
        self.canvas.config(bg=color)
        self.canvas.create_rectangle(
            0, 0,
            self.canvas.winfo_width(),
            self.canvas.winfo_height(),
            fill=color,
            outline=color
        )

    def draw_shape(self, shape_type="rectangle", name="shape", color="black", x=0, y=0, size=50):
        if shape_type == "rectangle":
            item = self.canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline=color)
        elif shape_type == "oval":
            item = self.canvas.create_oval(x, y, x+size, y+size, fill=color, outline=color)
        self.items[name] = item

    def draw_text(self, text="Hello", x=50, y=50, name="text", size=12, color="black"):
        item = self.canvas.create_text(x, y, text=text, fill=color, font=("Arial", size))
        self.items[name] = item

    def draw_sprite(self, path="icon.png", name="sprite", x=0, y=0):
        img = tk.PhotoImage(file=path)
        self.items[name] = img
        self.canvas.create_image(x, y, image=img, anchor="nw")

    def move(self, name="shape", dx=0, dy=0):
        if name in self.items:
            self.canvas.move(self.items[name], dx, dy)

    def goto(self, name="shape", x=0, y=0):
        if name in self.items:
            coords = self.canvas.coords(self.items[name])
            if coords:
                self.canvas.move(self.items[name], x - coords[0], y - coords[1])

    def delete(self, name="shape"):
        if name in self.items:
            self.canvas.delete(self.items[name])
            del self.items[name]

    def key_down(self, key="Return", function=lambda: print("Key pressed")):
        self.root.bind(f"<{key}>", lambda e: function())

    def mouse_down(self, button=1, function=lambda: print("Mouse clicked")):
        if isinstance(function, str):
            func = lambda: eval(function, {"zg": self})
        else:
            func = function
        self.canvas.bind(f"<Button-{button}>", lambda e: func())

    def collides(self, name1="shape", name2="shape", function=lambda: print("Collision!")):
        coords1 = self.canvas.bbox(self.items.get(name1))
        coords2 = self.canvas.bbox(self.items.get(name2))
        if coords1 and coords2:
            if not (coords1[2] < coords2[0] or coords1[0] > coords2[2] or
                    coords1[3] < coords2[1] or coords1[1] > coords2[3]):
                function()

    def sprite_down(self, name="sprite", function=lambda: print("Sprite clicked")):
        if name in self.items:
            self.canvas.tag_bind(self.items[name], "<Button-1>", lambda e: function())

    def stop(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


zg = _zg()
