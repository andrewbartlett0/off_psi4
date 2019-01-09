
# Example of how to match conformers among different QM methods
Last updated: Nov 30 2018  

## Instructions for using `match_minima.py`

1. Generate input file with [1] specified methods, [2] SDF filenames, and [3] whether or not to use single point energy calculations (True=SPE, False=OPT).
2. Match the molecules between different files.
    * `python ../../../match_minima.py -i match.in --eplot --tplot --verbose > match.out`
    * Consider requesting an interactive job on the cluster, as this can be pretty intensive.
    * This example has 1 molecule with ~20 conformers geometry optimized with 3 methods. So `match_minima` will perform a 20x20x20 molecule RMSD comparison.
    * Just the `refA` set took about 5 minutes (see `time.out` file).
    * The `match.out` files in this example have a bunch of numbers output for debugging/refinement. These have since been removed.
3. Plot results of match. Here, we'll read in the pickle file to not waste time re-matching. 
    * `python ../../match_minima.py -i match.in --readpickle --eplot --tplot`
    * Rename other image files *beforehand* to not be overwritten. [TODO: add detail; circumvent this]
    * Do not specify verbose flag to prevent overwriting dat files. 
    * Can specify either `eplot` or `tplot`, or both.
    * Can finagle plotting options, such as to only plot data from first and third files. To do this, edit `match_minima.py`:
       * For _time_ plot: edit `to_exclude` variable to exclude specific files. Ex: `to_exclude={1}`
       * For _ene_  plot: edit call to `plot_mol_minima` function and specify the parameter for `selected`. Ex: `plot_mol_minima(name, minE, thryList, selected=[0,2])`
       * TODO: make this consistent ^
4. Repeat steps 1-2 (step 3 optional) with other methods as reference. The order of the other input files should have the new reference method as the **first** line.
    * For example, compare `refA/match.in`, `refB/match.in`, `refC/match.in`.
    * Have each reference comparison in a separate directory.

## Instructions for using `match_plot.py`

Further analyze `match_minima` results by using `match_plot.py` which can generate three kinds of plots:  
(1) **RMSE heat plots** of all methods compared to all methods,  
(2) **time heat plots** of all methods compared to all methods, and  
(3) **scatter plots** of (log) ratio of wall time vs. RMSE using each method as reference.  

1. If you have multiple molecules, create directories for each, such as `mol0`, `mol1`, `mol2`, etc.
    * Only one mol in this example.
2. Generate input file similar to the `match_minima` input file except that it uses the `dat` files that were output from the `match_minima.py` script.
    * There should be one input file for each molecule.
    * Doesn't require SPE/OPT specification.
3. Call Python command for each mol. Specify molecule name for plot title and figure name.
    * `python ../../../match_plot.py -i heat.in -t test_mol --theatplot --eheatplot --etscatter`
    * Each one can be called individually (either `--theatplot` or `--eheatplot` or `--etscatter`).
    * To generate a single scatter plot, example: `python match_plot.py -i ../ref07/relene_Div_5.dat -t Div_5_fancy --onescatter`

