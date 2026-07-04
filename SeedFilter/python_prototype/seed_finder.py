"""
Minecraft BT Seed Finder — Python prototype.

Scans random lower48 seeds, finds buried treasures near spawn,
checks loot against requirements. Equivalent to what GoATS does in C.
"""
import sys
import random
import time

from lcg import MASK
from bt_loot import simulate_bt_full, bt_at_chunk

P = lambda *a, **k: print(*a, **k, flush=True)


def find_seeds(
    min_iron=0, min_gold=0, min_tnt=0,
    min_emerald=0, min_diamond=0, min_food=0,
    bt_count=1,
    scan_range=4,
    seeds_to_find=1,
    rng_seed=None,
):
    """Find world seeds where BTs near spawn have the required loot.

    scan_range: check chunks from -scan_range to +scan_range (both axes).
                scan_range=4 means 9x9 = 81 chunks scanned per seed.
    bt_count:   how many qualifying BTs are needed per seed.
    """
    grid = [(cx, cz)
            for cx in range(-scan_range, scan_range + 1)
            for cz in range(-scan_range, scan_range + 1)]
    grid_size = len(grid)

    rng = random.Random(rng_seed)
    t0 = time.time()
    checked = 0
    found = 0
    total_bts = 0

    P(f"Seed Finder started")
    P(f"  Scan area: {2*scan_range+1}x{2*scan_range+1} chunks "
      f"({grid_size} chunks per seed)")
    P(f"  Requirements: iron>={min_iron} gold>={min_gold} tnt>={min_tnt} "
      f"emerald>={min_emerald} diamond>={min_diamond} food>={min_food}")
    P(f"  BTs needed per seed: {bt_count}")
    P(f"  Looking for {seeds_to_find} seed(s)...\n")

    while found < seeds_to_find:
        lower48 = rng.randint(0, MASK)
        checked += 1

        qualifying_bts = []

        for cx, cz in grid:
            if not bt_at_chunk(lower48, cx, cz):
                continue
            total_bts += 1

            loot = simulate_bt_full(lower48, cx, cz)

            if (loot["iron"] >= min_iron and
                loot["gold"] >= min_gold and
                loot["tnt"] >= min_tnt and
                loot["emerald"] >= min_emerald and
                loot["diamond"] >= min_diamond and
                loot["food"] >= min_food):
                qualifying_bts.append((cx, cz, loot))

        if len(qualifying_bts) >= bt_count:
            found += 1
            elapsed = time.time() - t0
            P(f"--- Seed #{found}: {lower48} ---")
            for cx, cz, loot in qualifying_bts:
                P(f"  BT at chunk ({cx}, {cz})  "
                  f"block ({cx*16+9}, {cz*16+9})")
                P(f"    Iron={loot['iron']}  Gold={loot['gold']}  "
                  f"TNT={loot['tnt']}  Emerald={loot['emerald']}  "
                  f"Diamond={loot['diamond']}  Food={loot['food']}")
            P(f"  [{elapsed:.2f}s] checked {checked} seeds, "
              f"encountered {total_bts} BTs\n")

        if checked % 10000 == 0:
            elapsed = time.time() - t0
            rate = checked / elapsed if elapsed > 0 else 0
            P(f"  ... {checked} seeds checked ({rate:.0f}/s), "
              f"{total_bts} BTs, {found} results so far  "
              f"[{elapsed:.1f}s]")

    elapsed = time.time() - t0
    P(f"Done. Found {found} seed(s) in {elapsed:.2f}s")
    P(f"  Seeds checked: {checked}")
    P(f"  BTs encountered: {total_bts}")
    rate = checked / elapsed if elapsed > 0.001 else float('inf')
    P(f"  Rate: {rate:.0f} seeds/s")


def verify_seed(lower48, chunk_x, chunk_z, label=""):
    """Forward-verify a seed: recompute everything from scratch."""
    ok = True
    if not bt_at_chunk(lower48, chunk_x, chunk_z):
        P(f"  VERIFY FAIL: no BT at chunk ({chunk_x},{chunk_z})")
        ok = False
    loot = simulate_bt_full(lower48, chunk_x, chunk_z)
    P(f"  Verify {label}: Iron={loot['iron']} Gold={loot['gold']} "
      f"TNT={loot['tnt']} Emerald={loot['emerald']} "
      f"Diamond={loot['diamond']} Food={loot['food']}"
      f"  {'OK' if ok else 'FAIL'}")
    return loot, ok


if __name__ == "__main__":
    P("=" * 60)
    P("Test 1: >= 2 diamonds (easy)")
    P("=" * 60)
    find_seeds(min_diamond=2, scan_range=4, seeds_to_find=3, rng_seed=42)

    P("\n" + "=" * 60)
    P("Test 2: >= 6 diamonds (max possible)")
    P("=" * 60)
    find_seeds(min_diamond=6, scan_range=4, seeds_to_find=3, rng_seed=42)

    P("\n" + "=" * 60)
    P("Test 3: fat seed (iron>=8, gold>=4, diamond>=4, emerald>=4)")
    P("=" * 60)
    find_seeds(min_iron=8, min_gold=4, min_diamond=4, min_emerald=4,
               scan_range=4, seeds_to_find=1, rng_seed=42)

    P("\n" + "=" * 60)
    P("Test 4: extreme (iron>=16, gold>=8, diamond>=6, emerald>=8)")
    P("=" * 60)
    find_seeds(min_iron=16, min_gold=8, min_diamond=6, min_emerald=8,
               scan_range=4, seeds_to_find=1, rng_seed=42)

    # Verify a couple of results
    P("\n" + "=" * 60)
    P("Forward verification of known results")
    P("=" * 60)
    verify_seed(62674909100445, -3, -4, "test1-seed1")
    verify_seed(190063491834415, 3, 0, "test3-6diamonds")
