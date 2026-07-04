"""
Chain inversion: recover world seed from a known-good LCG loot state.

Forward chain (buriedtreasure.c):
  lower48 → setSeed → nextLong×2 → carveX, carveZ
  pop_seed = (chunkX*16 * carveX + chunkZ*16 * carveZ) ^ lower48  [masked 48-bit]
  dec_seed = pop_seed + 30001
  setSeed(dec_seed) → nextLong → loot_table_seed
  setSeed(loot_table_seed) → ... loot pools ...

Inverse chain:
  loot_internal_state → undo setSeed → loot_table_seed
  → undo nextLong → undo setSeed → decoration_seed
  → subtract 30001 → population_seed
  → solve for lower48
"""

from lcg import (
    A, A_INV, C, MASK,
    set_seed, next_state, prev_state, state_to_seed,
    next_long, skip_back,
)
from bt_loot import DECORATION_SALT


# ─── Invert setSeed ─────────────────────────────────────────────────────────

def undo_set_seed(internal_state: int) -> int:
    """setSeed(v) does: state = (v ^ A) & MASK. Inverse: v = state ^ A."""
    return (internal_state ^ A) & MASK


# ─── Invert nextLong ─────────────────────────────────────────────────────────

def undo_next_long(state_after: int) -> int:
    """nextLong does 2 LCG steps (next(32) twice). Undo by 2 backward steps."""
    return skip_back(state_after, 2)


# ─── Full chain inversion: loot state → world seed ──────────────────────────

def loot_state_to_loot_table_seed(loot_state_after_setseed: int) -> int:
    """Given the internal state right after setSeed(loot_table_seed),
    recover loot_table_seed."""
    return undo_set_seed(loot_state_after_setseed)


def loot_table_seed_to_decoration_seed_via_lts(lts: int) -> list[int]:
    """Given the FULL 64-bit loot_table_seed, recover decoration_seed.

    Forward: setSeed(dec_seed) → state0 → next(32)→state1 → next(32)→state2
    lts = (hi << 32) + lo, where hi = signed(state1 >> 16), lo = signed(state2 >> 16).

    We know hi and lo from lts. state1's top 32 bits = hi, bottom 16 unknown.
    Enumerate 2^16 candidates for state1, check state2 matches lo.
    """
    lts_u = lts & 0xFFFFFFFFFFFFFFFF
    hi_unsigned = (lts_u >> 32) & 0xFFFFFFFF
    lo_unsigned = lts_u & 0xFFFFFFFF

    results = []
    for low16 in range(1 << 16):
        state1 = (hi_unsigned << 16) | low16
        state2 = next_state(state1)
        if (state2 >> 16) & 0xFFFFFFFF == lo_unsigned:
            state0 = prev_state(state1)
            dec_seed = undo_set_seed(state0)
            results.append(dec_seed)
    return results


def loot_start_state_to_decoration_seed(loot_start_state: int) -> list[int]:
    """Given the LCG state right after setSeed(loot_table_seed), recover dec_seed.

    setSeed(lts) only uses lts & MASK (48 bits), so we lose the upper 16 bits
    of the 64-bit lts. But we can recover dec_seed by working with LCG states.

    Forward chain:
      state0 = setSeed(dec_seed)
      state1 = LCG(state0)   → hi = state1 >> 16 (top 32 bits)
      state2 = LCG(state1)   → lo = state2 >> 16 (top 32 bits)
      lts = (hi << 32) + lo  (64-bit, with sign extension)
      loot_start = setSeed(lts) = (lts ^ A) & MASK

    We know loot_start. So lts_low48 = (loot_start ^ A) & MASK.

    From lts_low48 we extract:
      lo_unsigned = lts_low48 & 0xFFFFFFFF  (= state2 >> 16, all 32 bits known)
      hi_lower16: lower 16 bits of hi_unsigned, derived from bits 32-47 of lts_low48

    Enumerate 2^16 candidates for state2's bottom 16 bits, invert to get state1,
    verify hi's lower 16 bits match, then recover state0 → dec_seed.
    """
    lts_low48 = (loot_start_state ^ A) & MASK

    lo_unsigned = lts_low48 & 0xFFFFFFFF
    lts_upper16 = (lts_low48 >> 32) & 0xFFFF

    # Recover hi_lower16 from lts bits 32-47:
    # bits 32-47 of lts = (hi_unsigned & 0xFFFF) - borrow
    # where borrow = 1 if lo is negative (lo_unsigned >= 2^31), else 0
    lo_negative = lo_unsigned >= (1 << 31)
    hi_lower16 = (lts_upper16 + (1 if lo_negative else 0)) & 0xFFFF

    results = []
    for state2_low16 in range(1 << 16):
        state2 = (lo_unsigned << 16) | state2_low16
        state1 = prev_state(state2)
        hi_candidate = (state1 >> 16) & 0xFFFFFFFF
        if (hi_candidate & 0xFFFF) == hi_lower16:
            state0 = prev_state(state1)
            dec_seed = undo_set_seed(state0)
            results.append(dec_seed)

    return results


