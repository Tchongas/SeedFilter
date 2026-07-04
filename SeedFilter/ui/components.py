"""Reusable UI widgets used across the GoATS filter tabs."""
import tkinter as tk
from tkinter import ttk


class Tooltip:
    """Simple hover tooltip for any widget."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        if self.tip:
            return
        try:
            x, y, _, _ = self.widget.bbox("insert")
        except (TypeError, AttributeError, tk.TclError):
            x = y = 0
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(
            self.tip,
            text=self.text,
            background="#ffffe0",
            foreground="#000000",
            relief="solid",
            borderwidth=1,
            wraplength=300,
            padding=4,
        )
        label.pack()

    def hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class FilterSection:
    """Collapsible card with a header (expand arrow + Enable checkbox + title)."""

    def __init__(self, parent, title, var, on_toggle=None, expanded=False):
        self.var = var
        self.on_toggle = on_toggle
        self.expanded = expanded

        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)

        self.header = ttk.Frame(self.frame)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.columnconfigure(0, weight=1)

        # Clickable title/arrow area
        self.title_frame = ttk.Frame(self.header)
        self.title_frame.grid(row=0, column=0, sticky="w")

        self.expand_btn = ttk.Button(
            self.title_frame,
            text="▶",
            width=2,
            command=self._toggle_expand,
        )
        self.expand_btn.pack(side="left", padx=2)

        self.title_label = ttk.Label(
            self.title_frame,
            text=title,
            font=("Segoe UI", 10, "bold"),
        )
        self.title_label.pack(side="left", padx=4)

        # Enable checkbox on the right, not part of the clickable area
        self.checkbox = ttk.Checkbutton(
            self.header,
            text="Enable",
            variable=var,
        )
        self.checkbox.grid(row=0, column=1, sticky="e", padx=4)

        # Clicking the title/arrow area toggles expansion.
        for widget in (self.title_frame, self.title_label):
            widget.bind("<Button-1>", lambda _e: self._toggle_expand())

        self.content = ttk.Frame(self.frame)
        self._trace = var.trace_add("write", lambda *_: self._on_var_change())

    def _toggle_expand(self):
        self.expanded = not self.expanded
        self.expand_btn.configure(text="▼" if self.expanded else "▶")
        if self.expanded:
            self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        else:
            self.content.grid_forget()
        self.apply_state()

    def _on_var_change(self):
        if self.var.get() and not self.expanded:
            self._toggle_expand()
        self.apply_state()
        if self.on_toggle:
            self.on_toggle()

    def apply_state(self):
        """Apply the current enabled/expanded state to all content widgets.

        Call this after all children have been added to self.content.
        """
        enabled = self.var.get()
        state = "normal" if enabled else "disabled"
        for child in self.content.winfo_children():
            self._set_state(child, state)
        header_state = "normal" if enabled else "disabled"
        for widget in (self.expand_btn, self.title_label):
            try:
                widget.configure(state=header_state)
            except tk.TclError:
                pass

    def _set_state(self, widget, state):
        try:
            widget.configure(state=state)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._set_state(child, state)


class ScrollableFrame(ttk.Frame):
    """Frame with a vertical scrollbar and mouse wheel support."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self._wheel_id = self.winfo_toplevel().bind("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_mousewheel(self, event):
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        if widget is None or not self._is_descendant(widget):
            return
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _is_descendant(self, widget):
        if widget == self:
            return True
        if widget is None:
            return False
        parent = widget.winfo_parent()
        if parent == "" or parent == ".":
            return False
        return self._is_descendant(widget._nametowidget(parent))


class LabeledSpinbox:
    """Spinbox paired with a label and optional tooltip."""

    def __init__(self, parent, label, var, from_, to, tooltip=None, width=8):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)
        ttk.Label(frame, text=label).pack(side="left")
        spin = ttk.Spinbox(frame, from_=from_, to=to, textvariable=var, width=width)
        spin.pack(side="right")
        if tooltip:
            Tooltip(spin, tooltip)


class LabeledEntry:
    """Entry paired with a label and optional tooltip."""

    def __init__(self, parent, label, var, tooltip=None, width=12):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)
        ttk.Label(frame, text=label).pack(side="left")
        entry = ttk.Entry(frame, textvariable=var, width=width)
        entry.pack(side="right")
        if tooltip:
            Tooltip(entry, tooltip)


class CheckGroup:
    """Group of checkboxes backed by a dict of booleans."""

    def __init__(self, parent, title, keys, var_dict, tooltip=None):
        frame = ttk.LabelFrame(parent, text=title, padding=4)
        frame.pack(fill="x", pady=4)
        for key in keys:
            var = var_dict[key]
            cb = ttk.Checkbutton(frame, text=key, variable=var)
            cb.pack(anchor="w", padx=4)
        if tooltip:
            Tooltip(frame, tooltip)
