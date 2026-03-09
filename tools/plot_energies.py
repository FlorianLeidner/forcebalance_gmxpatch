import os

import argparse

from pathlib import Path

import numpy as np

import matplotlib.pyplot as plt

from forcebalance.parser import parse_inputs
from forcebalance.forcefield import FF
from forcebalance.objective import Implemented_Targets


def plot_energy(t):

    emm = t.energy_all()
    eqm = t.eqm

    qm_minimum = np.argmin(eqm)
    eqm -= eqm[qm_minimum]
    emm -= emm[qm_minimum]

    x = np.arange(t.ns)

    dpi=300

    fig = plt.figure(figsize=(800/dpi, 600/dpi))

    ax = fig.add_subplot()

    ax.plot(x, eqm, marker="o", lw=2, ms=10, color="darkorchid", zorder=2, label="qm")
    ax.plot(x, emm, marker="o", lw=2, ms=10, color="mediumseagreen", zorder=3, label="mm")

    ax.grid(color="gray", lw=0.5, alpha=0.6, zorder=1)

    ax.set_xlabel("")
    ax.set_ylabel("$\\rm e\ (\\frac{kJ}{mol})$")
    ax.set_title(f"{t.name}")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.legend(loc="center", bbox_to_anchor=(1.05, 0.8))

    fig.savefig("energy_compare.png", dpi=dpi, bbox_inches="tight")

    plt.close()


def parse_args() -> argparse.Namespace:
    _description = "Plot the force field and quantum mechanics based energies"

    parser = argparse.ArgumentParser()

    parser.add_argument("fbin",
                        help="Forcebalance inpout file")
    parser.add_argument("--forcefield",
                        dest="forcefield",
                        default="forcefield",
                        help="The force field directory")
    parser.add_argument("--name",
                        dest="name",
                        default="plots",
                        help="Jobname")

    args = parser.parse_args()

    args.fbin = Path(args.fbin)
    if not args.fbin.exists():
        parser.error(f"{args.fbin} does not exist")

    args.forcefield = Path(args.forcefield)
    if not args.forcefield.exists():
        parser.error(f"{args.forcefield} does not exist")

    elif not args.forcefield.is_dir():
        parser.error(f"{args.forcefield} must be a directory")

    return args


def main():

    args = parse_args()

    # Parse FB input file
    options, target_options = parse_inputs(args.fbin)

    options["ffdir"] = args.forcefield

    ff = FF(options)

    # Retain AbInitio targets
    target_options = [l for l in target_options if "ABINITIO" in l.get("type")]

    root = Path(options["root"])

    options["input_file"] = args.name

    # Assemble targets from ImplementedTargets dictionary
    targets = []
    for target_name in target_options:
        targets.append(Implemented_Targets[target_name["type"]](options, target_name, ff))

    cwd = os.getcwd()

    for t in targets:

        os.chdir(root / t.tempdir)
        for fn in options['forcefield']:
            os.symlink(root / options['ffdir'] / fn, fn)

        plot_energy(t)

        os.chdir(cwd)


if __name__=="__main__":
    main()
