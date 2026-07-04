"""Tab contents for the GoATS filter UI."""
from tkinter import ttk

from .components import CheckGroup, FilterSection, LabeledSpinbox, ScrollableFrame, Tooltip


class GeneralTab:
    def __init__(self, parent, vars):
        self.parent = parent
        self.vars = vars
        self._build()

    def _build(self):
        scroll = ScrollableFrame(self.parent)
        scroll.pack(fill="both", expand=True, padx=8, pady=8)
        frame = scroll.inner

        ttk.Label(frame, text="Seeds to find (-1 = unlimited)").pack(anchor="w", pady=(4, 0))
        ttk.Spinbox(frame, from_=-1, to=10000, textvariable=self.vars["seeds_to_find"], width=10).pack(anchor="w", pady=2)

        ttk.Checkbutton(frame, text="Output seed info to data/seedinfo.txt", variable=self.vars["output_seed_info"]).pack(anchor="w", pady=8)

        ttk.Label(frame, text="Threads").pack(anchor="w")
        threads_spin = ttk.Spinbox(frame, from_=1, to=64, textvariable=self.vars["threads"], width=10)
        threads_spin.pack(anchor="w", pady=2)
        Tooltip(threads_spin, "More threads search faster, but use more CPU. Don't exceed your CPU thread count.")


