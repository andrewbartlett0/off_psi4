
# Potential errors and how to get around them

Errors thrown by Quanformer/Python:
 * `Input file already exists. Skipping.` Make sure each molecule has a unique name which is used to name directories.
 * `Output .sdf file already exists. Exiting initialize_confs.` Make sure the SMILES file is in the same location as output location.
   Can also use symbolic link (`ln -s source sink`).
 * `KeyError` from processing results. Did you remember to specify `spe` for single point calculations?
 * `ValueError` from `stitchSpe.py`. Did you specify the right keywords to extract the right SD tag? 

Errors thrown by Psi4:
 * `namingErr.dat`          Bad molecule name specification for Psi4. Avoid underscores.
 * `scratchDirErr.dat`      Psi4 cannot access scratch directory. Be sure to specify this location in your bash profile or in ~/.psi4rc file.
 * Segmentation fault from .... [TODO]

