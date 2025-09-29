import tkinter as tk
from tkinter import filedialog, messagebox
import time, threading, math

class PythonStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Studio 1.0")
        self.root.attributes("-fullscreen", True)  # Fullscreen

        self.workspace = None
        self.toolbox_frame = None
        self.selected = None
        self.mode = "cursor"
        self.running = False
        self.character_parts = []
        self.rotation_angle = {}

        self.show_splash()

    # ---------------- SPLASH ----------------
    def show_splash(self):
        splash = tk.Canvas(self.root, bg="black", highlightthickness=0)
        splash.pack(fill="both", expand=True)
        splash.create_rectangle(500, 300, 900, 500, outline="white", width=3)
        splash.create_text(700, 400, text="Python Studio 1.0", font=("Arial", 28, "bold"), fill="white")
        self.root.after(2000, lambda: self.show_loading(splash))

    # ---------------- LOADING ----------------
    def show_loading(self, splash):
        splash.destroy()
        load_screen = tk.Canvas(self.root, bg="white", highlightthickness=0)
        load_screen.pack(fill="both", expand=True)

        # Blue rectangle + text
        load_screen.create_rectangle(500, 200, 900, 260, outline="blue", width=3, fill="lightblue")
        load_screen.create_text(700, 230, text="Python Studio 1.0", font=("Arial", 20, "bold"), fill="black")

        # Loading squares
        squares = []
        for i in range(3):
            sq = load_screen.create_rectangle(600 + i*70, 400, 640 + i*70, 440, outline="black", width=2)
            squares.append(sq)

        def animate():
            for i in range(9):
                sq = squares[i % 3]
                load_screen.itemconfig(sq, fill="black")
                self.root.update()
                time.sleep(0.3)
                load_screen.itemconfig(sq, fill="")
            load_screen.destroy()
            self.show_menu()

        threading.Thread(target=animate).start()

    # ---------------- MAIN MENU ----------------
    def show_menu(self):
        menu = tk.Frame(self.root, bg="white")
        menu.pack(fill="both", expand=True)

        tk.Label(menu, text="Python Studio 1.0", font=("Arial", 40, "bold"), bg="white").pack(pady=60)

        tk.Button(menu, text="Create New Game", font=("Arial", 20),
                  command=lambda: [menu.destroy(), self.open_editor()]).pack(pady=15)

        tk.Button(menu, text="About", font=("Arial", 20),
                  command=lambda: messagebox.showinfo("About", "Python Studio 1.0\nCreated in Python with Tkinter")).pack(pady=15)

        tk.Button(menu, text="Exit", font=("Arial", 20), command=self.root.quit).pack(pady=15)

    # ---------------- EDITOR ----------------
    def open_editor(self):
        editor = tk.Frame(self.root, bg="white")
        editor.pack(fill="both", expand=True)

        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Home", menu=file_menu)
        file_menu.add_command(label="Add Part (Rectangle)", command=lambda: self.add_shape("block"))
        file_menu.add_command(label="Add Part (Sphere)", command=lambda: self.add_shape("sphere"))
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_map)
        file_menu.add_command(label="Exit", command=self.root.quit)

        menubar.add_command(label="Options")
        menubar.add_command(label="About")
        menubar.add_command(label="Change Game")
        menubar.add_command(label="Settings")

        # Toolbar
        toolbar = tk.Frame(editor, bg="lightgray", height=40)
        toolbar.pack(fill="x", side="top")

        tk.Button(toolbar, text="Cursor", command=lambda: self.set_mode("cursor")).pack(side="left", padx=5, pady=5)
        tk.Button(toolbar, text="Move", command=lambda: self.set_mode("move")).pack(side="left", padx=5, pady=5)
        tk.Button(toolbar, text="Resize", command=lambda: self.set_mode("resize")).pack(side="left", padx=5, pady=5)
        tk.Button(toolbar, text="Rotate", command=lambda: self.set_mode("rotate")).pack(side="left", padx=5, pady=5)

        tk.Button(toolbar, text="Run ▶", bg="green", fg="white", command=self.run_game).pack(side="left", padx=5, pady=5)
        tk.Button(toolbar, text="Stop ■", bg="red", fg="white", command=self.stop_game).pack(side="left", padx=5, pady=5)

        # Workspace (sky + baseplate)
        self.workspace = tk.Canvas(editor, bg="skyblue", highlightthickness=1, highlightbackground="black")
        self.workspace.pack(fill="both", expand=True)

        self.baseplate = self.workspace.create_rectangle(0, 650, 1920, 1080, fill="green", outline="black")

        self.workspace.bind("<Button-1>", self.select_part)
        self.workspace.bind("<B1-Motion>", self.drag_part)
        self.root.bind("<Delete>", self.delete_selected)
        self.root.bind("<BackSpace>", self.delete_selected)

        # Toolbox (full height)
        self.toolbox_frame = tk.Frame(editor, bg="lightblue", width=200)
        self.toolbox_frame.pack(fill="y", side="right")

        tk.Label(self.toolbox_frame, text="Python Toolbox", bg="lightblue", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(self.toolbox_frame, text="Add TNT", command=lambda: self.add_shape("tnt")).pack(pady=5)
        tk.Button(self.toolbox_frame, text="Add Energy", command=lambda: self.add_shape("energy")).pack(pady=5)

    # ---------------- TOOLS ----------------
    def set_mode(self, mode):
        self.mode = mode

    def add_shape(self, shape):
        if shape == "block":
            rect = self.workspace.create_rectangle(300, 300, 400, 400, fill="lightgray", outline="black", tags="part")
        elif shape == "sphere":
            oval = self.workspace.create_oval(350, 350, 420, 420, fill="orange", outline="black", tags="part")
        elif shape == "tnt":
            rect = self.workspace.create_rectangle(500, 500, 560, 560, fill="red", outline="black", tags="part")
            txt = self.workspace.create_text(530, 530, text="TNT", font=("Arial", 10, "bold"), tags=("part", "tnttext"))
            self.rotation_angle[rect] = 0
            self.rotation_angle[txt] = 0
        elif shape == "energy":
            oval = self.workspace.create_oval(600, 300, 660, 360, fill="yellow", outline="black", tags="part")

    def select_part(self, event):
        item = self.workspace.find_closest(event.x, event.y)
        if item and "part" in self.workspace.gettags(item):
            self.selected = item[0]
        else:
            self.selected = None

    def drag_part(self, event):
        if self.selected and self.mode in ["move", "cursor"]:
            x1, y1, x2, y2 = self.workspace.coords(self.selected)
            w, h = x2 - x1, y2 - y1
            self.workspace.coords(self.selected, event.x, event.y, event.x + w, event.y + h)

    def delete_selected(self, event=None):
        if self.selected:
            self.workspace.delete(self.selected)
            self.selected = None

    # ---------------- ROTATE ----------------
    def rotate_selected(self):
        if self.selected and self.mode == "rotate":
            angle = self.rotation_angle.get(self.selected, 0) + 15
            self.rotation_angle[self.selected] = angle
            # simple rotation simulation: scale bounding box
            x1, y1, x2, y2 = self.workspace.coords(self.selected)
            cx, cy = (x1+x2)/2, (y1+y2)/2
            size = (x2-x1)/2
            dx = size * math.cos(math.radians(angle))
            dy = size * math.sin(math.radians(angle))
            self.workspace.coords(self.selected, cx-dx, cy-dy, cx+dx, cy+dy)

    # ---------------- SAVE ----------------
    def save_map(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if filename:
            parts = self.workspace.find_withtag("part")
            with open(filename, "w") as f:
                for p in parts:
                    coords = self.workspace.coords(p)
                    f.write(f"{p}:{coords}\n")
            messagebox.showinfo("Saved", f"Map saved as {filename}")

    # ---------------- RUN / STOP ----------------
    def run_game(self):
        if self.running:
            return
        self.running = True

        # Roblox-like character (blocky figure)
        head = self.workspace.create_oval(100, 500, 130, 530, fill="yellow", tags="character")
        body = self.workspace.create_rectangle(100, 530, 130, 600, fill="blue", tags="character")
        left_arm = self.workspace.create_rectangle(80, 530, 100, 580, fill="blue", tags="character")
        right_arm = self.workspace.create_rectangle(130, 530, 150, 580, fill="blue", tags="character")
        left_leg = self.workspace.create_rectangle(100, 600, 115, 650, fill="green", tags="character")
        right_leg = self.workspace.create_rectangle(115, 600, 130, 650, fill="green", tags="character")

        self.character_parts = [head, body, left_arm, right_arm, left_leg, right_leg]

    def stop_game(self):
        self.running = False
        for part in self.character_parts:
            self.workspace.delete(part)
        self.character_parts.clear()

# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PythonStudio(root)
    root.mainloop()
