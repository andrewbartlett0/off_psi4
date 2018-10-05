
# Normalize atom indices between two conformers of the same molecule

Version: Oct 5 2018

This is an example application of the `matchTwoMols.py` script in the `tools` subdirectory.
We have a force field structure (`DrugBank_d3670.mol2`) and want to compare that to the QM structure (`DrugBank_d3670-220.sdf`).
However, the atom indices do not match. For example C3 in the mol2 file goes with C10 in sdf file.

Contents:
* `DrugBank_d3670.mol2` - Reference mol2 file with GAFF-minimized coordinates. 
* `DrugBank_d3670-220.sdf` - QM-minimized coordinates from using the GAFF structure as input.
* `output.mol2` - Adjusted QM coordinates with atom indices renumbered in accordance with mol2

Command:
* `python matchTwoMols.py DrugBank_d3670.mol2 DrugBank_d3670-220.sdf output.mol2`

**Caveat**: As noted in the header of the script, this is not a perfect alignment.
In this case, the heavy atoms are mostly correct but C8 and C10 should probably be switched.
For the hydrogen atoms, they are correctly assigned to their parent atoms, but the indices of H4 and H5 should be flip-flopped (among others).

