
"""
Helper functions used in the testing scripts.

"""

import openeye.oechem as oechem

def read_mol(infile):
    ifs = oechem.oemolistream()
    if not ifs.open(infile):
        oechem.OEThrow.Fatal("Unable to open {} for reading".format(infile))
    ifs.SetConfTest( oechem.OEAbsoluteConfTest() )
    mol = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, mol)
    return mol, ifs

