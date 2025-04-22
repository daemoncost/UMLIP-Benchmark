from argparse import ArgumentParser, Namespace

from ase.io import read
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

    MPSetGGAMPGenerator = MDSetGenerator(
        structure=structure,
        ensemble="NVT",
        start_temp=args.start_temp,
        end_temp=args.end_temp,
        time_step=args.time_step,
        nsteps=args.nsteps,
        user_potcar_functional="PBE_64",
        user_incar_settings={"ENCUT": args.ENCUT},
        config_dict=MPRelaxSet.CONFIG,
    )
    MPSetGGAMPGenerator.write_input(
        output_dir=args.output_dir,
    )
    print(
        f"Writing Input files for structure file {args.input_structure}"
        f"generated in {args.output_dir} with cutoff energy {args.ENCUT} eV."
    )


def parse_arguments() -> Namespace:
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description="Generate VASP input files for MD"
        "simulations. Do not forget to set the"
        "PMG_VASP_PSP_DIR in .pmgrc.yaml"
    )
    parser.add_argument(
        "--input_structure", type=str, help="Path to the input structure file."
    )
    parser.add_argument(
        "--output_dir", type=str, help="Directory to save the generated input files."
    )
    parser.add_argument(
        "--start_temp", type=float, default=300, help="Starting temperature in K."
    )
    parser.add_argument(
        "--end_temp", type=float, default=300, help="Ending temperature in K."
    )
    parser.add_argument("--nsteps", type=int, default=10, help="Number of MD steps.")
    parser.add_argument(
        "--ENCUT", type=float, default=520, help="Plane-wave cutoff energy in eV."
    )
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
