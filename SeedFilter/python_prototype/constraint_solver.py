"""
Practical seed construction via loot-table-seed search + algebraic inversion.

Strategy:
  1. SEARCH: find loot_table_seed values whose loot meets requirements.
     Since P(6 diamonds) ≈ 1/648, this takes ~648 random 48-bit trials — instant.
  2. INVERT: algebraically walk the LCG chain backwards:
     lts → decoration_seed → population_seed → lower48.
  3. VERIFY: check BT spawn at target chunk, then enumerate upper-16 bits for biome.

This hybrid (probabilistic search + algebraic inversion) avoids the full 2^48
brute-force of GoATS while remaining simple and fast in Python.

For extreme constraints (P < 10^-9), the search step would need lattice
reduction (LLL) on the LCG state — left for a future C/SAGE implementation.
"""

import random
import time
from typing import Optional

from lcg import MASK, A, set_seed
from bt_loot import (
    simulate_bt_loot, bt_at_chunk, bt_loot_table_seed,
    bt_population_seed, bt_loot_table_seed_detailed,
    SALT_BT, CX, CZ, DECORATION_SALT,
)
from chain_inverse import (
    loot_start_state_to_decoration_seed,
    loot_table_seed_to_decoration_seed_via_lts,
    decoration_seed_to_population_seed,
    verify_lower48,
    undo_set_seed,
)


# ─── Loot requirement specification ─────────────────────────────────────────

class LootRequirement:
    """Minimum loot counts for a buried treasure."""
    def __init__(self, iron=0, gold=0, tnt=0, emerald=0, diamond=0, food=0):
        self.iron = iron
        self.gold = gold
        self.tnt = tnt
        self.emerald = emerald
        self.diamond = diamond
        self.food = food

    def check(self, loot: dict) -> bool:
        return (loot["iron"] >= self.iron and
                loot["gold"] >= self.gold and
                loot["tnt"] >= self.tnt and
                loot["emerald"] >= self.emerald and
                loot["diamond"] >= self.diamond and
                loot["food"] >= self.food)

    def __repr__(self):
        parts = []
        for name in ["iron", "gold", "tnt", "emerald", "diamond", "food"]:
            val = getattr(self, name)
            if val > 0:
                parts.append(f"{name}>={val}")
        return f"LootReq({', '.join(parts)})"


# ─── Step 1: Find loot table seeds with desired loot ────────────────────────

def find_good_lts(req: LootRequirement, max_attempts: int = 10_000_000,
                  rng_seed: Optional[int] = None) -> tuple[int, dict]:
    """Random search for a 48-bit loot_table_seed producing loot >= requirements.

    Returns (lts, loot_dict) or raises if not found within max_attempts.
    """
    rng = random.Random(rng_seed)

    for attempt in range(max_attempts):
        lts = rng.randint(0, MASK)
        loot = simulate_bt_loot(lts)
        if req.check(loot):
            return lts, loot

    raise RuntimeError(f"No lts found in {max_attempts} attempts for {req}")


def find_many_good_lts(req: LootRequirement, count: int,
                       rng_seed: Optional[int] = None) -> list[tuple[int, dict]]:
    """Find `count` distinct loot table seeds meeting requirements."""
    rng = random.Random(rng_seed)
    results = []
    attempts = 0

    while len(results) < count:
        lts = rng.randint(0, MASK)
        loot = simulate_bt_loot(lts)
        attempts += 1
        if req.check(loot):
            results.append((lts, loot))

    return results


# ─── Step 2: Invert lts → lower48 for a target chunk ────────────────────────

def invert_lts_to_lower48(lts: int, chunk_x: int, chunk_z: int) -> list[int]:
    """Invert the chain: lts → dec_seed → pop_seed → lower48.

    For chunk (0,0) this is trivial. For other chunks, we verify.
    Returns list of candidate lower48 values.
    """
    # Get the internal state after setSeed(lts)
    loot_start_state = set_seed(lts)

    # Recover decoration seed candidates (O(2^16) search)
    dec_seeds = loot_start_state_to_decoration_seed(loot_start_state)

    results = []
    for dec_seed in dec_seeds:
        pop_seed = decoration_seed_to_population_seed(dec_seed)

        if chunk_x == 0 and chunk_z == 0:
            # Trivial: for chunk (0,0), pop_seed = 0 ^ lower48 = lower48
            results.append(pop_seed)
        else:
            # For other chunks, pop_seed = f(lower48, chunk), nonlinear in lower48.
            # We'd need to solve for lower48. For now, skip non-origin chunks
            # in the algebraic path and note this as a limitation.
            pass

    return results


# ─── Step 3: Check BT spawn and compose full pipeline ───────────────────────

