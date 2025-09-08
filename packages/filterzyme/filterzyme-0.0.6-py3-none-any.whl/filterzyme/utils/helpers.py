import os
import sys
import pandas as pd
import numpy as np
import logging
import textwrap
from pathlib import Path
from Bio.PDB import PDBParser, PDBIO, Select
import re
from collections import Counter
from io import StringIO
from biotite.structure import AtomArrayStack
from biotite.structure.io.pdb import PDBFile
from rdkit import Chem
from rdkit.Chem.rdchem import Mol

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# Define plotting aesthetics 
def clean_plt(ax, max_label_chars=25):
    ax.tick_params(direction='out', length=2, width=1.0)
    ax.spines['bottom'].set_linewidth(1.0)
    ax.spines['top'].set_linewidth(0)
    ax.spines['left'].set_linewidth(1.0)
    ax.spines['right'].set_linewidth(0)
    ax.tick_params(labelsize=10.0)
    ax.tick_params(axis='x', which='major', pad=2.0)
    ax.tick_params(axis='y', which='major', pad=2.0)

    # --- Wrap axis labels if too long ---
    for which in ["x", "y"]:
        label = getattr(ax, f"get_{which}label")()
        if label and len(label) > max_label_chars:
            wrapped = "\n".join(textwrap.wrap(label, max_label_chars))
            getattr(ax, f"set_{which}label")(wrapped)

    return ax

# Define logging titles
def log_section(title: str):
    border = "#" * 60
    logger.info(f"\n{border}")
    logger.info(f"### {title.upper().center(52)} ###")
    logger.info(f"{border}\n")

# Define logging subtitles
def log_subsection(title: str):
    border = "#" * 60
    logger.info(f"\n{border}")
    logger.info(f"### {title.center(52)} ###")
    logger.info(f"{border}\n")

def log_boxed_note(text):
    border = "-" * (len(text) + 8)
    logger.info(f"\n{border}\n|   {text}   |\n{border}\n")

def generate_boltz_structure_path(input_path):
    """
    Generate the structure file path of Boltz structure based on boltz output directory.
    """
    base_path = Path(input_path)
    base_name = base_path.name  
    new_path = base_path / f"boltz_results_{base_name}" / "predictions" / base_name / f"{base_name}_model_0.cif"

    return new_path

def generate_chai_structure_path(input_path):
    """
    Generate the structure file path of Chai structure based on chai output directory.
    """
    base_path = Path(input_path)
    base_name = base_path.name  
    new_path = base_path / 'chai' / f"{base_name}_0.cif"

    return new_path

def clean_protein_sequence(seq: str) -> str:
    """
    Cleans a protein sequence by:
    - Removing stop codons (*)
    - Removing whitespace or newline characters
    - Ensuring only valid amino acid letters remain (A-Z except B, J, O, U, X, Z)
    """
    if pd.isna(seq):
        return None
    seq = seq.upper()
    seq = re.sub(r'[^ACDEFGHIKLMNPQRSTVWY]', '', seq)  # Keep only standard 20 amino acids
    return seq

def delete_empty_subdirs(directory):
    '''Delete empty subdirectories'''
    directory = Path(directory)
    for subdir in directory.iterdir():
        if subdir.is_dir() and not any(subdir.iterdir()):
            subdir.rmdir()
            print(f"Deleted empty directory: {subdir}")


class suppress_stdout_stderr:
    def __enter__(self):
        # Open a null file
        self.devnull = open(os.devnull, 'w')
        self.old_stdout = os.dup(1)
        self.old_stderr = os.dup(2)
        os.dup2(self.devnull.fileno(), 1)
        os.dup2(self.devnull.fileno(), 2)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.dup2(self.old_stdout, 1)
        os.dup2(self.old_stderr, 2)
        os.close(self.old_stdout)
        os.close(self.old_stderr)
        self.devnull.close()


class LigandSelect(Select):
    def __init__(self, ligand_resname):
        self.ligand_resname = ligand_resname

    def accept_residue(self, residue):
        return residue.get_resname() == self.ligand_resname


class SingleLigandSelect(Select):
    def __init__(self, chain_id, resseq, resname=None):
        self.chain_id = chain_id
        self.resseq = resseq
        self.resname = (resname or "").strip()

    def accept_atom(self, atom):
        res = atom.get_parent()
        ch_match = res.get_parent().id == self.chain_id
        id_match = res.id[1] == self.resseq
        if self.resname:
            rn_match = res.get_resname().strip() == self.resname
        else:
            rn_match = True
        return ch_match and id_match and rn_match

