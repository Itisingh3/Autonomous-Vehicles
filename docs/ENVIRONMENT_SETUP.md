# Environment setup and checks

On Windows, use the supplied Docker environment; do not install Linux build
commands in PowerShell.  The container builds liboqs with only ML-KEM-768 and
ML-DSA-65 enabled and exposes a standalone smoke test.

```powershell
docker build --target smoke -t cav-pqc-crypto-smoke -f sim/omnet/Dockerfile sim/omnet
```

For a Linux host, install `build-essential`, `cmake`, `git`, `g++`, `make`, and
`python3-pip`, then build liboqs using the pinned Dockerfile commands. Install
SUMO and SUMO tools, then use the version set in
[`simulation/versions.lock`](../simulation/versions.lock): **OMNeT++ 6.1.0 +
Veins 5.3.1 + SUMO 1.22.0**. Check the headers/library with
`ls /usr/local/include/oqs` and `ls /usr/local/lib | grep oqs`.

Before adding a Veins experiment, record the exact OMNeT++, Veins, SUMO, liboqs
revision, compiler, operating system, SUMO/OMNeT seeds, and source revision.
Use version-compatible OMNeT++ and Veins releases; do not assume any arbitrary
pair will compile.

## Network-simulation stack

The final stack is installed in this order in an Ubuntu container or native
Ubuntu workstation:

OMNeT++ version: 6.0.1
Veins version: 5.2
SUMO version: 1.25.0
liboqs: ML-KEM-768 and ML-DSA-65
ProVerif: 2.05 (Windows-native)
Host: Windows + WSL opp_env

In the Linux shell, verify the installed tools with:

```bash
command -v omnetpp
sumo --version
sumo-gui --version
proverif --help
```

`omnetpp` starts a graphical IDE and may require an X/Wayland display. It is
not required for batch `opp_run` simulation. `sumo-gui` likewise requires a
display; headless `sumo` is sufficient for reproducible batch experiments.

## Python analysis tools

The optional reporting stack is installed with:

```bash
python3 -m pip install pandas matplotlib seaborn numpy
```

Pin the resulting version list in every final experiment manifest. Python ML
development dependencies remain in `requirements-deep.txt`.

On the present Windows host, OMNeT++/SUMO are intentionally containerized;
native ProVerif is installed at `C:\Tools\proverif2.05\proverif.exe`.
