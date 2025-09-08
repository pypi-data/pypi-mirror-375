import os
import pandas as pd
from pathlib import Path
import logging
from multiprocessing.dummy import Pool as ThreadPool
import re
from io import StringIO
from tqdm import tqdm
import numpy as np

from filterzyme.steps.step import Step


import biotite.database.rcsb as rcsb
import biotite.structure as struc
import biotite.structure.io.pdbx as pdbx
import biotite.structure.io.pdb as pdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_structure(type, file):
    if type == 'PDB':
        structure = pdb.get_structure(file, model=1)
    if type == 'PDBx':
        structure = pdbx.get_structure(file, model=1)
    return structure



def extract_ligands(structure):
    """
    Extract ligands from a Biotite structure (AtomArray or AtomArrayStack).
    """
    if not isinstance(structure, (struc.AtomArray, struc.AtomArrayStack)):
        return []

    # Identify ligand atoms
    is_ligand = ~struc.filter_amino_acids(structure) & ~struc.filter_solvent(structure)
    if not is_ligand.any():
        return []

    ligands = structure[is_ligand]
    ligand_structures = []

    # Use both res_id and chain_id for uniqueness
    unique_residues = set(zip(ligands.chain_id, ligands.res_id))
    for chain_id, res_id in unique_residues:
        mask = (ligands.chain_id == chain_id) & (ligands.res_id == res_id)
        ligand_structures.append(ligands[mask].copy())

    return ligand_structures



def extract_monomer(complex):
    complex = complex[struc.filter_amino_acids(complex)]
    # Get the monomer that belongs to the first atom in the structure
    return complex[struc.get_chain_masks(complex, [0])[0]]


def clean_pdb_atom_names(pdb_file):
    """
    Removes suffixes like '_1', '_2' from atom names in a Biotite PDBFile object.
    """
    atom_array = pdb_file.get_structure()
    cleaned_names = [
        re.sub(r'(_\d+|_)$', '', name)  # Removes "_", "_1", "_23", etc.
        for name in atom_array.atom_name
    ]
    atom_array.atom_name = cleaned_names
    pdb_file.set_structure(atom_array)
    return pdb_file


def truncate_atom_names(structure):
    # Truncate atom names to the first 4 characters
    structure.atom_name = [atom[:4] for atom in structure.atom_name]
    return structure


def truncate_residue_names(structure):
    structure.res_name = [res[:3] for res in structure.res_name]  # Truncate to 3 characters
    return structure


def get_residue_ids(structure):
    """Returns a set of (res_id, ins_code) for each residue."""
    return set(zip(structure.res_id, structure.ins_code))



def write_structure_to_file(combined, output_dir, entry_name, key1, key2):
    from io import StringIO

    output_dir = Path(output_dir) / entry_name
    output_dir.mkdir(parents=True, exist_ok=True)

    key = f"{key1}__{key2}"
    output_path = output_dir / f"{key}.pdb"

    pdb_file = pdb.PDBFile()
    pdb_file.set_structure(combined)
    pdb_file = clean_pdb_atom_names(pdb_file)

    # Write to string and split into lines
    buffer = StringIO()
    pdb_file.write(buffer)
    pdb_lines = buffer.getvalue().splitlines()

    result_lines = []
    prev_chain = None
    last_atom_line = None

    for line in pdb_lines:
        if line.startswith(('ATOM', 'HETATM')):
            chain_id = line[21]
            if prev_chain is not None and chain_id != prev_chain and last_atom_line:
                # Insert TER using last_atom_line info
                serial = last_atom_line[6:11]
                res_name = last_atom_line[17:20]
                chain = last_atom_line[21]
                res_seq = last_atom_line[22:26]
                ter_line = f"TER   {serial}      {res_name} {chain}{res_seq}"
                result_lines.append(ter_line)
            prev_chain = chain_id
            last_atom_line = line
        result_lines.append(line)

    # Add TER after last chain (if there was at least one ATOM/HETATM)
    if last_atom_line:
        serial = last_atom_line[6:11]
        res_name = last_atom_line[17:20]
        chain = last_atom_line[21]
        res_seq = last_atom_line[22:26]
        ter_line = f"TER   {serial}      {res_name} {chain}{res_seq}"
        result_lines.append(ter_line)

    result_lines.append("END")

    with open(output_path, "w") as f:
        f.write('\n'.join(result_lines) + '\n')

    return str(output_path)


def superimpose_within_same_docked_structure(protein_dict, ligand_dict, entry_name, output_dir):
    
    output_paths = []
    keys = list(protein_dict.keys())

    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            key1, key2 = keys[i], keys[j]
            try: 
                ref_structure = protein_dict[key1]
                ref_ligands = ligand_dict[key1]
                mov_structure = protein_dict[key2]
                mov_ligands = ligand_dict[key2]

                aligned, transform, _, _ = struc.superimpose_homologs(ref_structure, mov_structure)
                aligned.chain_id[:] = "B"

                ref_structure.chain_id[:] = "A"
                all_structures = [ref_structure, aligned]

                for i, lig in enumerate(ref_ligands):
                    lig = lig.copy()
                    lig.chain_id[:] = chr(84 + i)
                    lig.res_id[:] = i + 1
                    all_structures.append(lig)


                for i, lig in enumerate(mov_ligands):
                    lig_aligned = transform.apply(lig.copy())
                    lig_aligned.chain_id[:] = chr(76 + i)
                    lig_aligned.res_id[:] = i + len(ref_ligands) + 1
                    all_structures.append(lig_aligned)


                combined = struc.concatenate(all_structures)
                combined = truncate_residue_names(combined)
                combined = truncate_atom_names(combined)

                output_paths.append(write_structure_to_file(combined, output_dir, entry_name, key1, key2))
            
            except Exception as e:
                print(f"Failed {entry_name} {key1} vs {key2}: {e}")
            
    return output_paths



