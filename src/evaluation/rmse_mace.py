import os
import numpy as np
from ase.io import read
from mace.calculators import mace_mp, MACECalculator
from tqdm import tqdm
import json


def get_models(model_directory, device="cuda"):
    calc_list = {}

    for mlip_name in os.listdir(model_directory):
        mlip_path = os.path.join(model_directory, mlip_name)
        if not os.path.isdir(mlip_path):
            continue

        # Loop through each model file or subdirectory
        for model_name in os.listdir(mlip_path):
            model_path = os.path.join(mlip_path, model_name)

            if "mace" in mlip_name.lower():
                try:
                    calc = MACECalculator(
                        model_path, default_dtype="float32", device=device
                    )

                    calc_list[model_name] = calc
                except Exception as e:
                    print(f"Skipped MACE model {model_name}: {e}")

    # Add foundation MACE models (pretrained MACE-MP)
    try:
        calc = mace_mp(default_dtype="float32", device=device)
        calc_list["mace_mp"] = calc
    except Exception as e:
        print(f"Skipped mace_mp foundation model: {e}")

    print(f"Loaded {len(calc_list)} MLIP calculators.")
    return calc_list


def evaluate_model(traj_file, calc, model_name):
    """
    Evaluate a MACE foundation model on a trajectory and compute RMSE for energies and forces.

    Parameters
    ----------
    traj_file : str
        Path to extended XYZ file containing trajectory with reference energies and forces.
    model_name : str
        Foundation model to use: "mace_off", "mace_anicc", "mace_mp".
    device : str
        Device to run on ("cuda" or "cpu").
    """

    # Load trajectory
    atoms_list = read(traj_file, ":")
    true_energies = []
    pred_energies = []
    true_forces = []
    pred_forces = []

    for atoms in tqdm(atoms_list, desc=f"Evaluating {model_name}"):
        # Reference values
        true_energies.append(atoms.calc.get_potential_energy() / len(atoms))
        true_forces.append(atoms.calc.get_forces())

        # Prediction
        atoms.set_calculator(calc)
        pred_energies.append(atoms.get_potential_energy() / len(atoms))
        pred_forces.append(atoms.get_forces())

    # Convert to arrays
    true_energies = np.array(true_energies)
    pred_energies = np.array(pred_energies)
    true_forces = np.array(true_forces)
    pred_forces = np.array(pred_forces)

    # Compute RMSE
    e_rmse = np.sqrt(np.mean((true_energies - pred_energies) ** 2))
    f_rmse = np.sqrt(np.mean((true_forces - pred_forces) ** 2))

    return e_rmse, f_rmse


if __name__ == "__main__":
    traj_files = [
        "../trajectories/naphthalene_295K_Sharma_S/naphthalene_trajectory_fix.extxyz",
        "../trajectories/anthracene_293K_Sharma_S/anthracene_trajectory_fix.extxyz",
        "../trajectories/pentacene_295K_Sharma_S/pentacene_trajectory_fix.extxyz",
        "../trajectories/picene_295K_Sharma_S/picene_trajectory_fix.extxyz",
        "../trajectories/tetracene_295K_Sharma_S/tetracene_trajectory_fix.extxyz",
        "../trajectories/bulkAu_1500K_Kapil_VASP/traj.extxyz",
        "../trajectories/bulk_LiMgAlZnSn_600_J_Schmidt_VASP/out.traj",
        "../trajectories/bulk_LiMgAlZnSn_900_J_Schmidt_VASP/out.traj",
        "../trajectories/bulkMoS2_300K_J.Kioseoglou_VASP/traj.extxyz",
        "../trajectories/bulkMoS2_600K_J.Kioseoglou_VASP/traj.extxyz",
        "../trajectories/MAPbBr3_300K_Ivor_VASP/traj.extxyz",
    ]

    names = [
        "naphthalene_295K",
        "anthracene_293K",
        "pentacene_295K",
        "picene_295K",
        "tetracene_295K",
        "bulk_Au_1500K",
        "bulk_LiMgAlZnSn_600K",
        "bulk_LiMgAlZnSn_900K",
        "bulk_MoS2_300K",
        "bulk_MoS2_600K",
        "MAPbBr3_300K",
    ]

    model_directroy = "../foundation_models"
    calc_list = get_models(model_directroy, device="cuda")

    results = {}

    for ind, traj_file in enumerate(traj_files):
        dataset_name = names[ind]
        results[dataset_name] = {}

        for model, calc in calc_list.items():
            try:
                e_rmse, f_rmse = evaluate_model(traj_file, calc, model)
            except Exception as e:
                print(f"Failed to determine RMSE with {model}: {e}")
                e_rmse, f_rmse = np.nan, np.nan

            results[dataset_name][model] = {
                "energy_RMSE": float(e_rmse),
                "force_RMSE": float(f_rmse),
            }
            print(
                f"{dataset_name} | {model}: E_RMSE={e_rmse:.4f} eV, F_RMSE={f_rmse:.4f} eV/Å"
            )

    with open("rmse_results.json", "w") as f:
        json.dump(results, f, indent=2)
