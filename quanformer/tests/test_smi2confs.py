
# local testing on greenplanet
import sys
sys.path.insert(0, '/beegfs/DATA/mobley/limvt/openforcefield/pipeline/github/quanformer')

# define location of input files for testing
import os
mydir = os.path.dirname(os.path.abspath(__file__))

# -----------------------

import pytest
from smi2confs import *

def test_generate_confs():
    # TODO
    pass

def test_resolve_clashes():
    # TODO
    pass

def test_quick_opt():
    # TODO
    pass

def test_smi2confs():
    try:
        os.remove(os.path.join(mydir,'methane.sdf'))
    except FileNotFoundError:
        pass
    smi2confs(os.path.join(mydir,'methane.smi'))
    statinfo = os.stat('methane.sdf')
    assert statinfo.st_size == 612
    os.remove(os.path.join(mydir,'methane.sdf'))

# test manually without pytest
if 0:
    test_gen_confs()
    test_resolve_clashes()
    test_quick_opt()
    test_smi2confs()