class OverworldTab:
    def __init__(self, parent, vars):
        self.parent = parent
        self.vars = vars
        self._build()

    def _build(self):
        scroll = ScrollableFrame(self.parent)
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        # Buried treasure
        self._bt_section(scroll.inner)

        # Shipwreck
        self._ship_section(scroll.inner)

        # Village
        self._village_section(scroll.inner)

        # Ruined portal
        self._rp_section(scroll.inner)

        # Desert temple
        self._dt_section(scroll.inner)

        # Jungle temple
        self._jt_section(scroll.inner)

        # Lava pool
        self._lava_section(scroll.inner)

        # Magma ravine
        self._ravine_section(scroll.inner)

    def _bt_section(self, parent):
        sec = FilterSection(parent, "Buried Treasure", self.vars["buried_treasure"])
        LabeledSpinbox(sec.content, "Inclusion range (chunks)", self.vars["bt_inclusion"], 0, 32)
        LabeledSpinbox(sec.content, "Exclusion range (chunks)", self.vars["bt_exclusion"], 0, 32)
        LabeledSpinbox(sec.content, "Minimum count", self.vars["bt_count_min"], 0, 8)
        LabeledSpinbox(sec.content, "Maximum count", self.vars["bt_count_max"], 0, 8)
        self._loot_grid(sec.content, ["IRON", "GOLD", "TNT", "EMERALD", "DIAMOND", "FOOD"], "bt")
        CheckGroup(sec.content, "Quadrants", ["negX negZ", "posX negZ", "negX posZ", "posX posZ"], self._quad_vars("bt"))
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

    def _ship_section(self, parent):
        sec = FilterSection(parent, "Shipwreck", self.vars["shipwreck"])
        LabeledSpinbox(sec.content, "Range (chunks)", self.vars["ship_range"], 0, 32)
        CheckGroup(sec.content, "Ship types", ["FRONT", "BACK", "FULL"], self.vars["ship_types"])
        self._loot_grid(sec.content, ["IRON", "GOLD", "EMERALD", "DIAMOND", "CARROT", "WHEAT", "TNT"], "ship")
        CheckGroup(sec.content, "Quadrants", ["negX negZ", "posX negZ", "negX posZ", "posX posZ"], self._quad_vars("ship"))
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

    def _village_section(self, parent):
        sec = FilterSection(parent, "Village", self.vars["village"])
        LabeledSpinbox(sec.content, "Range (chunks)", self.vars["village_range"], 0, 32)
        CheckGroup(sec.content, "Biomes", ["PLAINS", "DESERT", "SAVANNA", "TAIGA", "TUNDRA"], self.vars["village_biomes"])
        CheckGroup(sec.content, "Quadrants", ["negX negZ", "posX negZ", "negX posZ", "posX posZ"], self._quad_vars("village"))
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

    def _rp_section(self, parent):
        sec = FilterSection(parent, "Ruined Portal", self.vars["ruined_portal"])
        LabeledSpinbox(sec.content, "Range (chunks)", self.vars["rp_range"], 0, 32)
        ttk.Checkbutton(sec.content, text="Must have lava", variable=self.vars["lava_portal"]).pack(anchor="w", pady=2)
        self._loot_grid(sec.content, ["IRON", "GOLD", "LIGHT", "OBSIDIAN", "LOOTING"], "rp", bool_keys=["LIGHT"])
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

    def _dt_section(self, parent):
        sec = FilterSection(parent, "Desert Temple", self.vars["desert_temple"])
        LabeledSpinbox(sec.content, "Range (chunks)", self.vars["dt_range"], 0, 32)
        self._loot_grid(sec.content, ["IRON", "GOLD", "DIAMOND", "EMERALD", "GUNPOWDER", "GODAPPLE"], "dt")
        CheckGroup(sec.content, "Quadrants", ["negX negZ", "posX negZ", "negX posZ", "posX posZ"], self._quad_vars("dt"))
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

    def _jt_section(self, parent):
        sec = FilterSection(parent, "Jungle Temple", self.vars["jungle_temple"])
        LabeledSpinbox(sec.content, "Range (chunks)", self.vars["jt_range"], 0, 32)
        CheckGroup(sec.content, "Quadrants", ["negX negZ", "posX negZ", "negX posZ", "posX posZ"], self._quad_vars("jt"))
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

    def _lava_section(self, parent):
        sec = FilterSection(parent, "Lava Pool", self.vars["lava_pool"])
        LabeledSpinbox(sec.content, "Range (chunks)", self.vars["lava_range"], 0, 32)
        LabeledSpinbox(sec.content, "Minimum pools", self.vars["pool_count"], 1, 10)
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

    def _ravine_section(self, parent):
        sec = FilterSection(parent, "Magma Ravine", self.vars["magma_ravine"])
        LabeledSpinbox(sec.content, "Range (chunks)", self.vars["ravine_range"], 0, 32)
        CheckGroup(sec.content, "Quadrants", ["negX negZ", "posX negZ", "negX posZ", "posX posZ"], self._quad_vars("ravine"))
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

    def _loot_grid(self, parent, keys, prefix, bool_keys=None):
        bool_keys = set(bool_keys or [])
        frame = ttk.LabelFrame(parent, text="Minimum loot", padding=4)
        frame.pack(fill="x", pady=4)
        for i, key in enumerate(keys):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(frame, text=key).grid(row=row, column=col, sticky="w", padx=4, pady=2)
            if key in bool_keys:
                ttk.Checkbutton(frame, variable=self.vars[f"{prefix}_{key}"]).grid(row=row, column=col + 1, sticky="w", padx=4)
            else:
                ttk.Spinbox(frame, from_=0, to=64, textvariable=self.vars[f"{prefix}_{key}"], width=8).grid(row=row, column=col + 1, sticky="w", padx=4, pady=2)

    def _quad_vars(self, base):
        return {
            "negX negZ": self.vars[f"{base}_quad_00"],
            "posX negZ": self.vars[f"{base}_quad_01"],
            "negX posZ": self.vars[f"{base}_quad_10"],
            "posX posZ": self.vars[f"{base}_quad_11"],
        }


