
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
from helper import *

def test_initiate_dict():
    d = initiate_dict()
    assert d['package'] == 'Psi4'
    assert d['missing'] == False

def test_get_conf_data():
    # TODO
    pass

def test_set_conf_data():
    # TODO
    pass

def test_check_title():
    mol, ifs = read_mol(os.path.join(mydir,'data_tests','methane_title-1.0.sdf'))
    mol = check_title(mol, os.path.join(mydir,'data_tests','methane_title-1.0.sdf'))
    assert mol.GetTitle() == 'methane_title10'
    ifs.close()

def test_get_psi_time():
    time = get_psi_time(os.path.join(mydir,'data_tests','timer.dat'))
    assert time == 847.00

def test_process_psi_out_spe():
    spe_dict = process_psi_out(os.path.join(mydir,'data_tests','output_spe.dat'), {}, 'spe')
    # {'basis': 'def2-tzvp', 'method': 'b3lyp-d3mbj', 'finalEnergy': -466.37497616456733}
    # actual energy: -466.3749761645673289
    assert spe_dict['basis'] == 'def2-tzvp'
    assert spe_dict['method'] == 'b3lyp-d3mbj'
    assert spe_dict['finalEnergy'] == pytest.approx(-466.37497616456733, 0.000000000001)

def test_process_psi_out_hess():
    hess_dict = process_psi_out(os.path.join(mydir,'data_tests','output_hess.dat'), {}, 'hess')
    assert hess_dict['basis'] == 'def2-sv(p)'
    assert hess_dict['method'] == 'mp2'
    hess = hess_dict['hessian']
    assert hess.shape == (36,36)
    assert hess[1,1] == 0.77147127082666

def test_process_psi_out_opt():
    opt_dict = process_psi_out(os.path.join(mydir,'data_tests','output_opt.dat'), {}, 'opt')
    # initial energy: -582.148922080397
    # final energy: -582.1568394053036
    assert opt_dict['basis'] == 'def2-SV(P)'
    assert opt_dict['method'] == 'mp2'
    assert opt_dict['numSteps'] == '8'
    assert opt_dict['initEnergy'] == pytest.approx(-582.148922080397, 0.000000000001)
    assert opt_dict['finalEnergy'] == pytest.approx(-582.1568394053036, 0.000000000001)
    assert opt_dict['coords'][0] == -0.0238533448
    assert len(opt_dict['coords']) == 69

def test_process_psi_out_two():
    # TODO what happens if passed in psi4 output with opt-->hess, or opt-->spe
    pass

#def test_getPsiResults():
#    infile = os.path.join(mydir,'data_tests','gbi-200.sdf')
#    outfile = os.path.join(mydir,'data_tests','gbi-210.sdf')
#    m, b = getPsiResults(infile, outfile, calctype='opt', psiout="output.dat", timeout="timer.dat")
#    print(m,b)
#    #os.remove(os.path.join(mydir,'data_tests','gbi-210.sdf'))

def test_getPsiOne():
    infile = os.path.join(mydir,'data_tests','gbi_single.sdf')
    outfile = os.path.join(mydir,'data_tests','gbi_single-210.sdf')
    psiout = os.path.join(mydir,'data_tests','GBI','1','output.dat')
    timeout = os.path.join(mydir,'data_tests','GBI','1','timer.dat')
    mol = getPsiOne(infile, outfile, 'opt', psiout, timeout)
    assert oechem.OEHasSDData(mol, "QM Psi4 Opt. Runtime (sec) mp2/def2-SV(P)") == True
    assert float(oechem.OEGetSDData(mol, "QM Psi4 Opt. Runtime (sec) mp2/def2-SV(P)")) == 847.0
    assert oechem.OEHasSDData(mol, "QM Psi4 Final Opt. Energy (Har) mp2/def2-SV(P)") == True
    assert float(oechem.OEGetSDData(mol, "QM Psi4 Final Opt. Energy (Har) mp2/def2-SV(P)")) ==  pytest.approx(-582.156839405,0.00000001)
    assert oechem.OEHasSDData(mol, "QM Psi4 Initial Opt. Energy (Har) mp2/def2-SV(P)") == True
    assert float(oechem.OEGetSDData(mol, "QM Psi4 Initial Opt. Energy (Har) mp2/def2-SV(P)")) ==  pytest.approx(-582.14892208,0.00000001)
    assert oechem.OEHasSDData(mol, "QM Psi4 Opt. Steps mp2/def2-SV(P)") == True
    assert int(oechem.OEGetSDData(mol, "QM Psi4 Opt. Steps mp2/def2-SV(P)")) == 8
    os.remove(os.path.join(mydir,'data_tests','gbi_single-210.sdf'))

# test manually without pytest
if 0:
    test_getPsiOne()
    #test_getPsiResults()
