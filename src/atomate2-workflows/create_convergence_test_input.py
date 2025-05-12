import os

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
    for ENCUT in [520, 600, 700, 800, 900, 1000]:
        for density in [64, 128, 256, 512]:
            MPSetGGAMPGenerator = MDSetGenerator(
                structure=structure,
                ensemble="NVT",
                start_temp=args.start_temp,
                end_temp=args.end_temp,
                time_step=args.time_step,
                nsteps=args.nsteps,
                user_potcar_functional=args.potcar_functional,
                user_incar_settings={"ENCUT": ENCUT, "ISPIN": 1, "PREC": "Accurate"},
                user_kpoints_settings={"reciprocal_density": density},
                config_dict=MPRelaxSet.CONFIG,
            )
            input_dir_path = os.path.join(args.output_dir,f"ENCUT_{ENCUT}_reciprocal_kdensity_{density}")
            MPSetGGAMPGenerator.write_input(
                output_dir=input_dir_path,
            )
            print(
                f"Writing Input files for structure file {args.input_structure}"
                f"generated in {input_dir_path} with cutoff energy {ENCUT} eV."
                f"Density {density} kpoints."
            )
            if ENCUT==700 and density==128:
                if ENCUT==700 and density==128:
                                MPSetGGAMPGenerator = MDSetGenerator(
                    structure=structure,
                    ensemble="NVT",
                    start_temp=args.start_temp,
                    end_temp=args.end_temp,
                    time_step=args.time_step,
                    nsteps=args.nsteps,
                    user_potcar_functional=args.potcar_functional,
                    user_incar_settings={"ENCUT": ENCUT, "ISPIN": 1, "PREC": "Accurate", "LREAL":False},
                    user_kpoints_settings={"reciprocal_density": density},
                    config_dict=MPRelaxSet.CONFIG,
                )
                input_dir_path = os.path.join(args.output_dir,f"LREAL_ENCUT_{ENCUT}_reciprocal_kdensity_{density}")
                MPSetGGAMPGenerator.write_input(
                    output_dir=input_dir_path,
                )
                print(
                    f"Writing Input files for structure file {args.input_structure}"
                    f"generated in {input_dir_path} with LREAL=False, cutoff energy {ENCUT} eV."
                    f"Density {density} kpoints."
                )


def parse_arguments() -> Namespace:
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description="Generate VASP input files for MD"
        "simulations. Iterates through multiple kpoint"
        "and ENCUT values. Do not forget to set the"
        "PMG_VASP_PSP_DIR in .pmgrc.yaml"
    )
    parser.add_argument(
        "--input_structure", type=str, help="Path to the input structure file."
    )
    parser.add_argument(
        "--output_dir", type=str, default="./", help="Directory to save the generated input files."
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
    parser.add_argument(
        "--potcar_functional", type=str, default="PBE_64", help="POTCAR functional type."
    )
    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_arguments()
    write_input_files(args)


if __name__ == "__main__":
    main()
