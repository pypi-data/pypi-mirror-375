import warnings
from scipy.optimize import minimize
import numpy as np
from ase import Atoms
from ase.neighborlist import NeighborList
from pymatgen.core import Structure
from pymatgen.analysis.ewald import EwaldSummation
from joblib import Parallel, delayed

# -------------------------------------------------------------------------------
# Potential parameters for TiO2
# -------------------------------------------------------------------------------
cutoff = 15.0

# Potential parameters and atomic charges
parameters = {
    'charges': {
        'Ti': 2.196,
        'O': -1.098
    },
    'buckingham': {
        ('Ti', 'Ti'): (31120.1, 0.1540, 5.25),
        ('O', 'O'): (11782.7, 0.2340, 30.22),
        ('O', 'Ti'): (16957.5, 0.1940, 12.59)
    },
    'lennard_jones': {
        ('Ti', 'Ti'): (1.0, 0.0),
        ('O', 'O'): (1.0, 0.0),
        ('O', 'Ti'): (1.0, 0.0)
    }
}

# -------------------------------------------------------------------------------
# Core functions for TiO2 potential calculations
# -------------------------------------------------------------------------------
def setup_type_arrays(symbols):
    """
    Create mapping between atom symbols and type indices
    
    Args:
        symbols: List of chemical symbols for all atoms
        
    Returns:
        type_indices: Array of type indices for each atom
        type_map: Dictionary mapping symbols to type indices
    """
    unique_symbols = sorted(set(symbols))
    type_map = {sym: i for i, sym in enumerate(unique_symbols)}
    type_indices = np.array([type_map[s] for s in symbols])
    return type_indices, type_map

def build_neighbor_list(atoms, cutoff):
    """
    Build neighbor list for a given atomic structure
    
    Args:
        atoms: ASE Atoms object
        cutoff: Distance cutoff for neighbor search
        
    Returns:
        nl: ASE NeighborList object
    """
    nl = NeighborList([cutoff/2] * len(atoms), 
                     self_interaction=False, 
                     bothways=True)
    nl.update(atoms)
    return nl

def calculate_short_range_energy(atoms, nl, type_indices, buck_params, lj_params):
    """
    Calculate short-range energy using Buckingham and Lennard-Jones potentials
    
    Args:
        atoms: ASE Atoms object
        nl: Neighbor list
        type_indices: Array of type indices for each atom
        buck_params: Buckingham potential parameters
        lj_params: Lennard-Jones potential parameters
        
    Returns:
        energy: Total short-range energy
    """
    positions = atoms.get_positions()
    cell = np.array(atoms.get_cell())
    energy = 0.0
    n_atoms = len(atoms)
    
    # Precompute all neighbors
    all_indices = []
    all_offsets = []
    for i in range(n_atoms):
        indices, offsets = nl.get_neighbors(i)
        all_indices.append(indices)
        all_offsets.append(offsets)
    
    # Calculate energy
    for i in range(n_atoms):
        indices = all_indices[i]
        offsets = all_offsets[i]
        
        for j, offset in zip(indices, offsets):
            if i < j:
                pos_i = positions[i]
                offset_dot = np.dot(offset, cell)
                pos_j = positions[j] + offset_dot
                r_vec = pos_i - pos_j
                r = np.linalg.norm(r_vec)
                
                if r <= cutoff and r > 1e-8:
                    type_i = type_indices[i]
                    type_j = type_indices[j]
                    
                    # Get parameters
                    A_buck, rho_buck, C_buck = buck_params[type_i, type_j]
                    A_lj, _ = lj_params[type_i, type_j]
                    
                    # Buckingham potential
                    r6 = r**6
                    buck = A_buck * np.exp(-r / rho_buck) - C_buck / r6
                    
                    # Lennard-Jones potential
                    r12 = r**12
                    lj = A_lj / r12
                    
                    energy += buck + lj
                    
    return energy

