import json
import numpy as np
from solidkit.properties.elastic import calculate_elastic_properties
from solidkit.optimization import optimize_structure
from solidkit.properties.strength import calculate_tensile_strength, calculate_shear_strength, plot_stress_strain

def compute_elastic_properties(atoms):
    """
    Computes the elastic properties and hardness of a given atomic structure.

    Args:
        atoms (ase.Atoms): The atomic structure with a calculator attached.

    Returns:
        dict: A dictionary containing the elastic properties and hardness.
    """
    print("Optimizing structure...")
    atoms = optimize_structure(atoms, fmax=0.01)
    print("Calculating elastic properties...")
    elastics = calculate_elastic_properties(atoms)

    # Estimate Vickers hardness from the calculated bulk and shear moduli
    # elastics['vickers_hardness'] = estimate_vickers_hardness(elastics['bulk_modulus'], elastics['shear_modulus'])

    print("Elastic properties and hardness calculated successfully.")
    return elastics

def compute_strengths(atoms, directions, slip_directions, end_strain, interval_strain):
    """
    Computes the tensile and shear strengths for given directions.

    Args:
        atoms (ase.Atoms): The atomic structure with a calculator attached.
        directions (list): List of directions for tensile strength calculation.
        slip_directions (list): List of slip directions for shear strength calculation.
        end_strain (float): The maximum strain to apply.
        interval_strain (float): The strain step size.

    Returns:
        dict: A dictionary containing the tensile and shear strength data.
    """
    results = {"tensile": {}, "shear": {}}

    for i, d in enumerate(directions):
        print(f"Calculating tensile strength in direction {d}...")
        strain, stress, _ = calculate_tensile_strength(
            atoms=atoms.copy(),
            calculator=atoms.calc,
            direction=d,
            end_strain=end_strain,
            interval_strain=interval_strain
        )
        results["tensile"][f"direction_{i}"] = {
            "direction": d,
            "strain": strain.tolist(),
            "stress": stress.tolist()
        }

    for i, (d, sd) in enumerate(zip(directions, slip_directions)):
        print(f"Calculating shear strength in direction {d} with slip direction {sd}...")
        strain, stress, _ = calculate_shear_strength(
            atoms=atoms.copy(),
            calculator=atoms.calc,
            direction=d,
            slip_direction=sd,
            end_strain=end_strain,
            interval_strain=interval_strain
        )
        results["shear"][f"slip_direction_{i}"] = {
            "direction": d,
            "slip_direction": sd,
            "strain": strain.tolist(),
            "stress": stress.tolist()
        }

    print("Tensile and shear strengths calculated successfully.")
    return results

def save_results_to_json(data, filename):
    """
    Saves the results to a JSON file.

    Args:
        data (dict): The data to save.
        filename (str): The name of the output JSON file.
    """
    # Convert numpy arrays to lists for JSON serialization
    def convert_numpy(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, default=convert_numpy)
    print(f"Results saved to {filename}")

def plot_strength_from_json(json_filename):
    """
    Reads strength data from a JSON file and plots it.

    Args:
        json_filename (str): The name of the input JSON file.
        plot_filename (str): The name of the output plot image file.
    """
    with open(json_filename, 'r') as f:
        results = json.load(f)

    plot_data_dict = {}

    if "strength_results" in results and "tensile" in results["strength_results"]:
        for key, value in results["strength_results"]["tensile"].items():
            direction_str = ''.join(map(str, value['direction']))
            plot_data_dict[f'Tensile [{direction_str}]'] = (
                np.array(value['strain']),
                np.array(value['stress']),
                fr'$\sigma_{{{direction_str}}}$'
            )

    if "strength_results" in results and "shear" in results["strength_results"]:
        for key, value in results["strength_results"]["shear"].items():
            direction_str = ''.join(map(str, value['direction']))
            slip_direction_str = ''.join(map(str, value['slip_direction']))
            plot_data_dict[f'Shear [{direction_str}][{slip_direction_str}]'] = (
                np.array(value['strain']),
                np.array(value['stress']),
                fr'$\sigma_{{{direction_str}{slip_direction_str}}}$'
            )

    if plot_data_dict:
        plot_stress_strain(plot_data_dict)
    else:
        print("WARN: No strength data found in the JSON file to plot.")


