"""Main application window for the GoATS filter UI."""
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import ttkbootstrap as tbs
from ttkbootstrap.constants import BOTH, LEFT, RIGHT, X, Y
from ttkbootstrap.widgets.scrolled import ScrolledText

from . import presets
from .model import Filter
from .runner import (
    find_seed_executable,
    run_seedfinder,
    run_seedfinder_streaming,
    save_filter,
)
from .tabs import EndTab, GeneralTab, NetherTab, OverworldTab, SpawnTab


class GoatsApp:
    """Modern ttkbootstrap UI for configuring and running GoATS filters."""

    def __init__(self, root):
        self.root = root
        self.root.title("GoATS - Minecraft Seed Finder")
        self.root.geometry("900x750")
        self.root.minsize(800, 600)

        self.filter = Filter()
        self.vars = {}
        self.proc = None
        self._build_vars()

        self._build_menu()
        self._build_layout()

    def _build_vars(self):
        """Create Tkinter variables bound to every filter field."""
        # General
        self.vars["version"] = tk.IntVar(value=self.filter.version)
        self.vars["seeds_to_find"] = tk.IntVar(value=self.filter.seeds_to_find)
        self.vars["output_seed_info"] = tk.BooleanVar(value=self.filter.output_seed_info)
        self.vars["threads"] = tk.IntVar(value=1)

        # Toggles and simple numeric fields
        simple = {
            "bastion": bool, "bast_range": int,
            "fortress": bool, "fort_range": int, "double_spawner": bool,
            "stronghold": bool, "sh_mode": int, "sh_dist": int, "sh_ocean": bool,
            "sh_x": int, "sh_z": int, "sh_margin": int,
            "village": bool, "village_range": int,
            "ruined_portal": bool, "rp_range": int, "lava_portal": bool,
            "lava_pool": bool, "lava_range": int, "pool_count": int,
            "buried_treasure": bool, "bt_inclusion": int, "bt_exclusion": int,
            "bt_count_min": int, "bt_count_max": int,
            "spawn_point": bool, "spawn_range": int, "accurate_spawn": bool,
            "zero_cycle": bool,
            "shipwreck": bool, "ship_range": int,
            "magma_ravine": bool, "ravine_range": int,
            "jungle_temple": bool, "jt_range": int,
            "desert_temple": bool, "dt_range": int,
            "end_cage": bool, "max_cage": int,
        }
        for name, kind in simple.items():
            value = getattr(self.filter, name)
            self.vars[name] = (tk.BooleanVar if kind is bool else tk.IntVar)(value=value)

        # Dict-backed fields
        self._dict_vars("bast_types", self.filter.bast_types)
        self._dict_vars("fort_quad", self.filter.fort_quad, quad_labels=True)
        self._dict_vars("bast_quad", self.filter.bast_quad, quad_labels=True)
        self._dict_vars("village_biomes", self.filter.village_biomes)
        self._dict_vars("village_quad", self.filter.village_quad, quad_labels=True)
        self._dict_vars("rp", self.filter.rp_loot)
        self._dict_vars("bt", self.filter.bt_loot)
        self._dict_vars("bt_quad", self.filter.bt_quad, quad_labels=True)
        self._dict_vars("zero_directions", self.filter.zero_directions)
        self._dict_vars("zero_towers", self.filter.zero_towers)
        self._dict_vars("ship_types", self.filter.ship_types)
        self._dict_vars("ship", self.filter.ship_loot)
        self._dict_vars("ship_quad", self.filter.ship_quad, quad_labels=True)
        self._dict_vars("ravine_quad", self.filter.ravine_quad, quad_labels=True)
        self._dict_vars("jt_quad", self.filter.jt_quad, quad_labels=True)
        self._dict_vars("dt", self.filter.dt_loot)
        self._dict_vars("dt_quad", self.filter.dt_quad, quad_labels=True)

    def _dict_vars(self, base, mapping, quad_labels=False):
        if quad_labels:
            keys = ["00", "01", "10", "11"]
        else:
            keys = list(mapping.keys())
        group = {}
        for key in keys:
            value = mapping[key]
            var = (tk.BooleanVar if isinstance(value, bool) else tk.IntVar)(value=value)
            self.vars[f"{base}_{key}"] = var
            group[key] = var
        self.vars[base] = group

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Open data folder", command=self._open_data)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        self.root.config(menu=menubar)

    def _build_layout(self):
        # Top bar
        top = tbs.Frame(self.root, padding=10)
        top.pack(fill=X)

        tbs.Label(top, text="Seed Filter", font=("Segoe UI", 14, "bold")).pack(side=LEFT, padx=(0, 20))

        # Version selector
        version_frame = tbs.Frame(top)
        version_frame.pack(side=LEFT, padx=4)
        tbs.Label(version_frame, text="Version:").pack(side=LEFT)
        tbs.Combobox(
            version_frame,
            textvariable=self.vars["version"],
            values=[16, 17, 18, 19, 20],
            width=8,
            state="readonly",
        ).pack(side=LEFT, padx=4)

        # Presets
        preset_frame = tbs.Frame(top)
        preset_frame.pack(side=LEFT, padx=4)
        tbs.Label(preset_frame, text="Preset:").pack(side=LEFT)
        self.preset_var = tk.StringVar(value="Default")
        self.preset_box = tbs.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=self._preset_names(),
            width=18,
            state="readonly",
        )
        self.preset_box.pack(side=LEFT, padx=4)
        self.preset_box.bind("<<ComboboxSelected>>", lambda _e: self._load_preset(self.preset_var.get()))
        tbs.Button(preset_frame, text="Save", command=self._save_preset, bootstyle="secondary").pack(side=LEFT, padx=2)
        tbs.Button(preset_frame, text="Delete", command=self._delete_preset, bootstyle="secondary").pack(side=LEFT, padx=2)
        tbs.Button(preset_frame, text="Import", command=self._import_preset, bootstyle="secondary").pack(side=LEFT, padx=2)

        # Action buttons
        btn_frame = tbs.Frame(top)
        btn_frame.pack(side=RIGHT)
        tbs.Button(btn_frame, text="Copy code", command=self._copy_filter_code, bootstyle="info").pack(side=RIGHT, padx=4)
        tbs.Button(btn_frame, text="Generate & Run", command=self._generate_and_run, bootstyle="success").pack(side=RIGHT, padx=4)

        # Notebook with tabs
        self.notebook = tbs.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        tabs = {
            "General": GeneralTab,
            "Overworld": OverworldTab,
            "Nether": NetherTab,
            "End": EndTab,
            "Spawn": SpawnTab,
        }
        for title, TabClass in tabs.items():
            frame = tbs.Frame(self.notebook)
            self.notebook.add(frame, text=title)
            TabClass(frame, self.vars)

        # Bottom status and live output log
        bottom = tbs.Frame(self.root, padding=10)
        bottom.pack(fill=X)

        status_frame = tbs.Frame(bottom)
        status_frame.pack(fill=X, pady=(4, 0))
        self.status = tbs.Label(status_frame, text="Ready")
        self.status.pack(side=LEFT)
        tbs.Button(
            status_frame,
            text="Stop seedfinder",
            command=self._stop_seedfinder,
            bootstyle="danger",
        ).pack(side=RIGHT)

        output_frame = tbs.Labelframe(bottom, text="Seedfinder output", padding=8)
        output_frame.pack(fill=X, pady=4)
        self.output = ScrolledText(output_frame, height=8, wrap="word", font=("Consolas", 9))
        self.output.pack(fill=X)

        self._refresh_preset_list()

    def _load_preset(self, name):
        self.filter = presets.get_preset(name)
        self._sync_vars_from_filter()
        self._refresh_preset_list()
        self.status.config(text=f"Loaded preset: {name}")

    def _preset_names(self):
        """Return the current list of preset names."""
        return presets.list_presets()

    def _refresh_preset_list(self):
        """Refresh the preset combobox values and keep the current selection if possible."""
        names = self._preset_names()
        self.preset_box.configure(values=names)
        if self.preset_var.get() not in names:
            self.preset_var.set("Default")

    def _save_preset(self):
        """Save the current filter as a named user preset."""
        name = self.preset_var.get().strip()
        if not name or name == "Default":
            name = simpledialog.askstring("Save preset", "Preset name:")
        if not name:
            return
        self._apply_vars()
        presets.save_preset(name, self.filter)
        self.preset_var.set(name)
        self._refresh_preset_list()
        self.status.config(text=f"Saved preset: {name}")

    def _delete_preset(self):
        """Delete the currently selected user preset."""
        name = self.preset_var.get()
        if name == "Default":
            messagebox.showerror("Delete preset", "Cannot delete the Default preset.")
            return
        if not messagebox.askyesno("Delete preset", f"Delete preset '{name}'?"):
            return
        try:
            presets.delete_preset(name)
            self.preset_var.set("Default")
            self._refresh_preset_list()
            self.status.config(text=f"Deleted preset: {name}")
        except ValueError as exc:
            messagebox.showerror("Delete preset", str(exc))

    def _import_preset(self):
        """Import a filter code string as a user preset."""
        code = simpledialog.askstring("Import preset", "Paste the filter code string:")
        if not code:
            return
        name = simpledialog.askstring("Import preset", "Name for this preset:")
        if not name:
            return
        try:
            presets.import_preset(name, code)
            self.preset_var.set(name)
            self._load_preset(name)
            self.status.config(text=f"Imported preset: {name}")
        except Exception as exc:
            messagebox.showerror("Import error", str(exc))

    def _copy_filter_code(self):
        """Copy the current filter code to the clipboard."""
        try:
            self._apply_vars()
            code = self.filter.to_code()
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            self.root.update()
            self.status.config(text="Filter code copied to clipboard.")
        except Exception as exc:
            self.status.config(text=f"Error: {exc}")
            messagebox.showerror("Filter error", str(exc))

    def _sync_vars_from_filter(self):
        """Push filter values back into the Tkinter variables."""
        simple = {
            "version": "version", "seeds_to_find": "seeds_to_find",
            "output_seed_info": "output_seed_info",
            "bastion": "bastion", "bast_range": "bast_range",
            "fortress": "fortress", "fort_range": "fort_range", "double_spawner": "double_spawner",
            "stronghold": "stronghold", "sh_mode": "sh_mode", "sh_dist": "sh_dist", "sh_ocean": "sh_ocean",
            "sh_x": "sh_x", "sh_z": "sh_z", "sh_margin": "sh_margin",
            "village": "village", "village_range": "village_range",
            "ruined_portal": "ruined_portal", "rp_range": "rp_range", "lava_portal": "lava_portal",
            "lava_pool": "lava_pool", "lava_range": "lava_range", "pool_count": "pool_count",
            "buried_treasure": "buried_treasure", "bt_inclusion": "bt_inclusion", "bt_exclusion": "bt_exclusion",
            "bt_count_min": "bt_count_min", "bt_count_max": "bt_count_max",
            "spawn_point": "spawn_point", "spawn_range": "spawn_range", "accurate_spawn": "accurate_spawn",
            "zero_cycle": "zero_cycle",
            "shipwreck": "shipwreck", "ship_range": "ship_range",
            "magma_ravine": "magma_ravine", "ravine_range": "ravine_range",
            "jungle_temple": "jungle_temple", "jt_range": "jt_range",
            "desert_temple": "desert_temple", "dt_range": "dt_range",
            "end_cage": "end_cage", "max_cage": "max_cage",
        }
        for var_name, attr_name in simple.items():
            self.vars[var_name].set(getattr(self.filter, attr_name))

        # Stronghold is always custom-position mode when enabled
        self.vars["sh_mode"].set(2 if self.filter.stronghold else 0)

        self._sync_dict("bast_types", self.filter.bast_types)
        self._sync_dict("fort_quad", self.filter.fort_quad)
        self._sync_dict("bast_quad", self.filter.bast_quad)
        self._sync_dict("village_biomes", self.filter.village_biomes)
        self._sync_dict("village_quad", self.filter.village_quad)
        self._sync_dict("rp", self.filter.rp_loot)
        self._sync_dict("bt", self.filter.bt_loot)
        self._sync_dict("bt_quad", self.filter.bt_quad)
        self._sync_dict("zero_directions", self.filter.zero_directions)
        self._sync_dict("zero_towers", self.filter.zero_towers)
        self._sync_dict("ship_types", self.filter.ship_types)
        self._sync_dict("ship", self.filter.ship_loot)
        self._sync_dict("ship_quad", self.filter.ship_quad)
        self._sync_dict("ravine_quad", self.filter.ravine_quad)
        self._sync_dict("jt_quad", self.filter.jt_quad)
        self._sync_dict("dt", self.filter.dt_loot)
        self._sync_dict("dt_quad", self.filter.dt_quad)

    def _sync_dict(self, base, mapping):
        for key, value in mapping.items():
            self.vars[f"{base}_{key}"].set(value)

    def _apply_vars(self):
        """Read Tkinter variables back into the filter object."""
        self.filter.version = self.vars["version"].get()
        self.filter.seeds_to_find = self.vars["seeds_to_find"].get()
        self.filter.output_seed_info = self.vars["output_seed_info"].get()

        simple = {
            "bastion": "bastion", "bast_range": "bast_range",
            "fortress": "fortress", "fort_range": "fort_range", "double_spawner": "double_spawner",
            "stronghold": "stronghold", "sh_mode": "sh_mode", "sh_dist": "sh_dist", "sh_ocean": "sh_ocean",
            "sh_x": "sh_x", "sh_z": "sh_z", "sh_margin": "sh_margin",
            "village": "village", "village_range": "village_range",
            "ruined_portal": "ruined_portal", "rp_range": "rp_range", "lava_portal": "lava_portal",
            "lava_pool": "lava_pool", "lava_range": "lava_range", "pool_count": "pool_count",
            "buried_treasure": "buried_treasure", "bt_inclusion": "bt_inclusion", "bt_exclusion": "bt_exclusion",
            "bt_count_min": "bt_count_min", "bt_count_max": "bt_count_max",
            "spawn_point": "spawn_point", "spawn_range": "spawn_range", "accurate_spawn": "accurate_spawn",
            "zero_cycle": "zero_cycle",
            "shipwreck": "shipwreck", "ship_range": "ship_range",
            "magma_ravine": "magma_ravine", "ravine_range": "ravine_range",
            "jungle_temple": "jungle_temple", "jt_range": "jt_range",
            "desert_temple": "desert_temple", "dt_range": "dt_range",
            "end_cage": "end_cage", "max_cage": "max_cage",
        }
        for var_name, attr_name in simple.items():
            setattr(self.filter, attr_name, self.vars[var_name].get())

        # Stronghold is always custom-position mode when enabled
        if self.filter.stronghold:
            self.filter.sh_mode = 2

        self._apply_dict("bast_types", self.filter.bast_types)
        self._apply_dict("fort_quad", self.filter.fort_quad)
        self._apply_dict("bast_quad", self.filter.bast_quad)
        self._apply_dict("village_biomes", self.filter.village_biomes)
        self._apply_dict("village_quad", self.filter.village_quad)
        self._apply_dict("rp", self.filter.rp_loot)
        self._apply_dict("bt", self.filter.bt_loot)
        self._apply_dict("bt_quad", self.filter.bt_quad)
        self._apply_dict("zero_directions", self.filter.zero_directions)
        self._apply_dict("zero_towers", self.filter.zero_towers)
        self._apply_dict("ship_types", self.filter.ship_types)
        self._apply_dict("ship", self.filter.ship_loot)
        self._apply_dict("ship_quad", self.filter.ship_quad)
        self._apply_dict("ravine_quad", self.filter.ravine_quad)
        self._apply_dict("jt_quad", self.filter.jt_quad)
        self._apply_dict("dt", self.filter.dt_loot)
        self._apply_dict("dt_quad", self.filter.dt_quad)

    def _apply_dict(self, base, mapping):
        for key in mapping:
            mapping[key] = self.vars[f"{base}_{key}"].get()

    def _generate(self):
        try:
            self._apply_vars()
            code = self.filter.build()
            path = save_filter(code)
            self.status.config(text=f"Filter saved to {path}")
            return True
        except Exception as exc:
            self.status.config(text=f"Error: {exc}")
            messagebox.showerror("Filter error", str(exc))
            return False

    def _generate_and_run(self):
        if not self._generate():
            return
        if self.proc is not None and self.proc.poll() is None:
            self.status.config(text="Seedfinder is already running.")
            return
        if not find_seed_executable():
            self.status.config(text="seed.exe not found. Compile the seedfinder first.")
            messagebox.showerror("Missing executable", "seed.exe was not found. Run compile.bat first.")
            return

        self.output.delete("1.0", "end")
        threads = self.vars["threads"].get()
        self.status.config(text=f"Starting seedfinder with {threads} thread(s)...")
        self.proc = run_seedfinder_streaming(
            threads,
            on_line=self._on_seed_line,
            on_done=self._on_seed_done,
        )
        if self.proc is None:
            self.status.config(text="Failed to start seedfinder.")

    def _on_seed_line(self, line):
        self.root.after(0, lambda: self._append_output(line))

    def _append_output(self, line):
        self.output.insert("end", line + "\n")

    def _on_seed_done(self, error):
        self.root.after(0, lambda: self._finish_seedfinder(error))

    def _finish_seedfinder(self, error):
        if error:
            self.status.config(text=f"Error: {error}")
            messagebox.showerror("Run error", error)
        else:
            self.status.config(text="Seedfinder finished.")
        self.proc = None

    def _stop_seedfinder(self):
        if self.proc is None or self.proc.poll() is not None:
            self.status.config(text="No seedfinder is running.")
            return
        self.proc.terminate()
        self.status.config(text="Stopped seedfinder.")
        self.proc = None

    def _open_data(self):
        from .paths import DATA_DIR
        os.startfile(DATA_DIR)


def main():
    root = tbs.Window(themename="darkly", title="Seed Filter")
    app = GoatsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
