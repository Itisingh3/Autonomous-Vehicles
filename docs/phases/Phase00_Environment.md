# Phase 00 — Reproducible environment

Use a Linux container or Ubuntu host for the OMNeT++/SUMO/Veins experiment.
Windows is the host only; Linux commands from the research instructions run
inside that environment.

## Required checks

- CMake, Git, compiler, and Python available;
- liboqs headers and ML-KEM-768 / ML-DSA-65 C++ smoke test pass;
- chosen OMNeT++ 6.x release initialized via `. setenv`;
- SUMO and SUMO tools installed; SUMO GUI is optional for headless batches;
- Veins release matches the chosen OMNeT++ release;
- ProVerif version is recorded and formal scripts execute; and
- Python report packages are pinned in the experiment manifest.

Run `tools/check_simulation_environment.sh` inside the Linux environment after
the selected OMNeT++/Veins versions are installed. Do not report a networking
result until this phase is recorded in the experiment manifest.
