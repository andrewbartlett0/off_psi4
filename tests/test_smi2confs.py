
# local testing vs. travis testing
try:
    from quanformer.smi2confs import *
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, '/home/limvt/Documents/off_psi4/quanformer')
    from smi2confs import *

# define location of input files for testing
import os
mydir = os.path.dirname(os.path.abspath(__file__))

# -----------------------

import pytest
from helper import *

def test_generate_confs():
    mol = read_mol(os.path.join(mydir,'data_tests','gbi_single.sdf'))
    mol_with_confs = generate_confs(mol)
    assert mol_with_confs.NumConfs() == 36

def test_resolve_clashes():
    mol = read_mol(os.path.join(mydir,'data_tests','steric_clash.smi'))
    mol = generate_confs(mol)
    for conf in mol.GetConfs():
        resolve_clashes(conf, os.path.join(mydir,'clashes.out'))
    statinfo = os.stat(os.path.join(mydir,'clashes.out'))
    assert statinfo.st_size == 405
    os.remove(os.path.join(mydir,'clashes.out'))

def test_quick_opt():
    # TODO
    pass

def test_smi2confs():
    os.chdir(mydir)
    smi2confs(os.path.join(mydir,'data_tests','methane.smi'))
    statinfo = os.stat(os.path.join(mydir,'methane.sdf'))
    assert statinfo.st_size == 612
    os.remove(os.path.join(mydir,'methane.sdf'))
    os.remove(os.path.join(mydir,'numConfs.txt'))

def test_smi2confs_rename():
    smi2confs(os.path.join(mydir,'data_tests','gbi_single.sdf'))
    statinfo = os.stat(os.path.join(mydir,'gbi_single_quanformer.sdf'))
    assert statinfo.st_size == 87408
    os.remove(os.path.join(mydir,'gbi_single_quanformer.sdf'))
    os.remove(os.path.join(mydir,'numConfs.txt'))

# test manually without pytest
if 1:
    test_generate_confs()
    test_resolve_clashes()
    test_quick_opt()
    test_smi2confs()
    test_smi2confs_rename()

