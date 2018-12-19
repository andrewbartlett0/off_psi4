# Work with conformers having specific atoms restrained
Version: Oct 23 2018  

The key is the SD tag of "Index list of atoms to freeze" in the molecule SDF file.  
The SD tag can be added to the initial Quanformer-generated SDF file before running QM calculations.  
(Not shown here but can be easily done/provided.)  
This can be applied to conduct a QM torsion scan or similar.  

An example script is provided to call the `confs_to_psi.py` script with the given SDF file.  
This approach is equivalent to running: `python executor.py -f example.sdf --setup -t opt -m 'mp2' -b 'def2-SV(P)'`


## Instructions

To replicate this example:

1. Replace the path in the `sys.path.insert` line with your path to this repository's code.

2. `python example.py`

## VTL notes

Greenplanet source: `/data11/home/jmaat/off_nitrogens/sdf_min/sdf_min_mol2/pyrnit_2_constituent_0_improper.sdf`  
* Removed all conformers except first four
* Renamed file name and molecule title for simplicity


