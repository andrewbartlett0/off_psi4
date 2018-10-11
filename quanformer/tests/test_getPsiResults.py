
# local testing vs. travis testing
try:
    from quanformer.getPsiResults import *
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, '/beegfs/DATA/mobley/limvt/openforcefield/pipeline/github/quanformer')
    from getPsiResults import *

# define location of input files for testing
import os
mydir = os.path.dirname(os.path.abspath(__file__))

# -----------------------

import pytest

def test_get_psi_time():
    time = get_psi_time(os.path.join(mydir,'data_tests','timer.dat'))
    assert time == 847.00

# test manually without pytest
if 0:
    test_get_psi_time()
