
# local testing vs. travis testing
try:
    from quanformer.confs2psi import *
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, '/beegfs/DATA/mobley/limvt/openforcefield/pipeline/github/quanformer')
    from confs2psi import *

# define location of input files for testing
import os
mydir = os.path.dirname(os.path.abspath(__file__))

# -----------------------

import pytest

def input_file_reader():
    return

def read_mol(infile):
    ifs = oechem.oemolistream()
    if not ifs.open(infile):
        oechem.OEThrow.Fatal("Unable to open {} for reading".format(infile))
    ifs.SetConfTest( oechem.OEAbsoluteConfTest() )
    mol = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, mol)
    return mol, ifs

def close_mol(ifs):
    ifs.close()

def test_make_frozen():
    mol, ifs = read_mol(os.path.join(mydir,'freeze.sdf'))
    test_string = make_psi_input(mol,mol.GetTitle(),'mp2','aug-cc-pVTZ')
    assert "4 xyz" in test_string
    assert "1 xyz" in test_string
    assert "3 xyz" in test_string
    assert "12 xyz" in test_string
    close_mol(ifs)

def test_make_dfmp2_dunning():
    mol, ifs = read_mol(os.path.join(mydir,'methane_c2p.sdf'))
    test_string = make_psi_input(mol,mol.GetTitle(),'mp2','aug-cc-pVTZ')
    assert "df_basis_mp2" not in test_string
    close_mol(ifs)

def test_make_dfmp2_qzvpd():
    mol, ifs = read_mol(os.path.join(mydir,'methane_c2p.sdf'))
    test_string = make_psi_input(mol,mol.GetTitle(),'mp2','def2-qzvpd')
    assert "df_basis_mp2" not in test_string
    close_mol(ifs)
    return

def test_make_dfmp2_svpp():
    mol, ifs = read_mol(os.path.join(mydir,'methane_c2p.sdf'))
    test_string = make_psi_input(mol,mol.GetTitle(),'mp2','def2-sv(p)')
    assert "def2-sv_p_-ri" in test_string
    close_mol(ifs)
    return

def test_confs2psi():
    return

# test manually without pytest
if 0:
    test_make_frozen()
    test_make_dfmp2_dunning()
