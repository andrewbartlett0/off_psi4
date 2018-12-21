#!/usr/bin/env python

"""
Purpose:    Take just the first instance of a duplicated molecule in multi-mol file.
By:         Victoria T. Lim
Version:    Dec 20 2018
Example:    python save_uniq_mols.py -i MiniDrugBank_filter04_extras.sdf -o MiniDrugBank_filter04.sdf
Note:       All of the first mol's conformers are also saved. Comment the SetConfTest line if you want just first confs.

"""

import openeye.oechem as oechem

def save_uniq_mols(infile, outfile):

    ### Read in molecules
    ifs = oechem.oemolistream()
    ifs.SetConfTest( oechem.OEAbsoluteConfTest() )
    if not ifs.open(infile):
        oechem.OEThrow.Warning("Unable to open %s for reading" % infile)
        return

    ### Open output file
    ofs = oechem.oemolostream()
    if not ofs.open(outfile):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % outfile)

    ### Go through all molecules
    already_saved = []
    for mol in ifs.GetOEMols():
        if mol.GetTitle() not in already_saved:
            oechem.OEWriteConstMolecule(ofs, mol)
            already_saved.append(mol.GetTitle())
    ifs.close()
    ofs.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--infile", required=True,
        help="Name of input molecules file.")
    parser.add_argument("-o", "--outfile", required=True,
        help="Name of output molecules file.")

    args = parser.parse_args()
    save_uniq_mols(args.infile, args.outfile)

