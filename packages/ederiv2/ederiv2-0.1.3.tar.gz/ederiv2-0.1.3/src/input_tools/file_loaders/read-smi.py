import os
import pickle
import pandas as pd
from pathlib import Path

def read_smi_files(data_folder, filenames:list[str]=None):
    
    all_smiles = []

    data_path = Path(data_folder)
    
    # List available .smi files for diagnostics
    available = sorted(p.name for p in data_path.glob("*.smi"))
    print(f"Available .smi files in {data_path}:\n  " + "\n  ".join(available) if available else "  (none)")


    if filenames:
        # Build list only with existing files
        smi_files = []
        for fname in filenames:
            p=os.path.join(data_path, fname)
            p = data_path / fname
            if not p.exists():
                print(f"Warning: file not found: {p}")
            else:
                smi_files.append(p)
        if not smi_files:
            print("No specified files found. Aborting.")
            return []
        smi_files = sorted(smi_files, key=lambda p: p.name.lower())
    else:
        try:
            smi_files = sorted(data_path.glob("*.smi"))
        except Exception as e:
            print(f"Error accessing directory {data_path}: {e}")
        
    for smi_file in smi_files:
        try:
            with open(smi_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    all_smiles.append(line)
                    
        except Exception as e:
            print(f"Error: {e} while reading file {smi_file}")
            continue
    
    return all_smiles

def save_to_pickle(data, output_file):
    try:
        with open(output_file, 'wb') as f:
            pickle.dump(data, f)
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving to pickle file: {e}")

def main():

    data_folder = "/home/meisam/GitHub_codes/eDeriv2/src/input_tools/reader/data_1/"
    in_smi_files=['9.frl.smi']
    
    output_file = "gdb_fragments-like_smi09_smiles.pkl"
    
    
    all_smiles = read_smi_files(data_folder, in_smi_files)
    
    print(f"\nTotal SMILES strings collected: {len(all_smiles)}")
    
    if all_smiles:
        
        df = pd.DataFrame({'fragments': all_smiles})
        save_to_pickle(df, output_file)
    else:
        print("No SMILES strings found!")

if __name__ == "__main__":
    main()
