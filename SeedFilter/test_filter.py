"""Quick test that the Filter model still builds the expected filter code."""
from ui.model import Filter


def main():
    f = Filter()
    f.buried_treasure = True
    f.bt_count_min = 1
    f.bt_count_max = 2
    f.bt_inclusion = 3
    f.bt_exclusion = 1
    f.bt_loot = {"IRON": 1, "GOLD": 0, "TNT": 0, "EMERALD": 0, "DIAMOND": 0, "FOOD": 0}
    f.bt_quad = {"00": True, "01": False, "10": True, "11": True}
    f.fortress = True
    f.fort_range = 8
    f.fort_quad = {"00": True, "01": True, "10": True, "11": True}
    print(f.build())


if __name__ == "__main__":
    main()
