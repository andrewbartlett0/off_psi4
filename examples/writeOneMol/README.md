
# Example use of `writeOneMol.py` script in the tools subdirectory

The file `molecules.sdf` contains two molecules named `AlkEthOH_c1178` and `GBI`.  

`AlkEthOH_c1178` has 5 conformers, and `GBI` has 2 conformers, for a total  
of 7 structures in the SDF file.

* To write out all conformer for the `GBI` molecule:  
  `python writeOneMol.py -f molecules.sdf -t GBI -x 1`
* To write out conformer 3 of the `AlkEthOH_c1178` molecule:  
  `python writeOneMol.py -f molecules.sdf -t AlkEthOH_c1178 -s "Original omega conformer number" -v 3 -x 2`

