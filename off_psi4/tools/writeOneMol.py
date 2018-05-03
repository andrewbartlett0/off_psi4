#!/usr/bin/env python

"""
This script writes out either (1) a single molecule from a multi-molecule file
or (2) a single conformer of some mol from file having many molecules
with multiple conformers of each. This script can be used, for example, to
isolate specific conformers that lead to a high RMSD energy value for a particular molecule.

Usage: python writeOneMol.py -f inputfile.sdf -t molName -s sdtag -v tagvalue -x filesuffix

By: Victoria T. Lim

"""

import os, sys
import openeye.oechem as oechem
import argparse


### ------------------- Script -------------------

def write_conf_mol(outfn, mol):
    """


    Parameters
    ----------
    outfn : str
        Filename of the output file
    mol : OpenEye oemol
        Single or multi-conformer molecule to write to output

    """

    ofs = oechem.oemolostream()
    if not ofs.open(outfn):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % outfn)
    oechem.OEWriteConstMolecule(ofs, mol)
    ofs.close()

def main(**kwargs):
    outfn = os.path.splitext(opt['infn'])[0]+'_'+opt['suffix']+'.mol2'
    success = False

    ### Read in .sdf file and distinguish each molecule's conformers
    ifs = oechem.oemolistream()
    ifs.SetConfTest( oechem.OEAbsoluteConfTest() )
    if not ifs.open(opt['infn']):
        oechem.OEThrow.Warning("Unable to open %s for reading" % opt['infn'])
        return

    for mol in ifs.GetOEMols():
        if mol.GetTitle() == opt['title']:
            # write out all confs in this mol if no SD tag is specified
            if opt['sdtag'] == "":
                success = True
                write_conf_mol(outfn, mol)
                return
            # look for the conformer in this mol with specific SD tag value
            for i, conf in enumerate( mol.GetConfs()):
                if oechem.OEGetSDData(conf, opt['sdtag']) == opt['value']:
                    success = True
                    write_conf_mol(outfn, conf)
    if not success:
        print("\n** Found no confs matching your criteria. **")
    ifs.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--infn", required=True,
        help="Name of input SDF file from which to write out the conformer.")
    parser.add_argument("-t", "--title", required=True,
        help="Molecule name in the file.")
    parser.add_argument("-s", "--sdtag", default="",
        help="SD tag to search for conformer. Leave blank if you want all conformers of this molecule.")
    parser.add_argument("-v", "--value",
        help="Value of the SD tag to write out that conformer.")
    parser.add_argument("-x", "--suffix",
        help="Suffix appened to input fn when writing out this conf.")

    args = parser.parse_args()
    opt = vars(args)

    ### Check that input file exists.
    if not os.path.exists(opt['infn']):
        raise parser.error("Error: Input file %s does not exist. Try again." % opt['infn'])
    ### Check that value was specified if SD tag was specified
    if opt['sdtag'] != "" and opt['value'] is None:
        raise parser.error("Error: Specify a value for the SD tag to be searched.")

    main(**opt)

