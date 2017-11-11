# Simulation
Dependencies: FreeCAD, COMSOL, Garfield++ (best with modified version), Geant4, ROOT, python3 + cogapp

For the configuration of the simulated setup see [simulation.conf](simulation.conf). This config file is used to cog the cpp source files and solver files to adapt the simulation accordingly.

## Particleconversion simulation procedure
Assuming you are in the particleconversion simulation directory:

1. Create build directory:

	`mkdir build && cd build`

2. Add simulation directory to your PYTHONPATH:

	`export PYTHONPATH="${PYTHONPATH}:../.."`

3. Configure Geant4 build:

	`cmake ..`

4. Build Geant4 simulation:

	`make`

5. Run simulation interactively or with macro file by setting the
   particleconversion.macro_path in [simulation.conf](simulation.conf)

6. If run interactively you might want to init visualisation:

	`/control/execute ../vis.mac`

## Drift simulation procedure
Assuming you are in the drift simulation directory:

1. Build Garfield++ executable:

	`make`

2. Run simulation:

	`./drift`

## Avalanche simulation procedure
Assuming you are in the avalanche simulation directory:

1. Export FreeCAD model (geometry/geometry.fcstd) to .step file.

2. Use COMSOL to load the mesh file and calculate the field map. Afterwards
   export it in a regular grid for Garfield++ to read in.

3. `make`

4. Run simulation:

	`./avalanche`

## More information

* Avalanche step 1: In
  [avalanche/geometry/create_mesh.py](avalanche/geometry/create_mesh.py) is a
  macro to create a mesh from given parameters.
  Please note, that due to a bug in FreeCAD 0.16, you should use the nightly
  version found in their git
  (FreeCAD-0.17.git201710112032.glibc2.17-x86_64.AppImage works).