def decoration_seed_to_population_seed(dec_seed: int) -> int:
    """pop_seed = dec_seed - DECORATION_SALT"""
    return (dec_seed - DECORATION_SALT) & MASK


def population_seed_to_lower48(pop_seed: int, chunk_x: int, chunk_z: int) -> list[int]:
    """Recover lower48 from population seed and chunk position.

    Forward: pop_seed = (chunkX*16 * carveX + chunkZ*16 * carveZ) ^ lower48  [& MASK]
    Where carveX = nextLong(setSeed(lower48)) | 1
          carveZ = nextLong(cont'd state)     | 1

    carveX and carveZ depend on lower48, making this a nonlinear equation.

    For chunk (0,0): chunkX*16 = 0 and chunkZ*16 = 0, so pop_seed = 0 ^ lower48 = lower48.
    This is the trivial case.

    For general chunks: we enumerate all 2^48 possible lower48 values... which is too many.
    Instead, we use the structure: carveX and carveZ are deterministic functions of lower48.

    Strategy: iterate over candidate lower48 values that produce the given pop_seed.
    Since this involves brute force, we offer two modes:
    1. For chunk (0,0): direct solution
    2. For other chunks: constrained search
    """
    if chunk_x == 0 and chunk_z == 0:
        return [pop_seed]

    # For non-zero chunks, we need to search.
    # carveX and carveZ depend on lower48 through 4 LCG steps from setSeed(lower48).
    # We can't easily invert this analytically, but we can:
    # 1. If we know lower48 approximately (e.g., from other constraints), verify.
    # 2. Use the fact that carveX|1 and carveZ|1 have their LSB set.
    #
    # For now, provide a verification function and a brute-force searcher
    # for small ranges.
    return None  # caller should use verify_lower48 or targeted search


def verify_lower48(lower48: int, chunk_x: int, chunk_z: int, expected_pop_seed: int) -> bool:
    """Check if a given lower48 produces the expected population seed at (chunk_x, chunk_z)."""
    from bt_loot import bt_population_seed
    actual = bt_population_seed(lower48, chunk_x, chunk_z)
    return actual == expected_pop_seed


def find_lower48_for_pop_seed(pop_seed: int, chunk_x: int, chunk_z: int,
                               search_range: range = None) -> list[int]:
    """Brute-force search for lower48 in a range. For chunk (0,0), instant."""
    if chunk_x == 0 and chunk_z == 0:
        return [pop_seed]

    if search_range is None:
        search_range = range(1 << 48)  # full search — very slow!

    results = []
    for candidate in search_range:
        if verify_lower48(candidate, chunk_x, chunk_z, pop_seed):
            results.append(candidate)
    return results


# ─── Complete inverse pipeline ───────────────────────────────────────────────

def invert_from_loot_state(loot_internal_state: int, chunk_x: int, chunk_z: int) -> list[int]:
    """Given the internal LCG state at the start of loot generation
    (i.e., right after setSeed(loot_table_seed)), recover candidate world seeds.

    Returns list of lower-48-bit world seed candidates.
    """
    dec_seeds = loot_start_state_to_decoration_seed(loot_internal_state)

    results = []
    for dec_seed in dec_seeds:
        pop_seed = decoration_seed_to_population_seed(dec_seed)
        if chunk_x == 0 and chunk_z == 0:
            results.append(pop_seed)
        else:
            if verify_lower48(pop_seed, chunk_x, chunk_z, pop_seed):
                results.append(pop_seed)

    return results


