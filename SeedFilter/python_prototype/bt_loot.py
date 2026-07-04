"""
Buried Treasure loot simulation — exact replica of buriedtreasure.c

Forward path:  world_seed + chunk_pos → loot contents
Also exposes every intermediate LCG state for the inversion pipeline.
"""

from lcg import (
    set_seed, next_bits, next_int, next_long, next_float,
    next_state, prev_state, state_to_seed, MASK, A
)

# ─── Constants ───────────────────────────────────────────────────────────────

SALT_BT = 10387320
CX = 341873128712    # region offset constant X
CZ = 132897987541    # region offset constant Z
DECORATION_SALT = 30001

# Loot pool 2: Ingots and TNT  (weight, min, max)
POOL2_TABLE = [
    (20, 1, 4),   # 0: iron
    (10, 1, 4),   # 1: gold
    ( 5, 1, 2),   # 2: tnt
]
POOL2_TOTAL_WEIGHT = sum(w for w, _, _ in POOL2_TABLE)  # 35

# Loot pool 3: Emerald, diamond, prismarine
POOL3_TABLE = [
    (5, 4, 8),    # 0: emerald
    (5, 1, 2),    # 1: diamond
    (5, 1, 5),    # 2: prismarine
]
POOL3_TOTAL_WEIGHT = sum(w for w, _, _ in POOL3_TABLE)  # 15

ITEM_NAMES = {
    "iron": 0, "gold": 1, "tnt": 2,
    "emerald": 3, "diamond": 4, "prismarine": 5,
    "food": 6,
}


# ─── Seed chain: world_seed → loot_table_seed ───────────────────────────────

def bt_population_seed(lower48: int, chunk_x: int, chunk_z: int) -> int:
    """Compute the population seed for a BT at (chunk_x, chunk_z)."""
    state = set_seed(lower48)
    state, carve_x = next_long(state)
    carve_x = carve_x | 1
    state, carve_z = next_long(state)
    carve_z = carve_z | 1

    block_x = chunk_x * 16 + 9
    block_z = chunk_z * 16 + 9

    # C code: ((bt_pos.x - 9) * carveX + (bt_pos.z - 9) * carveZ) ^ lower48
    # bt_pos.x - 9 = chunk_x * 16, bt_pos.z - 9 = chunk_z * 16
    pop_seed = ((block_x - 9) * carve_x + (block_z - 9) * carve_z) ^ lower48
    pop_seed &= MASK
    return pop_seed


def bt_loot_table_seed(lower48: int, chunk_x: int, chunk_z: int) -> int:
    """Compute the loot table seed for a BT."""
    pop_seed = bt_population_seed(lower48, chunk_x, chunk_z)
    decoration_seed = pop_seed + DECORATION_SALT

    state = set_seed(decoration_seed)
    state, lts = next_long(state)
    return lts


def bt_loot_table_seed_detailed(lower48: int, chunk_x: int, chunk_z: int) -> dict:
    """Return all intermediate values for debugging / inversion."""
    state0 = set_seed(lower48)
    state1, carve_x_raw = next_long(state0)
    carve_x = carve_x_raw | 1
    state2, carve_z_raw = next_long(state1)
    carve_z = carve_z_raw | 1

    block_x = chunk_x * 16 + 9
    block_z = chunk_z * 16 + 9

    pop_seed = ((block_x - 9) * carve_x + (block_z - 9) * carve_z) ^ lower48
    pop_seed &= MASK

    dec_seed = pop_seed + DECORATION_SALT
    state_dec = set_seed(dec_seed)
    state_after_lts, lts = next_long(state_dec)

    return {
        "lower48": lower48,
        "chunk": (chunk_x, chunk_z),
        "carve_x": carve_x,
        "carve_z": carve_z,
        "population_seed": pop_seed,
        "decoration_seed": dec_seed,
        "loot_table_seed": lts,
        "lts_internal_state": state_dec,
    }


# ─── Weighted item selection (matches C code) ───────────────────────────────

def _select_item(loot_value: int, table: list[tuple[int, int, int]]) -> int:
    """Replicate the C weighted selection loop."""
    item_id = 0
    while loot_value > 0:
        loot_value -= table[item_id][0]
        if loot_value >= 0:
            item_id += 1
    return item_id


# ─── Full loot simulation ───────────────────────────────────────────────────

