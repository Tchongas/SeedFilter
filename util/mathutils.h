#include <stdint.h>

void shuffle(uint64_t *seed, int *ind, int n_ind);
int64_t dist_sq(int64_t x1, int64_t z1, int64_t x2, int64_t z2);
int get_bit(int n, int bit);