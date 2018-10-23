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


## Comparing sets of single point energy calculations

**Prerequisites**
 * TODO

**Instructions**
 1. Create input file for `stitchSpe.py` -- see notes below.
 2. `python stitchSpe.py -i /path/and/input.dat --barplots`
 3. (opt.) If some mol has a high RMSD, identify the outlying conformer and visualize structure. (see `writeOneMol` in examples)


**Creating input file for analysis with `stitchSpe.py`**

 * This should be a text file directing the script to process a particular quantity.
 * The first uncommented line should be the keyword of the specific quantity (e.g., energy) found in the SD tag label.
 * Following lines should contain the following information in order, separated by a comma:
    * SDF file with full path
    * Boolean: True for SPE values, False for optimization values
    * method
    * basis set
 * The first SDF file listed will be the reference values for all following lines when computing RMSDs.
 * The SDF files on each line should ALL have the same molecules, same conformers, etc. These may differ in coordinates or SD tags.
 * Example:

```
 # comments begin with pound symbol and are ignored

 energy

 /path/and/setofMols-221-opt2.sdf, False, b3lyp-d3mbj ,    def2-tzvp
 /path/and/setofMols-221-spe1.sdf, True , b3lyp-d3mbj ,    def2-tzvp
 /path/and/setofMols-221-spe2.sdf, True , mp2         ,    cc-pvtz
 /path/and/setofMols-221-spe3.sdf, True , pbe0        ,    6-311g**
```

## Comparing energies before and after a set of geometry optimizations

**Prerequisites**
 1. `diffSpeOpt.py` -- [TODO write instructions]

**Instructions**
 * TODO


## Extracting a set of Hessian matrices for the modified Seminario method:

**Prerequisites**
 * SDF file with structures of all Hessian calculations
 * Pickle file with extracted Hessian data (from calling results with `executor.py`)

**Instructions**
Follow the three steps of preparing the modified Seminario code detailed at the top of `quan2modsem.py`.  
Then call the code. Example:
 *  python quan2modsem.py -i carbon-hess.sdf -p carbon-hess.hess.pickle

**References**

* [Modified Seminario method theory](10.1021/acs.jctc.7b00785)
* [Modified Seminario method code](https://github.com/aa840/ModSeminario_Py)




