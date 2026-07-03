# Gadget of Accessible Tourney Seedfinding (GoATS)

**GoATS** is a customizable Minecraft seedfinding program written mostly in C. It features powerful and efficient filtering tools for many different Minecraft versions, primarily suited for speedrunners and speedrun tournament organizers, available in an easily configurable and accessible manner.

This is primarily a wrapper on the Cubiomes C library, and as such, implements many of its basic features, such as simple filtering for structures like villages, fortresses, bastions, strongholds, etc. However, **GoATS** also includes many novel features such as lava pools, magma ravines, end cages, zero cycle towers, and even customizable loot-based filters for many structures (buried treasure, shipwreck, etc). A comprehensive list of its features can be found further below.

### Beta Disclaimer

_**GoATS is currently in BETA!** The code is still incomplete and pending optimizations, features, and full functionality._
As of right now, all included filters *should* work as intended for 1.16+, with at least partial functionality for most filters in 1.15-.

## Installation

*[Note: this installation tutorial is a work in progress, and a more in-depth video tutorial is planned for the official release.]*

Go to the Releases tab in the repo's front page, download the first `.zip` file, and extract it wherever you'd like.

**GoATS** requires the following dependencies:
- `gcc`, to compile the seedfinding code
- `python`, to run the filter customization script
- `java`, to run the lava checker **(Java 17 or above is required)**
- `make`, optional, for the console-based commands (Windows scripts do not require it)

If you cloned the source instead of downloading a release, also run:

```git submodule update --init --recursive```

This downloads the Cubiomes and SFMT libraries into `submodules/`.

### Windows (recommended)

1. Install **gcc** — the easiest option is [TDM-GCC](https://jmeubank.github.io/tdm-gcc/) or [MSYS2](https://www.msys2.org/).
2. Install **Python** from [python.org](https://www.python.org). Make sure the installer says **Add python.exe to PATH**.
3. Install **Java 17+** from [Adoptium](https://adoptium.net/) or Oracle. Only needed if you want to use the lava checker.
4. Make sure `gcc` and `python` are available in a Command Prompt window:
   ```cmd
   gcc --version
   python --version
   ```

### Linux

On Debian-based distributions, run:

```sudo apt install gcc python3 openjdk-17-jre-headless make```

Use your native package manager if you are not on Debian/Ubuntu.

### Mac

Install the dependencies with Homebrew:

```brew install gcc python3 java make```

## Usage

### Windows: the easy way

Double-click **`goats.bat`** to open a menu that lets you:

1. Generate the filter file (`config.py`)
2. Compile the seedfinder (`compile.bat`)
3. Run the seedfinder (`run.bat`)
4. Run the lava checker (requires Java)

You only need to recompile when the C code changes. Changing filter settings in `config.py` does not require a rebuild.

Alternatively, use the small graphical launcher:

```cmd
python goats_ui.py
```

It provides buttons for the same steps and shows the output in a window.

### Windows: individual commands

Open Command Prompt in the GoATS folder and run:

```cmd
compile.bat
python config.py
run.bat 4
```

The last command runs the filter with 4 threads. Omit the number to run on 1 thread.

### Command line (all platforms)

The `Makefile` is now cross-platform. It uses `python` on Windows and `python3` on Linux/Mac, and it runs the correct executable name.

Compile:

```make compile```

Generate the filter:

```make py```

Run:

```make run 4```

Skip naming the filter:

```make pyn```

Output to a file:

```make run > examplefile.txt```

## Features

The following is a list of everything you can choose to filter for using **GoATS**. This information is also available in the comments for `config.py`.

- **Shipwreck**: position, type (front/back/full), loot, quadrant
- **Ruined portal**: position, type (with lava/without lava), loot
- **Buried treasure**: position, quantity, loot, quadrant
- **Village**: position, biome, quadrant
- **Desert temple**: position, loot, quadrant
- **Jungle temple**: position, quadrant
- **Potential lava pool**: position, quantity, quadrant
- **Magma ravine**: position, quadrant
- **Bastion**: position, type, quadrant
- **Fortress**: position, double spawner, quadrant
- **Stronghold**: distance from origin, 150 150 blind distance, ocean-exposed
- **End spawn**: exposed end spawn, endstone cage height
- **Zero cycle**: whether front/back dragon, diagonal node tower height
- **Spawn point**: position, accuracy

### Additional Scripts

This program also comes with some extra features in the form of external scripts.

#### Lava checker

- Reads through the `data/seedinfo.txt` file (if it exists) and checks every potential lava pool in each seed, using Minecraft's own world-gen code to determine which ones actually successfuly generate
- Outputs all seeds with successfully generating lava pools in `data/lavachecker_seedinfo.txt`
- 100% accurate for 1.16+, but takes around 2 seconds per seed

On Windows, run it from `goats.bat` option 4, or from the command line with:

```cmd
java -jar jar/lava_checker.jar
```

On Linux/Mac:

```make lavachecker```

## Acknowledgements

This program is meant as a free-to-use tool for *anyone* interested in seedfinding!

If you're a speedrun tournament organizer or similar, and plan to use **GoATS** to aid in seedfinding for a tourney or any other project, you are more than welcome to go ahead, no prior permission or anything needed! (Although it'd be cool if you at least told me you're using it, mainly for the validation that people are actually using the stuff I've made! 😅)

If you have questions, suggestions, complaints, or anything of the sort, feel free to send me a DM over at `aeroastroid` on Discord.

Special thanks go out to:
- **Al3xanDE_17**, for inspiring me to dive into Minecraft tournament seedfinding and to create this project
- **AndyNovo**, for creating the [FSG filters](https://replit.com/@AndyNovo), which were an extremely helpful reference for the program's logic as well as many features
- **Cubitect**, for developing and open-sourcing [Cubiomes](https://github.com/cubitect/cubiomes), the primary technical backbone for C seedfinding in general
- **JelleJurre**, for making [seed-checker](https://github.com/jellejurre/seed-checker), which was used for the Java side of this project, such as the lava checker script
