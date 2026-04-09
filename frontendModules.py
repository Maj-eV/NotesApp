import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, simpledialog

from dataIO import init_local_data, get_collection_records, get_tasks, add_collection, add_task, delete_task, delete_collection, mark_task_complete
from scrollView import CollectionScrollWidget, ScrollWidget
import os

# Navy blue theme colors
PRIMARY_DARK = "#0d47a1"
PRIMARY_LIGHT = "#1565c0"
BG_DARK = "#1a3a52"
BG_CARD = "#263238"
TEXT_PRIMARY = "white"
TEXT_SECONDARY = "#90caf9"
TEXT_MUTED = "#b0bec5"
ACCENT_RED = "#d32f2f"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NotesApp")
        self.geometry("500x400")
        self.resizable(True, True)
        self.minsize(300, 200)
        self.configure(bg=BG_DARK)
        self._base_width = 500
        self._base_height = 400
        self._configure_responsive_fonts()
        self.current_user = None
        self.selected_collection = None

        container = tk.Frame(self, bg=BG_DARK)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in (LogIn, Register, TaskList, CollectionSelection):
            frame = PageClass(container, self)
            self.frames[PageClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.bind("<Configure>", self._on_resize)
        self.show_frame(LogIn)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    def _configure_responsive_fonts(self):
        self._default_font = tkfont.nametofont("TkDefaultFont")
        self._text_font = tkfont.nametofont("TkTextFont")
        self._fixed_font = tkfont.nametofont("TkFixedFont")
        self._base_default_size = self._default_font.cget("size")
        self._base_text_size = self._text_font.cget("size")
        self._base_fixed_size = self._fixed_font.cget("size")

    def _on_resize(self, event):
        if event.widget is not self:
            return

        width_scale = self.winfo_width() / self._base_width
        height_scale = self.winfo_height() / self._base_height
        scale = max(1.0, min(width_scale, height_scale))

        self._default_font.configure(size=max(9, int(self._base_default_size * scale)))
        self._text_font.configure(size=max(9, int(self._base_text_size * scale)))
        self._fixed_font.configure(size=max(9, int(self._base_fixed_size * scale)))

        for frame in self.frames.values():
            if hasattr(frame, "set_scale"):
                frame.set_scale(scale)

class CollectionSelection(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = tk.Label(self, text="Your collections", bg=BG_DARK, fg=TEXT_PRIMARY, font=(None, 14, "bold"))
        self.title_label.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.collection_widget = CollectionScrollWidget(self, self.open_collection)
        self.collection_widget.on_delete_collection = self.delete_collection
        self.collection_widget.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)

        button_frame = tk.Frame(self, bg=BG_DARK)
        button_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(8, 16))
        button_frame.grid_columnconfigure(0, weight=1)
        
        self.new_collection_button = tk.Button(
            button_frame, text="+ New collection", command=self.new_collection,
            bg=PRIMARY_DARK, fg=TEXT_PRIMARY, relief="flat", padx=12, pady=8,
            activebackground=PRIMARY_LIGHT, activeforeground=TEXT_PRIMARY
        )
        self.new_collection_button.grid(row=0, column=0, sticky="ew", pady=5)
        
        self.back_button = tk.Button(
            button_frame, text="Log out", command=self.log_out,
            bg=PRIMARY_LIGHT, fg=TEXT_PRIMARY, relief="flat", padx=12, pady=8,
            activebackground=PRIMARY_DARK, activeforeground=TEXT_PRIMARY
        )
        self.back_button.grid(row=1, column=0, sticky="ew")

    def on_show(self):
        user = self.controller.current_user
        collections = get_collection_records(user) if user else []
        self.collection_widget.set_collections(collections)

    def open_collection(self, collection):
        self.controller.selected_collection = collection
        self.controller.show_frame(TaskList)

    def log_out(self):
        self.controller.current_user = None
        self.controller.selected_collection = None
        self.controller.show_frame(LogIn)

    def new_collection(self):
        name = simpledialog.askstring("New Collection", "Collection name:")
        if name:
            try:
                add_collection(self.controller.current_user, name)
                self.on_show()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_collection(self, collection_id):
        try:
            delete_collection(self.controller.current_user, collection_id)
            self.on_show()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class TaskList(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header_label = tk.Label(self, text="Tasks", bg=BG_DARK, fg=TEXT_PRIMARY, font=(None, 14, "bold"))
        self.header_label.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.task_widget = ScrollWidget(self)
        self.task_widget.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)

        button_frame = tk.Frame(self, bg=BG_DARK)
        button_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(8, 16))
        button_frame.grid_columnconfigure(0, weight=1)
        
        self.add_task_button = tk.Button(
            button_frame, text="+ Add task", command=self.add_new_task,
            bg=PRIMARY_DARK, fg=TEXT_PRIMARY, relief="flat", padx=12, pady=8,
            activebackground=PRIMARY_LIGHT, activeforeground=TEXT_PRIMARY
        )
        self.add_task_button.grid(row=0, column=0, sticky="ew", pady=5)
        
        self.back_button = tk.Button(
            button_frame, text="Back to collections", command=lambda: self.controller.show_frame(CollectionSelection),
            bg=PRIMARY_LIGHT, fg=TEXT_PRIMARY, relief="flat", padx=12, pady=8,
            activebackground=PRIMARY_DARK, activeforeground=TEXT_PRIMARY
        )
        self.back_button.grid(row=1, column=0, sticky="ew")

    def on_show(self):
        for widget in self.task_widget.inner_frame.winfo_children():
            widget.destroy()

        selected_collection = self.controller.selected_collection or {}
        collection_name = selected_collection.get("name", "Unknown collection")
        collection_id = selected_collection.get("collection_id")
        user = self.controller.current_user

        self.header_label.configure(text=f"Tasks in {collection_name}")

        tasks = get_tasks(user, collection_id) if user is not None and collection_id is not None else []
        if not tasks:
            tk.Label(self.task_widget.inner_frame, text="No tasks in this collection", bg=BG_CARD, fg=TEXT_MUTED).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
            return

        self.task_widget.inner_frame.grid_columnconfigure(0, weight=1)
        for index, task in enumerate(tasks):
            title = task.get("title", "Untitled")
            content = task.get("content", "")
            completed = task.get("completion", False)
            
            task_frame = tk.Frame(self.task_widget.inner_frame, bg=BG_CARD, relief="flat", bd=0, highlightthickness=0)
            task_frame.grid(row=index, column=0, sticky="ew", padx=12, pady=8)
            task_frame.grid_columnconfigure(1, weight=1)
            
            checkbox_var = tk.BooleanVar(value=completed)
            checkbox = tk.Checkbutton(
                task_frame, variable=checkbox_var,
                command=lambda t=title, c=checkbox_var: self.toggle_task_completion(t, c.get()),
                bg=BG_CARD, fg=TEXT_PRIMARY, activebackground=BG_CARD, activeforeground=TEXT_PRIMARY,
                selectcolor=PRIMARY_DARK
            )
            checkbox.grid(row=0, column=0, padx=10, pady=(8, 2), sticky="w")
            
            label_frame = tk.Frame(task_frame, bg=BG_CARD)
            label_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(8, 2))
            label_frame.grid_columnconfigure(0, weight=1)
            
            title_text = f"✓ {title}" if completed else title
            title_color = TEXT_SECONDARY if completed else TEXT_PRIMARY
            
            tk.Label(label_frame, text=title_text, anchor="w", bg=BG_CARD, fg=title_color, font=(None, 10, "bold")).grid(row=0, column=0, sticky="ew")
            
            delete_btn = tk.Button(
                label_frame, text="✕",  command=lambda t=title: self.delete_task(t),
                bg=ACCENT_RED, fg=TEXT_PRIMARY, relief="flat", width=2, padx=4, pady=0,
                activebackground="#ff6f00", activeforeground=TEXT_PRIMARY
            )
            delete_btn.grid(row=0, column=1, padx=(8, 0))
            
            tk.Label(task_frame, text=content, anchor="nw", justify="left", wraplength=300, bg=BG_CARD, fg=TEXT_MUTED).grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))

    def add_new_task(self):
        title = simpledialog.askstring("New Task", "Task title:")
        if title:
            content = simpledialog.askstring("New Task", "Task content:")
            if content is not None:
                try:
                    collection_id = self.controller.selected_collection.get("collection_id")
                    add_task(title, self.controller.current_user, content, collection_id)
                    self.on_show()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def toggle_task_completion(self, title, completed):
        try:
            collection_id = self.controller.selected_collection.get("collection_id")
            mark_task_complete(title, self.controller.current_user, collection_id, completed)
            self.on_show()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_task(self, title):
        if messagebox.askyesno("Delete task", f"Delete '{title}'?"):
            try:
                collection_id = self.controller.selected_collection.get("collection_id")
                delete_task(title, self.controller.current_user, collection_id)
                self.on_show()
            except Exception as e:
                messagebox.showerror("Error", str(e))


