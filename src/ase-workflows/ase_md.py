"""
Run molecular dynamics simulation using ASE and MACE.
Adapted from Venkat Kapil's ASE-MACE example.
"""

import sys
import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

from ase import units
from ase.io import read, write
from ase.io.trajectory import Trajectory
from ase.md import MDLogger
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution

import mace
from mace.calculators import mace_mp
from monty.json import jsanitize


REQUIRED_MACE_VERSION = "0.3.12"
if mace.__version__ != REQUIRED_MACE_VERSION:
    raise RuntimeError(
        f"mace-torch version {REQUIRED_MACE_VERSION} required, but found {mace.__version__}"
    )


def run_md(args: Namespace) -> None:
    """
    Run molecular dynamics simulation using ASE and MACE.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments.
    """
    # Create output directory if it doesn't exist.
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Dump sanitized arguments to JSON.
    args_json = jsanitize(args.__dict__)
    json_file = args.output_dir / "args.json"
    with json_file.open("w") as f:
        json.dump(args_json, f, indent=4)

    # Read the input structure.
    atoms = read(args.input_structure)

    # Set up the calculator.
    atoms.calc = mace_mp("small", default_dtype="float32")

    # MD simulation parameters.
    temperature = args.start_temp  # in K
    friction = 0.01 / units.fs
    timestep = args.time_step * units.fs
    total_steps = 10000
    print_interval = 100

    # Initialize velocities using a Maxwell-Boltzmann distribution.
    MaxwellBoltzmannDistribution(atoms, temperature_K=temperature * 2.0)

    # Set up the Langevin dynamics.
    dyn = Langevin(
        atoms,
        timestep=timestep,
        temperature_K=temperature,
        friction=friction
    )

    # Write the trajectory.
    traj_file = args.output_dir / "md.traj"
    traj = Trajectory(traj_file, "w", atoms)
    dyn.attach(traj.write, interval=print_interval)
    dyn.attach(MDLogger(dyn, atoms, sys.stdout, header=True), interval=print_interval)

    # Run the MD simulation.
    dyn.run(total_steps)

    # Write the final structure.
    write(args.output_dir / "thermalized.extxyz", atoms)


def parse_arguments() -> Namespace:
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description="Run molecular dynamics simulation using ASE and MACE."
    )
    parser.add_argument(
        "--input_structure",
        type=str,
        required=True,
        help="Path to the input structure file."
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        required=True,
        help="Directory to save the generated input files."
    )
    parser.add_argument(
        "--start_temp",
        type=float,
        default=300,
        help="Starting temperature in K."
    )
    parser.add_argument(
        "--end_temp",
        type=float,
        default=300,
        help="Ending temperature in K."
    )
    parser.add_argument(
        "--time_step",
        type=float,
        default=1,
        help="Time step for MD in fs."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    run_md(args)


if __name__ == "__main__":
    main()