from rdkit import Chem
from rdkit.Chem import rdmolops
import pandas as pd

from ederiv.chem_handlers.mol_handler import MolHandler

class MolTranslator:
    def __init__(self):
        self.atom_map = {}
        self.mol = Chem.RWMol()
        self.atom_count = 0

    def reset(self):
        self.atom_map = {}
        self.mol = Chem.RWMol()
        self.atom_count = 0

    def parse_token(self, token):
        """
        Parse different types of bond instructions:
        - 'add_aromatic_bond_C2_C3' -> ('add', 'aromatic', 'C2', 'C3')
        - 'downgrade_single_bond_C1_C2' -> ('downgrade', 'single', 'C1', 'C2')  # single->none
        - 'downgrade_double_bond_C1_C2' -> ('downgrade', 'double', 'C1', 'C2')  # double->single
        - 'downgrade_triple_bond_C1_C2' -> ('downgrade', 'triple', 'C1', 'C2')  # triple->double
        - 'upgrade_single_bond_C1_C2' -> ('upgrade', 'single', 'C1', 'C2')  # single->double
        - 'upgrade_double_bond_C3_C4' -> ('upgrade', 'double', 'C3', 'C4')  # double->triple
        """
        if token.startswith("add_"):
            parts = token.split("_")
            bond_type = parts[1]  
            atom1 = parts[3]
            atom2 = parts[4]
            return 'add', bond_type, atom1, atom2
        elif token.startswith("downgrade_"):
            parts = token.split("_")
            bond_type = parts[1]  # should be 'single', 'double', or 'triple'
            atom1 = parts[3]
            atom2 = parts[4]
            return 'downgrade', bond_type, atom1, atom2
        elif token.startswith("upgrade_"):
            parts = token.split("_")
            bond_type = parts[1]  # should be 'single' or 'double'
            atom1 = parts[3]
            atom2 = parts[4]
            return 'upgrade', bond_type, atom1, atom2
        else:
            return None

    def _add_atom(self, atom_label):
        
        if atom_label not in self.atom_map:
            atom_symbol = ''.join([c for c in atom_label if c.isalpha()])

            atom = Chem.Atom(atom_symbol)
            idx = self.mol.AddAtom(atom)
            self.atom_map[atom_label] = idx
            self.atom_count += 1
        
    def _update_radicals(self):
        mol = self.mol

        expected_valence = {
            'C': 4,
            'N': 3,
            'O': 2,
            'H': 1,
        }

        for atom in mol.GetAtoms():
            symbol = atom.GetSymbol()
            if symbol == "H":
                continue

            idx = atom.GetIdx()
            total_bonds = sum([b.GetBondTypeAsDouble() for b in atom.GetBonds()])
            expl_H = sum(1 for n in atom.GetNeighbors() if n.GetSymbol() == "H")

            try:
                atom.CalcImplicitValence()
                impl_H = atom.GetNumImplicitHs()
            except:
                impl_H = 0

            valence = expected_valence.get(symbol, 0)
            radical_electrons = valence - total_bonds - impl_H
            # print(f"Total bonds for atom idx: {idx}, symbol: {symbol}, expl_H: {expl_H}, impl_H: {impl_H}, bonds: {total_bonds}, valence: {valence}, re: {radical_electrons}")

            # print(f"print {symbol} radical electorm, {radical_electrons}")
            if radical_electrons > 0 and expl_H > 0:
                atom.SetNumRadicalElectrons(int(radical_electrons))



    def _add_bond(self, bond_type, atom1_label, atom2_label):
        # if "H" in atom1_label or "H" in atom2_label:
        #     return

        self._add_atom(atom1_label)
        self._add_atom(atom2_label)
        idx1 = self.atom_map[atom1_label]
        idx2 = self.atom_map[atom2_label]

        bond_dict = {
            "single": Chem.BondType.SINGLE,
            "double": Chem.BondType.DOUBLE,
            "triple": Chem.BondType.TRIPLE,
            "aromatic": Chem.BondType.AROMATIC
        }

        bond_enum = bond_dict.get(bond_type.lower())
        if bond_enum is None:
            raise ValueError(f"Unsupported bond type: {bond_type}")

        if self.mol.GetBondBetweenAtoms(idx1, idx2) is None:
            self.mol.AddBond(idx1, idx2, bond_enum)
        
        # Sanitize and then update radicals
        mol = self.mol.GetMol()
        try:
            # Chem.SanitizeMol(mol, sanitizeOps=Chem.SanitizeFlags.SANITIZE_PROPERTIES)
            # print("molecule getting sanitized")
            Chem.SanitizeMol(mol)
        except Exception:
            pass
            
        self._update_radicals()

    def _downgrade_bond(self, bond_type, atom1_label, atom2_label):
        """
        Downgrade existing bond to next lower order:
        - downgrade_single_bond: single -> none (remove bond)
        - downgrade_double_bond: double -> single
        - downgrade_triple_bond: triple -> double
        """
        if atom1_label not in self.atom_map or atom2_label not in self.atom_map:
            return  # Atoms don't exist, nothing to downgrade
        
        idx1 = self.atom_map[atom1_label]
        idx2 = self.atom_map[atom2_label]
        
        # Get the bond between the atoms
        bond = self.mol.GetBondBetweenAtoms(idx1, idx2)
        if bond is None:
            raise ValueError(f"No bond exists between {atom1_label} and {atom2_label}")
        
        current_bond_type = bond.GetBondType()
        
        # Check if the existing bond matches what we want to downgrade
        if bond_type == "single" and current_bond_type != Chem.BondType.SINGLE:
            raise ValueError(f"Expected single bond between {atom1_label} and {atom2_label}, but found {current_bond_type}")
        elif bond_type == "double" and current_bond_type != Chem.BondType.DOUBLE:
            raise ValueError(f"Expected double bond between {atom1_label} and {atom2_label}, but found {current_bond_type}")
        elif bond_type == "triple" and current_bond_type != Chem.BondType.TRIPLE:
            raise ValueError(f"Expected triple bond between {atom1_label} and {atom2_label}, but found {current_bond_type}")
        
        # Remove the existing bond
        self.mol.RemoveBond(idx1, idx2)
        
        # Add the downgraded bond (if not single)
        if bond_type == "double":
            # Double -> Single
            self.mol.AddBond(idx1, idx2, Chem.BondType.SINGLE)
        elif bond_type == "triple":
            # Triple -> Double
            self.mol.AddBond(idx1, idx2, Chem.BondType.DOUBLE)
        # Single -> No bond (already removed)
        
        # Sanitize and update radicals
        mol = self.mol.GetMol()
        try:
            Chem.SanitizeMol(mol)
        except Exception:
            pass
        self._update_radicals()

    def _upgrade_bond(self, bond_type, atom1_label, atom2_label):
        """
        Upgrade existing bond to next higher order:
        - upgrade_single_bond: single -> double
        - upgrade_double_bond: double -> triple
        """
        if atom1_label not in self.atom_map or atom2_label not in self.atom_map:
            return  # Atoms don't exist, nothing to upgrade
        
        idx1 = self.atom_map[atom1_label]
        idx2 = self.atom_map[atom2_label]
        
        # Get the existing bond
        bond = self.mol.GetBondBetweenAtoms(idx1, idx2)
        if bond is None:
            raise ValueError(f"No bond exists between {atom1_label} and {atom2_label}")
        
        current_bond_type = bond.GetBondType()
        
        # Check if the existing bond matches what we want to upgrade
        if bond_type == "single" and current_bond_type != Chem.BondType.SINGLE:
            raise ValueError(f"Expected single bond between {atom1_label} and {atom2_label}, but found {current_bond_type}")
        elif bond_type == "double" and current_bond_type != Chem.BondType.DOUBLE:
            raise ValueError(f"Expected double bond between {atom1_label} and {atom2_label}, but found {current_bond_type}")
        
        # Remove the existing bond
        self.mol.RemoveBond(idx1, idx2)
        
        # Add the upgraded bond
        if bond_type == "single":
            # Single -> Double
            self.mol.AddBond(idx1, idx2, Chem.BondType.DOUBLE)
        elif bond_type == "double":
            # Double -> Triple
            self.mol.AddBond(idx1, idx2, Chem.BondType.TRIPLE)
        else:
            raise ValueError(f"Unsupported upgrade bond type: {bond_type}")
        
        # Sanitize and update radicals
        mol = self.mol.GetMol()
        try:
            Chem.SanitizeMol(mol)
        except Exception:
            pass
        self._update_radicals()

    @staticmethod
    def _assign_explicit_hydrogens(mol):
        """
        Iterate over atoms in a molecule and set the number of explicit hydrogens
        based on how many H atoms are directly bonded to each atom.
        This assumes H atoms are already added as separate atoms.
        """
        rw_mol = Chem.RWMol(mol)  # Make it editable

        for atom in rw_mol.GetAtoms():
            if atom.GetAtomicNum() == 1:
                continue  # skip hydrogen atoms

            # Count the number of hydrogen neighbors
            h_count = 0
            for neighbor in atom.GetNeighbors():
                if neighbor.GetAtomicNum() == 1:
                    h_count += 1

            # Set the number of explicit Hs
            atom.SetNumExplicitHs(h_count)
            # if h_count>0:
            #     atom.SetNumRadicalElectrons(1)

            # Optional: Prevent RDKit from adding implicit Hs
            # atom.SetNoImplicit(True)

        return rw_mol.GetMol()

    @staticmethod
    def _remove_isolated_atoms(mol):
        """
        Remove isolated atoms (atoms with no bonds) from the molecule.
        
        Args:
            mol: RDKit molecule object
            
        Returns:
            RDKit molecule object with isolated atoms removed
        """
        rw_mol = Chem.RWMol(mol)
        
        # Find atoms with no bonds
        atoms_to_remove = []
        for atom in rw_mol.GetAtoms():
            if len(atom.GetBonds()) == 0:
                atoms_to_remove.append(atom.GetIdx())
        
        # Remove isolated atoms (in reverse order to maintain indices)
        for atom_idx in sorted(atoms_to_remove, reverse=True):
            rw_mol.RemoveAtom(atom_idx)
        
        return rw_mol.GetMol()


    def build_molecule(self, instruction_list):
        self.reset()
        for token in instruction_list:
            if token in ["<START>", "<END>"]:
                continue
            parsed = self.parse_token(token)
            if parsed:
                action, bond_type, atom1, atom2 = parsed
                if action == 'add':
                    self._add_bond(bond_type, atom1, atom2)
                elif action == 'downgrade':
                    self._downgrade_bond(bond_type, atom1, atom2)
                elif action == 'upgrade':
                    self._upgrade_bond(bond_type, atom1, atom2)

        
        mol = self.mol.GetMol()
        Chem.SanitizeMol(mol)
        # self._print_atom_hydrogen_info(mol)
        valences=MolHandler().calculate_valences(mol)
        # print(valences)
        # mol = Chem.RemoveHs(mol, implicitOnly=False)
        # mol = Chem.AddHs(mol)
        Chem.SanitizeMol(mol)
        return mol
    
    @staticmethod
    def _print_atom_hydrogen_info(mol):
        """
        Print hydrogen-related properties for all atoms in the molecule.
        """
        print(f"{'Idx':>3} {'Symbol':>6} {'Expl_H':>7} {'Impl_H':>7} {'Total_H':>8} {'Radicals':>9}")
        print("-" * 45)

        for atom in mol.GetAtoms():
            idx = atom.GetIdx()
            symbol = atom.GetSymbol()
            expl_h = atom.GetNumExplicitHs()
            impl_h = atom.GetNumImplicitHs()
            total_h = atom.GetTotalNumHs()
            radicals = atom.GetNumRadicalElectrons()

            print(f"{idx:>3} {symbol:>6} {expl_h:>7} {impl_h:>7} {total_h:>8} {radicals:>9}")


    def to_smiles(self, instruction_list, remove_isolated=True):
        """
        Convert instruction list to SMILES string.
        
        Args:
            instruction_list: List of bond instructions
            remove_isolated: If True, remove isolated atoms from the final molecule
        
        Returns:
            SMILES string representation of the molecule
        """
        try:
            mol = self.build_molecule(instruction_list)
            
            if remove_isolated:
                # Remove isolated atoms (atoms with no bonds)
                mol = self._remove_isolated_atoms(mol)
            
            return Chem.MolToSmiles(mol)
        except Exception as e:
            print(f'Exception occured during molecule reconstruction from the instructions:{e}')


