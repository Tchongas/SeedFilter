"""
Quick end-to-end test of two approaches:
  A) Brute force: random lower48, scan chunks near spawn, check loot
  B) Algebraic:   find good lts, invert chain, check BT spawn
"""
import sys
import random
import time

from lcg import MASK
from bt_loot import (
    simulate_bt_loot, simulate_bt_full, bt_at_chunk,
    bt_loot_table_seed, bt_population_seed,
)
from chain_inverse import (
    loot_table_seed_to_decoration_seed_via_lts,
    decoration_seed_to_population_seed,
)

P = lambda *a, **k: print(*a, **k, flush=True)

SCAN_RANGE = 4  # scan chunks -4..+4 in both axes (81 chunks)
MIN_DIAMONDS = 4


# =====================================================================
# Approach A: brute force over lower48 (same logic as GoATS, in Python)
# =====================================================================
def brute_force_search(min_diamonds, scan_range, rng_seed=42, limit=500_000):
    P(f"\n{'='*60}")
    P(f"Approach A: Brute force (random lower48, scan {(2*scan_range+1)**2} chunks)")
    P(f"  Requirement: >= {min_diamonds} diamonds")
    P(f"{'='*60}")

    rng = random.Random(rng_seed)
    t0 = time.time()
    total = 0
    bt_found_total = 0

    while total < limit:
        total += 1
        lower48 = rng.randint(0, MASK)

        # Scan nearby chunks for BTs
        for cx in range(-scan_range, scan_range + 1):
            for cz in range(-scan_range, scan_range + 1):
                if not bt_at_chunk(lower48, cx, cz):
                    continue
                bt_found_total += 1

                # BT exists at (cx, cz) — check loot
                loot = simulate_bt_full(lower48, cx, cz)
                if loot["diamond"] >= min_diamonds:
                    elapsed = time.time() - t0
                    P(f"\n  FOUND! lower48 = {lower48}")
                    P(f"    BT chunk = ({cx}, {cz})")
                    P(f"    block pos = ({cx*16+9}, {cz*16+9})")
                    P(f"    Iron={loot['iron']}, Gold={loot['gold']}, "
                      f"TNT={loot['tnt']}")
                    P(f"    Emerald={loot['emerald']}, Diamond={loot['diamond']}, "
                      f"Food={loot['food']}")
                    P(f"    Seeds checked: {total}")
                    P(f"    BTs encountered: {bt_found_total}")
                    P(f"    Time: {elapsed:.3f}s")
                    return lower48, (cx, cz), loot

        if total % 5000 == 0:
            P(f"  [{time.time()-t0:.1f}s] {total} seeds, "
              f"{bt_found_total} BTs found so far...")

    P(f"  No result in {limit} attempts.")
    return None


# =====================================================================
# Approach B: algebraic (find lts -> invert -> check BT)
# Only for chunk (0,0) where pop_seed = lower48
# =====================================================================
def algebraic_search(min_diamonds, rng_seed=42, limit=500_000):
    P(f"\n{'='*60}")
    P(f"Approach B: Algebraic (find good lts, invert chain)")
    P(f"  Requirement: >= {min_diamonds} diamonds")
    P(f"  Target: chunk (0, 0) [pop_seed = lower48]")
    P(f"{'='*60}")

    rng = random.Random(rng_seed)
    t0 = time.time()
    total = 0
    loot_hits = 0

    while total < limit:
        total += 1
        lts = rng.randint(0, MASK)
        loot = simulate_bt_loot(lts)
        if loot["diamond"] < min_diamonds:
            continue
        loot_hits += 1

        # Invert: lts -> dec_seed -> pop_seed -> lower48
        dec_seeds = loot_table_seed_to_decoration_seed_via_lts(lts)
        for ds in dec_seeds:
            lower48 = decoration_seed_to_population_seed(ds)

            # Check BT at chunk (0,0)
            if bt_at_chunk(lower48, 0, 0):
                # Forward verify
                v_lts = bt_loot_table_seed(lower48, 0, 0)
                v_loot = simulate_bt_loot(v_lts)
                if v_loot["diamond"] >= min_diamonds:
                    elapsed = time.time() - t0
                    P(f"\n  FOUND! lower48 = {lower48}")
                    P(f"    BT chunk = (0, 0)")
                    P(f"    Iron={v_loot['iron']}, Gold={v_loot['gold']}, "
                      f"TNT={v_loot['tnt']}")
                    P(f"    Emerald={v_loot['emerald']}, "
                      f"Diamond={v_loot['diamond']}, Food={v_loot['food']}")
                    P(f"    LTS searched: {total} ({loot_hits} passed loot)")
                    P(f"    Time: {elapsed:.3f}s")
                    return lower48, (0, 0), v_loot

        if loot_hits % 100 == 0:
            P(f"  [{time.time()-t0:.1f}s] {loot_hits} good lts, {total} total")

    P(f"  No result in {limit} attempts.")
    return None


# =====================================================================
if __name__ == "__main__":
    P("Minecraft BT Seed Constructor - Prototype\n")

    # Run brute force
    result_a = brute_force_search(MIN_DIAMONDS, SCAN_RANGE, rng_seed=42)

    # Run algebraic
    result_b = algebraic_search(MIN_DIAMONDS, rng_seed=42)

    # Compare
    if result_a and result_b:
        P(f"\n{'='*60}")
        P("Comparison:")
        P(f"  Brute force found lower48={result_a[0]} at chunk {result_a[1]}")
        P(f"  Algebraic  found lower48={result_b[0]} at chunk {result_b[1]}")
