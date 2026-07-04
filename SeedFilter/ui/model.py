"""Build the space-separated filter code consumed by the C seedfinder."""


def quadrant_code(quad):
    """Bit-pack the four quadrants in the order the C parser expects.

    quad is a dict with keys "00", "01", "10", "11".
    """
    return (
        int(quad["11"]) * 8
        + int(quad["01"]) * 4
        + int(quad["10"]) * 2
        + int(quad["00"])
    )


def quadrant_from_code(code):
    """Return a quadrant dict from a bit-packed code."""
    return {
        "00": bool(code & 1),
        "01": bool((code >> 2) & 1),
        "10": bool((code >> 1) & 1),
        "11": bool((code >> 3) & 1),
    }


class Filter:
    """Holds every configurable field that becomes part of the filter code."""

    def __init__(self):
        # General
        self.version = 16
        self.seeds_to_find = 10
        self.output_seed_info = True

        # Bastion
        self.bastion = False
        self.bast_range = 8
        self.bast_types = {
            "BRIDGE": True,
            "TREASURE": True,
            "STABLES": True,
            "HOUSING": True,
        }
        self.bast_quad = {"00": True, "01": True, "10": True, "11": True}

        # Fortress
        self.fortress = False
        self.fort_range = 8
        self.double_spawner = False
        self.fort_quad = {"00": True, "01": True, "10": True, "11": True}

        # Stronghold
        # sh_mode: 0 = close to spawn, 1 = FSG 150/150 blind, 2 = custom position
        self.stronghold = False
        self.sh_mode = 0
        self.sh_dist = 1300
        self.sh_ocean = False
        self.sh_x = 150
        self.sh_z = 150
        self.sh_margin = 20

        # Village
        self.village = False
        self.village_range = 8
        self.village_biomes = {
            "PLAINS": True,
            "DESERT": True,
            "SAVANNA": True,
            "TAIGA": True,
            "TUNDRA": True,
        }
        self.village_quad = {"00": True, "01": True, "10": True, "11": True}

        # Ruined portal
        self.ruined_portal = False
        self.rp_range = 9
        self.lava_portal = False
        self.rp_loot = {
            "IRON": 0,
            "GOLD": 0,
            "LIGHT": False,
            "OBSIDIAN": 0,
            "LOOTING": 0,
        }

        # Lava pool
        self.lava_pool = False
        self.lava_range = 9
        self.pool_count = 1

        # Buried treasure
        self.buried_treasure = False
        self.bt_inclusion = 1
        self.bt_exclusion = 1
        self.bt_count_min = 1
        self.bt_count_max = 1
        self.bt_loot = {
            "IRON": 0,
            "GOLD": 0,
            "TNT": 0,
            "EMERALD": 0,
            "DIAMOND": 0,
            "FOOD": 0,
        }
        self.bt_quad = {"00": True, "01": True, "10": True, "11": True}

        # Spawn
        self.spawn_point = False
        self.spawn_range = 40
        self.accurate_spawn = False

        # Zero cycle
        self.zero_cycle = False
        self.zero_directions = {"FRONT": True, "BACK": True}
        self.zero_towers = {
            76: True,
            79: True,
            82: True,
            85: True,
            88: True,
            91: True,
            94: True,
            97: True,
            100: True,
            103: True,
        }

        # Shipwreck
        self.shipwreck = False
        self.ship_range = 9
        self.ship_types = {"FRONT": True, "BACK": True, "FULL": True}
        self.ship_loot = {
            "IRON": 0,
            "GOLD": 0,
            "EMERALD": 0,
            "DIAMOND": 0,
            "CARROT": 0,
            "WHEAT": 0,
            "TNT": 0,
        }
        self.ship_quad = {"00": True, "01": True, "10": True, "11": True}

        # Magma ravine
        self.magma_ravine = False
        self.ravine_range = 9
        self.ravine_quad = {"00": True, "01": True, "10": True, "11": True}

        # Jungle temple
        self.jungle_temple = False
        self.jt_range = 9
        self.jt_quad = {"00": True, "01": True, "10": True, "11": True}

        # Desert temple
        self.desert_temple = False
        self.dt_range = 9
        self.dt_loot = {
            "IRON": 0,
            "GOLD": 0,
            "DIAMOND": 0,
            "EMERALD": 0,
            "GUNPOWDER": 0,
            "GODAPPLE": 0,
        }
        self.dt_quad = {"00": True, "01": True, "10": True, "11": True}

        # End cage
        self.end_cage = False
        self.max_cage = 0

    def _append_int(self, code, value):
        return f"{code}{value} "

    def _append_bool(self, code, value):
        return f"{code}{int(value)} "

    def build(self):
        if not (20 >= self.version >= 7):
            raise ValueError("Minecraft version must be between 7 and 20")
        if self.seeds_to_find < -1:
            raise ValueError("Seeds to find must be -1 or greater")

        code = ""
        code = self._append_int(code, self.version)
        code = self._append_int(code, self.seeds_to_find)
        code = self._append_bool(code, self.output_seed_info)

        # Bastion
        code = self._append_bool(code, self.bastion)
        if self.bastion:
            code = self._append_int(code, self.bast_range)
            types = (
                self.bast_types["BRIDGE"] * 8
                + self.bast_types["TREASURE"] * 4
                + self.bast_types["STABLES"] * 2
                + self.bast_types["HOUSING"]
            )
            if not types:
                raise ValueError("At least one bastion type must be enabled")
            code = self._append_int(code, types)
            quad = quadrant_code(self.bast_quad)
            if not quad:
                raise ValueError("At least one bastion quadrant must be enabled")
            code = self._append_int(code, quad)

        # Fortress
        code = self._append_bool(code, self.fortress)
        if self.fortress:
            code = self._append_int(code, self.fort_range)
            code = self._append_bool(code, self.double_spawner)
            quad = quadrant_code(self.fort_quad)
            if not quad:
                raise ValueError("At least one fortress quadrant must be enabled")
            code = self._append_int(code, quad)

        # Stronghold
        code = self._append_bool(code, self.stronghold)
        if self.stronghold:
            code = self._append_int(code, self.sh_mode)
            code = self._append_int(code, self.sh_dist)
            code = self._append_bool(code, self.sh_ocean)
            code = self._append_int(code, self.sh_x)
            code = self._append_int(code, self.sh_z)
            code = self._append_int(code, self.sh_margin)

        # Village
        code = self._append_bool(code, self.village)
        if self.village:
            code = self._append_int(code, self.village_range)
            biome = (
                self.village_biomes["PLAINS"] * 16
                + self.village_biomes["DESERT"] * 8
                + self.village_biomes["SAVANNA"] * 4
                + self.village_biomes["TAIGA"] * 2
                + self.village_biomes["TUNDRA"]
            )
            if not biome:
                raise ValueError("At least one village biome must be enabled")
            code = self._append_int(code, biome)
            quad = quadrant_code(self.village_quad)
            if not quad:
                raise ValueError("At least one village quadrant must be enabled")
            code = self._append_int(code, quad)

        # Ruined portal
        code = self._append_bool(code, self.ruined_portal)
        if self.ruined_portal:
            code = self._append_int(code, self.rp_range)
            code = self._append_bool(code, self.lava_portal)
            code = self._append_int(code, self.rp_loot["IRON"])
            code = self._append_int(code, self.rp_loot["GOLD"])
            code = self._append_bool(code, self.rp_loot["LIGHT"])
            code = self._append_int(code, self.rp_loot["OBSIDIAN"])
            code = self._append_int(code, self.rp_loot["LOOTING"])

        # Lava pool
        code = self._append_bool(code, self.lava_pool)
        if self.lava_pool:
            code = self._append_int(code, self.lava_range)
            code = self._append_int(code, self.pool_count)

        # Buried treasure
        code = self._append_bool(code, self.buried_treasure)
        if self.buried_treasure:
            code = self._append_int(code, self.bt_inclusion)
            code = self._append_int(code, self.bt_exclusion)
            code = self._append_int(code, self.bt_count_min)
            code = self._append_int(code, self.bt_count_max)
            code = self._append_int(code, self.bt_loot["IRON"])
            code = self._append_int(code, self.bt_loot["GOLD"])
            code = self._append_int(code, self.bt_loot["TNT"])
            code = self._append_int(code, self.bt_loot["EMERALD"])
            code = self._append_int(code, self.bt_loot["DIAMOND"])
            code = self._append_int(code, self.bt_loot["FOOD"])
            quad = quadrant_code(self.bt_quad)
            if not quad:
                raise ValueError("At least one buried treasure quadrant must be enabled")
            code = self._append_int(code, quad)

        # Spawn
        code = self._append_bool(code, self.spawn_point)
        if self.spawn_point:
            code = self._append_int(code, self.spawn_range)
            code = self._append_bool(code, self.accurate_spawn)

        # Zero cycle
        code = self._append_bool(code, self.zero_cycle)
        if self.zero_cycle:
            front_back = self.zero_directions["FRONT"] * 2 + self.zero_directions["BACK"]
            if not front_back:
                raise ValueError("At least one zero-cycle direction must be enabled")
            code = self._append_int(code, front_back)
            towers = (
                self.zero_towers[76] * 512
                + self.zero_towers[79] * 256
                + self.zero_towers[82] * 128
                + self.zero_towers[85] * 64
                + self.zero_towers[88] * 32
                + self.zero_towers[91] * 16
                + self.zero_towers[94] * 8
                + self.zero_towers[97] * 4
                + self.zero_towers[100] * 2
                + self.zero_towers[103]
            )
            if not towers:
                raise ValueError("At least one zero-cycle tower must be enabled")
            code = self._append_int(code, towers)

        # Shipwreck
        code = self._append_bool(code, self.shipwreck)
        if self.shipwreck:
            code = self._append_int(code, self.ship_range)
            ship_types = (
                self.ship_types["FRONT"] * 4
                + self.ship_types["BACK"] * 2
                + self.ship_types["FULL"]
            )
            if not ship_types:
                raise ValueError("At least one shipwreck type must be enabled")
            code = self._append_int(code, ship_types)
            code = self._append_int(code, self.ship_loot["IRON"])
            code = self._append_int(code, self.ship_loot["GOLD"])
            code = self._append_int(code, self.ship_loot["EMERALD"])
            code = self._append_int(code, self.ship_loot["DIAMOND"])
            code = self._append_int(code, self.ship_loot["CARROT"])
            code = self._append_int(code, self.ship_loot["WHEAT"])
            code = self._append_int(code, self.ship_loot["TNT"])
            quad = quadrant_code(self.ship_quad)
            if not quad:
                raise ValueError("At least one shipwreck quadrant must be enabled")
            code = self._append_int(code, quad)

        # Magma ravine
        code = self._append_bool(code, self.magma_ravine)
        if self.magma_ravine:
            code = self._append_int(code, self.ravine_range)
            quad = quadrant_code(self.ravine_quad)
            if not quad:
                raise ValueError("At least one magma ravine quadrant must be enabled")
            code = self._append_int(code, quad)

        # Jungle temple
        code = self._append_bool(code, self.jungle_temple)
        if self.jungle_temple:
            code = self._append_int(code, self.jt_range)
            quad = quadrant_code(self.jt_quad)
            if not quad:
                raise ValueError("At least one jungle temple quadrant must be enabled")
            code = self._append_int(code, quad)

        # Desert temple
        code = self._append_bool(code, self.desert_temple)
        if self.desert_temple:
            code = self._append_int(code, self.dt_range)
            code = self._append_int(code, self.dt_loot["IRON"])
            code = self._append_int(code, self.dt_loot["GOLD"])
            code = self._append_int(code, self.dt_loot["DIAMOND"])
            code = self._append_int(code, self.dt_loot["EMERALD"])
            code = self._append_int(code, self.dt_loot["GUNPOWDER"])
            code = self._append_int(code, self.dt_loot["GODAPPLE"])
            quad = quadrant_code(self.dt_quad)
            if not quad:
                raise ValueError("At least one desert temple quadrant must be enabled")
            code = self._append_int(code, quad)

        # End cage
        code = self._append_bool(code, self.end_cage)
        if self.end_cage:
            code = self._append_int(code, self.max_cage)

        return code.strip()

    def to_code(self):
        """Return the space-separated filter code string."""
        return self.build()

    @classmethod
    def from_code(cls, text):
        """Parse a filter code string back into a Filter instance."""
        tokens = [int(x) for x in text.strip().split()]
        it = iter(tokens)
        f = cls()

        f.version = next(it)
        f.seeds_to_find = next(it)
        f.output_seed_info = bool(next(it))

        # Bastion
        f.bastion = bool(next(it))
        if f.bastion:
            f.bast_range = next(it)
            types = next(it)
            f.bast_types = {
                "BRIDGE": bool((types >> 3) & 1),
                "TREASURE": bool((types >> 2) & 1),
                "STABLES": bool((types >> 1) & 1),
                "HOUSING": bool(types & 1),
            }
            f.bast_quad = quadrant_from_code(next(it))

        # Fortress
        f.fortress = bool(next(it))
        if f.fortress:
            f.fort_range = next(it)
            f.double_spawner = bool(next(it))
            f.fort_quad = quadrant_from_code(next(it))

        # Stronghold
        f.stronghold = bool(next(it))
        if f.stronghold:
            f.sh_mode = next(it)
            f.sh_dist = next(it)
            f.sh_ocean = bool(next(it))
            f.sh_x = next(it)
            f.sh_z = next(it)
            f.sh_margin = next(it)

        # Village
        f.village = bool(next(it))
        if f.village:
            f.village_range = next(it)
            biome = next(it)
            f.village_biomes = {
                "PLAINS": bool((biome >> 4) & 1),
                "DESERT": bool((biome >> 3) & 1),
                "SAVANNA": bool((biome >> 2) & 1),
                "TAIGA": bool((biome >> 1) & 1),
                "TUNDRA": bool(biome & 1),
            }
            f.village_quad = quadrant_from_code(next(it))

        # Ruined portal
        f.ruined_portal = bool(next(it))
        if f.ruined_portal:
            f.rp_range = next(it)
            f.lava_portal = bool(next(it))
            f.rp_loot = {
                "IRON": next(it),
                "GOLD": next(it),
                "LIGHT": bool(next(it)),
                "OBSIDIAN": next(it),
                "LOOTING": next(it),
            }

        # Lava pool
        f.lava_pool = bool(next(it))
        if f.lava_pool:
            f.lava_range = next(it)
            f.pool_count = next(it)

        # Buried treasure
        f.buried_treasure = bool(next(it))
        if f.buried_treasure:
            f.bt_inclusion = next(it)
            f.bt_exclusion = next(it)
            f.bt_count_min = next(it)
            f.bt_count_max = next(it)
            f.bt_loot = {
                "IRON": next(it),
                "GOLD": next(it),
                "TNT": next(it),
                "EMERALD": next(it),
                "DIAMOND": next(it),
                "FOOD": next(it),
            }
            f.bt_quad = quadrant_from_code(next(it))

        # Spawn
        f.spawn_point = bool(next(it))
        if f.spawn_point:
            f.spawn_range = next(it)
            f.accurate_spawn = bool(next(it))

        # Zero cycle
        f.zero_cycle = bool(next(it))
        if f.zero_cycle:
            direction = next(it)
            f.zero_directions = {
                "FRONT": bool((direction >> 1) & 1),
                "BACK": bool(direction & 1),
            }
            towers = next(it)
            f.zero_towers = {
                76: bool((towers >> 9) & 1),
                79: bool((towers >> 8) & 1),
                82: bool((towers >> 7) & 1),
                85: bool((towers >> 6) & 1),
                88: bool((towers >> 5) & 1),
                91: bool((towers >> 4) & 1),
                94: bool((towers >> 3) & 1),
                97: bool((towers >> 2) & 1),
                100: bool((towers >> 1) & 1),
                103: bool(towers & 1),
            }

        # Shipwreck
        f.shipwreck = bool(next(it))
        if f.shipwreck:
            f.ship_range = next(it)
            ship_types = next(it)
            f.ship_types = {
                "FRONT": bool((ship_types >> 2) & 1),
                "BACK": bool((ship_types >> 1) & 1),
                "FULL": bool(ship_types & 1),
            }
            f.ship_loot = {
                "IRON": next(it),
                "GOLD": next(it),
                "EMERALD": next(it),
                "DIAMOND": next(it),
                "CARROT": next(it),
                "WHEAT": next(it),
                "TNT": next(it),
            }
            f.ship_quad = quadrant_from_code(next(it))

        # Magma ravine
        f.magma_ravine = bool(next(it))
        if f.magma_ravine:
            f.ravine_range = next(it)
            f.ravine_quad = quadrant_from_code(next(it))

        # Jungle temple
        f.jungle_temple = bool(next(it))
        if f.jungle_temple:
            f.jt_range = next(it)
            f.jt_quad = quadrant_from_code(next(it))

        # Desert temple
        f.desert_temple = bool(next(it))
        if f.desert_temple:
            f.dt_range = next(it)
            f.dt_loot = {
                "IRON": next(it),
                "GOLD": next(it),
                "DIAMOND": next(it),
                "EMERALD": next(it),
                "GUNPOWDER": next(it),
                "GODAPPLE": next(it),
            }
            f.dt_quad = quadrant_from_code(next(it))

        # End cage
        f.end_cage = bool(next(it))
        if f.end_cage:
            f.max_cage = next(it)

        return f
