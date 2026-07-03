"""
Java LCG (Linear Congruential Generator) — exact replica of java.util.Random.

All operations work on 48-bit internal state.
Functions are stateless: they take a state and return (new_state, output).
"""

MASK = (1 << 48) - 1
A = 0x5DEECE66D          # multiplier
C = 11                   # increment
A_INV = pow(A, -1, 1 << 48)  # modular inverse of A mod 2^48


# ─── Core primitives ────────────────────────────────────────────────────────

def set_seed(value: int) -> int:
    """setSeed(v): internal_state = (v ^ A) & MASK"""
    return (value ^ A) & MASK


def next_bits(state: int, bits: int) -> tuple[int, int]:
    """One LCG step, returns (new_state, top `bits` bits as signed int)."""
    state = (state * A + C) & MASK
    # Java does arithmetic right shift: (int)((long)state >> (48 - bits))
    val = state >> (48 - bits)
    if bits < 48 and val >= (1 << (bits - 1)):
        val -= (1 << bits)
    return state, int(val)


def next_int(state: int, n: int) -> tuple[int, int]:
    """Exact replica of java.util.Random.nextInt(n)."""
    if n <= 0:
        raise ValueError("n must be positive")
    m = n - 1
    # Power of two fast path
    if (n & m) == 0:
        state, raw = next_bits(state, 31)
        return state, (n * (raw & 0x7FFFFFFF)) >> 31
    # General case with rejection
    while True:
        state, raw = next_bits(state, 31)
        bits = raw & 0x7FFFFFFF
        val = bits % n
        if bits - val + m >= 0:
            return state, val


def next_long(state: int) -> tuple[int, int]:
    """nextLong(): two next(32) calls combined into a 64-bit value.
    Java: ((long)next(32) << 32) + next(32) — lo is sign-extended before add."""
    state, hi = next_bits(state, 32)
    state, lo = next_bits(state, 32)
    return state, (hi << 32) + lo


def next_float(state: int) -> tuple[int, float]:
    """nextFloat(): next(24) / 2^24."""
    state, raw = next_bits(state, 24)
    return state, (raw & 0xFFFFFF) / (1 << 24)


# ─── Forward / backward skip in O(log n) ────────────────────────────────────

def _skip_params(n: int, mul: int, inc: int) -> tuple[int, int]:
    """Compute (M, A) such that state' = M*state + A after n LCG steps
    with multiplier `mul` and increment `inc`."""
    m = 1
    a = 0
    im = mul & MASK
    ia = inc & MASK
    k = n & MASK  # wraps for negative via modular arithmetic
    while k:
        if k & 1:
            m = (m * im) & MASK
            a = (im * a + ia) & MASK
        ia = ((im + 1) * ia) & MASK
        im = (im * im) & MASK
        k >>= 1
    return m, a


def skip_forward(state: int, n: int) -> int:
    """Advance LCG state by n steps."""
    m, a = _skip_params(n, A, C)
    return (state * m + a) & MASK


def skip_back(state: int, n: int) -> int:
    """Rewind LCG state by n steps."""
    c_inv = ((-C) * A_INV) & MASK  # inverse increment
    m, a = _skip_params(n, A_INV, c_inv)
    return (state * m + a) & MASK


# ─── Single step inverse ────────────────────────────────────────────────────

def prev_state(state: int) -> int:
    """One LCG step backwards."""
    return ((state - C) * A_INV) & MASK


def next_state(state: int) -> int:
    """One LCG step forward (without extracting bits)."""
    return (state * A + C) & MASK


# ─── Utilities ───────────────────────────────────────────────────────────────

def crack_next_int_state(output: int, n: int) -> list[int]:
    """Given nextInt(n) == output, enumerate all possible *post-step* states.

    After next(31), state has its top 31 bits determine `bits`,
    and the bottom 17 bits are free. We enumerate the ~2^17 candidates.
    """
    candidates = []
    is_power_of_2 = (n & (n - 1)) == 0

    for low17 in range(1 << 17):
        if is_power_of_2:
            # bits = next(31), return (n * bits) >> 31
            # For power-of-2 n, we need (n * bits) >> 31 == output
            # bits can range from output * (2^31 / n) to (output+1) * (2^31 / n) - 1
            step = (1 << 31) // n
            for bits in range(output * step, (output + 1) * step):
                state = (bits << 17) | low17
                if state <= MASK:
                    candidates.append(state)
            break  # only need one pass through low17 for p-o-2
        else:
            # General: bits = top 31 bits; val = bits % n
            # Rejection: bits - val + (n-1) >= 0
            # We need val == output
            # bits = k*n + output for k = 0, 1, ...
            bits_val = output
            while bits_val < (1 << 31):
                if bits_val - output + (n - 1) >= 0:  # rejection check
                    state = (bits_val << 17) | low17
                    if state <= MASK:
                        candidates.append(state)
                bits_val += n

    return candidates


def state_to_seed(internal_state: int) -> int:
    """Undo setSeed: value = internal_state ^ A (masked to 48 bits)."""
    return (internal_state ^ A) & MASK


def seed_to_state(seed_value: int) -> int:
    """Apply setSeed: same as set_seed()."""
    return set_seed(seed_value)


# ─── Self-test ───────────────────────────────────────────────────────────────

def _self_test():
    # Test basic round-trip
    s0 = set_seed(12345)
    s1 = next_state(s0)
    assert prev_state(s1) == s0, "prev_state failed"

    # Test skip forward/back
    s = set_seed(99999)
    s_fwd = skip_forward(s, 100)
    s_back = skip_back(s_fwd, 100)
    assert s_back == s, "skip round-trip failed"

    # Test nextInt matches Java behavior for known seed
    # Java: new Random(0).nextInt(10) == 0
    s = set_seed(0)
    s, val = next_int(s, 10)
    assert val == 0, f"nextInt(10) with seed 0 should be 0, got {val}"

    # Test nextLong
    s = set_seed(0)
    s, lng = next_long(s)
    # Java: new Random(0).nextLong() == -4962768465676381896
    expected = -4962768465676381896 & 0xFFFFFFFFFFFFFFFF
    lng_unsigned = lng & 0xFFFFFFFFFFFFFFFF
    assert lng_unsigned == expected, f"nextLong mismatch: {lng_unsigned} != {expected}"

    # Test A_INV
    assert (A * A_INV) & MASK == 1, "A_INV is wrong"

    print("All LCG self-tests passed.")


if __name__ == "__main__":
    _self_test()
