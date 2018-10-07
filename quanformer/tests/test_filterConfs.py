
# local testing on greenplanet
import sys
sys.path.insert(0, '/beegfs/DATA/mobley/limvt/openforcefield/pipeline/github/quanformer')

# define location of input files for testing
import os
mydir = os.path.dirname(os.path.abspath(__file__))

# -----------------------

import pytest
from filterConfs import *

def test_identify_minima():
    ifs = oechem.oemolistream()
    if not ifs.open('gbi.sdf'):
        oechem.OEThrow.Fatal("Unable to open gbi.sdf for reading")
    ifs.SetConfTest( oechem.OEAbsoluteConfTest() )
    mol = next(ifs.GetOEMols())
    assert mol.NumConfs() == 36
    # use same params defined in filterConfs.py script
    assert IdentifyMinima(mol,'MM Szybki SD Energy', 5.E-4, 0.2) is True
    assert mol.NumConfs() == 5
    ifs.close()

def test_filter_confs():
    # TODO
    pass

# test manually without pytest
if 0:
    test_identify_minima()
    test_filter_confs()

