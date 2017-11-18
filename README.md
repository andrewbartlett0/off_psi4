
# TODO
Version: 2017-11-17
Add python script descriptions, add example set.
Update instructions.

# Overview

This repository contains a pipeline for generating large sets of QM-optimized molecules using Psi4/Turbomole.  
For each molecule, conformers are [1] generated, then [2] MM-optimized. Then the user can setup QM geometry  
optimizations or single point energy (SPE) calculations with the desired method. For example, this may entail  
a quick fine-tuning QM calculation with the MP2/def2-SV(P) level of theory, then using the results of those  
calculations for a more intensive B3LYP-D3MBJ/def2-TZVP geometry optimization. 

## Repository contents
Pipeline components and description:

  * confs2psi.py
  * confs2turb.py
  * executor.py
  * filterConfs.py
  * getPsiResults.py
  * getTurbResults.py
  * matchMinima.py
  * matchPlot.py
  * procTags.py
  * smi2confs.py
  * stitchSpe.py

There are other scripts in this repository that are not integral to the pipeline:
  * catMols.py
  * cleanfromvmd.py
  * findIntraHB.py
  * loadFromXYZ.py
  * plotTimes.py
  * selectConfs.tcl
  * viewer.ipynb
  * writeOneConf.py

## Python Dependencies

  * [OEChem Python Toolkit](https://docs.eyesopen.com/toolkits/python/quickstart-python/install.html)
  * [Psi4 QM software package](http://www.psicode.org/)
     * [Conda install](http://www.psicode.org/psi4manual/master/conda.html) of Psi4 recommended
     * [Conda install of dftd3](http://www.psicode.org/psi4manual/master/dftd3.html)


## Output files throughout the pipeline

 SDF files are numbered with the following code system.
 Here, x is used as a placeholder for either 0, 1, or 2.

 * no suffix = original file with all omega conformers
 * 1xx = MM opt but no filter
 * 2xx = MM opt and filter
 * x1x = QM opt but no filter
 * x2x = QM opt and filter
 * xx1 = either QM second opt or SPE and no filter
 * xx2 = either QM second opt or SPE and filter

The starting filename is `basename.sdf` and the final filename code is `basename-222.sdf`.
The `-221` files can be used to compare relative energies of single pt energy calcns,
without energy filtering to remove conformers deemed to be alike.

An `-f` prefix means filtered but no MM. For example, `basename-f020.sdf` means 
filtered from orig, no MM opt/filter, QM opt/filter, and no second QM stage.


## Instructions
Execute these commands in the directory that you want input/output files to be generated.
Before starting, you need an input file with a list of SMILES strings and corresponding molecule titles.
See section on "Naming molecules in the input SMILES file" and "File name limitations".

 1. Generate conformers, quick MM optimization, Psi4 input files.
     * python executor.py -f file.smi --setup -m 'mp2' -b 'def2-sv(p)'

 2. Run Psi4 jobs.

 3. Get Psi4 results from the last set of optimizations.
     * python executor.py -f /include/full/path/to/file-200.sdf --results -m 'mp2' -b 'def2-sv(p)'

 4. In a new (sub)directory, set up Psi4 SPE calculations from last results.
     * python executor.py -f /include/full/path/to/file-220.sdf --setup --spe -m 'b3lyp-d3mbj' -b 'def2-tzvp'

 5. Run Psi4 jobs.

 6. Get Psi4 results from SPE.
     * python executor.py -f /include/full/path/to/file-220.sdf --results --spe -m 'b3lyp-d3mbj' -b 'def2-tzvp'

 7. Combine results from various job types to calculate model uncertainty.
     * See section on "Creating input file for stitchSpe.py"
     * mpython /data12/cmf/limvt/qm_AlkEthOH/pipeline/01_scripts/stitchSpe.py -i /path/and/input.dat --barplots

 8. (opt.) If some mol has a high RMSD, identify conformer and visualize structure.
     * mpython /data12/cmf/limvt/qm_AlkEthOH/pipeline/01_scripts/writeOneConf.py ...............

 9. (opt.) Get wall clock times, num opt steps, relative energies. 
     * mpython /data12/cmf/limvt/qm_AlkEthOH/pipeline/01_scripts/avgTimeEne.py --relene -f /path/&/file.sdf -m 'b3lyp-d3mbj' -b 'def2-tzvp'


### File name limitations

Base names (e.g. basename.smi, basename.sdf) can contain underscores but NO dashes or dots.
  * Dash is used for SDF numbering code (see below).
  * Dot is used for splitting based on file extension.

### Naming molecules in the input SMILES file

Smiles file should contain, in each line: "SMILESSTRING title" and be named in format of filename.smi.
  * Molecule title should have no dashes, as Psi4 will raise an error.
  * Molecule title should NOT start with a number, as Psi4 will raise error.

Examples:
  * CC(C(C(C)O)O)O AlkEthOH\_c42
  * CCCC AlkEthOH\_c1008
  * CCOC(C)(C)C(C)(C)O AlkEthOH\_c1178


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
 
 \# comments begin with pound symbol and are ignored
 
 energy
 
 /path/and/setofMols-221-opt2.sdf, False, b3lyp-d3mbj ,    def2-tzvp   
 /path/and/setofMols-221-spe1.sdf, True , b3lyp-d3mbj ,    def2-tzvp   
 /path/and/setofMols-221-spe2.sdf, True , mp2, cc-pvtz ,  
 /path/and/setofMols-221-spe3.sdf, True , pbe0, 6-311g\*\*


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

## Potential errors and how to get around them
 * `KeyError` from processing results. Did you specify spe for single point calculations?
 * Segmentation fault from ....

## References
 * [Psi4]()
 * [Turbomole]()
 * DFT-D3 dispersion: [A consistent and accurate ab initio parametrization of density functional dispersion correction (DFT-D) for the 94 elements H-Pu](http://aip.scitation.org/doi/full/10.1063/1.3382344)
 * BJ-damping: [Effect of the damping function in dispersion corrected density functional theory](http://onlinelibrary.wiley.com/doi/10.1002/jcc.21759/abstract)
 * Modifications of D3BJ: [Revised damping parameters to D3 Dispersion Correction to Density Functional Theory](http://pubs.acs.org/doi/abs/10.1021/acs.jpclett.6b00780)
