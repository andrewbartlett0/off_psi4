
# Auxiliary scripts for Quanformer
Last updated: Dec 19 2018

Also see [this list](http://vergil.chemistry.gatech.edu/resources/utilities.html) from the Sherrill group.  

| Script                | Description
| ----------------------|----------------------------------------------------------------------------------------|
| `catMols.py`          | concatenates molecules from various files into single output file                      |
| `cleanfromvmd.py`     | clean molecules that were filtered ad hoc through VMD                                  |
| `convertExtension.py` | read in mol from one file type and write out to another file type                      |
| `findIntraHB.py`      | identify molecules that may have internal hydrogen bonding                             |
| `jobcount.sh`         | count total number of conformer calculations as well as number of unfinished jobs      |
| `loadFromXYZ.py`      | copy coordinates from XYZ to MOL2 file                                                 |
| `matchTwoMols.py`     | read in a molecule from two distinct files and match their atom indices                |
| `selectConfs.tcl`     | script for VMD to further filter molecule set, e.g., by some internal distance         |
| `viewer.ipynb`        | visualize molecules in iPython notebook                                                |
| `write_first_confs.py`| write out first conformers of all molecules                                            |
| `writeOneMol.py`      | write out single mol and all its conformers OR single conformer of specified mol       |
| `xyzByStep.sh`        | simple Bash processing of Psi4 output file to see geometries throughout optimization   |

Other helpful scripts:
 * [This list](http://vergil.chemistry.gatech.edu/resources/utilities.html) from the Sherrill group
 * [OpenEye script](https://docs.eyesopen.com/toolkits/python/oechemtk/oechem_examples/oechem_example_molextract.html) to extract molecules by title
 * [OpenEye script](https://docs.eyesopen.com/toolkits/cookbook/python/_downloads/ecdfcd69f00dc4e2d4e0f826e749b6b0/moldb_titlesort.py) to sort molecules by title

