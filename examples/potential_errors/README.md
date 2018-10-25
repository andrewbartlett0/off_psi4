
# Potential errors and how to get around them

Errors thrown by Quanformer/Python:
 * `Output .sdf file already exists. Exiting smi2confs.` Make sure the SMILES file is in the same location as the desired output location. Use a symbolic link if you need.
 * `KeyError` from processing results. Did you remember to specify `spe` for single point calculations?
 * `ValueError` from `stitchSpe.py`. Did you specify the right keywords to extract the right SD tag? 

Errors thrown by Psi4:
 * `namingErr.dat`          Bad molecule name specification for Psi4. Avoid underscores.
 * `scratchDirErr.dat`      Psi4 cannot access scratch directory. Be sure to specify this location in your bash profile or in ~/.psi4rc file.
 * Segmentation fault from .... [TODO]

