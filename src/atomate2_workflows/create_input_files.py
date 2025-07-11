#!/usr/bin/env python3

import warnings
from argparse import ArgumentParser, Namespace

from atomate2.vasp.sets.core import MDSetGenerator, RelaxSetGenerator
from pymatgen.core import Structure
from pymatgen.io.vasp.sets import MPRelaxSet


def rescale_density(structure: Structure, target_density: float) -> Structure:
    """
    Return a new Structure with lattice scaled such that its
    mass density matches the target density.

    The atomic positions are scaled accordingly so the structure's shape
    and fractional coordinates remain unchanged.
    The composition and symmetry are preserved. This operation only changes
    the lattice volume.

    Args:
        structure (Structure): The input pymatgen Structure object.
        target_density (float): Desired mass density in g/cm^3.

    Returns:
        Structure: A new Structure object with rescaled lattice matching
        the target density.

    Example:
        >>> from pymatgen.core import Structure
        >>> struct = Structure.from_file("POSCAR")
        >>> new_struct = rescale_density(struct, 7.5)
        >>> print(new_struct.density)
        7.5
    """
    current_density = structure.density  # in g/cm^3
    new_volume = structure.lattice.volume * (current_density / target_density)
    structure.scale_lattice(float(new_volume))
    return structure


def write_input_files(args: Namespace) -> None:
    """
    Generate VASP input files for a molecular dynamics simulation.

    Parameters
    ----------
    args : Namespace
        Command line arguments with keys: input_structure, output_dir, start_temp,
        end_temp, time_step, nsteps, ENCUT.
    """
    structure = Structure.from_file(args.input_structure)
    # Rescale the structure to a target density before relaxation
    if args.density is not None:
        structure = rescale_density(structure, args.density)
        if args.system_type == "molecule":
            raise RuntimeError(
                "Rescaling density is likely not appropriate for molecular systems."
            )
    else:
        warnings.warn(
            "No target density provided. Using the original density."
        )

    MPRelaxSetGenerator = RelaxSetGenerator(
        structure=structure,
        user_potcar_functional=args.potcar_functional,
        user_incar_settings={
            "ISIF": 4,
            "EDIFF": 1e-6,
            "ENCUT": 700,
            "ISPIN": 1,
            "KSPACING": 1 / 12.0,
            "ISMEAR": 0,
            "SIGMA": 0.05,
            "KPAR": args.KPAR,
            "NCORE": args.NCORE,
        },
        config_dict=MPRelaxSet.CONFIG,
    )
    time_step = 1  # Default time step for MD simulations
    if args.system_type == "molecule":
        time_step = 0.5
    MPSetGGAMPGenerator = MDSetGenerator(
        structure=structure,
        ensemble="NVT",
        start_temp=args.start_temp,
        end_temp=args.end_temp,
        time_step=time_step,
        nsteps=args.nsteps,
        user_potcar_functional=args.potcar_functional,
        user_incar_settings={
            "EDIFF": 1e-6,
            "ENCUT": 700,
            "ISPIN": 1,
            "KSPACING": 1 / 12.0,
            "ISMEAR": 0,
            "SIGMA": 0.05,
            "LASPH": True,
            "KPAR": args.KPAR,
            "NCORE": args.NCORE,
        },
        config_dict=MPRelaxSet.CONFIG,
    )
    if args.write_relax_input:
        MPRelaxSetGenerator.write_input(
            output_dir=args.output_dir,
        )
        print(
            "Writing Input files for relaxation of structure"
            f" file {args.input_structure}"
            f" in {args.output_dir}."
        )
    else:
        MPSetGGAMPGenerator.write_input(
            output_dir=args.output_dir,
        )
        print(
            f"Writing Input files for MD simulation of "
            f"structure file {args.input_structure}"
            f" in {args.output_dir}."
        )
    print(
        """
    If your system is a surface, add suitable dipole corrections.
    https://www.vasp.at/wiki/index.php/Electrostatic_corrections
    Test if ALGO Normal or Fast is suitable for your system.
    Also set suitable parallelization settings in the INCAR file
    or use the --KPAR, --NCORE, --NPAR flags.
    In case of a restart, generate a new folder from the last
    CONTCAR file using the script again.
    """
    )


def parse_arguments() -> Namespace:
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description="Generate VASP input files for Relaxation and Molecular Dynamics"
        " simulations. Do not forget to set the PMG_VASP_PSP_DIR in .pmgrc.yaml and"
        " to use PBE64 POTCARs."
        " 1st step run relaxation with --write_relax_input flag,"
        " then use the CONTCAR file"
        " to run the MD simulation"
        " if your system contains hydrogen consider using a smaller timestep (0.5 fs) "
    )
    parser.add_argument(
        "--density",
        type=float,
        help="Target density in g/cm^3 for rescaling the crystal structure.",
    )
    parser.add_argument(
        "--write_relax_input",
        action="store_true",
        help="Flag to write input files for relaxation instead of MD.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="vasp_inputs",
        help="Directory to write the VASP input files.",
    )
    parser.add_argument(
        "--input_structure", type=str, help="Path to the input structure file."
    )
    parser.add_argument(
        "--KPAR", type=int, default=1, help="Number of K-point parallelization."
    )
    parser.add_argument(
        "--NCORE", type=int, default=1, help="Number of core parallelization."
    )
    parser.add_argument(
        "--start_temp", type=float, default=300, help="Starting temperature in K."
    )
    parser.add_argument(
        "--end_temp", type=float, default=300, help="Ending temperature in K."
    )
    parser.add_argument("--nsteps", type=int, default=10, help="Number of MD steps.")
    parser.add_argument(
        "--potcar_functional",
        type=str,
        default="PBE_64",
        help="POTCAR functional type.",
    )
    parser.add_argument(
        "--system_type",
        type=str,
        choices=["bulk", "molecule"],
        default="bulk",
        help="Type of system: 'bulk' or 'molecule'",
    )
    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_arguments()
    write_input_files(args)


if __name__ == "__main__":
    main()
