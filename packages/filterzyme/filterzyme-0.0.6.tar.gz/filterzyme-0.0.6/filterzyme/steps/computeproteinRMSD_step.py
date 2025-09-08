from filterzyme.steps.step import Step
from filterzyme.utils.helpers import clean_plt,extract_entry_name_from_PDB_filename

import pandas as pd
from pathlib import Path
import logging
from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os 

import biotite.structure as struc
import biotite.structure.io.pdb as pdb
from biotite.structure.io.pdb import PDBFile
from scipy.spatial.distance import cdist  
from openbabel import openbabel as ob
from openbabel import pybel
import tempfile
from Bio import PDB
from itertools import combinations_with_replacement

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Global plot style
plt.rcParams['svg.fonttype'] = 'none'  # Ensure text is saved as text
sns.set(rc={'figure.figsize': (3,3), 'font.family': 'sans-serif', 'font.sans-serif': 'DejaVu Sans', 'font.size': 12}, 
        style='ticks')


def compute_proteinRMSD(pdb_file):
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure('complex', pdb_file)
    model = structure[0]

    # Need both chains
    if 'A' not in model or 'B' not in model:
        logger.warning(f"Chains A/B not found in {pdb_file}")
        return np.nan
    
    # Get C-alpha atoms from both chains
    chain_A, chain_B = model['A'], model['B']
    atoms_A = [a for a in chain_A.get_atoms() if a.get_name() == 'CA']
    atoms_B = [a for a in chain_B.get_atoms() if a.get_name() == 'CA']

    # Ensure that the number of C-alpha atoms in both chains match
    if len(atoms_A) != len(atoms_B) or len(atoms_A) == 0:
        logger.warning(f"CA count mismatch or zero in {pdb_file}: {len(atoms_A)} vs {len(atoms_B)}")
        return np.nan

    sup = PDB.Superimposer()
    sup.set_atoms(atoms_A, atoms_B)
    sup.apply(chain_B.get_atoms())
    return float(sup.rms)



def get_tool_from_structure_name(structure_name: str) -> str:
    """
    Extracts the docking tool name from a structure string (e.g., 'Q97WW0_1_vina' -> 'vina').
    Assumes the tool is the last segment after the last underscore.
    """
    if '_' in structure_name:
        return structure_name.split('_')[-1]
    return "UNKNOWN_tool" # Fallback if format doesn't match



def compute_tool_pair_stats(rmsd_df, tools=["chai", "vina", "boltz"]):
    # Normalize tool names
    rmsd_df["tool1"] = rmsd_df["tool1"].str.strip().str.lower()
    rmsd_df["tool2"] = rmsd_df["tool2"].str.strip().str.lower()
    tools = [t.strip().lower() for t in tools]

    # Define consistent pair labels
    def get_pair_label(row):
        t1, t2 = sorted([row["tool1"], row["tool2"]])
        return f"{t1}-{t2}"

    rmsd_df["tool_pair"] = rmsd_df.apply(get_pair_label, axis=1)

    all_pairwise_rmsds = []
    pairwise_stats = []

    for t1, t2 in combinations_with_replacement(tools, 2):
        label = f"{min(t1, t2)}-{max(t1, t2)}"
        subset = rmsd_df[rmsd_df["tool_pair"] == label]
        rmsds = subset["proteinRMSD"].dropna().tolist()

        all_pairwise_rmsds.extend(rmsds)

        pairwise_stats.append({
            "tool_pair": label,
            "mean_proteinRMSD": np.mean(rmsds) if rmsds else np.nan,
            "std_proteinRMSD": np.std(rmsds) if rmsds else np.nan,
            "n": len(rmsds)
        })

    # Overall stats
    pairwise_stats.append({
        "tool_pair": "overall",
        "overall_proteinRMSD_mean": np.mean(all_pairwise_rmsds) if all_pairwise_rmsds else np.nan,
        "overall_proteinRMSD_std": np.std(all_pairwise_rmsds) if all_pairwise_rmsds else np.nan,
        "n": len(all_pairwise_rmsds)
    })

    return pd.DataFrame(pairwise_stats)


def compute_entrywise_tool_pair_stats(rmsd_df, tools=["chai", "vina", "boltz"]):
    from itertools import combinations_with_replacement

    tools = [t.strip().lower() for t in tools]
    all_stats = []

    for entry, group in rmsd_df.groupby("Entry"):
        group = group.copy()
        group["tool1"] = group["tool1"].str.strip().str.lower()
        group["tool2"] = group["tool2"].str.strip().str.lower()

        def get_pair_label(row):
            t1, t2 = sorted([row["tool1"], row["tool2"]])
            return f"{t1}-{t2}"
        
        group["tool_pair"] = group.apply(get_pair_label, axis=1)

        entry_stats = {"Entry": entry}

        for t1, t2 in combinations_with_replacement(tools, 2):
            label = f"{min(t1, t2)}-{max(t1, t2)}"
            subset = group[group["tool_pair"] == label]
            rmsds = subset["proteinRMSD"].dropna().tolist()
            entry_stats[f"{label}_mean_proteinRMSD"] = np.mean(rmsds) if rmsds else np.nan
            entry_stats[f"{label}_std_proteinRMSD"] = np.std(rmsds) if rmsds else np.nan

        all_stats.append(entry_stats)

    return pd.DataFrame(all_stats)