def extract_entry_name_from_PDB_filename(name):
    '''Extracts the entry name from a PDB filename of docked structures.
    '''
    suffix = name.rsplit('_', 1)[-1]
    parts = name.split('_')

    if suffix in {'boltz'}:
        # Return everything except the last 3 parts
        return '_'.join(parts[:-3])
    elif suffix in {'vina', 'chai'}:
        # Return everything except the last 2 parts
        return '_'.join(parts[:-2])
    else:
        return name  # fallback if unknown suffix


def extract_ligand_from_PDB(input_pdb, output_pdb, ligand_resname):
    """
    Extracts a ligand from a PDB file and writes it to a new PDB.

    Parameters:
    - input_pdb: str, path to the complex PDB file
    - output_pdb: str, path to write the ligand-only PDB file
    - ligand_resname: str, 3-letter residue name of the ligand (e.g., 'LIG')
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("docked", input_pdb)

    io = PDBIO()
    io.set_structure(structure)
    io.save(str(output_pdb), LigandSelect(ligand_resname))


def add_metrics(best_strucutures_df, df_dockmetrics):
    """
    Merges docking metrics from df_dockmetrics into best_strucutures_df based on the 'Entry' column.
    Extracts structure IDs and vina indices from the 'best_structure' column.
    """
    chai_columns = ["chai_aggregate_score", "chai_ptm", "chai_iptm",
        "chai_per_chain_ptm", "chai_per_chain_pair_iptm", 
        "chai_has_clashes", "chai_chain_chain_clashes"]
    
    boltz_columns = ["boltz2_confidence_score", "boltz2_ptm", "boltz2_iptm", 
        "boltz2_ligand_iptm", "boltz2_protein_iptm", 
        "boltz2_complex_plddt", "boltz2_complex_iplddt", 
        "boltz2_complex_pde", "boltz2_complex_ipde", 
        "boltz2_chains_ptm", "boltz2_pair_chains_iptm"]
    

    def extract_structure_id(full_name):
        parts = full_name.split("_")
        if parts[-1] in {"vina", "chai", "boltz"}:
            return "_".join(parts[:-1])
        return full_name

    def extract_index(structure):
        if structure.endswith("_vina"):
            try:
                return int(structure.split("_")[-2])
            except:
                return None
        return None

    df_dockmetrics_reduced = df_dockmetrics[["Entry"] + dict_columns + ["vina_affinities"]].drop_duplicates(subset="Entry")
    merged_df = pd.merge(best_strucutures_df, df_dockmetrics_reduced, on="Entry", how="left")

    # Extract structure ID and replace dict columns with values
    structure_ids = merged_df["docked_structure"].map(extract_structure_id)

    for col in dict_columns:
        merged_df[col] = [
            d.get(structure_id) if isinstance(d, dict) else None
            for d, structure_id in zip(merged_df[col], structure_ids)
        ]

    # Extract vina affinity
    vina_indices = merged_df["docked_structure"].map(extract_vina_index)

    merged_df["vina_affinity"] = [
        v.get(idx) if isinstance(v, dict) and idx is not None else None
        for v, idx in zip(merged_df["vina_affinities"], vina_indices)
    ]

    merged_df_final = merged_df.drop(columns=["vina_affinities"])

    return merged_df_final



def extract_docking_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process a DataFrame containing 'docked_structure', 'tool', CHAI/BOLTZ dict columns,
    and (optionally) 'vina_affinities'. For dict-backed metrics:
      - CHAI/BOLTZ columns: try key=structure_id; if not found and dict has a single entry,
        use that single value. Otherwise leave as NaN.
      - boltz2_affinity_* columns: if the cell is a one-item dict, extract its value; else
        try key=structure_id; else NaN.
      - Vina: extract per-pose from 'vina_affinities' using the pose index inferred from
        'docked_structure', into a new 'vina_affinity' column, then drop 'vina_affinities'.

    structure_id := docked_structure with the last underscore-part removed.
    """
    chai_columns = [
        "chai_aggregate_score", "chai_ptm", "chai_iptm",
        "chai_per_chain_ptm", "chai_per_chain_pair_iptm",
        "chai_has_clashes", "chai_chain_chain_clashes",
    ]
    boltz_columns = [
        "boltz2_confidence_score", "boltz2_ptm", "boltz2_iptm",
        "boltz2_ligand_iptm", "boltz2_protein_iptm",
        "boltz2_complex_plddt", "boltz2_complex_iplddt",
        "boltz2_complex_pde", "boltz2_complex_ipde",
        "boltz2_chains_ptm", "boltz2_pair_chains_iptm",
        "boltz2_affinity_pred_value", "boltz2_affinity_probability_binary",
        "boltz2_affinity_pred_value1", "boltz2_affinity_probability_binary1",
        "boltz2_affinity_pred_value2", "boltz2_affinity_probability_binary2",
    ]
    boltz_affinity_like = [
        "boltz2_affinity_pred_value", "boltz2_affinity_probability_binary",
        "boltz2_affinity_pred_value1", "boltz2_affinity_probability_binary1",
        "boltz2_affinity_pred_value2", "boltz2_affinity_probability_binary2",
    ]

    if "docked_structure" not in df.columns:
        raise KeyError("Expected column 'docked_structure' not found.")
    if "tool" not in df.columns:
        raise KeyError("Expected column 'tool' not found.")

    out = df.copy()

    # structure_id: everything before the final underscore
    out["structure_id"] = out["docked_structure"].astype(str).str.rsplit("_", n=1).str[0]

    # id just before the final part (e.g. pose index for vina)
    out["vina_id"] = out["docked_structure"].astype(str).str.split("_").str[-2]
    out["vina_id"] = pd.to_numeric(out["vina_id"], errors="coerce")

    # tool masks
    tool_lower = out["tool"].astype(str).str.lower()
    mask_chai  = tool_lower.str.contains(r"\bchai\b",  na=False)
    mask_boltz = tool_lower.str.contains(r"\bboltz\b", na=False)
    mask_vina  = tool_lower.str.contains(r"\bvina\b",  na=False)

    def pick_value_from_dict(val, key=None, prefer_key=True):
        """
        If val is a dict:
          - if prefer_key and key is provided, try key (and str(key)) lookups
          - else if the dict has a single item, return that single value
          - else return np.nan
        If val is not a dict, return val unchanged.
        """
        if not isinstance(val, dict):
            return val
        if prefer_key and key is not None:
            if key in val:
                return val[key]
            skey = str(key)
            if skey in val:
                return val[skey]
        if len(val) == 1:
            return next(iter(val.values()))
        return np.nan

    # ---------------- CHAI: only on CHAI rows; others -> NaN ------------------
    exist_chai = [c for c in chai_columns if c in out.columns]
    for col in exist_chai:
        out.loc[mask_chai, col] = out.loc[mask_chai].apply(
            lambda r: pick_value_from_dict(r[col], key=r["structure_id"], prefer_key=True),
            axis=1,
        )
        out.loc[~mask_chai, col] = np.nan

    # ---------------- BOLTZ: only on BOLTZ rows; others -> NaN ----------------
    exist_boltz = [c for c in boltz_columns if c in out.columns]
    for col in exist_boltz:
        if col in boltz_affinity_like:
            out.loc[mask_boltz, col] = out.loc[mask_boltz].apply(
                lambda r: (
                    next(iter(r[col].values()))
                    if isinstance(r[col], dict) and len(r[col]) == 1
                    else pick_value_from_dict(r[col], key=r["structure_id"], prefer_key=True)
                ),
                axis=1,
            )
        else:
            out.loc[mask_boltz, col] = out.loc[mask_boltz].apply(
                lambda r: pick_value_from_dict(r[col], key=r["structure_id"], prefer_key=True),
                axis=1,
            )
        out.loc[~mask_boltz, col] = np.nan

    # ---------------- Vina: only on Vina rows; others -> NaN ------------------
    if "vina_affinities" in out.columns:
        def _get_vina_affinity(r):
            aff = r["vina_affinities"]
            vid = r["vina_id"]
            if not isinstance(aff, dict) or pd.isna(vid):
                return np.nan
            # try both numeric and string forms; also try int(vid) if possible
            if vid in aff:
                return aff[vid]
            svid = str(vid)
            if svid in aff:
                return aff[svid]
            try:
                ivid = int(vid)
                if ivid in aff: return aff[ivid]
                if str(ivid) in aff: return aff[str(ivid)]
            except Exception:
                pass
            return np.nan

        out.loc[mask_vina, "vina_affinity"] = out.loc[mask_vina].apply(_get_vina_affinity, axis=1)
        out.loc[~mask_vina, "vina_affinity"] = np.nan
        out = out.drop(columns=["vina_affinities"])

    # Cleanup helper columns
    out = out.drop(columns=["structure_id", "vina_id"])
    return out