def calculate_short_range_forces(atoms, nl, type_indices, buck_params, lj_params):
    """
    Calculate short-range forces using Buckingham and Lennard-Jones potentials
    
    Args:
        atoms: ASE Atoms object
        nl: Neighbor list
        type_indices: Array of type indices for each atom
        buck_params: Buckingham potential parameters
        lj_params: Lennard-Jones potential parameters
        
    Returns:
        forces: Array of forces on all atoms
    """
    positions = atoms.get_positions()
    cell = np.array(atoms.get_cell())
    n_atoms = len(atoms)
    forces = np.zeros((n_atoms, 3))
    
    # Precompute all neighbors
    all_indices = []
    all_offsets = []
    for i in range(n_atoms):
        indices, offsets = nl.get_neighbors(i)
        all_indices.append(indices)
        all_offsets.append(offsets)
    
    # Calculate forces
    for i in range(n_atoms):
        indices = all_indices[i]
        offsets = all_offsets[i]
        
        for j, offset in zip(indices, offsets):
            pos_i = positions[i]
            offset_dot = np.dot(offset, cell)
            pos_j = positions[j] + offset_dot
            r_vec = pos_i - pos_j
            r = np.linalg.norm(r_vec)
            
            if r <= cutoff and r > 1e-8:
                type_i = type_indices[i]
                type_j = type_indices[j]
                
                # Get parameters
                A_buck, rho_buck, C_buck = buck_params[type_i, type_j]
                A_lj, _ = lj_params[type_i, type_j]
                
                # Unit vector
                unit_vec = r_vec / r
                
                # Buckingham force
                buck_force_mag = (A_buck / rho_buck) * np.exp(-r / rho_buck) - 6 * C_buck / r**7
                buck_force = buck_force_mag * unit_vec
                
                # Lennard-Jones force
                lj_force_mag = 12 * A_lj / r**13
                lj_force = lj_force_mag * unit_vec
                
                total_force = buck_force + lj_force
                forces[i] += total_force
                forces[j] -= total_force
                
    return forces

def calculate_ewald_energy_pymatgen(atoms):
    """
    Calculate Ewald energy using pymatgen
    
    Args:
        atoms: ASE Atoms object
        
    Returns:
        energy: Ewald energy
    """
    symbols = atoms.get_chemical_symbols()
    positions = atoms.get_positions()
    cell = atoms.get_cell()
    
    structure = Structure(lattice=cell, species=symbols, coords=positions, coords_are_cartesian=True)
    
    charges = [parameters['charges'][s] for s in symbols]
    structure.add_oxidation_state_by_site(charges)
    
    ewald = EwaldSummation(structure)
    return ewald.total_energy

def calculate_ewald_forces_pymatgen(atoms):
    """
    Calculate Ewald forces using pymatgen
    
    Args:
        atoms: ASE Atoms object
        
    Returns:
        forces: Ewald forces
    """
    symbols = atoms.get_chemical_symbols()
    positions = atoms.get_positions()
    cell = atoms.get_cell()
    
    structure = Structure(lattice=cell, species=symbols, coords=positions, coords_are_cartesian=True)
    
    charges = [parameters['charges'][s] for s in symbols]
    structure.add_oxidation_state_by_site(charges)
    
    ewald = EwaldSummation(structure, compute_forces=True)
    return ewald.forces

# -------------------------------------------------------------------------------
# Optimization functions
# -------------------------------------------------------------------------------
def total_energy(positions, atoms, nl, type_indices, buck_params, lj_params):
    """
    Calculate total energy for optimization
    
    Args:
        positions: Atomic positions as a flat array
        atoms: ASE Atoms object
        nl: Neighbor list
        type_indices: Array of type indices for each atom
        buck_params: Buckingham potential parameters
        lj_params: Lennard-Jones potential parameters
        
    Returns:
        energy: Total energy
    """
    atoms = atoms.copy()
    atoms.set_positions(positions.reshape(-1, 3))
    
    short_range = calculate_short_range_energy(atoms, nl, type_indices, buck_params, lj_params)
    ewald = calculate_ewald_energy_pymatgen(atoms)
    
    return short_range + ewald

def total_forces(positions, atoms, nl, type_indices, buck_params, lj_params):
    """
    Calculate total forces for optimization
    
    Args:
        positions: Atomic positions as a flat array
        atoms: ASE Atoms object
        nl: Neighbor list
        type_indices: Array of type indices for each atom
        buck_params: Buckingham potential parameters
        lj_params: Lennard-Jones potential parameters
        
    Returns:
        forces: Total forces as a flat array
    """
    atoms = atoms.copy()
    atoms.set_positions(positions.reshape(-1, 3))
    
    short_range_forces = calculate_short_range_forces(atoms, nl, type_indices, buck_params, lj_params)
    ewald_forces = calculate_ewald_forces_pymatgen(atoms)
    
    return -(short_range_forces + ewald_forces).reshape(-1)

