import warnings
from argparse import ArgumentParser, Namespace

from ase.io import read
from atomate2.vasp.sets import RelaxSetGenerator
from atomate2.vasp.sets.core import MDSetGenerator
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.io.vasp.sets import MPRelaxSet


def write_input_files(args: Namespace) -> None:
    """
    Generate VASP input files for a molecular dynamics simulation.

    Parameters
    ----------
    args : Namespace
        Command line arguments with keys: input_structure, output_dir, start_temp,
        end_temp, time_step, nsteps, ENCUT.
    """
    atoms = read(args.input_structure)
    structure = AseAtomsAdaptor.get_structure(atoms)
    structure.add_site_property("velocities", atoms.get_velocities())
    MPRelaxSetGenerator = RelaxSetGenerator(
        structure=structure,
        user_potcar_functional="PBE_64",
        user_incar_settings={
            "ENCUT": args.ENCUT,
            "ISPIN": 1,
            "KSPACING": 1 / 12.0,
            "EDIFF": 1e-5,
            "ISMEAR": 0,
            "SIGMA": 0.05,
            "KPAR": args.KPAR,
            "NCORE": args.NCORE,
        },
        config_dict=MPRelaxSet.CONFIG,
    )
    MPSetGGAMPGenerator = MDSetGenerator(
        structure=structure,
        ensemble="NVT",
        start_temp=args.start_temp,
        end_temp=args.end_temp,
        time_step=args.time_step,
        nsteps=args.nsteps,
        user_potcar_functional="PBE_64",
        user_incar_settings={
            "ENCUT": 700,
            "ISPIN": 1,
            "KSPACING": 1 / 12.0,
            "EDIFF": 1e-5,
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
            output_dir=args.relax_output_dir,
        )
        print(
            "Writing Input files for relaxation of structure"
            f" file {args.input_structure}"
            f" generated in {args.relax_output_dir}."
        )
    else:
        MPSetGGAMPGenerator.write_input(
            output_dir=args.output_dir,
        )
        print(
            f"Writing Input files for MD simulation of "
            f"structure file {args.input_structure}"
            f" generated in {args.output_dir}."
        )
    warnings.warn(
        "If your system is a surface add suitable dipole corrections."
        "https://www.vasp.at/wiki/index.php/Electrostatic_corrections"
        "Test if ALGO Normal Or Fast is suitable for your system."
        "Also set suitable parallelization settings in the INCAR file"
        " or --KPAR, --NCORE, --NPAR,  flags."
        "In case of a restart generate a new folder from the last"
        " CONTCAR file using the script again."
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
    )
    parser.add_argument(
        "--write_relax_input",
        action="store_true",
        help="Flag to write input files for relaxation instead of MD.",
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
        "--time_step", type=float, default=1.0, help="Time step for MD in fs."
    )
    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_arguments()
    write_input_files(args)


if __name__ == "__main__":
    main()
