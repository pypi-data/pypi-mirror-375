# ZGame

ZGame is a simple game engine for Python. 


## Installation

```bash
pip install zgame
```

## How to use
Include this at the top of your code. 

```python
from zgame import zg
import tkinter
```

# zgame Commands

These are the available commands in zgame:

```python
zg.fill(color="white")  
# Fill the canvas with a color. Default is white. Fills the entire canvas.

zg.draw_shape(shape_type="rectangle", name="shape", color="black", x=0, y=0, size=50)
# Draws a rectangle or oval. All arguments optional.

zg.draw_text(text="Hello", x=50, y=50, name="text", size=12, color="black")
# Draws text. All arguments optional.

zg.draw_sprite(path="icon.png", name="sprite", x=0, y=0)
# Draws an image sprite. All arguments optional.

zg.move(name="shape", dx=0, dy=0)  
# Move a shape or sprite by dx/dy.

zg.goto(name="shape", x=0, y=0)  
# Move a shape or sprite to specific coordinates.

zg.delete(name="shape")  
# Delete a shape, text, or sprite.

zg.key_down(key="Return", function=lambda: print("Key pressed"))
# Bind a key to a function. Default is Return key printing a message.

zg.mouse_down(button=1, function=lambda: print("Mouse clicked"))
# Bind a mouse button click to a function or a string of code. Left click = 1

zg.collides(name1="shape", name2="shape", function=lambda: print("Collision!"))
# Checks if two items collide and runs a function.

zg.sprite_down(name="sprite", function=lambda: print("Sprite clicked"))
# Runs a function when a sprite is clicked.

zg.stop()  
# Closes the window.

zg.run()  
# Starts the window.
```

