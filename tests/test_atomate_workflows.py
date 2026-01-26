from pathlib import Path
from types import SimpleNamespace

import pymatgen.io.vasp.sets as vasp_sets
import pytest
from pymatgen.core import Lattice, Structure
from pymatgen.io.vasp.inputs import Incar

from atomate2_workflows.create_input_files import rescale_density, write_input_files


@pytest.fixture(autouse=True)
def hermetic_potcar(monkeypatch, tmp_path):
    """
    Make input writing independent of real POTCARs by:
    - forcing write_input(potcar_spec=True)
    """
    orig_write_input = vasp_sets.VaspInputSet.write_input

    def _write_input_patched(self, output_dir=".", **kwargs):
        kwargs = {**kwargs, "potcar_spec": True}
        return orig_write_input(self, output_dir=output_dir, **kwargs)

    monkeypatch.setattr(
        vasp_sets.VaspInputSet, "write_input", _write_input_patched, raising=True
    )
    monkeypatch.setenv("PMG_VASP_PSP_DIR", str(tmp_path))


def make_args(
    input_structure: Path,
    output_dir: Path,
    *,
    write_relax_input: bool = False,
    density: float | None = None,
    start_temp: float = 300,
    end_temp: float = 300,
    nsteps: int = 10,
    KPAR: int = 1,
    NCORE: int = 1,
    potcar_functional: str = "PBE_64",
    system_type: str = "bulk",
):
    # Build a Namespace compatible with write_input_files() signature.
    return SimpleNamespace(
        input_structure=str(input_structure),
        output_dir=str(output_dir),
        write_relax_input=write_relax_input,
        density=density,
        start_temp=start_temp,
        end_temp=end_temp,
        nsteps=nsteps,
        KPAR=KPAR,
        NCORE=NCORE,
        potcar_functional=potcar_functional,
        system_type=system_type,
    )


@pytest.mark.parametrize(
    "case_dir,mode,extra_kwargs,expected_file",
    [
        # Bulk, RELAX mode (with density rescale)
        (
            "Si_bulk",
            "relax",
            {"density": 2.33, "system_type": "bulk", "write_relax_input": True},
            "INCAR.relax.expected",
        ),
        # Bulk, MD mode (no density override)
        (
            "Si_bulk",
            "md",
            {"density": None, "system_type": "bulk", "write_relax_input": False},
            "INCAR.md.expected",
        ),
    ],
)
def test_incar_matches_golden(tmp_path, case_dir, mode, extra_kwargs, expected_file):
    """
    End-to-end: runs generator, reads produced INCAR,
    compare (as dict) with a reference file.
    """
    data_root = Path(__file__).parent / "data" / case_dir
    poscar = data_root / "POSCAR"
    expected_incar = data_root / expected_file
    outdir = tmp_path / f"out_{mode}"
    outdir.mkdir(parents=True, exist_ok=True)

    args = make_args(poscar, outdir, **extra_kwargs)
    write_input_files(args)

    produced_incar = Path(args.output_dir) / "INCAR"
    assert produced_incar.exists(), "Generator did not write INCAR"
    got = Incar.from_file(produced_incar).as_dict()
    ref = Incar.from_file(expected_incar).as_dict()

    # To help with debugging, print the diff-like info on failure.
    missing = {k: ref[k] for k in ref.keys() - got.keys()}
    extra = {k: got[k] for k in got.keys() - ref.keys()}
    value_mismatch = {
        k: (ref[k], got.get(k)) for k in ref.keys() & got.keys() if ref[k] != got.get(k)
    }

    assert not missing and not extra and not value_mismatch, (
        f"\nMissing keys: {missing}"
        f"\nExtra keys: {extra}"
        f"\nValue mismatch: {value_mismatch}"
    )


def test_density_rescale_raises_on_molecule(tmp_path):
    """
    The script should raise RuntimeError when
    --density is used with system_type='molecule'.
    """
    data_root = Path(__file__).parent / "data" / "Si_bulk"
    poscar = data_root / "POSCAR"
    outdir = tmp_path / "out_mol"
    outdir.mkdir(parents=True, exist_ok=True)

    args = make_args(
        poscar,
        outdir,
        density=0.1,  # any value; just to trigger the guard
        system_type="molecule",
        write_relax_input=True,
    )

    with pytest.raises(RuntimeError):
        write_input_files(args)


def test_rescale_density_changes_volume_inverse_with_density(tmp_path):
    """
    Quick, non-IO check: density scaling should adjust volume inversely.
    """
    # A trivial cubic structure (Al)
    a = 4.0
    struct = Structure(Lattice.cubic(a), ["Al"], [[0, 0, 0]])
    d0 = struct.density
    target = d0 * 2.51
    s2 = rescale_density(struct.copy(), target)
    assert pytest.approx(s2.lattice.volume, rel=1e-6) == struct.lattice.volume / 2.51