class LogIn(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.form = tk.Frame(self, bg=BG_DARK)
        self.form.grid(row=1, column=0, sticky="ew", padx=20)

        self.username_label = tk.Label(self.form, text="Username:", bg=BG_DARK, fg=TEXT_PRIMARY)
        self.username_label.grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(self.form, bg=BG_CARD, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.username_entry.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.password_label = tk.Label(self.form, text="Password:", bg=BG_DARK, fg=TEXT_PRIMARY)
        self.password_label.grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(self.form, show="*", bg=BG_CARD, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.password_entry.grid(row=3, column=0, sticky="ew", pady=5)
        
        self.login_button = tk.Button(
            self.form, text="Log In", command=self.log_in,
            bg=PRIMARY_DARK, fg=TEXT_PRIMARY, relief="flat", padx=12, pady=8,
            activebackground=PRIMARY_LIGHT, activeforeground=TEXT_PRIMARY
        )
        self.login_button.grid(row=4, column=0, sticky="ew", pady=10)
        
        self.register_button = tk.Button(
            self.form, text="Register", command=lambda: controller.show_frame(Register),
            bg=PRIMARY_LIGHT, fg=TEXT_PRIMARY, relief="flat", padx=12, pady=8,
            activebackground=PRIMARY_DARK, activeforeground=TEXT_PRIMARY
        )
        self.register_button.grid(row=5, column=0, sticky="ew", pady=5)

        self.form.grid_columnconfigure(0, weight=1)

    def set_scale(self, scale: float):
        pad_small = max(5, int(5 * scale))
        pad_large = max(10, int(10 * scale))
        side_pad = max(20, int(20 * scale))

        self.form.grid_configure(padx=side_pad)
        self.username_label.grid_configure(pady=pad_small)
        self.username_entry.grid_configure(pady=pad_small)
        self.password_label.grid_configure(pady=pad_small)
        self.password_entry.grid_configure(pady=pad_small)
        self.login_button.grid_configure(pady=pad_large)

    def log_in(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            user_file = f"usrAppData_{username}.json"
            if os.path.exists(user_file):
                self.controller.current_user = username
                messagebox.showinfo("Success", "Login successful!")
                self.controller.show_frame(CollectionSelection)
            else:
                messagebox.showerror("Error", "User not found. Please register first.")
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")


class Register(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.form = tk.Frame(self, bg=BG_DARK)
        self.form.grid(row=1, column=0, sticky="ew", padx=20)
        
        self.username_label = tk.Label(self.form, text="Username:", bg=BG_DARK, fg=TEXT_PRIMARY)
        self.username_label.grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(self.form, bg=BG_CARD, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.username_entry.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.password_label = tk.Label(self.form, text="Password:", bg=BG_DARK, fg=TEXT_PRIMARY)
        self.password_label.grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(self.form, show="*", bg=BG_CARD, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.password_entry.grid(row=3, column=0, sticky="ew", pady=5)

        self.register_button = tk.Button(
            self.form, text="Register", command=self.register,
            bg=PRIMARY_DARK, fg=TEXT_PRIMARY, relief="flat", padx=12, pady=8,
            activebackground=PRIMARY_LIGHT, activeforeground=TEXT_PRIMARY
        )
        self.register_button.grid(row=5, column=0, sticky="ew", pady=5)

        self.form.grid_columnconfigure(0, weight=1)

    def set_scale(self, scale: float):
        pad_small = max(5, int(5 * scale))
        pad_large = max(10, int(10 * scale))
        side_pad = max(20, int(20 * scale))

        self.form.grid_configure(padx=side_pad)
        self.username_label.grid_configure(pady=pad_small)
        self.username_entry.grid_configure(pady=pad_small)
        self.password_label.grid_configure(pady=pad_small)
        self.password_entry.grid_configure(pady=pad_small)
        self.register_button.grid_configure(pady=pad_large)
    
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            try:
                init_local_data(username, password)
                self.controller.current_user = username
                messagebox.showinfo("Success", "Registration successful!")
                self.controller.show_frame(CollectionSelection)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
