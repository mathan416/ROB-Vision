# Batocera receiver

The Batocera port runs on **Batocera 43.1 x86_64** and uses the stock FCEUmm or Nestopia core through a small R.O.B. Vision frame wrapper. The included `.so` files were built for x86_64 Linux; `build-cores.sh` rebuilds them with GCC on an x86_64 Linux host. ARM Batocera systems need a separate build and have not been tested.

Install from the [versioned release command](../../docs/INSTALLATION_GUIDE.md) as `root` on Batocera. The same console command detects Batocera or RetroPie, checks supported hardware before changing files, and opens first-time pairing. A source checkout and a separate pairing command are unnecessary for a normal install.

The installer retains an existing pairing token and controller URL on repeat runs. It enables the `ROBVision` Batocera service, installs its separate `zz-robvision-game` hook, and selects `robvision_fceumm` for the exact Gyromite and Stack-Up ROM names in `config/games.json`. An existing FCEUmm/Nestopia selection for one of those ROMs is retained. An unknown custom core choice is left alone. Other games, including VirtualGlove's Super Glove Ball, are not changed. Exit any Batocera game before installation. The installer suspends and resumes EmulationStation around the receiver restart to avoid virtual joystick hotplug during menu input handling.

The console command prints the first-time pairing code and fingerprint. Enter them on Setup while it is still running.

Enter the code and certificate fingerprint on the UNO Q Setup page, using the Batocera hostname. Pairing restarts the service. The receiver creates a virtual Controller 2; only Gyromite receives per-ROM Player 2 settings. Its joystick index is detected in SDL2 order at service startup before Batocera generates RetroArch's game configuration; the Linux `jsN` number can differ. Stack-Up sends six movement commands to the virtual robot and has no controller return path.

Batocera keeps system core paths read-only. The service adds the R.O.B. Vision wrappers through a runtime overlay. If VirtualGlove already mounted that overlay, R.O.B. Vision adds its own files without changing VirtualGlove's service, hook, core, or game choice. The wrappers call the installed stock FCEUmm and Nestopia libraries. The frame socket and virtual pad disappear when the receiver stops; the overlay is rebuilt at boot.

To switch one supported ROM to Nestopia, edit only its `nes["ROM filename"].core` entry in `/userdata/system/batocera.conf` to `robvision_nestopia`. The installer preserves this choice on later runs. Keep `.emulator=libretro`.

**Checked on the test machine:** repeat installation, both wrapper libraries loading, automatic exact-ROM FCEUmm selection, explicit Nestopia launches for both games, Gyromite's generated Player 2 index and A/B assignments, live UNO Q Batocera online and frame-linked status during Stack-Up, and preservation of VirtualGlove's core. A full playthrough and live Batocera gate response remain to be checked.
