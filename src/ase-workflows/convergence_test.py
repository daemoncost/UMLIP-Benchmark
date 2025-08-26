import os

import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

# pick a calculation to compare others to
n = 0  # chose comparison of initial (0)/final (-1) structures of MD trajectories


for _, dirnames, _ in os.walk("."):
    dirs = dirnames
    break

data_dict = {}
for d in dirs:
    out_path = os.path.join(d, "OUTCAR")
    # ignore dirs without OUTCAR
    if not os.path.exists(out_path):
        continue

    with open(out_path, "r") as o:
        lines = o.readlines()

    iter_times = [0] * 10
    iter_iters = [0] * 10
    for l_index, line in enumerate(lines):
        # ENCUT
        if "ENCUT =" in line:
            encut = int(line.split("ENCUT =")[1])
        elif "generate k-points for" in line:
            kline = line.split(":")[1].strip()
            k = int(kline[0])
        elif "--------------------------------------- Iteration" in line:
            it = (
                int(line.split("Iteration")[1].split("(")[0].strip()) - 1
            )  # because VASP numbers them from 1
            for m in range(8, 13):
                try:
                    lline = lines[l_index + m]
                    if "LOOP" in lline:
                        iter_time = float(lline.split("real time")[-1])
                        iter_times[it] += iter_time
                        iter_iters[it] += 1
                        break
                except Exception as e:
                    print(f"Not {m}: {e}")

    outcar = read(out_path, ":")

    results = {}
    results["natoms"] = len(outcar[0])
    results["energies"] = [struct.get_potential_energy() for struct in outcar]
    results["forces"] = [struct.get_forces() for struct in outcar]
    results["iter_times"] = iter_times
    results["total_time"] = float(lines[-11].split(":")[1])

    # construct data_dict
    if k not in data_dict:
        data_dict[k] = {}

    data_dict[k][encut] = results


initial = data_dict[2][520]
initial_e = initial["energies"][n]
initial_f = initial["forces"][n]
initial_time = initial["total_time"]

# plot 3 plots: energy errors, force errors, time
fig, ax = plt.subplots(3, 2, sharex=True, figsize=(10, 10))
x = range(len(data_dict.keys()))

size = 125  # marker size
fontsize = 12

titles = ["INITIAL", "FINAL"]
title = titles[n]

# reorder `data_dict` from smallest to largest k/encut
data_dict = dict(sorted(data_dict.items()))
for k in data_dict.keys():
    results = dict(sorted(data_dict[k].items()))

    e_error = []
    e_error_rel = []
    f_error = []
    f_mae = []
    timing = []
    abs_timing = []
    avg5_timing = []
    x_labels = []

    for encut, value in results.items():
        # energy
        e_error.append((value["energies"][n] - initial_e) * 1000 / value["natoms"])

        # relative
        e_error_rel.append(
            (value["energies"][0] - value["energies"][-1]) * 1000 / value["natoms"]
        )

        # force
        f_error.append(np.max(value["forces"][n] - initial_f) * 1000)
        f_mae.append(np.mean(np.abs(value["forces"][n] - initial_f)) * 1000)

        # timing
        avg5_timing.append(np.average(value["iter_times"][5:]))
        abs_timing.append(value["total_time"])
        timing.append(value["total_time"] - initial_time)

        # labels
        x_labels.append(str(encut))
        label = f"{k}x{k}x{k}"

    # plot
    ax[0, 0].scatter(x, e_error, label=label, s=size)
    ax[0, 0].set_ylabel("E - E(0) [meV/at]", fontsize=fontsize)

    ax[1, 0].scatter(x, e_error_rel, label=label, s=size)
    ax[1, 0].set_ylabel("Ei - Ef [meV/at]", fontsize=fontsize)

    ax[2, 0].scatter(x, f_error, label=label, s=size)
    ax[2, 0].set_ylabel("max(F - F(0)) [meV/A]", fontsize=fontsize)

    ax[0, 1].scatter(x, abs_timing, label=label, s=size)
    ax[0, 1].set_ylabel("t [s]", fontsize=fontsize)

    ax[1, 1].scatter(x, avg5_timing, label=label, s=size)
    ax[1, 1].set_ylabel("average for last 5 iter. [s]", fontsize=fontsize)

    ax[2, 1].scatter(x, f_mae, label=label, s=size)
    ax[2, 1].set_ylabel("MAE(F - F(0)) [meV/A]", fontsize=fontsize)

    ax[0, 0].set_xticks(x)
    ax[0, 0].set_xticklabels(x_labels, fontsize=fontsize)
    ax[2, 0].set_xlabel("ENCUT", fontsize=fontsize)

###

plt.rcParams.update({"font.size": fontsize})
plt.suptitle(title)
plt.tight_layout()
plt.legend(loc="best")

plt.show()
