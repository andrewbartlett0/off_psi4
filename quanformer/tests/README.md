
# Data sources for testing
Last updated: Oct 11 2018

| filename          | test script        | source                                                                                       |
|-------------------|--------------------|----------------------------------------------------------------------------------------------|
| `freeze.sdf`      | `confs2psi.py`     | `/data11/home/jmaat/off_nitrogens/sdf_min/sdf_min_mol2/pyrnit_2_constituent_11_improper.sdf` |
| `GBI`             | `getPsiResults.py` | `/beegfs/DATA/mobley/limvt/openforcefield/pipeline/03_examples/set1/GBI`                     |
| `gbi-200.sdf`     | `getPsiResults.py` | `/beegfs/DATA/mobley/limvt/openforcefield/pipeline/03_examples/set1/examples2-200.sdf`       |
| `gbi.sdf`         | `filterConfs.py`   | `/beegfs/DATA/mobley/limvt/openforcefield/pipeline/03_examples/set1/examples2.sdf`           |
| `gbi_single.sdf`  | `getPsiResults.py` | `gbi-200.sdf` with only first conformer                                                      |
| `methane.smi`     | `smi2confs.py`     | self-generated                                                                               |
| `methane_c2p.sdf` | `confs2psi.py`     | `test_smi2confs()`                                                                           |
| `output_hess.dat` | `getPsiResults.py` | `/beegfs/DATA/mobley/limvt/openforcefield/hessian/sandbox_benzene/benzene/output.dat`        |
| `output_opt.dat`  | `getPsiResults.py` | `/beegfs/DATA/mobley/limvt/openforcefield/pipeline/03_examples/set1/GBI/1/output.dat`        |
| `output_spe.dat`  | `getPsiResults.py` | `/beegfs/DATA/mobley/limvt/openforcefield/pipeline/set1_01_main/SPE1/AlkEthOH_c1178/1/output.dat` |
| `timer.dat`       | `getPsiResults.py` | `/beegfs/DATA/mobley/limvt/openforcefield/pipeline/03_examples/set1/GBI/1/timer.dat`         |

