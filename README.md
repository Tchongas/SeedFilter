# Seed Filter

A modern, point-and-click Minecraft seed finder. Pick the structures, loot, and conditions you want, then hit **Generate & Run** to search for matching seeds.

![Seed Filter UI](https://via.placeholder.com/800x500?text=Seed+Filter+UI+Screenshot)

## Quick start

1. Download the latest release and extract the `.zip`.
2. Install the Python dependency:
   ```cmd
   pip install -r requirements.txt
   ```
3. Double-click **`RUNME.bat`** in the extracted folder.
4. The Seed Filter window opens and a shortcut is created on your Desktop.

That's it. No command line needed.

> If you are building from source, clone the repo and run `git submodule update --init --recursive` to fetch Cubiomes and SFMT.

## Features

- **Visual filter builder** — enable the structures you want and configure each one in collapsible cards.
- **Presets** — save your favorite configurations, name them, and import presets from other people as a short string of numbers.
- **Structure filtering** — villages, bastions, fortresses, strongholds, ruined portals, shipwrecks, buried treasure, desert/jungle temples, magma ravines, and lava pools.
- **Loot filters** — require minimum amounts of iron, gold, diamonds, emeralalds, TNT, food, and more for supported structures.
- **Quadrants** — restrict structures to specific regions relative to spawn.
- **Stronghold custom position** — search for a stronghold near any nether coordinates with a configurable margin.
- **Version selector** — supports Minecraft 1.16 through 1.20, defaulting to 1.16.
- **Copy filter code** — copy the generated filter string to the clipboard from the top bar.
- **Live output** — watch the seedfinder output as it runs, with the final results kept in view.

## How to use

1. Open the app with `RUNME.bat`.
2. Browse the tabs (**General**, **Overworld**, **Nether**, **End**, **Spawn**) and enable the filters you want.
3. Configure each enabled section:
   - Ranges, loot requirements, quadrants, biomes, etc.
   - For strongholds, set the target nether X/Z and a margin.
4. Choose the Minecraft version in the top bar.
5. Click **Generate & Run**.
6. The matching seeds are saved to `SeedFilter/data/` and shown in the output panel.

Use **Save / Import** in the preset dropdown to store or share configurations.

## Building from source

The seedfinding core is written in C and uses the Cubiomes library. If you change the C code, recompile:

```cmd
cd SeedFilter
compile.bat
```

The UI itself is Python and does not need recompilation.

## Dependencies

- **Python 3.x** — for the UI.
- **gcc** — for compiling the C seedfinder (TDM-GCC, MinGW, or MSYS2 on Windows).
- **Java 17+** — only if you want to run the legacy lava checker.
- **ttkbootstrap** — used by the UI for styling.

Core libraries:
- [Cubiomes](https://github.com/cubitect/cubiomes) — world and structure generation.
- [SFMT](https://github.com/MersenneTwister-Lab/SFMT) — SIMD-oriented fast Mersenne Twister.

## Sharing

You can zip the whole folder and send it to someone else. The recipient only needs:

- Windows
- Python 3.x
- `ttkbootstrap` (install with `pip install -r requirements.txt`)

`RUNME.bat` will create the Desktop shortcut for them on first run.

> Tip: exclude the `.git/` folder when zipping to keep the archive small.

## Acknowledgements

This project is a free-to-use tool for anyone interested in Minecraft seedfinding.

Special thanks to:
- **Al3xanDE_17** — for inspiring the project.
- **AndyNovo** — for the [FSG filters](https://replit.com/@AndyNovo), a reference for logic and features.
- **Cubitect** — for [Cubiomes](https://github.com/cubitect/cubiomes), the backbone of C seedfinding.
- **JelleJurre** — for [seed-checker](https://github.com/jellejurre/seed-checker), used for the Java lava checker.
