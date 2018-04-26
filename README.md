
# QM Pipeline
Version: 2018-04-25

This repository contains a pipeline for generating large sets of QM-optimized molecules using Psi4 or Turbomole.  
For each molecule, conformers are generated then MM-optimized. The user can set up QM geometry optimizations or  
single point energy (SPE) calculations with the desired method. For example, one may choose to do a quick   
fine-tuning geometry optimization with the MP2/def2-SV(P) level of theory, then using the results of those  
calculations for a more intensive B3LYP-D3MBJ/def2-TZVP geometry optimization. 

## Repository contents

Pipeline components and description:

| Script               | Stage     | Brief description                                                          |
| ---------------------|-----------|----------------------------------------------------------------------------|
| `confs2psi.py`       | setup     | generate Psi4 input files for each conformer/molecule                      |
| `confs2turb.py`      | setup     | generate Turbomole input files for each conformer/molecule                 |
| `diffSpeOpt`         | analysis  | compare how diff OPT energy is from pre-OPT single point energy            |
| `executor.py`        | N/A       | main interface connecting "setup" and "results" scripts for Psi4           |
| `filterConfs.py`     | setup     | remover conformers of molecules that may be same structure                 |
| `getPsiResults.py`   | results   | get job results from Psi4                                                  |
| `getTurbResults.py`  | results   | get job results from Turbomole                                             |
| `matchMinima.py`     | analysis  | match conformers from sets of different optimizations                      |
| `matchPlot.py`       | analysis  | additional plots that can be used from `matchMinima.py` results            |
| `plotTimes.py`       | analysis  | plot calculation time averaged over the conformers for each molecule       |
| `procTags.py`        | results   | store QM energies & conformer details as data tags in SDF molecule files   |
| `smi2confs.py`       | setup     | generate molecular structures and conformers for input SMILES string       |
| `stitchSpe.py`       | analysis  | calculate relative conformer energies from sets of different SPEs          |


There are other scripts in this repository that are not integral to the pipeline. These are found in the `tools` directory.

| Script               | Brief description
| ---------------------|----------------------------------------------------------------------------------------|
| `catMols.py`         | concatenates molecules from various files into single output file                      |
| `cleanfromvmd.py`    | clean molecules that were filtered ad hoc through VMD                                  |
| `findIntraHB.py`     | identify molecules that may have internal hydrogen bonding                             |
| `loadFromXYZ.py`     | copy coordinates from XYZ to MOL2 file                                                 |
| `selectConfs.tcl`    | script for VMD to further filter molecule set, e.g., by some internal distance         |
| `viewer.ipynb`       | visualize molecules in iPython notebook                                                |
| `writeOneConf.py`    | write out a single conformer of specified molecule based on tagged identifier          |
| `xyzByStep.sh`       | simple Bash processing of Psi4 output file to see geometries throughout optimization   |


