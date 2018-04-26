
# QM Pipeline
README last updated: 2018-04-26

This repository contains a pipeline for generating large sets of QM-optimized molecules using Psi4 or Turbomole.  
For each molecule, conformers are generated then MM-optimized. The user can set up QM geometry optimizations or  
single point energy (SPE) calculations with the desired method. For example, one may choose to do a quick   
fine-tuning geometry optimization with the MP2/def2-SV(P) level of theory, then using the results of those  
calculations for a more intensive B3LYP-D3MBJ/def2-TZVP geometry optimization. 

## I. Repository contents

Pipeline components and description:

| Script               | Stage         | Brief description                                                          |
| ---------------------|---------------|----------------------------------------------------------------------------|
| `confs2psi.py`       | setup         | generate Psi4 input files for each conformer/molecule                      |
| `confs2turb.py`      | setup         | generate Turbomole input files for each conformer/molecule                 |
| `diffSpeOpt.py`      | analysis      | compare how diff OPT energy is from pre-OPT single point energy            |
| `executor.py`        | N/A           | main interface connecting "setup" and "results" scripts for Psi4           |
| `filterConfs.py`     | setup/results | remover conformers of molecules that may be same structure                 |
| `getPsiResults.py`   | results       | get job results from Psi4                                                  |
| `getTurbResults.py`  | results       | get job results from Turbomole                                             |
| `matchMinima.py`     | analysis      | match conformers from sets of different optimizations                      |
| `matchPlot.py`       | analysis      | additional plots that can be used from `matchMinima.py` results            |
| `plotTimes.py`       | analysis      | plot calculation time averaged over the conformers for each molecule       |
| `procTags.py`        | results       | store QM energies & conformer details as data tags in SDF molecule files   |
| `smi2confs.py`       | setup         | generate molecular structures and conformers for input SMILES string       |
| `stitchSpe.py`       | analysis      | calculate relative conformer energies from sets of different SPEs          |

**Example workflow**:
`smi2confs.py` &rarr; `confs2psi.py` &rarr; `filterConfs.py` &rarr; \[QM jobs\] &rarr; `filterConfs.py` &rarr; analysis

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


