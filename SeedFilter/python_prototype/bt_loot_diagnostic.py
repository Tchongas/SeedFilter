"""
Diagnostic tool to determine correct decoration salt and loot rolling
method for Buried Treasure in Minecraft 1.18+.

Usage: python bt_loot_diagnostic.py <world_seed> <bt_chunk_x> <bt_chunk_z>

Tries all plausible decoration salts and both LCG / Xoroshiro rolling,
printing predicted loot for each combination so you can compare with
in-game results.
"""

import sys
import struct


# =============================================================================
#  Xoroshiro128++ (matches cubiomes / Minecraft XoroshiroRandomSource)
# =============================================================================

def _rotl64(x, k):
    x &= 0xFFFFFFFFFFFFFFFF
    return ((x << k) | (x >> (64 - k))) & 0xFFFFFFFFFFFFFFFF


def _stafford13(v):
    v &= 0xFFFFFFFFFFFFFFFF
    v = ((v ^ (v >> 30)) * 0xbf58476d1ce4e5b9) & 0xFFFFFFFFFFFFFFFF
    v = ((v ^ (v >> 27)) * 0x94d049bb133111eb) & 0xFFFFFFFFFFFFFFFF
    return (v ^ (v >> 31)) & 0xFFFFFFFFFFFFFFFF