def superimpose_different_docked_structure(protein_1_dict, ligand_1_dict, protein_2_dict, ligand_2_dict, entry_name, output_dir):
    output_paths = []

    for structure1_key, protein_1_structure in protein_1_dict.items():
        protein_1_structure.chain_id[:] = "A"
        ligands1 = ligand_1_dict[structure1_key]

        for structure2_key, protein_2_structure in protein_2_dict.items():
            try:
                structure2_aligned, transform, _, _ = struc.superimpose_homologs(protein_1_structure, protein_2_structure)
                structure2_aligned.chain_id[:] = "B"

                ligands2 = ligand_2_dict[structure2_key]

                all_structures = [protein_1_structure, structure2_aligned]

                for i, lig in enumerate(ligands1):
                    lig = lig.copy()
                    lig.chain_id[:] = chr(84 + i)
                    lig.res_id[:] = i + 1
                    all_structures.append(lig)

                for i, lig in enumerate(ligands2):
                    lig_aligned = transform.apply(lig.copy())
                    lig_aligned.chain_id[:] = chr(86 + i)
                    lig_aligned.res_id[:] = i + len(ligands1) + 1
                    all_structures.append(lig_aligned)

                combined = struc.concatenate(all_structures)
                combined = truncate_residue_names(combined)
                combined = truncate_atom_names(combined)

                output_paths.append(write_structure_to_file(combined, output_dir, entry_name, structure1_key, structure2_key))

            except Exception as e:
                print(f"Failed {entry_name} {structure1_key} vs {structure2_key}: {e}")

    return output_paths


class SuperimposeStructures(Step):
    def __init__(self, structure_1 = None, structure_2 = None, name1: str = '', name2: str = '', output_dir: str = '', num_threads=1): 
        self.structure_1 = structure_1
        self.structure_2 = structure_2
        self.name1 = name1
        self.name2 = name2
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.num_threads = num_threads or 1

    def __execute(self, df: pd.DataFrame, output_dir) -> list:
        
        all_output_paths = []

        for _, row in tqdm(df.iterrows(), total=len(df), desc="Superimposing structures"):

            entry_name = row['Entry']
            structure_1 = {}
            structure_1_ligands = {}
            structure_2 = {}
            structure_2_ligands = {}
            row_output_paths = []

            for structure_1_path in row[self.structure_1]:
                structure_1_path = Path(structure_1_path)
                if not structure_1_path.exists():
                    logger.warning(f"Structure 1 path not found: {structure_1_path}")
                    continue

                try:
                    with open(structure_1_path, "r") as f:
                        key = structure_1_path.stem
                        pdb_data = pdb.PDBFile.read(f)
                        full_structure = pdb.get_structure(pdb_data, model=1)
                        structure_1[key] = extract_monomer(full_structure)
                        structure_1_ligands[key] = extract_ligands(full_structure)
                except Exception as e:
                    logger.error(f"Error processing {structure_1_path}: {e}")

            for structure_2_path in row[self.structure_2]:
                structure_2_path = Path(structure_2_path)
                if not structure_2_path.exists():
                    logger.warning(f"Structure 2 path not found: {structure_2_path}")
                    continue

                try:
                    with open(structure_2_path, "r") as f:
                        key = structure_2_path.stem
                        pdb_data = pdb.PDBFile.read(f)
                        full_structure = pdb.get_structure(pdb_data, model=1)
                        structure_2[key] = extract_monomer(full_structure)
                        structure_2_ligands[key] = extract_ligands(full_structure)
                except Exception as e:
                    logger.error(f"Error processing {structure_2_path}: {e}")

            # Superimpose only within this row's proteins
            row_output_paths = []
            row_output_paths += superimpose_within_same_docked_structure(structure_1, structure_1_ligands, entry_name, self.output_dir)
            row_output_paths += superimpose_within_same_docked_structure(structure_2, structure_2_ligands, entry_name, self.output_dir)
            row_output_paths += superimpose_different_docked_structure(structure_1, structure_1_ligands, structure_2, structure_2_ligands, entry_name, self.output_dir)
            all_output_paths.append(row_output_paths)

        return all_output_paths


    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.output_dir:
            if self.num_threads > 1:
                output_filenames = []
                df_list = np.array_split(df, self.num_threads)
                for df_chunk in df_list:
                    output_filenames += self.__execute(df_chunk, self.output_dir)
                    
                df['superimposedstructure_dir'] = output_filenames
                return df
            
            else:
                output_filenames = self.__execute(df, self.output_dir)
                df['superimposedstructure_dir'] = output_filenames
                return df
        else:
            print('No output directory provided')