## II. Python Dependencies

  * [OEChem Python Toolkit](https://docs.eyesopen.com/toolkits/python/quickstart-python/install.html)
  * [Psi4 QM software package](http://www.psicode.org/)
     * [Conda install](http://www.psicode.org/psi4manual/master/conda.html) of Psi4 recommended
     * [Conda install of dftd3](http://www.psicode.org/psi4manual/master/dftd3.html)


## III. Output files throughout the pipeline

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


## IV. Instructions
This section lists instructions on how to take a set of molecules from their starting SMILES strings to:
 * Generate conformers
 * MM minimize those conformers using the MMFF94S force field
 * Filter out potentially redundant structures
    * Output: `file-200.sdf`
 * Create Psi4 input files for MP2/def2-SV(P) geometry optimizations
 * Extract results from completed Psi4 jobs
    * Output: `file-210.sdf`
 * Filter out potentially redundant structures
    * Output: `file-220.sdf`
 * Create new Psi4 input files for B3LYP/def2-TZVP geometry optimizations
 * Extract results from completed Psi4 jobs
    * Output: `file-221.sdf`
 * Filter out potentially redundant structures
    * Output: `file-222.sdf`

Before starting, you need an input file (here called `file.smi`) with your list of SMILES strings and molecule titles.
See subsections below on "Naming molecules in the input SMILES file" and "File name limitations".
TODO: I don't think the full path is required in many of these commands anymore. Need to verify.

 1. Generate conformers, perform quick MM optimization, and create Psi4 input files.
    * `python executor.py -f file.smi --setup -m 'mp2' -b 'def2-sv(p)'`

 2. Run Psi4 QM calculations.
    * You can check the geometry during optimization with the `xyzByStep.sh` script in the tools directory.  
      E.g., `xyzByStep.sh 10 output.dat view.xyz`

 3. Get Psi4 results.
    * `python executor.py -f /include/full/path/to/file-200.sdf --results -m 'mp2' -b 'def2-sv(p)'`

 4. In a different directory (e.g., subdirectory), set up Psi4 OPT2 calculations from last results.
    * [for stage 2 OPT] `python executor.py -f /include/full/path/to/file-220.sdf --setup -m 'b3lyp-d3mbj' -b 'def2-tzvp'`
    * [for stage 2 SPE] `python executor.py -f /include/full/path/to/file-220.sdf --setup --spe -m 'b3lyp-d3mbj' -b 'def2-tzvp'`

 5. Run Psi4 jobs.
    * You can check the geometry during optimization with the `xyzByStep.sh` script in the tools directory.  
      E.g., `xyzByStep.sh 10 output.dat view.xyz`

 6. Get Psi4 results from second-level calculations.
    * [for stage 2 OPT] `python executor.py -f /include/full/path/to/file-220.sdf --results -m 'b3lyp-d3mbj' -b 'def2-tzvp'`
    * [for stage 2 SPE] `python executor.py -f /include/full/path/to/file-220.sdf --results --spe -m 'b3lyp-d3mbj' -b 'def2-tzvp'`

 7. Combine results from various job types to calculate model uncertainty.
    * See subsection below on "Creating input file for stitchSpe.py"
    * `python /data12/cmf/limvt/qm_AlkEthOH/pipeline/01_scripts/stitchSpe.py -i /path/and/input.dat --barplots`

 8. (opt.) If some mol has a high RMSD, identify the outlying conformer and visualize structure.
    * `python /data12/cmf/limvt/qm_AlkEthOH/pipeline/01_scripts/writeOneConf.py  ___TODO___`

 9. (opt.) Get wall clock times, num opt steps, relative energies. 
    * `python /data12/cmf/limvt/qm_AlkEthOH/pipeline/01_scripts/avgTimeEne.py --relene -f /include/full/path/to/file.sdf -m 'b3lyp-d3mbj' -b 'def2-tzvp'`

### A. File name limitations

Base names (e.g. `basename.smi`, `basename.sdf`) can contain underscores but NO dashes or dots.
  * Dash is used for SDF numbering code (see above).
  * Dot is used for splitting based on file extension.
  * Examples:
    * Good: `basename_set1.smi`
    * Bad:  `basename-set1.smi`
    * Bad:  `basename.set1.smi`

### B. Naming molecules in the input SMILES file

Smiles file should contain, in each line: `SMILES_STRING molecule_title` and be named in format of `basename.smi`.
  * Molecule title should have no dashes, as Psi4 will raise an error.
  * Molecule title should NOT start with a number, as Psi4 will raise error.
  * Example:
```
CC(C(C(C)O)O)O AlkEthOH_c42
CCCC AlkEthOH_c1008
CCOC(C)(C)C(C)(C)O AlkEthOH_c1178
```

### C. Creating input file for analysis with `stitchSpe.py`

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

## V. Potential errors and how to get around them [TODO]
 * `KeyError` from processing results. Did you specify spe for single point calculations?
 * Segmentation fault from ....


## VI. Some terms and references

Pertaining to software packages:
 * [Psi4](http://www.psicode.org/)
 * [Turbomole](http://www.turbomole.com/)

Pertaining to files and formatting:
  * SMILES - simplified molecular input line entry system, ([more info](http://www.daylight.com/dayhtml/doc/theory/theory.smiles.html))
  * SDF - structure data file, ([more info](http://link.fyicenter.com/out.php?ID=571), [example](http://biotech.fyicenter.com/resource/sdf_format.html))

Pertaining to QM method:
  * `MP2` - second order Moller-Plesset perturbation theory (adds electron correlation effects upon Hartree-Fock)
  * `B3LYP` - DFT hybrid functional, (Becke, three-parameter, Lee-Yang-Parr) exchange-correlation functional
  * `PBE0` - DFT functional hybrid functional, (Perdew–Burke-Ernzerhof)
  * `D3` - Grimme et al. dispersion correction method, ([ref](http://aip.scitation.org/doi/full/10.1063/1.3382344))
  * `D3BJ` - D3 with Becke-Johnson damping, ([ref](http://onlinelibrary.wiley.com/doi/10.1002/jcc.21759/abstract))
  * `D3MBJ` - Sherrill et al. modifications to D3BJ approach, ([ref](http://pubs.acs.org/doi/abs/10.1021/acs.jpclett.6b00780))

Pertaining to basis set:
  * `def2` - 'default' basis sets with additional polarization fx compared to 'def-'
  * `SV(P)` - double zeta valence with polarization on all non-hydrogen atoms
  * `TZVP` - triple zeta valence with polarization on all atoms