def optimize_structure(atoms):
    """
    Optimize atomic structure using TiO2 potential
    
    Args:
        atoms: ASE Atoms object to optimize
        
    Returns:
        optimized_atoms: Optimized ASE Atoms object
    """
    # Precomputations
    symbols = atoms.get_chemical_symbols()
    type_indices, type_map = setup_type_arrays(symbols)
    
    # Precompute parameter matrices
    n_types = len(type_map)
    buck_params = np.zeros((n_types, n_types, 3))
    lj_params = np.zeros((n_types, n_types, 2))
    
    for (sym1, sym2), params in parameters['buckingham'].items():
        i, j = type_map[sym1], type_map[sym2]
        buck_params[i, j] = params
        buck_params[j, i] = params
    
    for (sym1, sym2), params in parameters['lennard_jones'].items():
        i, j = type_map[sym1], type_map[sym2]
        lj_params[i, j] = params
        lj_params[j, i] = params
    
    # Build neighbor list
    nl = build_neighbor_list(atoms, cutoff)
    
    x0 = atoms.get_positions().reshape(-1)
    
    # Suppress optimization warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        # Robust optimization method
        result = minimize(
            fun=total_energy,
            x0=x0,
            args=(atoms, nl, type_indices, buck_params, lj_params),
            method='L-BFGS-B',
            jac=total_forces,
            options={'disp': False, 'gtol': 0.01, 'maxiter': 150}
        )

    optimized_atoms = atoms.copy()
    optimized_atoms.set_positions(result.x.reshape(-1, 3))
    optimized_atoms.info['e'] = result.fun
    
    return optimized_atoms

# -------------------------------------------------------------------------------
# Parallel processing functions
# -------------------------------------------------------------------------------
def TiO2_parallel(poscar_list, n_jobs=2):
    """
    Optimize multiple structures in parallel
    
    Args:
        poscar_list: List of ASE Atoms objects
        n_jobs: Number of parallel jobs
        
    Returns:
        results: List of optimized ASE Atoms objects
    """
    results = Parallel(n_jobs=n_jobs)(delayed(optimize_structure)(poscar) for poscar in poscar_list)
    return results

