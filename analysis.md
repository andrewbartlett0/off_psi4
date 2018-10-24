/* vim: set filetype=markdown : */


# Analyzing Quanformer Results

Document last updated: Oct 23 2018   
This file describes and guides the user through various analyses that can be conducted from different implementations of Quanformer.


## Comparing sets of geometry optimizations

**Prerequisites**
 * TODO

**Instructions**
 1. `matchMinima.py` -- [TODO write instructions]
 1. `matchPlot.py` -- [TODO write instructions]


--------------------------------------------------------------------------------


## Comparing sets of single point energy calculations

The relative energies for a set of molecules/conformers can be evaluated among various QM methods.
The same starting SDF file should be used in the various QM calculations, and no conformers should be "lost" (such as from redundant structures, incomplete optimizations).
This section is closely related to the one above of comparing sets of geometry optimizations, but it does not need to ensure matching structures.

**Prerequisites**
 * TODO

**Instructions**
 1. Create input file for `stitchSpe.py` -- see notes below.
 2. `python stitchSpe.py -i /path/and/input.dat --plotbars [--reffile filename.sdf]`
 3. (opt.) If some mol has a high RMSD, identify the outlying conformer and visualize structure. (see `writeOneMol` in examples)

**Output**
 1. Data file with relative energies, either by RMSD (if there is a reference file) or with avgs/stdevs (if no reference file)
 2. `barplot.png`

**Creating input file for analysis with `stitchSpe.py`**

 * This should be a text file directing the script to process a particular quantity.
 * The SDF files on each line should ALL have the same molecules, same conformers, etc. These may differ in coordinates or SD tags.
 * If you have one file that should be taken as reference for RMSD calculations of energy, specify that in the python call with `--reffile [filename]`.
 * Each line should contain these columns, comma-separated:
    1. Name of SDF file with full path
    2. Calculation type, either: 'spe' or 'opt'
    3. QM method
    4. QM basis set
 * Example input file:
```
 # comments begin with pound symbol and are ignored
 /path/and/setofMols-221-opt2.sdf, opt, b3lyp-d3mbj, def2-tzvp
 /path/and/setofMols-221-spe1.sdf, spe, b3lyp-d3mbj, def2-tzvp
 /path/and/setofMols-221-spe2.sdf, spe, mp2        , cc-pvtz
 /path/and/setofMols-221-spe3.sdf, spe, pbe0       , 6-311g**
```

--------------------------------------------------------------------------------


## Comparing energies before and after a set of geometry optimizations

**Prerequisites**
 1. `diffSpeOpt.py` -- [TODO write instructions]

**Instructions**
 * TODO


--------------------------------------------------------------------------------


## Interfacing with modified Seminario method

The modified Seminario method is a way to obtain force field parameters (force constants and equilibrium values) based on the connectivity and Hessian of a molecule.  

**Prerequisites**
 * SDF file with structures of all Hessian calculations
 * Pickle file with extracted Hessian data (from calling results with `executor.py`)

**Instructions**
Follow the three steps of preparing the modified Seminario code detailed at the top of `quan2modsem.py`.  
Then call the code. Example:
 *  python quan2modsem.py -i carbon-hess.sdf -p carbon-hess.hess.pickle

**Output**
Each conformer's directory will have the three files:
 * `Modified_Seminario_Angle`
 * `Modified_Seminario_Bonds`
 * `MSM_log`

**References**

* [Modified Seminario method theory](10.1021/acs.jctc.7b00785)
* [Modified Seminario method code](https://github.com/aa840/ModSeminario_Py)