def apply_translator_to_df(df, instruction_col="actions"):
    translator = MolTranslator()
    df["recons_smiles"] = df[instruction_col].apply(translator.to_smiles)
    return df
    

if __name__ == "__main__":
    # print("=" * 60)
    # print("COMPREHENSIVE MOL_TRANSLATOR TEST SUITE")
    # print("=" * 60)
    
    instructions = ['<START>', 'add_single_bond_C1_C2', 
                    'add_single_bond_C1_C3', 'add_double_bond_C3_O1', 
                    'add_single_bond_C1_H1', '<END>']

    translator = MolTranslator()
    smiles = translator.to_smiles(instructions)
    print("Original SMILES:", smiles)

    # Test new functionality
    test_instructions = ['<START>', 'add_single_bond_C1_C2', 
                        'add_single_bond_C1_C3', 'add_single_bond_C3_C4',
                        'upgrade_single_bond_C3_C4',  # Upgrade C3-C4 to double bond
                        'downgrade_single_bond_C1_C2',  # Remove C1-C2 bond
                        '<END>']

    translator2 = MolTranslator()
    smiles2 = translator2.to_smiles(test_instructions, remove_isolated=True)
    print("New Translator2 functionality SMILES:", smiles2)

    # Test new functionality
    test_instructions = ['<START>', 'add_single_bond_C1_C2', 
                        'add_single_bond_C1_C3', 'add_single_bond_C3_C4',
                        'upgrade_single_bond_C3_C4',  # Upgrade C3-C4 to double bond
                        'downgrade_double_bond_C3_C4',
                        '<END>']

    translator3 = MolTranslator()
    smiles3 = translator3.to_smiles(test_instructions, remove_isolated=False)
    print("New Translator3 functionality SMILES:", smiles3)

    