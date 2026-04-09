import tkinter as tk
from tkinter import ttk, messagebox

# Navy blue theme
BG_CARD = "#263238"
TEXT_SECONDARY = "#90caf9"
ACCENT_RED = "#d32f2f"

class ScrollWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_CARD, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=BG_CARD)
        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.inner_frame = tk.Frame(self.canvas, bg=BG_CARD)
        self._win_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set, bg=BG_CARD)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.inner_frame.bind("<Configure>", self._update_scroll)
        self.canvas.bind("<Configure>", self._resize_window)

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_scroll))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
    
    def _update_scroll(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_window(self, event):
        w = max(event.width, self.inner_frame.winfo_reqwidth())
        self.canvas.itemconfig(self._win_id, width=w)

    def _on_scroll(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")


class CollectionScrollWidget(ScrollWidget):
    def __init__(self, parent, on_select, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_select = on_select
        self._items = []

    def set_collections(self, collections):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        self._items = list(collections)
        if not self._items:
            tk.Label(self.inner_frame, text="No collections yet", bg=BG_CARD, fg=TEXT_SECONDARY).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
            return

        self.inner_frame.grid_columnconfigure(0, weight=1)
        for index, collection in enumerate(self._items):
            name = collection.get("name", "Unnamed collection")
            collection_id = collection.get("collection_id")
            
            button_frame = tk.Frame(self.inner_frame, bg=BG_CARD, highlightthickness=0, bd=0)
            button_frame.grid(row=index, column=0, sticky="ew", padx=12, pady=8)
            button_frame.grid_columnconfigure(0, weight=1)
            
            button = tk.Button(
                button_frame,
                text=f"{collection_id}. {name}" if collection_id is not None else name,
                anchor="w",
                command=lambda item=collection: self.on_select(item),
                bg=BG_CARD,
                fg=TEXT_SECONDARY,
                relief="flat",
                font=(None, 11),
                padx=12,
                pady=10,
                activebackground="#1a237e",
                activeforeground="#e3f2fd",
                highlightthickness=0,
                bd=0
            )
            button.grid(row=0, column=0, sticky="ew")
            
            delete_btn = tk.Button(
                button_frame,
                text="✕",
                command=lambda cid=collection_id, cname=name: self._delete_collection(cid, cname),
                bg=ACCENT_RED,
                fg="white",
                relief="flat",
                width=2,
                padx=4,
                pady=0,
                activebackground="#ff6f00",
                activeforeground="white",
                highlightthickness=0,
                bd=0
            )
            delete_btn.grid(row=0, column=1, padx=(4, 0))
    
    def _delete_collection(self, collection_id, collection_name):
        if messagebox.askyesno("Delete collection", f"Delete '{collection_name}' and all its tasks?"):
            if hasattr(self, "on_delete_collection"):
                self.on_delete_collection(collection_id)
