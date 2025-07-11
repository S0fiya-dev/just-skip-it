from src.gui.video_drop import VideoDropWindow
import tkinter as tk
from tkinter import messagebox

def main():
    try:
        app = VideoDropWindow()
        app.run()
    except ImportError:
        messagebox.showerror(
            "Error", 
            "Module tkinterdnd2 not installed!\nInstall it with command: pip install tkinterdnd2"
        )

if __name__ == "__main__":
    main()