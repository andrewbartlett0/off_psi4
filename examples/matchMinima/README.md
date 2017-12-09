
# Example of how to use `matchMinima.py` script
Last updated: 12-08-2017

1. Generate input file with specified methods, filenames for analysis, and whether or not to use single point energy calculations (True=SPE, False=OPT).
2. Match the molecules between different files.
   Consider requesting an interactive job on the cluster, as this can be pretty intensive.
   This example has 1 molecule with ~20 conformers in 3 files. That means it'll take a 20x20x20 molecule RMSD comparison.
   I listed my start and end time in the `time.out` file for the refA calculation.
   Note: output file has a bunch of numbers for used in debugging/refining for script creation.
   They'll be cleaned up in a future version of this script. (TODO)
   * `python ../../../matchMinima.py -i match.in --eplot --tplot --verbose > match.out`
3. Can finagle plotting options, such as to only plot data from first and third files.  
   Here, we'll read in the pickle file to not spend much time re-matching. 
   To select specific options to plot, edit matchMinima script:
   * Select ones for time plot: edit `to_exclude` variable to exclude specific files. Ex: `to_exclude={1}`
   * Select ones for ene  plot: edit call to `plotMolMinima` function and specify the parameter for `selected`. Ex: `plotMolMinima(name, minE, thryList, selected=[0,2])`
   * TODO: make this consistent ^
4. Rename other files to not be overwritten. [TODO: CIRCUMVENT THIS?]
5. Now re-generate the data (I would turn the verbose flag off to not rewrite dat files).
   Can specify either `eplot` or `tplot`, or both.
   * `python ../../matchMinima.py -i match.in --readpickle --eplot --tplot`

To continue onto the next section, redo the above, but switching the order of the input file. The first line in the input file is the reference, i.e., all other conformers are compared to this file. Have each reference comparison a new directory.

## How to use `matchPlot.py` script
1. If you have multiple molecules, create directories for each, such as `mol0`, `mol1`, `mol2`, etc. (only single mol in this example)
2. Generate input file similar to the `matchMinima` input file except that it uses the `dat` files that were output from the `matchMinima.py` script.
   Doesn't require SPE/OPT specification.
3. Execute this command for each mol, specifying the molecule name in command line arguments for plot labels.
   `python ../../../matchPlot.py -i heat.in --theatplot test_mol --eheatplot test_mol --etscatter test_mol`

