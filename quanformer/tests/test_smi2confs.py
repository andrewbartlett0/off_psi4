
# local testing vs. travis testing
try:
    from quanformer.smi2confs import *
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, '/beegfs/DATA/mobley/limvt/openforcefield/pipeline/github/quanformer')
    from smi2confs import *

# define location of input files for testing
import os
mydir = os.path.dirname(os.path.abspath(__file__))

# -----------------------

import pytest

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
        os.remove(os.path.join(mydir,'data_tests','methane.sdf'))
    except FileNotFoundError:
        pass
    smi2confs(os.path.join(mydir,'data_tests','methane.smi'))
    statinfo = os.stat(os.path.join(mydir,'data_tests','methane.sdf'))
    assert statinfo.st_size == 612
    os.remove(os.path.join(mydir,'data_tests','methane.sdf'))
    os.remove(os.path.join(mydir,'data_tests','numConfs.txt'))

# test manually without pytest
if 0:
    test_gen_confs()
    test_resolve_clashes()
    test_quick_opt()
    test_smi2confs()

