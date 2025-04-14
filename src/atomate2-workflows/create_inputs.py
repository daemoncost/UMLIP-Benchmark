from argparse import ArgumentParser

from atomate2.vasp.sets.core import MDSetGenerator
from pymatgen.core.structure import Structure
from pymatgen.io.vasp.sets import MPRelaxSet


def main(args):
    structure = Structure.from_file(args.input_structure)
    MPSetGGAMPGenerator = MDSetGenerator(
        structure=structure,
        ensemble="NVT",
        start_temp=300,
        end_temp=300,
        time_step=1,
        nsteps=10,
        user_potcar_functional="PBE_64",
        user_incar_settings={"ENCUT": args.ENCUT},
        config_dict=MPRelaxSet.CONFIG,
    )
    MPSetGGAMPGenerator.write_input(
        output_dir=args.output_dir,
    )
    print(
        f"Input files for structure file {args.input_structure}"
        "generated in {args.output_dir} with cutoff energy {args.ENCUT} eV."
    )


parser = ArgumentParser(description="Generate VASP input files for MD simulations.")
parser.add_argument(
    "--input_structure", type=str, help="Path to the input structure file."
)
parser.add_argument(
    "--output_dir", type=str, help="Directory to save the generated input files."
)
parser.add_argument(
    "--ENCUT", type=float, default=520, help="Plane-wave cutoff energy in eV."
)
args = parser.parse_args()
main(args)