def get_hetatm_chain_ids(pdb_path):
    with open(pdb_path, "r") as f:
        pdb_file = PDBFile.read(f)
    structure = pdb_file.get_structure()
    structure = structure[0]

    hetatm_chains = set(structure.chain_id[structure.hetero])
    atom_chains = set(structure.chain_id[~structure.hetero])

    # Exclude chains that also have ATOM records (i.e., protein chains)
    ligand_only_chains = hetatm_chains - atom_chains

    return list(ligand_only_chains)


def extract_chain_as_rdkit_mol(pdb_path, chain_id, sanitize=False):
    '''
    Extract ligand chain as RDKit mol objects given their chain ID. 
    '''
    # Read full structure
    with open(pdb_path, "r") as f:
        pdb_file = PDBFile.read(f)
    structure = pdb_file.get_structure()
    if isinstance(structure, AtomArrayStack):
        structure = structure[0]  # first model only

    # Extract chain
    mask = structure.chain_id == chain_id

    if len(mask) != structure.array_length():
        raise ValueError(f"Mask shape {mask.shape} doesn't match atom array length {structure.array_length()}")

    chain = structure[mask]

    if chain.shape[0] == 0:
        raise ValueError(f"No atoms found for chain {chain_id} in {pdb_path}")

    # Convert to PDB string using Biotite
    temp_pdb = PDBFile()
    temp_pdb.set_structure(chain)
    pdb_str_io = StringIO()
    temp_pdb.write(pdb_str_io)
    pdb_str = pdb_str_io.getvalue()

    # Convert to RDKit mol from PDB string
    mol = Chem.MolFromPDBBlock(pdb_str, sanitize=sanitize)

    return mol