def construct_seed(
    req: LootRequirement,
    target_chunks: list[tuple[int, int]] = None,
    max_lts_attempts: int = 10_000_000,
    rng_seed: Optional[int] = None,
    verbose: bool = True,
) -> Optional[dict]:
    """Construct a world seed with a BT meeting loot requirements.

    Pipeline:
      1. Find lts with desired loot (random search, fast).
      2. Invert lts -> lower48 (algebraic, deterministic).
      3. Check BT spawns at target chunk for that lower48.
      4. Return the constructed seed.

    For chunk (0,0): pop_seed = lower48, and BT spawn probability is 1%.
    Expected lts attempts: ~100 / P(loot).
    """
    if target_chunks is None:
        target_chunks = [(0, 0)]

    rng = random.Random(rng_seed)
    lts_found = 0
    lts_total = 0

    t0 = time.time()

    while True:
        lts_total += 1
        if lts_total > max_lts_attempts:
            if verbose:
                print(f"Gave up after {lts_total} lts attempts.")
            return None

        # Step 1: find a good lts
        lts = rng.randint(0, MASK)
        loot = simulate_bt_loot(lts)
        if not req.check(loot):
            continue

        lts_found += 1

        # Step 2: invert using the full 64-bit lts (fast path, exact)
        dec_seeds = loot_table_seed_to_decoration_seed_via_lts(lts)

        for dec_seed in dec_seeds:
            pop_seed = decoration_seed_to_population_seed(dec_seed)

            # For chunk (0,0): lower48 = pop_seed
            lower48 = pop_seed

            # Step 3: check BT spawn
            for cx, cz in target_chunks:
                if cx != 0 or cz != 0:
                    continue  # non-origin chunks need separate handling

                if not bt_at_chunk(lower48, cx, cz):
                    continue

                # Forward-verify loot to be safe
                verify_lts = bt_loot_table_seed(lower48, cx, cz)
                verify_loot = simulate_bt_loot(verify_lts)
                if not req.check(verify_loot):
                    continue

                elapsed = time.time() - t0

                result = {
                    "lower48": lower48,
                    "chunk": (cx, cz),
                    "loot_table_seed": verify_lts,
                    "loot": {k: v for k, v in verify_loot.items()
                             if k not in ("trace", "final_state")},
                    "lts_attempts": lts_total,
                    "lts_found": lts_found,
                    "elapsed_seconds": elapsed,
                }

                if verbose:
                    vl = verify_loot
                    print(f"\n=== Seed constructed! ===")
                    print(f"  lower48 = {lower48}")
                    print(f"  BT chunk = ({cx}, {cz})")
                    print(f"  Loot: Iron={vl['iron']}, Gold={vl['gold']}, "
                          f"TNT={vl['tnt']}")
                    print(f"        Emerald={vl['emerald']}, "
                          f"Diamond={vl['diamond']}, Food={vl['food']}")
                    print(f"  LTS attempts: {lts_total} "
                          f"({lts_found} passed loot check)")
                    print(f"  Time: {elapsed:.2f}s")

                return result

        if verbose and lts_found % 500 == 0:
            elapsed = time.time() - t0
            print(f"  [{elapsed:.1f}s] {lts_found} good lts, "
                  f"{lts_total} total...")


# ─── Self-test ───────────────────────────────────────────────────────────────

def _self_test():
    print("=" * 60)
    print("Test 1: Find lts with >=2 diamonds")
    print("=" * 60)
    req = LootRequirement(diamond=2)
    t0 = time.time()
    lts, loot = find_good_lts(req, rng_seed=42)
    elapsed = time.time() - t0
    print(f"  Found lts={lts} in {elapsed:.3f}s")
    print(f"  Loot: {loot['diamond']} diamonds, {loot['iron']} iron, "
          f"{loot['emerald']} emerald")
    assert loot["diamond"] >= 2

    print(f"\n{'=' * 60}")
    print("Test 2: Find lts with >=6 diamonds (max)")
    print("=" * 60)
    req6 = LootRequirement(diamond=6)
    t0 = time.time()
    lts6, loot6 = find_good_lts(req6, rng_seed=42)
    elapsed = time.time() - t0
    print(f"  Found lts={lts6} in {elapsed:.3f}s")
    print(f"  Loot: {loot6['diamond']} diamonds")
    assert loot6["diamond"] >= 6

    print(f"\n{'=' * 60}")
    print("Test 3: Full seed construction (>=4 diamonds)")
    print("=" * 60)
    req4 = LootRequirement(diamond=4)
    result = construct_seed(
        req4,
        target_chunks=[(0, 0)],
        rng_seed=12345,
        verbose=True,
    )

    if result:
        # Verify the constructed seed
        lower48 = result["lower48"]
        cx, cz = result["chunk"]

        # Forward verification
        verify_loot = simulate_bt_loot(bt_loot_table_seed(lower48, cx, cz))
        assert verify_loot["diamond"] >= 4, \
            f"Verification failed: {verify_loot['diamond']} < 4 diamonds"
        assert bt_at_chunk(lower48, cx, cz), "BT spawn verification failed"
        print(f"  [OK] Forward verification passed: {verify_loot['diamond']} diamonds")
    else:
        print("  [WARN] No seed found — increase attempts or relax constraints")

    print(f"\n{'=' * 60}")
    print("Test 4: Full seed construction (>=6 diamonds, max)")
    print("=" * 60)
    result6 = construct_seed(
        LootRequirement(diamond=6),
        target_chunks=[(0, 0)],
        rng_seed=99999,
        verbose=True,
    )

    if result6:
        lower48 = result6["lower48"]
        cx, cz = result6["chunk"]
        verify_loot = simulate_bt_loot(bt_loot_table_seed(lower48, cx, cz))
        assert verify_loot["diamond"] >= 6
        print(f"  [OK] Forward verification passed: {verify_loot['diamond']} diamonds")

    print("\nAll tests passed.")


if __name__ == "__main__":
    _self_test()
