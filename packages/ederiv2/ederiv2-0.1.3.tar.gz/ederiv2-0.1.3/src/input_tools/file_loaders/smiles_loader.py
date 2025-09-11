import os
import pandas as pd
from typing import Dict, Optional


class SmilesLoader:
    def __init__(self, base_path: str):
        # Treat as a folder path (ensure trailing separator)
        self._base_path = os.path.join(os.path.abspath(base_path), '')

    def from_pickle_df_files(self, filenames:Dict, target_column:Optional[str]=None) -> list[str]:
        dfs = [pd.read_pickle(os.path.join(self._base_path, filenames[key])) for key in filenames] 
        # Only concatenate if there are multiple DataFrames
        if not dfs:
            raise ValueError("No DataFrames loaded from dataset_filenames.")
        elif len(dfs) == 1:
            df_final = dfs[0].reset_index(drop=True)
        else:
            df_final = pd.concat(dfs, ignore_index=True)
            
        # Check if target_column exists and print some samples for debugging
        if target_column not in df_final.columns:
            raise KeyError(f"{target_column} column not found in the loaded DataFrames.")

        smiles = [x for x in df_final['fragments'] if isinstance(x, str) and len(x) > 1]
        
        return smiles