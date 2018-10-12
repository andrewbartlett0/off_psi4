/* vim: set filetype=markdown : */


# Analyzing Quanformer results

README last updated: Oct 12 2018  


## Analyzing sets of geometry optimizations

 1. `matchMinima.py` -- [TODO write instructions]


## Analyzing sets of single point energy calculations

 1. See subsection below on "Creating input file for stitchSpe.py"
 2. `python stitchSpe.py -i /path/and/input.dat --barplots`
 3. (opt.) If some mol has a high RMSD, identify the outlying conformer and visualize structure. (see examples directory of `writeOneMol`)


### Creating input file for analysis with `stitchSpe.py`

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


## Extracting Hessian matrices, such as for the modified Seminario method:

 1. `oe2modsem.py` [TODO instructions and reference]


## References