# -------------------------------------------------------------------------------
# Example usage
# -------------------------------------------------------------------------------
input_text = """random_000_0001 -159.20142913
1.0
  4.5001550000000003  -2.9976120000000002  -0.0183040000000000
 -0.0147400000000000   6.0171260000000002   0.0312390000000000
  0.0027910000000000  -0.0233510000000000   4.4929649999999999
O Ti
8 4
Cartesian
  3.0213949090740000  -2.0139062004339996   0.2627437860700000   !O1
  0.7643394467970001   2.4908692604640001   0.7663209771330000   !O2
  3.0141508544540003   0.9945969349340003   0.2783628985140000   !O3
  2.5403454622700004  -0.5225455236400002   2.5173486534420002   !O4
  0.2832043157200000   3.9823296655960005   3.0208006079340000   !O5
  2.5329440400309999   2.4859906495500002   2.5329051301479999   !O6
  0.2906012959790000   0.9737783218850000   3.0052665206399998   !O7
  0.7716148339950001  -0.5175827227290000   0.7507155903239999   !O8
  1.6449655244120001   3.9927927548120001   1.6574142340679998   !Ti1
  3.9038445495500000  -0.5262877136340001   3.8791160392279997   !Ti2
  3.8964341549110002   2.4822542212700003   3.8947174821919996   !Ti3
  1.6524075014240001   0.9842055813120002   1.6418484817399999   !Ti4
random_000_0002 -159.06090960
1.0
  4.5220900000000004  -0.0074300000000000  -0.0147120000000000
  0.0083680000000000   5.3774769999999998  -0.1397070000000000
  0.0161420000000000   0.1281550000000000   4.9340270000000004
O Ti
8 4
Cartesian
  2.2582038353799998   4.9973731094029992   4.5862908178390001   !O1
  4.2972508839519996   3.7478140535180002   3.7968659135080003   !O2
  2.0366927599019999   2.3089814454390001   4.6568713773690007   !O3
  4.5105025643080010   1.0587663096560000   3.8659959569680002   !O4
  4.2910999065580002   4.9088709837070006   1.2980233426830001   !O5
  2.0266929602980004   1.0199309825750000   2.2216877204350003   !O6
  4.5043695174700007   2.2197422916600003   1.3671455548460001   !O7
  2.2481858493760001   3.7083006537309995   2.1510880424730003   !O8
  0.9990794319360000   0.7175278935460000   0.5909794850500000   !Ti1
  3.2750677754060002   5.2145033286580009   2.9354033877440000   !Ti2
  1.0098387849620001   2.5295064597329997   3.0126023211550006   !Ti3
  3.2642453008320000   3.4025635340700000   0.5138192518740001   !Ti4
random_000_0003 -158.41202269
1.0
  4.8230560000000002  -0.0000380000000000  -0.0000370000000000
 -0.0000380000000000   4.8230570000000004  -0.0000380000000000
 -0.0000370000000000  -0.0000380000000000   4.8230560000000002
O Ti
8 4
Cartesian
  0.2876184719350001   0.2876184719350001   0.2876184719350000   !O1
  1.1318743895470000   3.5434505032220005   2.6988731897820002   !O2
  3.5434500031790002   2.6988735146390002   1.1318793877140001   !O3
  2.6988736897500001   1.1318788877090000   3.5434503280730003   !O4
  3.5434296716820004   3.5434344947759997   3.5434344947750001   !O5
  2.6991351725830000   0.2874191891850000   1.1319820333720001   !O6
  0.2874148660890000   1.1319865315019999   2.6991398205300001   !O7
  1.1319815333740000   2.6991354975480002   0.2874145412370000   !O8
  1.9154517271309999   1.9154517271310001   1.9154517271309999   !Ti1
  4.3269612263430011   1.9154667803780003   4.3270094572730002   !Ti2
  1.9154576341800003   4.3270142803780010   4.3269655494360002   !Ti3
  4.3270041341900001   4.3269660494280009   1.9154672803760002   !Ti4
random_000_0004 -157.98431779
1.0
  5.2444490000000004  -0.0620250000000000  -1.5767439999999999
  0.0646550000000000   5.3320140000000000   0.0058310000000000
 -1.1451290000000001   0.0081820000000000   5.2080739999999999
O Ti
8 4
Cartesian
  2.8946490650810000   0.0131869778350000   0.4050852277800001   !O1
  0.3209018572690001   4.0429542660370004   1.1977459130240000   !O2
 -0.2840400060940000   1.3811667245019998   3.7989900143159998   !O3
  2.3543310370820003   2.6830458163439999   3.0121922740789997   !O4
  3.1059635908949996   0.0073867350080000   3.1815347749940002   !O5
  0.5322679436200001   4.0374734069400002   3.9741571557760000   !O6
  1.0724328615100001   1.3672374249140000   1.3673910391499999   !O7
  3.7108002356909999   2.6694259738960002   0.5804937280210000   !O8
  3.0164543041630001   1.3432371320900001   1.7948476298520002   !Ti1
  0.4103712883400000   2.7072321822549998   2.5845769695959997   !Ti2
  0.9506286668580001   0.0371392954660000  -0.0224010871010000   !Ti3
  3.6213213563570004   4.0051640980610008  -0.8062711828400001   !Ti4
"""
def example():
    """
    Example function demonstrating how to use the TiO2 optimization library
    """
    import time
    from aegon.libposcar import readposcars, writeposcars
    
    file = 'tio2.vasp'
    with open(file, "w") as f: 
        f.write(input_text)
    
    print('SERIAL OPTIMIZATION')
    begin_time = time.time()
    for iposcar in readposcars(file):
        start_time = time.time()
        poscar = optimize_structure(iposcar)
        end_time = time.time()
        print("%s: %.15f at %.2f" % (poscar.info['i'], poscar.info['e'], end_time-start_time))
    end_time = time.time()
    print("Total time = %.2f" % (end_time-begin_time))
    
    print('PARALLEL OPTIMIZATION')
    listposcar = readposcars(file)
    start_time = time.time()
    result = TiO2_parallel(listposcar, n_jobs=4)
    end_time = time.time()
    for iposcar in result:
        print("%s: %.15f" % (iposcar.info['i'], iposcar.info['e']))
    print("Total time = %.2f" % (end_time-start_time))
    
    writeposcars(result, 'final.vasp', 'C')

# Uncomment to run example
#example()
