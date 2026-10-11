import tkinter as tk
from app import InteractiveMapApp


def main():
    root = tk.Tk()
    InteractiveMapApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()