class NetherTab:
    def __init__(self, parent, vars):
        self.parent = parent
        self.vars = vars
        self._build()

    def _build(self):
        scroll = ScrollableFrame(self.parent)
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        # Bastion
        sec = FilterSection(scroll.inner, "Bastion", self.vars["bastion"])
        LabeledSpinbox(sec.content, "Range (chunks)", self.vars["bast_range"], 0, 32)
        CheckGroup(sec.content, "Types", ["BRIDGE", "TREASURE", "STABLES", "HOUSING"], self.vars["bast_types"])
        CheckGroup(sec.content, "Quadrants", ["negX negZ", "posX negZ", "negX posZ", "posX posZ"], self._quad_vars("bast"))
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

        # Fortress
        sec = FilterSection(scroll.inner, "Fortress", self.vars["fortress"])
        LabeledSpinbox(sec.content, "Range (chunks)", self.vars["fort_range"], 0, 32)
        ttk.Checkbutton(sec.content, text="Double spawner", variable=self.vars["double_spawner"]).pack(anchor="w", pady=2)
        CheckGroup(sec.content, "Quadrants", ["negX negZ", "posX negZ", "negX posZ", "posX posZ"], self._quad_vars("fort"))
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

    def _quad_vars(self, base):
        return {
            "negX negZ": self.vars[f"{base}_quad_00"],
            "posX negZ": self.vars[f"{base}_quad_01"],
            "negX posZ": self.vars[f"{base}_quad_10"],
            "posX posZ": self.vars[f"{base}_quad_11"],
        }


class EndTab:
    def __init__(self, parent, vars):
        self.parent = parent
        self.vars = vars
        self._build()

    def _build(self):
        scroll = ScrollableFrame(self.parent)
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        # Stronghold (always custom position when enabled)
        sec = FilterSection(scroll.inner, "Stronghold", self.vars["stronghold"])
        ttk.Checkbutton(sec.content, text="Ocean exposed", variable=self.vars["sh_ocean"]).pack(anchor="w", pady=2)

        coord_frame = ttk.Frame(sec.content)
        coord_frame.pack(fill="x", pady=2)
        ttk.Label(coord_frame, text="Target X").pack(side="left", padx=(0, 4))
        ttk.Spinbox(coord_frame, from_=-10000, to=10000, textvariable=self.vars["sh_x"], width=10).pack(side="left")
        ttk.Label(coord_frame, text="  ").pack(side="left", padx=2)
        ttk.Label(coord_frame, text="Z").pack(side="left", padx=(0, 4))
        ttk.Spinbox(coord_frame, from_=-10000, to=10000, textvariable=self.vars["sh_z"], width=10).pack(side="left")

        LabeledSpinbox(sec.content, "Margin (nether blocks)", self.vars["sh_margin"], 0, 1000)
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

        # Zero cycle
        sec = FilterSection(scroll.inner, "Zero Cycle Tower", self.vars["zero_cycle"])
        CheckGroup(sec.content, "Directions", ["FRONT", "BACK"], self.vars["zero_directions"])
        tower_frame = ttk.LabelFrame(sec.content, text="Allowed tower heights", padding=4)
        tower_frame.pack(fill="x", pady=4)
        for height in [76, 79, 82, 85, 88, 91, 94, 97, 100, 103]:
            ttk.Checkbutton(tower_frame, text=str(height), variable=self.vars[f"zero_towers_{height}"]).pack(side="left", padx=4)
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)

        # End cage
        sec = FilterSection(scroll.inner, "End Cage", self.vars["end_cage"])
        LabeledSpinbox(sec.content, "Max cage height (0 = no cage)", self.vars["max_cage"], 0, 100)
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)


class SpawnTab:
    def __init__(self, parent, vars):
        self.parent = parent
        self.vars = vars
        self._build()

    def _build(self):
        scroll = ScrollableFrame(self.parent)
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        sec = FilterSection(scroll.inner, "Spawn Point", self.vars["spawn_point"])
        LabeledSpinbox(sec.content, "Max distance (blocks)", self.vars["spawn_range"], 0, 500)
        ttk.Checkbutton(sec.content, text="Accurate spawn check (slow)", variable=self.vars["accurate_spawn"]).pack(anchor="w", pady=2)
        sec.apply_state()
        sec.frame.pack(fill="x", pady=6)