def simulate_bt_loot(loot_table_seed: int) -> dict:
    """Simulate all BT loot pools from a loot table seed.

    Returns dict with item counts and a trace of every LCG call.
    """
    s = set_seed(loot_table_seed)
    trace = []  # (step_name, state_before, state_after, output)

    def tracked_next_int(state, n, label):
        s_before = state
        state, val = next_int(state, n)
        trace.append((label, s_before, state, val))
        return state, val

    iron = gold = tnt = emerald = diamond = prismarine = food = 0

    # Pool 1: Heart of the Sea — no random calls

    # Pool 2: Ingots and TNT (5-8 rolls)
    s, pool2_rolls = tracked_next_int(s, 4, "pool2_extra_rolls")
    pool2_rolls += 5

    for roll in range(pool2_rolls):
        s, loot_val = tracked_next_int(s, POOL2_TOTAL_WEIGHT, f"pool2_roll{roll}_item")
        item_id = _select_item(loot_val, POOL2_TABLE)
        _, min_c, max_c = POOL2_TABLE[item_id]
        s, extra = tracked_next_int(s, max_c - min_c + 1, f"pool2_roll{roll}_count")
        count = min_c + extra

        if item_id == 0:
            iron += count
        elif item_id == 1:
            gold += count
        elif item_id == 2:
            tnt += count

    # Pool 3: Emerald, diamond, prismarine (1-3 rolls)
    s, pool3_rolls = tracked_next_int(s, 3, "pool3_extra_rolls")
    pool3_rolls += 1

    for roll in range(pool3_rolls):
        s, loot_val = tracked_next_int(s, POOL3_TOTAL_WEIGHT, f"pool3_roll{roll}_item")
        item_id = _select_item(loot_val, POOL3_TABLE)
        _, min_c, max_c = POOL3_TABLE[item_id]
        s, extra = tracked_next_int(s, max_c - min_c + 1, f"pool3_roll{roll}_count")
        count = min_c + extra

        if item_id == 0:
            emerald += count
        elif item_id == 1:
            diamond += count
        elif item_id == 2:
            prismarine += count

    # Pool 4: Chestplate / sword (0-1 rolls)
    s, pool4_rolls = tracked_next_int(s, 2, "pool4_rolls")

    for roll in range(pool4_rolls):
        s, _ = tracked_next_int(s, 2, f"pool4_roll{roll}_item")

    # Pool 5: Fish (always 2 rolls)
    for roll in range(2):
        s, _ = tracked_next_int(s, 2, f"pool5_roll{roll}_item")
        s, fish_extra = tracked_next_int(s, 3, f"pool5_roll{roll}_count")
        food += 2 + fish_extra

    return {
        "iron": iron,
        "gold": gold,
        "tnt": tnt,
        "emerald": emerald,
        "diamond": diamond,
        "prismarine": prismarine,
        "food": food,
        "trace": trace,
        "final_state": s,
    }


def simulate_bt_full(lower48: int, chunk_x: int, chunk_z: int) -> dict:
    """End-to-end: world seed + chunk → loot contents."""
    lts = bt_loot_table_seed(lower48, chunk_x, chunk_z)
    loot = simulate_bt_loot(lts)
    loot["loot_table_seed"] = lts
    return loot


# ─── Check if a BT spawns at a given chunk ──────────────────────────────────

def bt_at_chunk(lower48: int, chunk_x: int, chunk_z: int) -> bool:
    """Does this chunk attempt to generate a BT? (1/100 chance)"""
    salt = SALT_BT
    finder_seed = lower48 + salt + chunk_x * CX + chunk_z * CZ
    state = finder_seed ^ A
    state &= MASK
    state, chance = next_float(state)
    return chance < 0.01


# ─── Self-test ───────────────────────────────────────────────────────────────

def _self_test():
    # Test that loot simulation produces valid results
    # Use a known seed and verify the chain is internally consistent
    test_seed = 123456789

    details = bt_loot_table_seed_detailed(test_seed, 0, 0)
    lts = details["loot_table_seed"]

    loot = simulate_bt_loot(lts)
    total_items = (loot["iron"] + loot["gold"] + loot["tnt"] +
                   loot["emerald"] + loot["diamond"] + loot["prismarine"] +
                   loot["food"])
    assert total_items > 0, "Loot simulation produced no items"

    # Pool 2 rolls should be 5-8
    pool2_roll_call = [t for t in loot["trace"] if t[0] == "pool2_extra_rolls"][0]
    assert 0 <= pool2_roll_call[3] <= 3, "Pool 2 extra rolls out of range"

    # Pool 3 rolls should be 1-3
    pool3_roll_call = [t for t in loot["trace"] if t[0] == "pool3_extra_rolls"][0]
    assert 0 <= pool3_roll_call[3] <= 2, "Pool 3 extra rolls out of range"

    # Verify chain inversion consistency: every state can be inverted
    for label, s_before, s_after, val in loot["trace"]:
        assert prev_state(next_state(s_before)) == s_before, \
            f"State inversion failed at {label}"

    print(f"BT loot self-test passed. Seed {test_seed}, chunk (0,0):")
    print(f"  Iron={loot['iron']}, Gold={loot['gold']}, TNT={loot['tnt']}")
    print(f"  Emerald={loot['emerald']}, Diamond={loot['diamond']}, "
          f"Prismarine={loot['prismarine']}")
    print(f"  Food={loot['food']}")
    print(f"  Total LCG calls: {len(loot['trace'])}")


if __name__ == "__main__":
    _self_test()
