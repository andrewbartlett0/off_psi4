
# Example of how to use `diffSpeOpt.py` script
Last updated: 12-18-2017

The purpose of this script is to compare energies before optimization
 (essentially the single point energy calculation)
 and after QM geometry optimization.

WARNING: If comparing many files, they should all be analogous!
 E.g., same number of conformers without filtering, so that
 reference conformer subtracted among all will be the same reference conf.

## Procedure
1. Organize all SDF files. Can use symbolic links if desired.
2. Create input file for Python script (`diff.in` in this example).
3. Run the script:
`python diffSpeOpt.py -i diff.in > py.out`
4. With interactive python mode (command line), can move plot around.
Saved image has only a static view.