def atom_composition_fingerprint(mol):
    """
    Returns a Counter of atom symbols in the molecule (e.g., {'C': 10, 'N': 2}).
    """
    return Counter([atom.GetSymbol() for atom in mol.GetAtoms()])


def norm_l1_dist(fp_a, fp_b, keys=None):
    """
    Normalized L1 distance on element counts. Used to pick the closest element-count vector
    of all ligands to the reference ligand. 
    """
    if keys is None:
        keys = set(fp_a) | set(fp_b)
    num = 0.0
    den = 0.0
    for k in keys:
        a = fp_a.get(k, 0)
        b = fp_b.get(k, 0)
        num += abs(a - b)
        den += a + b
    return 0.0 if den == 0 else num / den


def closest_ligands_by_element_composition(ligand_mols, reference_smiles, top_k = 2):
    """
    Filters a list of RDKit Mol objects based on atom element composition
    matching a reference SMILES. It returns a mol object that matches the element composition. 
    Because sometimes some atoms especially hydrogens can get lost in conversions, I pick the ligand
    with the closest atom composition to the reference; doesn't have to match perfectly. 
    """
    ref_mol = Chem.MolFromSmiles(reference_smiles)
    if ref_mol is None:
        raise ValueError("Reference SMILES could not be parsed.")

    # calculate atom composition of the reference smile string i.e. the ligand of interest
    ref_fp = atom_composition_fingerprint(ref_mol)

    out = []
    for mol in ligand_mols:
        if mol is None:
            continue
        try:
            fp = atom_composition_fingerprint(mol)
            dist = norm_l1_dist(ref_fp, fp)
            score = 1.0 - dist
            out.append((mol, score))
        except Exception as e:
            print(f"Error processing ligand: {e}")
            continue
    # return closest matching lgiands
    out.sort(key=lambda t: t[1], reverse=True)
    return [mol for mol, _ in out[:top_k]]


def ensure_3d(m: Chem.Mol) -> Chem.Mol:
    """Make sure we have a conformer (PDB usually has one; this is a fallback)."""
    if m is None:
        return None
    if m.GetNumConformers() == 0:
        m = Chem.AddHs(m)
        AllChem.EmbedMolecule(m, randomSeed=0xf00d)
        m = Chem.RemoveHs(m)
    return m


def as_mol(x):
    # In case anything returns (mol, score) or a dict
    if isinstance(x, Mol): return x
    if isinstance(x, tuple) and x and isinstance(x[0], Mol): return x[0]
    if isinstance(x, dict) and isinstance(x.get("mol"), Mol): return x["mol"]
    return None


def valid_file_list(val):
# Ensure it's a list of existing files
    if isinstance(val, str):
        val = [val]
    if not isinstance(val, (list, tuple)):
        return False
    return all(isinstance(p, str) and Path(p).is_file() for p in val)


