# ─── Self-test ───────────────────────────────────────────────────────────────

def _self_test():
    from bt_loot import bt_loot_table_seed_detailed, simulate_bt_loot

    test_seed = 123456789
    cx, cz = 0, 0

    # Forward chain
    details = bt_loot_table_seed_detailed(test_seed, cx, cz)
    lts = details["loot_table_seed"]
    lts_state = details["lts_internal_state"]  # state after setSeed(dec_seed)

    # Simulate loot to get the state after setSeed(lts)
    loot = simulate_bt_loot(lts)
    # The first trace entry's state_before is the state after setSeed(lts)
    loot_start_state = loot["trace"][0][1]

    # Test 1: undo setSeed on loot start state recovers lower 48 bits of lts
    recovered_lts_low48 = loot_state_to_loot_table_seed(loot_start_state)
    assert recovered_lts_low48 == (lts & MASK), \
        f"LTS low48 recovery failed: {recovered_lts_low48} != {lts & MASK}"
    print(f"[OK] Recovered loot_table_seed lower 48 bits: {recovered_lts_low48}")

    # Test 2a: recover decoration seed from full 64-bit lts
    dec_seeds_full = loot_table_seed_to_decoration_seed_via_lts(lts)
    expected_dec = details["decoration_seed"]
    assert expected_dec in dec_seeds_full, \
        f"Decoration seed {expected_dec} not in full-lts candidates {dec_seeds_full}"
    print(f"[OK] Recovered decoration_seed via full lts: {expected_dec} "
          f"(from {len(dec_seeds_full)} candidates)")

    # Test 2b: recover decoration seed from loot_start_state (only 48 bits of lts)
    dec_seeds_from_state = loot_start_state_to_decoration_seed(loot_start_state)
    assert expected_dec in dec_seeds_from_state, \
        f"Decoration seed {expected_dec} not in state-based candidates"
    print(f"[OK] Recovered decoration_seed via loot state: {expected_dec} "
          f"(from {len(dec_seeds_from_state)} candidates)")

    # Test 3: recover population seed
    pop_seed = decoration_seed_to_population_seed(expected_dec)
    assert pop_seed == details["population_seed"], \
        f"Population seed mismatch: {pop_seed} != {details['population_seed']}"
    print(f"[OK] Recovered population_seed: {pop_seed}")

    # Test 4: recover lower48 for chunk (0,0)
    candidates = find_lower48_for_pop_seed(pop_seed, cx, cz)
    assert test_seed in candidates, \
        f"lower48 {test_seed} not in candidates {candidates}"
    print(f"[OK] Recovered lower48: {test_seed}")

    # Test 5: full round-trip
    full_candidates = invert_from_loot_state(loot_start_state, cx, cz)
    assert test_seed in full_candidates, \
        f"Full inversion failed: {test_seed} not in {full_candidates}"
    print(f"[OK] Full inversion round-trip passed ({len(full_candidates)} candidates)")

    # Test with non-zero chunk
    cx2, cz2 = 1, -1
    details2 = bt_loot_table_seed_detailed(test_seed, cx2, cz2)
    lts2 = details2["loot_table_seed"]
    dec_seeds2 = loot_table_seed_to_decoration_seed_via_lts(lts2)
    expected_dec2 = details2["decoration_seed"]
    assert expected_dec2 in dec_seeds2, \
        f"Non-zero chunk dec seed recovery failed"
    pop2 = decoration_seed_to_population_seed(expected_dec2)
    assert verify_lower48(test_seed, cx2, cz2, pop2), \
        "verify_lower48 failed for non-zero chunk"
    print(f"[OK] Non-zero chunk ({cx2},{cz2}) chain inversion verified")

    print("\nAll chain inversion tests passed.")


if __name__ == "__main__":
    _self_test()
