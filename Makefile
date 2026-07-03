ifeq (run,$(firstword $(MAKECMDGOALS)))
  ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(ARGS):;@:)
endif

ifeq ($(OS),Windows_NT)
	PYTHON := python
	SEED := seed.exe
else
	PYTHON := python3
	SEED := ./seed
endif

L_FILTERS := $(wildcard ./filters/*.c)
L_LOGIC := $(wildcard ./logic/*.c)
L_UTIL := $(wildcard ./util/*.c)
L_CUBIOMES := $(filter-out ./submodules/cubiomes/tests.c,$(wildcard ./submodules/cubiomes/*.c))
L_SFMT := ./submodules/sfmt/SFMT.c

compile:
	gcc main.c $(L_FILTERS) $(L_LOGIC) $(L_UTIL) $(L_CUBIOMES) $(L_SFMT) -lm -pthread -Ofast -DSFMT_MEXP=19937 -g -mavx -Wno-format -o seed

py:
	$(PYTHON) config.py

pyn:
	$(PYTHON) config.py noname

run:
	$(SEED) $(ARGS)

lavachecker:
	java -jar jar/lava_checker.jar