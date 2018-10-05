
# Potential errors and how to get around them

Errors thrown by Quanformer
 * `KeyError` from processing results. Did you remember to specify `spe` for single point calculations?

Errors thrown by Psi4:
 * `namingErr.dat`          Bad molecule name specification for Psi4. Avoid underscores.
 * `scratchDirErr.dat`      Psi4 cannot access scratch directory. Be sure to specify this location in your bash profile or in ~/.psi4rc file.
 * Segmentation fault from .... [TODO]

