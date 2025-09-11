"""
This module defines the hello function that greets the desired user
"""
import matplotlib
matplotlib.use("Qt5Agg") 
matplotlib.rcParams['toolbar'] = 'none' 

import random
import click
import requests 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from io import BytesIO
from PyQt5 import QtCore, QtWidgets, QtGui

@click.command()
@click.option(
    "--count",
    default=1,
    help="The number of cat to display",
)
@click.option("--frameless", 
    is_flag=True, 
    help="Hide OS window toolbar (frameless mode)."
    )
def dispcat(count:int, frameless:bool):
    """
    Displays one or more random cat images in separate windows on the current screen.

    Downloads cat images from TheCatAPI and displays each image in a new matplotlib window.
    Windows are positioned randomly within the available screen area. Optionally, the OS window
    toolbar can be hidden for a frameless display.

    Args:
        count (int): The number of cat images to display.
        frameless (bool): If True, windows are shown without OS window toolbars.
    """
    
    tens = count//10
    
    results = []
    for ten in range(tens+1):
        results.extend(requests.get(f"https://api.thecatapi.com/v1/images/search?limit={10}").json())
        # limit = count - tens*10 if ten==tens else 10
    
    # Get QApplication instance
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    # Detect the "current" screen (the one with the cursor / active window)
    screen = app.screenAt(QtGui.QCursor.pos()) or app.primaryScreen()
    geo = screen.availableGeometry()

    
    for i, cat in zip(range(count), results):
        # img = mpimg.imread(cat['url'])
        response = requests.get(cat['url'])
        img = Image.open(BytesIO(response.content))
        
        w, h = img.size
        
        dpi=100
        
        fig = plt.figure(figsize=(w/dpi, h/dpi), dpi=dpi)                 # ← no num arg: guarantees a NEW window
        ax = fig.add_axes([0, 0, 1, 1])   
        ax.imshow(img)
        ax.axis("off")
        
        try:
            fig.canvas.manager.set_window_title(f"Image {i+1}")
        except Exception:
            pass
        
        mngr = plt.get_current_fig_manager()
        
        # no border zone
        if frameless:
            window = mngr.window
            window.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # no title bar, no buttons
            window.resize(w, h)
        
        max_x = geo.x() + geo.width() - w
        max_y = geo.y() + geo.height() - h
        
        x = random.randint(geo.x(), max(max_x, geo.x()))
        y = random.randint(geo.y(), max(max_y, geo.y()))
        
        try:
            mngr.window.move(x, y)  # Tk geometry string
        except Exception as e:
            print("Could not move window:", e)
        
        plt.show(block=False)
        plt.pause(0.05) 
    plt.show()

if __name__ == "__main__":
    dispcat()
