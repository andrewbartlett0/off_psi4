
# local testing vs. travis testing
try:
    from quanformer.procTags import *
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, '/beegfs/DATA/mobley/limvt/openforcefield/pipeline/github/quanformer')
    from procTags import *

# define location of input files for testing
import os
mydir = os.path.dirname(os.path.abspath(__file__))

# -----------------------

import pytest
from helper import *

def test_GetSDList():
    # TODO
    pass

def test_SetSDTags_hess():
    mol, ifs = read_mol(os.path.join(mydir,'data_tests','gbi_single.sdf'))
    props = {'method':'test-m', 'basis':'test-b', 'package':'test-p',
             'time':-1}
    SetSDTags(mol, props, 'hess')
    assert oechem.OEHasSDData(mol, "QM test-p Hessian Runtime (sec) test-m/test-b") == True
    assert oechem.OEGetSDData(mol, "QM test-p Hessian Runtime (sec) test-m/test-b") == '-1'

def test_SetSDTags_spe_notfinish():
    mol, ifs = read_mol(os.path.join(mydir,'data_tests','gbi_single.sdf'))
    props = {'method':'test-m', 'basis':'test-b', 'package':'test-p',
             'time':-1}
    SetSDTags(mol, props, 'spe')
    assert oechem.OEHasSDData(mol, "QM test-p Single Pt. Runtime (sec) test-m/test-b") == True
    assert oechem.OEGetSDData(mol, "QM test-p Single Pt. Runtime (sec) test-m/test-b") == '-1'
    assert oechem.OEHasSDData(mol, "Note on Single Pt. test-m/test-b") == True
    assert oechem.OEGetSDData(mol, "Note on Single Pt. test-m/test-b") == "JOB DID NOT FINISH"
    ifs.close()

def test_SetSDTags_spe_didfinish():
    mol, ifs = read_mol(os.path.join(mydir,'data_tests','gbi_single.sdf'))
    props = {'method':'test-m', 'basis':'test-b', 'package':'test-p',
             'time':-1, 'finalEnergy':-2}
    SetSDTags(mol, props, 'spe')
    assert oechem.OEHasSDData(mol, "QM test-p Single Pt. Runtime (sec) test-m/test-b") == True
    assert oechem.OEGetSDData(mol, "QM test-p Single Pt. Runtime (sec) test-m/test-b") == '-1'
    assert oechem.OEHasSDData(mol, "QM test-p Final Single Pt. Energy (Har) test-m/test-b") == True
    assert oechem.OEGetSDData(mol, "QM test-p Final Single Pt. Energy (Har) test-m/test-b") == '-2'
    ifs.close()

def test_SetSDTags_opt():
    # TODO
    pass

def test_DeleteTag():
    # TODO
    pass

# test manually without pytest
if 0:
    test_SetSDTags_hess()
    test_SetSDTags_spe_notfinish()
    test_SetSDTags_spe_didfinish()