## Python Dependencies

  * [OEChem Python Toolkit](https://docs.eyesopen.com/toolkits/python/quickstart-python/install.html)
  * [Psi4 QM software package](http://www.psicode.org/)
     * [Conda install](http://www.psicode.org/psi4manual/master/conda.html) of Psi4 recommended
     * [Conda install of dftd3](http://www.psicode.org/psi4manual/master/dftd3.html)


## Output files throughout the pipeline

SDF files are numbered with the following code system. Let's say the pipeline starts with a file called `basename.smi`  
and contains the list of SMILES strings.
1. The first file generated will be `basename.sdf`. This contains all molecules and all conformers of each molecule.
2. The next file will be `basename-100.sdf`, where `-100` means all molecules have been MM-optimized.
3. Then comes `basename-200.sdf`, in which the MM-optimized molecules are filtered to remove any redundant structures (i.e., duplicate minima).
4. After that is `basename-210.sdf`, which contains the QM-calculated molecules of the `-200` file.
5. The QM molecules are filtered analogously to step 3 to yield `basename-220.sdf`.

This process can go through a second round of QM calculations. QM calculations can be either geometry optimizations or  
single point energy calculations. If the `basename-200.sdf` is fed into each route, then each route will have its own  
`basename-210.sdf` file. Don't do this in the same directory obviously, else one file will be overwritten. The endmost  
product will be `basename-222.sdf` though one could certainly stop before QM stage 2.

Why bother keeping the `-221` files? They can be used to compare relative energies of single point energy calculations,  
or geometry optimizations, since (mol1,confA) will start from the same structure of the compared files. After filtering,  
the number of conformers may be reduced, so it can be hard to compare one to one.

An `-f` prefix means that the Omega-generated conformers were filtered based on their structures, but that these have not  
been MM-optimized. For example, `basename-f020.sdf` means filtered from OpenEye Omega, no MM opt/filter, yes QM opt/filter, no QM stage 2.

In summary,

 * no suffix = original file with all omega conformers
 * `1xx` = MM opt but no filter
 * `2xx` = MM opt and filter
 * `x1x` = QM opt but no filter
 * `x2x` = QM opt and filter
 * `xx1` = either QM second opt or SPE and no filter
 * `xx2` = either QM second opt or SPE and filter


## Instructions

Execute these commands in the directory that you want input/output files to be generated.
Before starting, you need an input file with a list of SMILES strings and corresponding molecule titles.
See section on "Naming molecules in the input SMILES file" and "File name limitations".

 1. Generate conformers, quick MM optimization, Psi4 input files.
    * `python executor.py -f file.smi --setup -m 'mp2' -b 'def2-sv(p)'`

 2. Run Psi4 jobs.

 3. Get Psi4 results from the last set of optimizations.
    * `python executor.py -f /include/full/path/to/file-200.sdf --results -m 'mp2' -b 'def2-sv(p)'`

 4. In a new (sub)directory, set up Psi4 OPT2 calculations from last results.
    * `python executor.py -f /include/full/path/to/file-220.sdf --setup -m 'b3lyp-d3mbj' -b 'def2-tzvp'`
    * [for SPE] `python executor.py -f /include/full/path/to/file-220.sdf --setup --spe -m 'b3lyp-d3mbj' -b 'def2-tzvp'`

 5. Run Psi4 jobs.
    * `xyzByStep.sh 10 output.dat view.xyz` -- can use to view geometry during optimizations. (replace 10 with number of atoms.)

 6. Get Psi4 results from second-level calculations.
    * `python executor.py -f /include/full/path/to/file-220.sdf --results -m 'b3lyp-d3mbj' -b 'def2-tzvp'`
    * [for SPE] `python executor.py -f /include/full/path/to/file-220.sdf --results --spe -m 'b3lyp-d3mbj' -b 'def2-tzvp'`

 7. Combine results from various job types to calculate model uncertainty.
    * See section on "Creating input file for stitchSpe.py"
    * `python /data12/cmf/limvt/qm_AlkEthOH/pipeline/01_scripts/stitchSpe.py -i /path/and/input.dat --barplots`

 8. (opt.) If some mol has a high RMSD, identify conformer and visualize structure.
    * `python /data12/cmf/limvt/qm_AlkEthOH/pipeline/01_scripts/writeOneConf.py  ___TODO___`

 9. (opt.) Get wall clock times, num opt steps, relative energies. 
    * `python /data12/cmf/limvt/qm_AlkEthOH/pipeline/01_scripts/avgTimeEne.py --relene -f /path/&/file.sdf -m 'b3lyp-d3mbj' -b 'def2-tzvp'`

## Important Notes

### File name limitations

Base names (e.g. `basename.smi`, `basename.sdf`) can contain underscores but NO dashes or dots.
  * Dash is used for SDF numbering code (see above).
  * Dot is used for splitting based on file extension.
  * Examples:
    * Good: `basename_set1.smi`
    * Bad:  `basename-set1.smi`
    * Bad:  `basename.set1.smi`

### Naming molecules in the input SMILES file

Smiles file should contain, in each line: `SMILES_STRING molecule_title` and be named in format of `basename.smi`.
  * Molecule title should have no dashes, as Psi4 will raise an error.
  * Molecule title should NOT start with a number, as Psi4 will raise error.
  * Example:
```
CC(C(C(C)O)O)O AlkEthOH_c42
CCCC AlkEthOH_c1008
CCOC(C)(C)C(C)(C)O AlkEthOH_c1178
```

### Creating input file for `stitchSpe.py`

 * This should be a text file directing the script to process a particular quantity.
 * The first uncommented line should be the keyword of the specific quantity (e.g., energy) found in the SD tag label.
 * Following lines should contain the following information in order, separated by a comma:
    * sdf file with full path
    * Boolean, True if SPE, False if optimization
    * method
    * basis set
 * The first sdf file listed will be the reference values for all following lines when computing RMSDs.
 * The sdf files on each line should ALL have the same molecules, same conformers, etc. These may differ in coordinates or SD tags.
 * Example:

```
 # comments begin with pound symbol and are ignored

 energy

 /path/and/setofMols-221-opt2.sdf, False, b3lyp-d3mbj ,    def2-tzvp
 /path/and/setofMols-221-spe1.sdf, True , b3lyp-d3mbj ,    def2-tzvp
 /path/and/setofMols-221-spe2.sdf, True , mp2,  cc-pvtz ,
 /path/and/setofMols-221-spe3.sdf, True , pbe0, 6-311g**
```


## Some terms

 * Pertaining to method
   * MP2 - second order Moller-Plesset perturbation theory (adds electron corr effects upon Hartree-Fock)
   * B3LYP - DFT hybrid functional, (Becke, three-parameter, Lee-Yang-Parr) exchange-correlation functional
   * PBE0 - DFT functional hybrid functional, (Perdew–Burke-Ernzerhof)
   * D3 - Grimme et al. dispersion correction method
   * D3BJ - D3 with Becke-Johnson damping
   * D3MBJ - Sherrill et al. modifications to D3BJ approach

 * Pertaining to basis set
   * def2 - 'default' basis sets with additional polarization fx compared to 'def-'
   * SV(P) - double zeta valence with polarization on all non-hydrogen atoms
   * TZVP - triple zeta valence with polarization on all atoms

## Potential errors and how to get around them [TODO]
 * `KeyError` from processing results. Did you specify spe for single point calculations?
 * Segmentation fault from ....

## References
 * [Psi4]()
 * [Turbomole]()
 * DFT-D3 dispersion: [A consistent and accurate ab initio parametrization of density functional dispersion correction (DFT-D) for the 94 elements H-Pu](http://aip.scitation.org/doi/full/10.1063/1.3382344)
 * BJ-damping: [Effect of the damping function in dispersion corrected density functional theory](http://onlinelibrary.wiley.com/doi/10.1002/jcc.21759/abstract)
 * Modifications of D3BJ: [Revised damping parameters to D3 Dispersion Correction to Density Functional Theory](http://pubs.acs.org/doi/abs/10.1021/acs.jpclett.6b00780)