def visualize_rmsd_by_entry(rmsd_df, output_dir="proteinRMSD_heatmaps"):
    '''
    Visualizes RMSD values as heatmaps for each entry in the resulting dataframe.
    '''   
    os.makedirs(output_dir, exist_ok=True)

    for entry, group in rmsd_df.groupby('Entry'):
        # Get all docked structures for the entry
        docked_proteins = list(set(group['docked_structure1']) | set(group['docked_structure2']))
        docked_proteins = sorted(docked_proteins, key=lambda x: (0 if "chai" in x.lower() else 1, x))
    
        rmsd_matrix = pd.DataFrame(np.nan, index=docked_proteins, columns=docked_proteins)

        for _, row in group.iterrows():
            l1, l2, rmsd = row['docked_structure1'], row['docked_structure2'], row['proteinRMSD']
            rmsd_matrix.loc[l1, l2] = rmsd
            rmsd_matrix.loc[l2, l1] = rmsd

        plt.figure(figsize=(6, 5))
        sns.heatmap(rmsd_matrix, annot=False, cmap="viridis", square=True, cbar=True)
        plt.title(f"Heatmap of protein RMSD: {entry}", fontsize=14)
        plt.xlabel("Docked Structures")
        plt.ylabel("Docked Structures")
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        plt.tight_layout()

        filename = f"{entry.replace('/', '_')}_heatmap.png"
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()


class ProteinRMSD(Step):
    def __init__(self, entry_col = 'Entry', input_dir: str = '', output_dir: str = '', visualize_heatmaps = False,  num_threads=1): 
        self.entry_col = entry_col
        self.input_dir = Path(input_dir)   
        self.output_dir = Path(output_dir)
        self.visualize_heatmaps = visualize_heatmaps
        self.num_threads = num_threads or 1

    def __execute(self, df) -> list:

        rmsd_values = []

        # Iterate through all subdirectories in the input directory
        for sub_dir in self.input_dir.iterdir():
            print(f"Processing entry: {sub_dir.name}")

            # Process all PDB files in subdirectories
            for pdb_file_path in sub_dir.glob("*.pdb"):
                if not pdb_file_path.exists():
                    print(f"File does not exist: {pdb_file_path}")

                rmsd = compute_proteinRMSD(pdb_file_path)  # Compute protein RMSD for the PDB file

                # Store the RMSD value in a dictionary to append later
                pdb_file_name = pdb_file_path.name
                structure_names = pdb_file_name.replace(".pdb", "").split("__")
                
                docked_structure1_name = structure_names[0] if len(structure_names) > 0 else None
                docked_structure2_name = structure_names[1] if len(structure_names) > 1 else None

                entry_name = sub_dir.name 

                tool1_name = get_tool_from_structure_name(docked_structure1_name)
                tool2_name  = get_tool_from_structure_name(docked_structure2_name)

                rmsd_values.append({
                    'Entry': entry_name, 
                    'pdb_file': pdb_file_path.name,  # Store the name of the PDB file
                    'docked_structure1' : docked_structure1_name, 
                    'docked_structure2' : docked_structure2_name, 
                    'tool1' : tool1_name, 
                    'tool2': tool2_name,
                    'proteinRMSD': rmsd,   # Store the calculated RMSD value
                })
 
        # Pairwise protein_RMSD comparisons
        rmsd_df = pd.DataFrame(rmsd_values)
        
        # Compute per-entry tool pair statistics
        entry_pair_stats = compute_entrywise_tool_pair_stats(rmsd_df)

        # Compute overall mean/std RMSD per entry
        entry_overall_stats = (
            rmsd_df.groupby("Entry")["proteinRMSD"]
            .agg(entry_overall_mean_proteinRMSD="mean", entry_overall_std_proteinRMSD="std")
            .reset_index()
        )

        # Merge both stats into rmsd_df
        rmsd_df = rmsd_df.merge(entry_pair_stats, on="Entry", how="left")
        rmsd_df = rmsd_df.merge(entry_overall_stats, on="Entry", how="left")
        print(rmsd_df)

        # Optionally generate heatmaps
        if self.visualize_heatmaps:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            visualize_rmsd_by_entry(rmsd_df, output_dir=self.output_dir)

        # Merge with the original df to keep metadata
        rmsd_df = pd.merge(rmsd_df, df, on='Entry', how='left')
        
        #  Per-structure DF (one row each)
        # Collect unique docked structures per Entry from pairwise df
        per_entry_structures = (
            rmsd_df[['Entry', 'docked_structure1', 'docked_structure2']]
            .dropna(subset=['Entry'])
            .copy()
        )
        stacked = pd.concat([
            per_entry_structures[['Entry', 'docked_structure1']]
                .rename(columns={'docked_structure1': 'docked_structure'}),
            per_entry_structures[['Entry', 'docked_structure2']]
                .rename(columns={'docked_structure2': 'docked_structure'})
        ], ignore_index=True)

        # Keep one row per (Entry, docked_structure)
        stacked = stacked.dropna(subset=['docked_structure']).drop_duplicates()

        # Add parsed tool per structure
        stacked['tool'] = stacked['docked_structure'].apply(get_tool_from_structure_name)

        # Bring in per-entry stats (same columns as pairwise)
        structures_df = stacked.merge(entry_pair_stats, on='Entry', how='left') \
                               .merge(entry_overall_stats, on='Entry', how='left')

        # Bring in the original input metadata columns (everything in df except duplicates)
        # This duplicates the metadata for each structure within an Entry, as requested.
        structures_df = structures_df.merge(df, on='Entry', how='left')

        # Reorder columns a bit for readability
        first_cols = ['Entry', 'docked_structure', 'tool']
        other_cols = [c for c in structures_df.columns if c not in first_cols]
        structures_df = structures_df[first_cols + other_cols]

        # Return both outputs
        return rmsd_df, structures_df


    def execute(self, df) -> pd.DataFrame:
        self.input_dir = Path(self.input_dir)
        return self.__execute(df)
