#!/usr/bin/env python

"""
Extract the first conformers of each molecule from a multi-molecule, multi-conformer file.

Usage: python write_first_confs.py -f inputfile.sdf -o outputfile.sdf

By: Victoria T. Lim

"""

import os, sys
import openeye.oechem as oechem
import argparse


### ------------------- Script -------------------


def write_first_confs(infile, outfile):

    ### Read in .sdf file and distinguish each molecule's conformers
    ifs = oechem.oemolistream()
    ifs.SetConfTest( oechem.OEAbsoluteConfTest() )
    if not ifs.open(infile):
        oechem.OEThrow.Warning("Unable to open %s for reading" % infile)
        return

    ### Open output file
    ofs = oechem.oemolostream()
    if not ofs.open(outfile):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % outfile)

    for mol in ifs.GetOEMols():
        conf = mol.GetConf(oechem.OEHasConfIdx(0))
        oechem.OEWriteConstMolecule(ofs, conf)
    ifs.close()
    ofs.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--infile", required=True,
        help="Name of input SDF file.")
    parser.add_argument("-o", "--outfile", required=True,
        help="Name of output SDF file.")

    args = parser.parse_args()

    ### Check that input file exists.
    if not os.path.exists(args.infile):
        raise parser.error("Error: Input file %s does not exist. Try again." % args.infile)

    write_first_confs(args.infile, args.outfile)