class Xoroshiro:
    def __init__(self):
        self.lo = 0
        self.hi = 0

    def set_seed(self, value):
        value &= 0xFFFFFFFFFFFFFFFF
        XH = 0x6a09e667f3bcc909
        XL = 0x9e3779b97f4a7c15
        l = (value ^ XH) & 0xFFFFFFFFFFFFFFFF
        h = (l + XL) & 0xFFFFFFFFFFFFFFFF
        self.lo = _stafford13(l)
        self.hi = _stafford13(h)

    def next_long(self):
        l = self.lo
        h = self.hi
        n = (_rotl64((l + h) & 0xFFFFFFFFFFFFFFFF, 17) + l) & 0xFFFFFFFFFFFFFFFF
        h ^= l
        self.lo = (_rotl64(l, 49) ^ h ^ ((h << 21) & 0xFFFFFFFFFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF
        self.hi = _rotl64(h, 28)
        return n

    def next_long_j(self):
        """Mimics java.util.Random.nextLong() via WorldgenRandom:
        next(32)<<32 + next(32), each consuming one xoroshiro output."""
        a = _to_signed32(self.next_long() >> 32)
        b = _to_signed32(self.next_long() >> 32)
        return _to_unsigned64((a << 32) + b)

    def next_int(self, bound):
        """Minecraft XoroshiroRandomSource.nextInt(bound) — multiplication method."""
        raw = self.next_long() & 0xFFFFFFFF
        m = raw * bound
        low = m & 0xFFFFFFFF
        if low < bound:
            threshold = ((~bound + 1) & 0xFFFFFFFF) % bound
            while low < threshold:
                raw = self.next_long() & 0xFFFFFFFF
                m = raw * bound
                low = m & 0xFFFFFFFF
        return (m >> 32) & 0xFFFFFFFF

    def next_float(self):
        return (self.next_long() >> 40) * 5.9604645e-8


def _to_signed32(v):
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v >= 0x80000000 else v


def _to_signed64(v):
    v &= 0xFFFFFFFFFFFFFFFF
    return v - 0x10000000000000000 if v >= 0x8000000000000000 else v


def _to_unsigned64(v):
    return v & 0xFFFFFFFFFFFFFFFF


# =============================================================================
#  Java LCG (java.util.Random)
# =============================================================================

class JavaLCG:
    MASK = (1 << 48) - 1
    MULT = 0x5DEECE66D
    ADD = 0xB

    def __init__(self):
        self.state = 0

    def set_seed(self, seed):
        self.state = (seed ^ self.MULT) & self.MASK

    def _next(self, bits):
        self.state = (self.state * self.MULT + self.ADD) & self.MASK
        return _to_signed32(self.state >> (48 - bits))

    def next_int(self, bound):
        if bound <= 0:
            raise ValueError
        if (bound & (bound - 1)) == 0:
            return ((bound * self._next(31)) >> 31) & 0xFFFFFFFF
        while True:
            bits = self._next(31)
            val = bits % bound
            if bits - val + (bound - 1) >= 0:
                return val

    def next_long(self):
        a = self._next(32)
        b = self._next(32)
        return _to_unsigned64((a << 32) + b)

    def next_float(self):
        return self._next(24) / (1 << 24)


# =============================================================================
#  Seed derivation
# =============================================================================

def get_population_seed(world_seed, block_x, block_z):
    xr = Xoroshiro()
    xr.set_seed(world_seed)
    a = xr.next_long_j()
    b = xr.next_long_j()
    a = _to_unsigned64(a | 1)
    b = _to_unsigned64(b | 1)
    pop = _to_unsigned64(
        _to_signed64(_to_unsigned64(block_x * _to_signed64(a))) +
        _to_signed64(_to_unsigned64(block_z * _to_signed64(b)))
    ) ^ world_seed
    return _to_unsigned64(pop)


def get_loot_table_seed(pop_seed, salt):
    dec_seed = _to_unsigned64(pop_seed + salt)
    xr = Xoroshiro()
    xr.set_seed(dec_seed)
    lts = xr.next_long_j()
    return lts


# =============================================================================
#  Loot rolling — Xoroshiro method (correct for 1.18+)
# =============================================================================

def roll_bt_loot_xoro(loot_table_seed):
    xr = Xoroshiro()
    xr.set_seed(loot_table_seed)

    iron = gold = tnt = emerald = diamond = prismarine = food = 0

    # Pool 1: Heart of the Sea — 1 guaranteed, no random calls

    # Pool 2: Ingots/TNT (weights: iron 20, gold 10, tnt 5; total 35)
    rolls = 5 + xr.next_int(4)  # 5-8 rolls
    for _ in range(rolls):
        w = xr.next_int(35)
        if w < 20:
            iron += 1 + xr.next_int(4)
        elif w < 30:
            gold += 1 + xr.next_int(4)
        else:
            tnt += 1 + xr.next_int(2)

    # Pool 3: Gems (weights: emerald 5, diamond 5, prismarine 5; total 15)
    rolls = 1 + xr.next_int(3)  # 1-3 rolls
    for _ in range(rolls):
        w = xr.next_int(15)
        if w < 5:
            emerald += 4 + xr.next_int(5)
        elif w < 10:
            diamond += 1 + xr.next_int(2)
        else:
            prismarine += 1 + xr.next_int(5)

    # Pool 4: Armor/Sword (0-1 rolls, 2 equal items)
    rolls = xr.next_int(2)
    for _ in range(rolls):
        xr.next_int(2)

    # Pool 5: Fish (2 rolls, cod/salmon equally weighted, 2-4 each)
    for _ in range(2):
        xr.next_int(2)
        food += 2 + xr.next_int(3)

    # Pool 6: Potion of Water Breathing — 1 guaranteed, no random calls

    return iron, gold, tnt, emerald, diamond, prismarine, food


# =============================================================================
#  Loot rolling — Java LCG method (pre-1.18, for comparison)
# =============================================================================

def roll_bt_loot_lcg(loot_table_seed):
    rng = JavaLCG()
    rng.set_seed(loot_table_seed)

    iron = gold = tnt = emerald = diamond = prismarine = food = 0

    # Pool 2
    rolls = 5 + rng.next_int(4)
    for _ in range(rolls):
        w = rng.next_int(35)
        if w < 20:
            iron += 1 + rng.next_int(4)
        elif w < 30:
            gold += 1 + rng.next_int(4)
        else:
            tnt += 1 + rng.next_int(2)

    # Pool 3
    rolls = 1 + rng.next_int(3)
    for _ in range(rolls):
        w = rng.next_int(15)
        if w < 5:
            emerald += 4 + rng.next_int(5)
        elif w < 10:
            diamond += 1 + rng.next_int(2)
        else:
            prismarine += 1 + rng.next_int(5)

    # Pool 4
    rolls = rng.next_int(2)
    for _ in range(rolls):
        rng.next_int(2)

    # Pool 5
    for _ in range(2):
        rng.next_int(2)
        food += 2 + rng.next_int(3)

    return iron, gold, tnt, emerald, diamond, prismarine, food


# =============================================================================
#  Main
# =============================================================================

def bt_at_chunk(lower48, chunk_x, chunk_z):
    """Check if a BT generates at this chunk (mirrors bt_at_chunk in C)."""
    salt = 10387320
    cX = 341873128712
    cZ = 132897987541
    finder_seed = _to_unsigned64(lower48 + salt + chunk_x * cX + chunk_z * cZ)
    finder_seed = (finder_seed ^ 0x5DEECE66D) & ((1 << 48) - 1)
    # nextFloat: next(24) / (1 << 24)
    finder_seed = (finder_seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
    val = (finder_seed >> 24) / (1 << 24)
    return val < 0.01


def find_bt_chunks(seed, max_range=2):
    """Find all BT chunks near origin."""
    lower48 = seed & ((1 << 48) - 1)
    result = []
    for cx in range(-max_range, max_range + 1):
        for cz in range(-max_range, max_range + 1):
            if bt_at_chunk(lower48, cx, cz):
                result.append((cx, cz))
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python bt_loot_diagnostic.py <world_seed> [bt_chunk_x bt_chunk_z]")
        print("  world_seed: full 64-bit seed (signed or unsigned)")
        print("  bt_chunk_x/z: optional, auto-detected if omitted")
        sys.exit(1)

    world_seed = int(sys.argv[1])
    world_seed = _to_unsigned64(world_seed)

    if len(sys.argv) >= 4:
        chunks_to_test = [(int(sys.argv[2]), int(sys.argv[3]))]
    else:
        chunks_to_test = find_bt_chunks(world_seed, max_range=2)
        if not chunks_to_test:
            print("No BT chunks found near origin!")
            sys.exit(1)
        print(f"Auto-detected BT chunks: {chunks_to_test}")
        print()

    for chunk_x, chunk_z in chunks_to_test:
        block_x = chunk_x * 16
        block_z = chunk_z * 16

        pop_seed = get_population_seed(world_seed, block_x, block_z)

        print(f"World seed:      {_to_signed64(world_seed)} (0x{world_seed:016X})")
        print(f"BT chunk:        ({chunk_x}, {chunk_z})  ->  block ({block_x}, {block_z})")
        print(f"Population seed: 0x{pop_seed:016X}")
        print()

        salts_to_try = list(range(20000, 20011)) + list(range(30000, 30011))

        header = f"{'Salt':>6}  {'Method':>5}  {'Iron':>4} {'Gold':>4} {'TNT':>3} {'Emer':>4} {'Dia':>3} {'Prism':>5} {'Food':>4}"
        print(header)
        print("-" * len(header))

        for salt in salts_to_try:
            lts = get_loot_table_seed(pop_seed, salt)

            ir, go, tn, em, di, pr, fo = roll_bt_loot_xoro(lts)
            print(f"{salt:>6}  {'XORO':>5}  {ir:>4} {go:>4} {tn:>3} {em:>4} {di:>3} {pr:>5} {fo:>4}")

            ir2, go2, tn2, em2, di2, pr2, fo2 = roll_bt_loot_lcg(lts)
            print(f"{'':>6}  {'LCG':>5}  {ir2:>4} {go2:>4} {tn2:>3} {em2:>4} {di2:>3} {pr2:>5} {fo2:>4}")

        print()
        print("=" * 70)
        print()

    print("Compare with in-game loot to find the matching salt + method.")
    print("The XORO row uses Xoroshiro128++ for rolling (expected for 1.18+).")
    print("The LCG row uses Java LCG for rolling (pre-1.18 / legacy).")


if __name__ == "__main__":
    main()
