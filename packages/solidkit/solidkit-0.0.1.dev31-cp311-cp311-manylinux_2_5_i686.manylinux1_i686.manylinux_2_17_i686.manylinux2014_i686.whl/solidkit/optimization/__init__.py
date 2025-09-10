#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from ase.io import read, write
from ase.optimize import LBFGS, MDMin, FIRE, FIRE2, BFGS, LBFGSLineSearch
from ase.units import GPa


def get_calculator(potential='', atoms=None, stress_sign=True):
    """
    Initializes and returns an ASE calculator based on the input argument.

    Args:
        calculator_arg (str): The command-line argument for the calculator.
        atoms (ase.Atoms): The atoms object, needed for some calculators.
        stress_sign (bool):
            If True (default), use the stress as is. If False, invert the sign
            of the stress components.
    """
    if getattr(atoms, 'calc', None):
        calc = atoms.calc
    else:
        calc = None
    if potential.lower().endswith('.pth'):
        from mattersim.forcefield import MatterSimCalculator
        try:
            import torch
            device = "cuda"if torch.cuda.is_available() else "cpu"
        except Exception as e:
            device = "cpu"
        calc = MatterSimCalculator(load_path=potential, device=device)
    elif potential.lower().endswith('.tersoff'):
        from ase.calculators.tersoff import Tersoff
        calc = Tersoff.from_lammps(potential)
        def todict_m(*args, **kwargs):
            return {}
        calc.todict = todict_m
    elif not calc:
        raise ValueError(f"Unsupported calculator type: '{potential}'")

    # This wrapper function modifies the stress reported by the calculator.
    def calculate_modify_stress(self, *args, **kwargs):
        self.calc.calculate_old(self, *args, **kwargs)
        if 'stress' in self.calc.results:
            self.calc.results['stress'] *= -1.0

    if not stress_sign:
        if not hasattr(calc, 'calculate_old'):
            calc.calculate_old = calc.calculate
            calc.calculate = calculate_modify_stress

    return calc

def optimize_structure(atoms, fmax=0.05, method='LBFGS', steps=5000, trajectory='relax.traj', pressure=None, calculator=None):
    """
    Performs geometry optimization (and optionally cell optimization) for a given atomic structure.

    This function makes a copy of the atoms object, attaches an ASE calculator,
    applies a potential-specific stress correction if needed, and runs a
    user-selected optimization algorithm to relax the atomic positions and,
    optionally, the unit cell to a target pressure.

    Note: The stress modification (stress_sign=False: `stress *= -1.0`) is
    needed for some calculators with a different definition of stress.

    Args:
        atoms (ase.Atoms):
            The ASE Atoms object to be optimized.
        fmax (float):
            The maximum force tolerance for convergence (in eV/Å).
        method (str):
            The name of the ASE optimizer to use.
            Supported options: 'LBFGS', 'FIRE', 'MDMin', etc.
        steps (int):
            The maximum number of optimization steps.
        trajectory (str or Trajectory):
            Filename for the trajectory of the optimization. Can be None.
        pressure (float, optional):
            The target hydrostatic pressure in GPa. If provided, both the atomic
            positions and the cell will be relaxed to this target pressure.
            If None (default), only the atomic positions are relaxed.
        calculator (ase.calculators.calculator.Calculator, optional):
            The ASE calculator to use. If not provided, it's assumed that one
            is already attached to the atoms object.

    Returns:
        ase.Atoms: The optimized ASE Atoms object.
    """
    atoms_opt = atoms.copy()

    calc = calculator if calculator else atoms.calc
    if calc is None:
        raise ValueError("ASE calculator not found. Please attach a calculator to the Atoms object or pass it as an argument.")

    atoms_opt.calc = calc

    optimizer_map = {
        'lbfgs': LBFGS,
        'fire': FIRE,
        'fire2': FIRE2,
        'mdmin': MDMin,
        'bfgs': BFGS,
        'lbfgslinesearch': LBFGSLineSearch,
    }

    optimizer_class = optimizer_map.get(method.lower(), None)
    if not optimizer_class:
        raise ValueError(
            f"Unknown optimizer method: {method}. "
            f"Available options are: {list(optimizer_map.keys())}"
        )

    # Set up the optimizer, optionally with cell relaxation
    if not trajectory: trajectory = None
    if pressure is not None:
        try:
            # from ase.filters import FrechetCellFilter as UnitCellFilter
            from ase.filters import ExpCellFilter as UnitCellFilter
        except Exception:
            from ase.filters import UnitCellFilter
        print(f"Cell optimization enabled. Target pressure: {pressure} GPa")
        # Convert pressure from GPa to ASE units (eV/Å^3)
        pressure_ase = pressure * GPa
        dyn_obj = UnitCellFilter(atoms_opt, scalar_pressure=pressure_ase)
        optimizer = optimizer_class(dyn_obj, trajectory=trajectory)
    else:
        print("Optimizing forces only (cell is fixed).")
        optimizer = optimizer_class(atoms_opt, trajectory=trajectory)

    def print_final():
        # step = optimizer.get_number_of_steps()
        forces = atoms_opt.get_forces()
        # Get max force components for each direction
        maxf = np.max(np.abs(forces), axis=0)
        fmt = "{:>15.6f}"
        print(f" Max forces (eV/Å) :")
        print(" "*5 + fmt.format(maxf[0]) + fmt.format(maxf[1]) + fmt.format(maxf[2]))

        if pressure is not None:
            # stress = atoms_opt.get_stress(voigt=False)
            # Voigt notation: [xx, yy, zz, yz, xz, xy]
            sv = atoms_opt.get_stress(voigt=True) / GPa
            print(f" Stress (GPa):")
            print(" "*5 + fmt.format(sv[0]) + fmt.format(sv[1]) + fmt.format(sv[2]))
            print(" "*5 + fmt.format(sv[3]) + fmt.format(sv[4]) + fmt.format(sv[5]))

    # Attach the status printer to the optimizer
    # optimizer.attach(print_final, interval=1)

    print("\nStarting optimization...")
    print("-" * 60)
    optimizer.run(fmax=fmax, steps=steps)
    print("-" * 60)
    print_final()

    return atoms_opt
